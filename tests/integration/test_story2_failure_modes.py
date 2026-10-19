"""User Story 2 — "No findings" never pretends to be a clean review (spec acceptance scenarios 1–7, SC-003).

Every failure after preflight still yields a report, and the report's completion status, degradations and exit code
tell it apart from a review with accepted findings. Runs through ``run_review`` and through the Typer app.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from itertools import combinations
from pathlib import Path

import httpx
import openai
import pytest
from langchain_core.messages import AIMessage
from rich.console import Console
from typer.testing import CliRunner

from agentic_review.agents import pipeline_agent
from agentic_review.agents.pipeline_agent import ReviewRequest, Reviewed, run_review
from agentic_review.agents.review_port import build_review_port
from agentic_review.cli.app import app
from agentic_review.cli.exit_codes import exit_code_for
from agentic_review.core.findings.report import ReviewReport
from agentic_review.core.output.json_out import to_json
from agentic_review.core.output.terminal import render_terminal
from tests.conftest import CANARY_KEY
from tests.support.report_assertions import (
    assert_invariants,
    assert_no_canary,
    assert_stage_durations,
    assert_valid_report,
)
from tests.support.repo_builder import RepoBuilder
from tests.support.scripted_chat_model import ScriptedChatModel, ai_reply, finding_call

ALL_STAGES = ("preflight", "changeSet", "assembly", "review", "output")
D5_WORDING = "cannot tell a change with nothing to report from a model that did not use the finding tool"
_REQUEST = httpx.Request("POST", "https://example.invalid/v1/chat/completions")


def _provider_down() -> openai.APIConnectionError:
    return openai.APIConnectionError(message=f"could not reach host (key {CANARY_KEY})", request=_REQUEST)


@pytest.fixture
def repo(tmp_path: Path) -> RepoBuilder:
    builder = RepoBuilder(tmp_path / "repo").init()
    builder.write("src/app.ts", "".join(f"export const v{i} = {i};\n" for i in range(1, 21)))
    builder.commit("initial")
    builder.write("src/app.ts", "".join(f"export const v{i} = {i * 2};\n" for i in range(1, 21)))
    return builder


def _factory(model: ScriptedChatModel) -> Callable[..., object]:
    return lambda settings, credential: build_review_port(settings, credential, chat_model=model)


def _review(
    repo: RepoBuilder,
    env: dict[str, str],
    script: Sequence[AIMessage | BaseException],
    *,
    ceiling: int | None = None,
) -> tuple[ReviewReport, ScriptedChatModel]:
    model = ScriptedChatModel(script)
    result = run_review(ReviewRequest(cwd=repo.root, ceiling=ceiling), env=env, port_factory=_factory(model))
    assert isinstance(result, Reviewed), result
    return result.report, model


def _render(report: ReviewReport) -> str:
    console = Console(record=True, width=200, no_color=True, force_terminal=False)
    render_terminal(report, console)
    return console.export_text()


def _check(report: ReviewReport, stages: Sequence[str] = ALL_STAGES) -> str:
    text = _render(report)
    document = to_json(report)
    assert_valid_report(document)
    assert_invariants(report)
    assert_no_canary(document, text)
    assert_stage_durations(report, stages)
    return text


def _codes(report: ReviewReport) -> list[str]:
    return [d.code for d in report.degradations]


def _signature(report: ReviewReport) -> tuple[int, str, tuple[str, ...]]:
    return exit_code_for(report.verdict), report.run.completion_status, tuple(sorted(_codes(report)))


def _over_budget(repo: RepoBuilder) -> None:
    repo.write(".agentic-review.yml", "schemaVersion: 1\nbudget:\n  maxTokens: 10\n")


# --- scenarios ------------------------------------------------------------------------------------------------------


def test_scenario1_provider_failure_is_no_judgement(repo: RepoBuilder, canary_env: dict[str, str]) -> None:
    report, _ = _review(repo, canary_env, [_provider_down()])
    assert report.run.completion_status == "provider-error"
    assert _codes(report) == ["provider-error"] and report.degradations[0].source == "CF-6"
    assert report.verdict == "no-judgement" and exit_code_for(report.verdict) == 2
    assert report.findings == []
    assert (report.run.tool_calls_total, report.run.tokens_in, report.run.budget_hit) == (0, None, False)
    text = _check(report)
    assert "No review was performed" in text
    assert "no findings" not in text.lower()


def test_scenario2_repair_success_is_a_normal_report(repo: RepoBuilder, canary_env: dict[str, str]) -> None:
    script = [ai_reply([finding_call(startLine=99, endLine=99)]), ai_reply([finding_call()])]
    report, model = _review(repo, canary_env, script)
    assert model.call_count == 2
    assert report.run.completion_status == "emitted" and report.degradations == []
    assert report.run.repair_turns == 1 and [f.turn_index for f in report.findings] == [1]
    _check(report)


def test_scenario3_repair_failure_with_nothing_accepted(repo: RepoBuilder, canary_env: dict[str, str]) -> None:
    """AC-13: output that cannot be validated after the one repair turn is no judgement, not a clean review."""
    bad = finding_call(startLine=99, endLine=99)  # past the end of src/app.ts (20 lines)
    script = [ai_reply([bad]), ai_reply([finding_call(startLine=99, endLine=99)])]
    report, _ = _review(repo, canary_env, script)
    assert report.run.completion_status == "invalid-model-output"
    assert _codes(report) == ["invalid-model-output"]
    assert exit_code_for(report.verdict) == 2
    assert "No review was performed" in _check(report)


def test_scenario4_no_tool_call(repo: RepoBuilder, canary_env: dict[str, str]) -> None:
    report, _ = _review(repo, canary_env, [ai_reply(content="All good.")])
    assert report.run.completion_status == "no-tool-call"
    assert _codes(report) == ["no-tool-call"]
    assert report.verdict == "no-findings" and exit_code_for(report.verdict) == 0
    text = _check(report)
    assert D5_WORDING in text
    assert D5_WORDING in to_json(report)


def test_scenario5_ceiling_reached_keeps_findings(repo: RepoBuilder, canary_env: dict[str, str]) -> None:
    calls = [finding_call(startLine=n, endLine=n) for n in (1, 2, 3)]
    report, _ = _review(repo, canary_env, [ai_reply(calls)], ceiling=2)
    assert report.run.completion_status == "ceiling-reached"
    assert report.run.tool_call_ceiling == 2 and report.run.tool_calls_total == 2
    assert [f.start_line for f in report.findings] == [1, 2]
    assert _codes(report) == ["tool-budget-exhausted"]
    _check(report)


def test_scenario6_diff_over_the_limit(repo: RepoBuilder, canary_env: dict[str, str]) -> None:
    _over_budget(repo)
    report, model = _review(repo, canary_env, [])
    assert model.call_count == 0
    assert report.run.completion_status == "budget-exhausted"
    assert [(d.source, d.code) for d in report.degradations] == [("CF-4", "budget-exhausted")]
    assert "10" in report.degradations[0].detail
    assert report.run.budget_hit is True and report.run.budget_limit == 10
    assert (report.run.tool_calls_total, report.run.tokens_in, report.findings) == (0, None, [])
    assert exit_code_for(report.verdict) == 2
    text = _check(report, stages=("preflight", "changeSet", "assembly", "output"))
    assert "No review was performed" in text


def test_scenario7_accepted_findings_with_no_damage_are_clean(repo: RepoBuilder, canary_env: dict[str, str]) -> None:
    report, _ = _review(repo, canary_env, [ai_reply([finding_call(severity="nit")])])
    assert report.run.completion_status == "emitted" and report.degradations == []
    _check(report)


# --- SC-003: every outcome is distinguishable --------------------------------------------------------------------


def test_outcomes_differ_pairwise(repo: RepoBuilder, canary_env: dict[str, str]) -> None:
    signatures = {
        "findings": _signature(_review(repo, canary_env, [ai_reply([finding_call(severity="nit")])])[0]),
        "blocking": _signature(_review(repo, canary_env, [ai_reply([finding_call(severity="blocking")])])[0]),
        "provider-error": _signature(_review(repo, canary_env, [_provider_down()])[0]),
        "invalid-model-output": _signature(
            _review(repo, canary_env, [ai_reply([finding_call(startLine=99, endLine=99)]), ai_reply()])[0]
        ),
        "no-tool-call": _signature(_review(repo, canary_env, [ai_reply()])[0]),
        "ceiling-reached": _signature(
            _review(repo, canary_env, [ai_reply([finding_call(), finding_call(startLine=2, endLine=2)])], ceiling=1)[0]
        ),
        # Nothing-to-review is built by User Story 4 (T087); until then its row is the contract's, not a run's.
        "nothing-to-review": (0, "nothing-to-review", ()),
    }
    _over_budget(repo)
    signatures["budget-exhausted"] = _signature(_review(repo, canary_env, [])[0])

    assert len(signatures) == 8
    for (a, sig_a), (b, sig_b) in combinations(signatures.items(), 2):
        assert sig_a != sig_b, f"{a} and {b} are indistinguishable: {sig_a}"


# --- through the CLI ----------------------------------------------------------------------------------------------


def _cli(repo: RepoBuilder, monkeypatch: pytest.MonkeyPatch, script: Sequence[object], *args: str):  # noqa: ANN202
    model = ScriptedChatModel(script)
    monkeypatch.setattr(pipeline_agent, "build_review_port", _factory(model))
    monkeypatch.chdir(repo.root)
    return CliRunner().invoke(app, ["review", *args]), model


def test_cli_provider_failure_exits_2(repo: RepoBuilder, canary_env: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
    result, _ = _cli(repo, monkeypatch, [_provider_down()])
    assert result.exit_code == 2, result.output
    assert "No review was performed" in result.stdout
    assert_no_canary(result.stdout, result.stderr)


def test_cli_no_tool_call_exits_0_with_the_d5_wording(
    repo: RepoBuilder, canary_env: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    result, _ = _cli(repo, monkeypatch, [ai_reply()])
    assert result.exit_code == 0, result.output
    assert D5_WORDING in " ".join(result.stdout.split())


def test_cli_budget_exhausted_exits_2_without_calling_the_model(
    repo: RepoBuilder, canary_env: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    _over_budget(repo)
    result, model = _cli(repo, monkeypatch, [])
    assert result.exit_code == 2, result.output
    assert model.call_count == 0
    assert "budget-exhausted" in result.stdout


def test_cli_ceiling_flag_overrides_the_config(
    repo: RepoBuilder, canary_env: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = [finding_call(startLine=n, endLine=n) for n in (1, 2, 3)]
    result, _ = _cli(repo, monkeypatch, [ai_reply(calls)], "--ceiling", "1")
    assert result.exit_code == 0, result.output
    assert "tool-budget-exhausted" in result.stdout
    assert "0 blocking / 1 important / 0 nit" in result.stdout


@pytest.mark.parametrize("value", ["0", "-3"])
def test_cli_ceiling_below_one_is_refused_before_anything_runs(
    repo: RepoBuilder, canary_env: dict[str, str], monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    result, model = _cli(repo, monkeypatch, [], "--ceiling", value)
    assert result.exit_code == 3
    assert model.call_count == 0
    assert result.stdout == ""
    assert "--ceiling" in result.stderr and "Nothing was reviewed" in result.stderr
