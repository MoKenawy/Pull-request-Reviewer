"""User Story 3 — a rule's scope decides what gets reviewed. **AC-18**, SRS FR-6.1a, spec 003 FR-013 … FR-015.

Two things are proved here that nothing else can prove:

1. The covered file is in the diff the model received and the uncovered one is **not** — and the uncovered one is
   in the report's excluded list with a reason distinguishable from a configured exclusion (AC-18 clause 1).
2. When nothing is left in scope the run **completes**, calls the model **zero** times, writes a report, and the
   verdict is ``nothing-to-review`` — its own verdict, not a clean review (FR-015, SC-003).

The degradation list is asserted **empty** throughout. That is the executable form of "a scope exclusion is not a
degradation": nothing failed, exactly as a configured exclusion is not a failure (contracts/rule-scope.md §3).

**How these fixtures isolate rule scope.** The shipped library is always loaded — FR-6.3a ships it and there is no
way to switch it off — so a file that must fall outside *every* scope has to be somewhere no shipped rule reaches.
These fixtures use ``scripts/`` and ``tools/``. That such directories exist at all is a decision, not an accident:
research R-9 chose narrow scopes precisely so this path is live from day one rather than latent, and
``tests/unit/patterns/test_shipped_rules.py`` pins both halves — the union covers an ordinary source file, and it
does not cover everything.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from pathlib import Path

from langchain_core.messages import AIMessage
from rich.console import Console

from agentic_review.agents.pipeline_agent import ReviewRequest, Reviewed, run_review
from agentic_review.agents.review_port import build_review_port
from agentic_review.core.findings.report import RULES_NO_SCOPE_MATCH, ReviewReport
from agentic_review.core.output.json_out import to_json
from agentic_review.core.output.terminal import render_terminal
from tests.support.report_assertions import assert_invariants, assert_valid_report
from tests.support.repo_builder import RepoBuilder
from tests.support.scripted_chat_model import ScriptedChatModel, ai_reply, finding_call

ENV = {"AGENTIC_REVIEW_API_KEY": "sk-test-rule-scope"}

ONLY_API = """\
rules:
  - id: api-only-rule
    title: Only files under src/api are in this rule's scope
    category: interface-contract
    defaultSeverity: important
    appliesWhen:
      include: ["src/api/**"]
    wrong: |
      export function f(): string | undefined { return undefined; }
    correct: |
      export function f(): string { return ""; }
"""

NOTHING_MATCHES = """\
rules:
  - id: matches-nothing-rule
    title: A rule scoped to a directory this repository does not have
    category: correctness
    defaultSeverity: nit
    appliesWhen:
      include: ["packages/nonexistent/**"]
    wrong: |
      const a = 1;
    correct: |
      const b = 2;
"""

PRODUCTION_AND_TESTS = """\
rules:
  - id: production-code-rule
    title: All TypeScript under src, except tests
    category: correctness
    defaultSeverity: important
    appliesWhen:
      include: ["src/**/*.ts"]
      exclude: ["**/*.test.ts"]
    wrong: |
      if (x = 1) {}
    correct: |
      if (x === 1) {}
  - id: tests-only-rule
    title: Test files, which the rule above excludes
    category: test-evidence
    defaultSeverity: important
    appliesWhen:
      include: ["src/**/*.test.ts"]
    wrong: |
      expect(result).toBeDefined();
    correct: |
      expect(result.valid).toBe(false);
"""


def _factory(model: ScriptedChatModel) -> Callable[..., object]:
    return lambda settings, credential: build_review_port(settings, credential, chat_model=model)


def _repo(tmp_path: Path, rules: str, files: dict[str, str]) -> RepoBuilder:
    """A repository configuring ``rules``, with ``files`` modified since the last commit."""
    repo = RepoBuilder(tmp_path / "repo").init()
    repo.write("review-rules.yml", rules)
    repo.write(".agentic-review.yml", "patterns:\n  rules: ./review-rules.yml\n")
    for path, text in files.items():
        repo.write(path, text)
    repo.commit("initial")
    for path, text in files.items():
        repo.write(path, text.replace("= 1", "= 2").replace("toBeDefined", "toBeTruthy"))
    return repo


def _review(repo: RepoBuilder, script: Sequence[AIMessage]) -> tuple[ReviewReport, ScriptedChatModel]:
    model = ScriptedChatModel(script)
    result = run_review(ReviewRequest(cwd=repo.root), env=ENV, port_factory=_factory(model))
    assert isinstance(result, Reviewed), result
    return result.report, model


def _terminal(report: ReviewReport) -> str:
    console = Console(record=True, width=200, no_color=True, force_terminal=False)
    render_terminal(report, console)
    return console.export_text()


def _excluded(report: ReviewReport) -> dict[str, str]:
    return {entry.path: entry.rule for entry in report.change_summary.excluded}


# --- AC-18 clause 1 (T042) ------------------------------------------------------------------------------------------


def test_a_file_no_rule_covers_is_not_sent_and_is_reported_with_its_own_reason(tmp_path: Path) -> None:
    """AC-18 clause 1. The uncovered file is absent from the diff and present in the stated scope, with a reason
    distinguishable from a configured exclusion and from a non-reviewed language."""
    repo = _repo(
        tmp_path,
        ONLY_API,
        {
            "src/api/handler.ts": "export const covered = 1;\n",
            "scripts/widget.ts": "export const uncovered = 1;\n",
            "docs/notes.md": "notes = 1\n",
        },
    )
    report, model = _review(repo, [ai_reply([finding_call(file="src/api/handler.ts", startLine=1, endLine=1)])])

    sent = model.received[0][1].content
    assert "src/api/handler.ts" in sent
    assert "scripts/widget.ts" not in sent, "a file no rule covers reached the model"

    excluded = _excluded(report)
    assert excluded["scripts/widget.ts"] == RULES_NO_SCOPE_MATCH
    # Distinguishable from the other two mechanisms, which is the whole requirement (FR-014):
    assert excluded["scripts/widget.ts"] != "config:scripts/widget.ts"
    assert "docs/notes.md" not in excluded  # not a reviewed language: a different array, its own reason
    notes = next(f for f in report.change_summary.files if f.path == "docs/notes.md")
    assert notes.not_reviewed_reason == "not-typescript-or-javascript"

    # Nothing failed. A scope exclusion is not a degradation (contracts/rule-scope.md §3).
    assert report.degradations == []
    assert report.run.completion_status == "emitted"

    document = json.loads(to_json(report))
    reasons = {entry["rule"] for entry in document["changeSummary"]["excluded"]}
    assert RULES_NO_SCOPE_MATCH in reasons

    text = _terminal(report)
    assert RULES_NO_SCOPE_MATCH in text
    assert "of which 1 file no loaded review rule applies to." in text

    assert_valid_report(to_json(report))
    assert_invariants(report)


def test_a_file_one_rule_excludes_and_another_includes_is_still_reviewed(tmp_path: Path) -> None:
    """**AC-18 clause 2**, end to end. A pooled implementation of the predicate reaches the model with the test
    file missing, and every other assertion in this file still passes."""
    repo = _repo(
        tmp_path,
        PRODUCTION_AND_TESTS,
        {"src/thing.ts": "export const a = 1;\n", "src/thing.test.ts": "expect(x).toBeDefined();\n"},
    )
    # One finding per reviewed file: a reply that leaves a reviewed file uncalled earns a second turn asking about
    # it, which would make `call_count` say nothing about scope.
    script = [
        ai_reply(
            [
                finding_call(file="src/thing.ts", startLine=1, endLine=1),
                finding_call(file="src/thing.test.ts", startLine=1, endLine=1),
            ]
        )
    ]
    report, model = _review(repo, script)
    assert model.call_count == 1

    sent = model.received[0][1].content
    assert "src/thing.test.ts" in sent, "the pooled exclusion bug: a rule's own file was dropped by another rule"
    assert "src/thing.ts" in sent
    assert _excluded(report) == {}
    assert report.degradations == []
    assert_invariants(report)


# --- AC-18 / FR-015: nothing left in scope (T043) -------------------------------------------------------------------


def test_when_no_file_is_in_scope_the_run_completes_and_is_never_called_clean(tmp_path: Path) -> None:
    """FR-015, SC-003, contracts/rule-scope.md §5. This is the route feature 001's T087 describes, built here.

    The verdict is asserted, not the exit code alone: 0 is shared with a clean review, and the verdict is what
    tells "reviewed and found nothing" from "never looked" apart.
    """
    repo = _repo(
        tmp_path,
        NOTHING_MATCHES,
        {"scripts/thing.ts": "export const a = 1;\n", "tools/other.ts": "export const b = 1;\n"},
    )
    model = ScriptedChatModel([])  # any call at all raises: the script is empty
    result = run_review(ReviewRequest(cwd=repo.root), env=ENV, port_factory=_factory(model))
    assert isinstance(result, Reviewed), result
    report = result.report

    assert model.call_count == 0, "the model was called although nothing was in scope"
    assert report.run.completion_status == "nothing-to-review"
    assert report.verdict == "nothing-to-review"
    assert report.verdict != "no-findings", "an empty scope must not be reported as a clean review"
    assert report.findings == []
    assert report.degradations == [], "nothing failed; an empty scope is not a degradation"

    excluded = _excluded(report)
    assert set(excluded) == {"scripts/thing.ts", "tools/other.ts"}
    assert set(excluded.values()) == {RULES_NO_SCOPE_MATCH}
    assert all(not f.reviewed for f in report.change_summary.files)

    assert "of which 2 files no loaded review rule applies to." in _terminal(report)

    assert_valid_report(to_json(report))
    assert_invariants(report)


def test_an_empty_scope_is_distinguishable_from_an_empty_change_set(tmp_path: Path) -> None:
    """Both reach the same outcome by design — one *nothing reviewed* outcome, not a second invented for this
    cause — so what must differ is the stated scope: one names the files it set aside, the other has none."""
    scoped_out = _repo(tmp_path / "a", NOTHING_MATCHES, {"scripts/thing.ts": "export const a = 1;\n"})
    empty = RepoBuilder(tmp_path / "b" / "repo").init()
    empty.write("src/thing.ts", "export const a = 1;\n")
    empty.commit("initial")

    first = run_review(ReviewRequest(cwd=scoped_out.root), env=ENV, port_factory=_factory(ScriptedChatModel([])))
    second = run_review(ReviewRequest(cwd=empty.root), env=ENV, port_factory=_factory(ScriptedChatModel([])))
    assert isinstance(first, Reviewed) and isinstance(second, Reviewed)

    assert first.report.verdict == second.report.verdict == "nothing-to-review"
    assert _excluded(first.report) == {"scripts/thing.ts": RULES_NO_SCOPE_MATCH}
    assert _excluded(second.report) == {}
    assert first.report.degradations == [] and second.report.degradations == []


def test_the_review_stage_never_opens_when_nothing_is_in_scope(tmp_path: Path) -> None:
    """No prompt is assembled and no review is timed: the skip is visible in the trace, not a silent no-op."""
    repo = _repo(tmp_path, NOTHING_MATCHES, {"scripts/thing.ts": "export const a = 1;\n"})
    result = run_review(ReviewRequest(cwd=repo.root), env=ENV, port_factory=_factory(ScriptedChatModel([])))
    assert isinstance(result, Reviewed)
    durations = json.loads(to_json(result.report))["run"]["stageDurationsMs"]
    assert set(durations) == {"preflight", "changeSet", "output"}
    assert "review" not in durations and "assembly" not in durations
