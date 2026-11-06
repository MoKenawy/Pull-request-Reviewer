"""User Story 1 — a finding tells me which rule it came from. **AC-4**, spec 003 FR-018, FR-021, SC-002.

Drives the real graph with the stand-in model: one finding citing a shipped rule, one citing nothing. The first
must carry its identifier in the terminal, the JSON **and** the HTML; the second must carry none. That is the whole
of AC-4 — whether a *real* model cites rules, and how often, is a measurement, and measurement is feature 007
(research R-12, constitution Principle VI). Nothing here claims a catch rate.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage

from agentic_review.agents.pipeline_agent import ReviewRequest, Reviewed, run_review
from agentic_review.agents.review_port import build_review_port
from agentic_review.core.assembly.prompt import system_message
from agentic_review.core.findings.report import ReviewReport
from agentic_review.core.output.html import render_html
from agentic_review.core.output.json_out import to_json
from agentic_review.core.output.terminal import render_terminal
from agentic_review.core.patterns import load_library
from agentic_review.core.patterns.render import RULES_HEADING
from rich.console import Console
from tests.support.report_assertions import assert_invariants, assert_valid_report
from tests.support.scripted_chat_model import ScriptedChatModel, ai_reply, finding_call

LIBRARY = load_library()
CITED = sorted(LIBRARY.ids)[0]
"""Deliberately read from the loaded library rather than hard-coded: renaming a shipped rule must fail here."""


@pytest.fixture
def repo(tmp_path: Path) -> object:
    from tests.support.repo_builder import RepoBuilder

    builder = RepoBuilder(tmp_path / "repo").init()
    builder.write("src/app.ts", "".join(f"export const v{i} = {i};\n" for i in range(1, 21)))
    builder.commit("initial")
    builder.write("src/app.ts", "".join(f"export const v{i} = {i * 2};\n" for i in range(1, 21)))
    return builder


def _factory(model: ScriptedChatModel) -> Callable[..., object]:
    return lambda settings, credential: build_review_port(settings, credential, chat_model=model)


def _review(repo: object, script: Sequence[AIMessage]) -> tuple[ReviewReport, ScriptedChatModel]:
    model = ScriptedChatModel(script)
    env = {"AGENTIC_REVIEW_API_KEY": "sk-test-rule-attribution"}
    result = run_review(ReviewRequest(cwd=repo.root), env=env, port_factory=_factory(model))  # type: ignore[attr-defined]
    assert isinstance(result, Reviewed), result
    return result.report, model


def _terminal(report: ReviewReport) -> str:
    console = Console(record=True, width=200, no_color=True, force_terminal=False)
    render_terminal(report, console)
    return console.export_text()


ONE_CITED_ONE_NOT = [
    finding_call(
        severity="important",
        category="error-handling",
        startLine=2,
        endLine=4,
        ruleId=CITED,
        rationale="The doubled value is saved without awaiting, so a rejection escapes the catch.",
    ),
    finding_call(
        severity="nit",
        category="maintainability",
        startLine=7,
        endLine=7,
        evidence={"kind": "unverified", "reason": "naming judgement"},
        rationale="These names say nothing about what the values are for.",
    ),
]


def test_a_rule_derived_finding_names_its_rule_in_every_output_and_one_without_names_none(repo: object) -> None:
    """AC-4, and FR-021's "both the terminal and the structured output"— the HTML too, since CF-7 renders three."""
    report, model = _review(repo, [ai_reply(ONE_CITED_ONE_NOT)])
    assert model.call_count == 1
    assert report.run.completion_status == "emitted" and report.degradations == []

    cited, bare = report.findings[0], report.findings[1]
    assert {cited.rule_id, bare.rule_id} == {CITED, None}
    if cited.rule_id is None:  # order is canonical, not scripted; normalise rather than assume
        cited, bare = bare, cited
    assert cited.rule_id == CITED and bare.rule_id is None

    document = json.loads(to_json(report))
    by_rule = {finding.get("ruleId") for finding in document["findings"]}
    assert by_rule == {CITED, None} or by_rule == {CITED}  # the bare finding omits the key entirely
    assert any("ruleId" not in finding for finding in document["findings"])

    terminal = _terminal(report)
    assert f"rule: {CITED}" in terminal
    assert terminal.count("rule: ") == 1  # the finding with no rule prints no rule line

    html = render_html(report)
    assert CITED in html

    assert_valid_report(to_json(report))
    assert_invariants(report)


def test_the_whole_shipped_library_reached_the_model_in_the_system_message(repo: object) -> None:
    """FR-006, FR-007, FR-010. Every rule, every review, in the static prefix — no per-run subset."""
    _, model = _review(repo, [ai_reply(ONE_CITED_ONE_NOT)])
    system, user = model.received[0][0].content, model.received[0][1].content
    assert RULES_HEADING in system
    for rule in LIBRARY.rules:
        assert rule.id in system, f"{rule.id} never reached the model"
        assert rule.id not in user
        assert rule.applies_when.include[0] in system  # each rule's declared scope travels with it (FR-008)


def test_a_finding_citing_a_rule_the_run_never_loaded_does_not_reach_the_report(repo: object) -> None:
    """FR-019 / SC-002 at the level AC-4 needs: nothing invented survives into an output.

    The rejection path itself, and the repair turn it buys, are User Story 4's (T050–T052).
    """
    script = [
        ai_reply([finding_call(ruleId="no-such-rule-anywhere", startLine=2, endLine=4)]),
        ai_reply([finding_call(ruleId=CITED, startLine=2, endLine=4)]),
    ]
    report, _ = _review(repo, script)
    assert [finding.rule_id for finding in report.findings] == [CITED]
    assert "no-such-rule-anywhere" not in to_json(report)


def test_the_static_prefix_is_what_system_message_builds(repo: object) -> None:
    """Pins the seam: if the review agent stopped joining instructions and rules here, this fails rather than a
    rule silently vanishing from the prompt (the C1 divergence recorded in implementation-notes.md)."""
    _, model = _review(repo, [ai_reply(ONE_CITED_ONE_NOT)])
    system = model.received[0][0].content
    from agentic_review.core.patterns import rules_block

    assert system.endswith(rules_block(LIBRARY))
    assert system == system_message(system[: -len(rules_block(LIBRARY)) - 1], rules_block(LIBRARY))
