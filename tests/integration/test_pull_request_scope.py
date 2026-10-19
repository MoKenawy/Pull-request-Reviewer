"""The pull-request scope and the range scope, end to end — FR-10.3a/d (SRS v1.5), FR-10.3c, ADR-0011.

A local repository served over ``file://`` stands in for GitHub, so the real clone, fetch and three-dot diff run with
no network (SC-006). Every report is validated against the published schema, checked for invariants, scanned for the
planted credential, and checked for stage durations (SC-002, SC-007, SC-008).
"""

from __future__ import annotations

import tempfile
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage
from rich.console import Console
from typer.testing import CliRunner

from agentic_review.agents import pipeline_agent
from agentic_review.agents.pipeline_agent import ReviewRequest, Reviewed, run_review
from agentic_review.agents.review_port import build_review_port
from agentic_review.cli.app import app
from agentic_review.core.changeset.diff_parser import synthesise_added_file
from agentic_review.core.changeset.model import ChangedFile, ChangeSet
from agentic_review.core.changeset.pull_request import WORKSPACE_PREFIX, PullRequestError, PullRequestRef
from agentic_review.core.findings.report import ResolvedScope, ReviewReport
from agentic_review.core.output.json_out import to_json
from agentic_review.core.output.terminal import render_terminal
from agentic_review.core.pipeline.preflight import PreflightFailure
from tests.support.pull_request_remote import PR_URL, PullRequestRemote
from tests.support.repo_builder import RepoBuilder
from tests.support.report_assertions import (
    assert_invariants,
    assert_no_canary,
    assert_stage_durations,
    assert_valid_report,
)
from tests.support.scripted_chat_model import ScriptedChatModel, ai_reply, finding_call

ALL_STAGES = ("preflight", "changeSet", "assembly", "review", "output")
# One call per reviewed file: a reviewed file no call names costs a second turn (the coverage rule of CF-6).
FINDINGS = [
    finding_call(file="src/app.ts", startLine=21, endLine=21, rationale="The new export is never read."),
    finding_call(file="src/added.ts", startLine=2, endLine=2, severity="nit", rationale="Name says little."),
]


@pytest.fixture
def remote(pull_request_remote: PullRequestRemote) -> PullRequestRemote:
    return pull_request_remote


@pytest.fixture
def temp_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "tmp"
    root.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(root))
    return root


@pytest.fixture
def elsewhere(tmp_path: Path) -> Path:
    """A directory that is not inside any git repository: a pull request needs none."""
    directory = tmp_path / "elsewhere"
    directory.mkdir()
    return directory


def _factory(model: ScriptedChatModel) -> Callable[..., object]:
    return lambda settings, credential: build_review_port(settings, credential, chat_model=model)


def _render(report: ReviewReport) -> str:
    console = Console(record=True, width=240, no_color=True, force_terminal=False)
    render_terminal(report, console)
    return console.export_text()


def _check(report: ReviewReport) -> str:
    text = _render(report)
    document = to_json(report)
    assert_valid_report(document)
    assert_invariants(report)
    assert_no_canary(document, text)
    assert_stage_durations(report, ALL_STAGES)
    return text


def _leftovers(temp_root: Path) -> list[Path]:
    return sorted(temp_root.glob(f"{WORKSPACE_PREFIX}*"))


def _review_pull_request(
    remote: PullRequestRemote,
    cwd: Path,
    env: dict[str, str],
    script: Sequence[AIMessage],
    **request: object,
) -> tuple[ReviewReport, ScriptedChatModel]:
    model = ScriptedChatModel(script)
    result = run_review(
        ReviewRequest(cwd=cwd, pr=PR_URL, **request),  # type: ignore[arg-type]
        env=env,
        port_factory=_factory(model),
        pull_requests=remote.source(),
    )
    assert isinstance(result, Reviewed), result
    return result.report, model


# --- a pull request ---------------------------------------------------------------------------------------------------


def test_a_pull_request_is_reviewed_from_outside_any_repository(
    remote: PullRequestRemote, elsewhere: Path, temp_root: Path, canary_env: dict[str, str]
) -> None:
    report, model = _review_pull_request(remote, elsewhere, canary_env, [ai_reply(FINDINGS)])

    scope = report.change_summary.scope
    assert (scope.kind, scope.base_ref, scope.head_ref, scope.was_defaulted) == (
        "pull-request",
        "main",
        "refs/pull/7/head",
        False,
    )
    files = {f.path: f for f in report.change_summary.files}
    assert {path for path, f in files.items() if f.reviewed} == {"src/added.ts", "src/app.ts"}
    assert files["README.md"].not_reviewed_reason == "not-typescript-or-javascript"
    assert "src/untouched.ts" not in files  # what main did after the pull request branched
    assert [(e.path, e.rule) for e in report.change_summary.excluded] == [("dist/bundle.js", "default:build-output")]

    # Line 21 exists only at the pull request's head, so the finding proves validation read that version.
    assert [(f.file, f.start_line) for f in report.findings] == [("src/app.ts", 21), ("src/added.ts", 2)]
    assert report.verdict == "findings" and report.degradations == []

    sent = model.received[0][1].content
    assert "export const extra = true;" in sent and "src/added.ts" in sent
    assert "src/untouched.ts" not in sent and "dist/bundle.js" not in sent and "more words" not in sent

    text = _check(report)
    compared = f"({remote.branch_point}..{remote.head_commit})"
    assert f"pull request acme/widgets#7 against main, the default branch {compared}" in text
    assert "No checks were run in this build." in text
    assert _leftovers(temp_root) == []


def test_a_finding_beyond_the_pull_request_head_is_rejected(
    remote: PullRequestRemote, elsewhere: Path, temp_root: Path, canary_env: dict[str, str]
) -> None:
    def beyond() -> dict[str, object]:
        return finding_call(file="src/app.ts", startLine=22, endLine=22)

    script = [ai_reply([beyond(), FINDINGS[1]]), ai_reply([beyond()])]
    report, _ = _review_pull_request(remote, elsewhere, canary_env, script)
    assert [f.file for f in report.findings] == ["src/added.ts"]  # line 22 is past the end of the head version
    assert "invalid-model-output" in [d.code for d in report.degradations]


def test_configuration_inside_the_pull_request_is_not_honoured(
    remote: PullRequestRemote, elsewhere: Path, temp_root: Path, canary_env: dict[str, str]
) -> None:
    # The pull request adds an .agentic-review.yml naming another provider URL and a ceiling of 1 (FR-10.3d).
    report, _ = _review_pull_request(remote, elsewhere, canary_env, [ai_reply(FINDINGS)])
    assert report.run.tool_call_ceiling == 25
    assert "attacker.invalid" not in to_json(report)
    assert ".agentic-review.yml" in {f.path for f in report.change_summary.files if not f.reviewed}


def test_the_working_directory_configuration_is_not_this_reviews_configuration(
    remote: PullRequestRemote, tmp_path: Path, temp_root: Path, canary_env: dict[str, str]
) -> None:
    local = RepoBuilder(tmp_path / "local").init()
    local.write(".agentic-review.yml", "agent:\n  toolCallCeiling: 2\n").commit("mine")
    report, _ = _review_pull_request(remote, local.root, canary_env, [ai_reply(FINDINGS)])
    assert report.run.tool_call_ceiling == 25

    mine = tmp_path / "mine.yml"
    mine.write_text("agent:\n  toolCallCeiling: 2\n", encoding="utf-8")
    report, _ = _review_pull_request(remote, local.root, canary_env, [ai_reply(FINDINGS)], config_path=mine)
    assert report.run.tool_call_ceiling == 2


def test_a_named_base_branch_is_stated(
    remote: PullRequestRemote, elsewhere: Path, temp_root: Path, canary_env: dict[str, str]
) -> None:
    report, _ = _review_pull_request(remote, elsewhere, canary_env, [ai_reply(FINDINGS)], base="release")
    scope = report.change_summary.scope
    assert scope.base_ref == "release" and "against release (" in scope.description
    _check(report)


def test_an_unknown_pull_request_stops_before_the_model(
    remote: PullRequestRemote, elsewhere: Path, temp_root: Path, canary_env: dict[str, str]
) -> None:
    model = ScriptedChatModel([])
    result = run_review(
        ReviewRequest(cwd=elsewhere, pr="https://github.com/acme/widgets/pull/99"),
        env=canary_env,
        port_factory=_factory(model),
        pull_requests=remote.source(),
    )
    assert isinstance(result, PreflightFailure)
    assert "Pull request #99 was not found in acme/widgets" in result.message
    assert model.call_count == 0
    assert_no_canary(result.message)
    assert _leftovers(temp_root) == []


def test_the_temporary_clone_is_removed_when_a_later_stage_fails(
    remote: PullRequestRemote, elsewhere: Path, temp_root: Path, canary_env: dict[str, str]
) -> None:
    def broken(_settings: object, _credential: object) -> object:
        raise RuntimeError("the review step broke")

    with pytest.raises(RuntimeError, match="the review step broke"):
        run_review(
            ReviewRequest(cwd=elsewhere, pr=PR_URL),
            env=canary_env,
            port_factory=broken,  # type: ignore[arg-type]
            pull_requests=remote.source(),
        )
    assert _leftovers(temp_root) == []


class InMemoryPullRequest:
    """What a source backed by something other than git would hand back: a change set, and nothing on disk."""

    def __init__(self) -> None:
        self.closed = False

    def change_set(self, exclude: Sequence[str]) -> ChangeSet:
        hunk = synthesise_added_file("export const served = 1;\nexport const elsewhere = 2;\n")
        assert hunk is not None
        return ChangeSet(
            repo_root=Path("not-a-repository"),
            scope=ResolvedScope(
                kind="pull-request",
                base_ref="main",
                head_ref="refs/pull/7/head",
                was_defaulted=False,
                description="pull request acme/widgets#7 against main · 1 file",
            ),
            files=(
                ChangedFile(
                    path="src/served.ts",
                    change_type="added",
                    previous_path=None,
                    language="ts",
                    is_binary=False,
                    changed_line_ranges=((1, 2),),
                    hunks=(hunk,),
                    added_lines=2,
                    removed_lines=0,
                ),
            ),
            excluded=(),
        )

    def line_counts(self, change_set: ChangeSet) -> Mapping[str, int]:
        return {"src/served.ts": 2}

    def close(self) -> None:
        self.closed = True


class InMemorySource:
    def __init__(self) -> None:
        self.opened = InMemoryPullRequest()

    def open(self, pr: PullRequestRef, *, base: str | None) -> InMemoryPullRequest:
        if pr.number != 7:
            raise PullRequestError(f"Pull request #{pr.number} is not served.\nNothing was reviewed.")
        return self.opened


def test_a_source_that_never_touches_git_produces_the_same_kind_of_report(
    elsewhere: Path, temp_root: Path, canary_env: dict[str, str]
) -> None:
    """The seam ADR-0011 names: replacing the git transport is a second ``PullRequestSource``, nothing more."""
    source = InMemorySource()
    model = ScriptedChatModel([ai_reply([finding_call(file="src/served.ts", startLine=2, endLine=2)])])
    result = run_review(
        ReviewRequest(cwd=elsewhere, pr=PR_URL), env=canary_env, port_factory=_factory(model), pull_requests=source
    )
    assert isinstance(result, Reviewed), result
    report = result.report
    assert report.change_summary.scope.kind == "pull-request"
    assert [(f.file, f.start_line) for f in report.findings] == [("src/served.ts", 2)]
    assert "export const elsewhere = 2;" in model.received[0][1].content
    assert source.opened.closed
    _check(report)
    assert _leftovers(temp_root) == []


# --- the command line ---------------------------------------------------------------------------------------------------


def test_cli_reviews_a_pull_request(
    remote: PullRequestRemote,
    elsewhere: Path,
    temp_root: Path,
    canary_env: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model = ScriptedChatModel([ai_reply(FINDINGS)])
    monkeypatch.setattr(pipeline_agent, "build_review_port", _factory(model))
    monkeypatch.setattr(pipeline_agent, "GitPullRequestSource", remote.source)
    monkeypatch.chdir(elsewhere)
    result = CliRunner().invoke(app, ["review", "--pr", PR_URL])
    assert result.exit_code == 0, result.output
    assert "pull request acme/widgets#7 against main, the default branch" in result.stdout
    assert "src/app.ts:21" in result.stdout and "Verdict:" in result.stdout
    assert result.stderr == ""
    assert_no_canary(result.stdout, result.stderr)
    assert _leftovers(temp_root) == []


@pytest.mark.parametrize(
    "arguments,fragment",
    [
        (["--pr", "acme/widgets#7"], "is not a GitHub pull request URL"),
        (["--pr", PR_URL, "--scope", "range"], "remove --scope"),
        (["--pr", PR_URL, "--head", "feature"], "--head cannot be used with --pr"),
        (["--pr", "https://github.com/acme/widgets/pull/99"], "Pull request #99 was not found"),
        (["--pr", PR_URL, "--base", "no-such-branch"], "The base branch 'no-such-branch' does not exist"),
        (["--scope", "staged"], "'staged' is not available in this build"),
    ],
)
def test_cli_problems_exit_3_before_the_model(
    remote: PullRequestRemote,
    elsewhere: Path,
    temp_root: Path,
    canary_env: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
    arguments: list[str],
    fragment: str,
) -> None:
    model = ScriptedChatModel([])
    monkeypatch.setattr(pipeline_agent, "build_review_port", _factory(model))
    monkeypatch.setattr(pipeline_agent, "GitPullRequestSource", remote.source)
    monkeypatch.chdir(elsewhere)
    result = CliRunner().invoke(app, ["review", *arguments])
    assert result.exit_code == 3, result.output
    assert fragment in result.stderr and "Nothing was reviewed." in result.stderr
    assert result.stdout == ""
    assert model.call_count == 0
    assert_no_canary(result.stderr)
    assert _leftovers(temp_root) == []


# --- a local branch range ---------------------------------------------------------------------------------------------


@pytest.fixture
def branches(tmp_path: Path) -> RepoBuilder:
    builder = RepoBuilder(tmp_path / "repo").init()
    builder.write("src/app.ts", "".join(f"export const v{i} = {i};\n" for i in range(1, 11)))
    builder.commit("initial")
    builder.checkout("feature", create=True)
    builder.write("src/app.ts", "".join(f"export const v{i} = {i * 2};\n" for i in range(1, 13)))
    builder.commit("feature work")
    builder.checkout("main")
    builder.write("src/app.ts", "only on disk\n")  # uncommitted, and on another branch: not part of the range
    return builder


def test_cli_reviews_a_branch_range_without_checking_it_out(
    branches: RepoBuilder, canary_env: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    model = ScriptedChatModel([ai_reply([finding_call(file="src/app.ts", startLine=12, endLine=12)])])
    monkeypatch.setattr(pipeline_agent, "build_review_port", _factory(model))
    monkeypatch.chdir(branches.root)
    result = CliRunner().invoke(app, ["review", "--scope", "range", "--base", "main", "--head", "feature"])
    assert result.exit_code == 0, result.output
    assert "changes on feature since it left main (" in result.stdout
    assert "(default)" not in result.stdout
    assert "src/app.ts:12" in result.stdout
    sent = model.received[0][1].content
    assert "export const v12 = 24;" in sent and "only on disk" not in sent
    assert_no_canary(result.stdout, result.stderr)


def test_range_report_records_both_refs(branches: RepoBuilder, canary_env: dict[str, str]) -> None:
    model = ScriptedChatModel([ai_reply([finding_call(file="src/app.ts", startLine=12, endLine=12)])])
    result = run_review(
        ReviewRequest(cwd=branches.root, scope="range", base="main", head="feature"),
        env=canary_env,
        port_factory=_factory(model),
    )
    assert isinstance(result, Reviewed), result
    scope = result.report.change_summary.scope
    assert (scope.kind, scope.base_ref, scope.head_ref, scope.was_defaulted) == ("range", "main", "feature", False)
    _check(result.report)


@pytest.mark.parametrize(
    "arguments,fragment",
    [
        (["--scope", "range"], "add --base REF"),
        (["--scope", "range", "--base", "nope"], "The range base 'nope' does not exist"),
        (["--scope", "range", "--base", "main", "--head", "ghost"], "The range head 'ghost' does not exist"),
        (["--base", "main"], "--base is only used with the range scope"),
    ],
)
def test_cli_range_problems_exit_3(
    branches: RepoBuilder,
    canary_env: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
    arguments: list[str],
    fragment: str,
) -> None:
    model = ScriptedChatModel([])
    monkeypatch.setattr(pipeline_agent, "build_review_port", _factory(model))
    monkeypatch.chdir(branches.root)
    result = CliRunner().invoke(app, ["review", *arguments])
    assert result.exit_code == 3, result.output
    assert fragment in result.stderr and result.stdout == ""
    assert model.call_count == 0
