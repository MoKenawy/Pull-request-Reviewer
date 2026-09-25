"""User Story 1 — Review my uncommitted changes (spec acceptance scenarios 1–5).

Runs through ``run_review`` with the real review graph driven by the stand-in model, and through the Typer app.
Every report is validated against the published schema, checked for invariants, scanned for the planted credential,
and checked for stage durations (SC-002, SC-007, SC-008).
"""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage
from rich.console import Console
from typer.testing import CliRunner

from agentic_review.cli.app import app
from agentic_review.agents.review_port import build_review_port
from agentic_review.core.findings.report import ReviewReport
from agentic_review.core.output.json_out import to_json
from agentic_review.core.output.terminal import render_terminal
from agentic_review.agents import pipeline_agent
from agentic_review.agents.pipeline_agent import ReviewRequest, Reviewed, run_review
from tests.support.report_assertions import (
    assert_invariants,
    assert_no_canary,
    assert_stage_durations,
    assert_valid_report,
)
from tests.support.repo_builder import RepoBuilder
from tests.support.scripted_chat_model import ScriptedChatModel, ai_reply, finding_call

ALL_STAGES = ("preflight", "changeSet", "assembly", "review", "output")


@pytest.fixture
def repo(tmp_path: Path) -> RepoBuilder:
    builder = RepoBuilder(tmp_path / "repo").init()
    builder.write("src/app.ts", "".join(f"export const v{i} = {i};\n" for i in range(1, 21)))
    builder.write("README.md", "# demo\n")
    builder.commit("initial")
    builder.write("src/app.ts", "".join(f"export const v{i} = {i * 2};\n" for i in range(1, 21)))
    builder.write("README.md", "# demo\nmore\n")
    return builder


def _factory(model: ScriptedChatModel) -> Callable[..., object]:
    return lambda settings, credential: build_review_port(settings, credential, chat_model=model)


def _review(repo: RepoBuilder, env: dict[str, str], script: Sequence[AIMessage]) -> tuple[ReviewReport, ScriptedChatModel]:
    model = ScriptedChatModel(script)
    result = run_review(ReviewRequest(cwd=repo.root / "src"), env=env, port_factory=_factory(model))
    assert isinstance(result, Reviewed), result
    return result.report, model


def _render(report: ReviewReport) -> str:
    console = Console(record=True, width=200, no_color=True, force_terminal=False)
    render_terminal(report, console)
    return console.export_text()


def _check(report: ReviewReport, *extra_outputs: str) -> None:
    text = to_json(report)
    assert_valid_report(text)
    assert_invariants(report)
    assert_no_canary(text, *extra_outputs)
    assert_stage_durations(report, ALL_STAGES)


IMPORTANT_AND_NIT = [
    finding_call(severity="important", category="error-handling", startLine=2, endLine=4,
                 rationale="Doubling changes the exported contract."),
    finding_call(severity="nit", category="maintainability", startLine=7, endLine=7,
                 evidence={"kind": "unverified", "reason": "naming judgement"}, rationale="Names are opaque."),
]


def test_scenario1_default_scope_is_stated(repo: RepoBuilder, canary_env: dict[str, str]) -> None:
    report, _ = _review(repo, canary_env, [ai_reply(IMPORTANT_AND_NIT)])
    scope = report.change_summary.scope
    assert scope.kind == "working-tree" and scope.was_defaulted
    text = _render(report)
    assert "uncommitted changes in the working tree (default)" in text
    _check(report, text)


def test_scenario2_findings_shown_with_every_field(repo: RepoBuilder, canary_env: dict[str, str]) -> None:
    report, model = _review(repo, canary_env, [ai_reply(IMPORTANT_AND_NIT, usage=(900, 60))])
    assert model.call_count == 1
    assert report.verdict == "findings" and report.run.completion_status == "emitted"
    assert report.degradations == []
    text = _render(report)
    for fragment in (
        "src/app.ts:2-4", "important", "error-handling", "Doubling changes the exported contract.", "diff hunk 0",
        "src/app.ts:7", "nit", "maintainability", "Names are opaque.", "unverified: naming judgement",
        "0 blocking / 1 important / 1 nit",
    ):
        assert fragment in text
    assert (report.run.tokens_in, report.run.tokens_out) == (900, 60)
    _check(report, text)


def test_scenario3_blocking_finding(repo: RepoBuilder, canary_env: dict[str, str]) -> None:
    report, _ = _review(repo, canary_env, [ai_reply([finding_call(severity="blocking")])])
    assert report.verdict == "blocking"
    _check(report, _render(report))


def test_scenario4_absent_capabilities_are_stated(repo: RepoBuilder, canary_env: dict[str, str]) -> None:
    report, model = _review(repo, canary_env, [ai_reply(IMPORTANT_AND_NIT)])
    text = _render(report)
    assert "No checks were run in this build." in text
    assert "No related context was gathered in this build." in text
    assert "passed" not in text.lower()
    assert report.evidence.status == "not-attempted" and report.evidence.checks == []
    assert report.context == [] and report.run.requested_depth is None and report.run.achieved_depth is None
    sent = model.received[0][1].content
    assert "No checks were run. No related context was gathered." in sent
    assert "README.md" not in sent
    _check(report, text)


def test_scenario5_terminal_and_json_show_the_same_findings(repo: RepoBuilder, canary_env: dict[str, str]) -> None:
    report, _ = _review(repo, canary_env, [ai_reply(IMPORTANT_AND_NIT)])
    text = _render(report)
    document = json.loads(to_json(report))
    assert document["findings"] == [f.model_dump(mode="json", by_alias=True) for f in report.findings]
    for finding in document["findings"]:
        assert f"{finding['file']}:{finding['startLine']}" in text
        assert finding["severity"] in text and finding["category"] in text and finding["rationale"] in text
    _check(report, text)


@pytest.mark.parametrize(
    "script,exit_code",
    [([ai_reply(IMPORTANT_AND_NIT)], 0), ([ai_reply([finding_call(severity="blocking")])], 1)],
)
def test_cli_review_with_no_options(
    repo: RepoBuilder,
    canary_env: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
    script: list[AIMessage],
    exit_code: int,
) -> None:
    model = ScriptedChatModel(script)
    monkeypatch.setattr(pipeline_agent, "build_review_port", _factory(model))
    monkeypatch.chdir(repo.root)
    result = CliRunner().invoke(app, ["review"])
    assert result.exit_code == exit_code, result.output
    assert "uncommitted changes in the working tree (default)" in result.stdout
    assert "No checks were run in this build." in result.stdout
    assert "Verdict:" in result.stdout
    assert result.stderr == ""
    assert_no_canary(result.stdout, result.stderr)
