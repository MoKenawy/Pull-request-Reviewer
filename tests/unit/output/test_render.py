"""Terminal and JSON from one report — FR-8.1b, FR-10.4a, contracts/cli.md "Terminal summary"."""

from __future__ import annotations

import json
from typing import Any

from rich.console import Console

from agentic_review.core.findings.report import RULES_NO_SCOPE_MATCH, ReviewReport
from agentic_review.core.output.json_out import to_json
from agentic_review.core.output.terminal import render_terminal
from tests.support import report_factory


def _report(**overrides: Any) -> ReviewReport:
    return report_factory.report(**overrides)


def _render(report: ReviewReport) -> str:
    console = Console(record=True, width=200, no_color=True, force_terminal=False)
    render_terminal(report, console)
    return console.export_text()


def test_required_content_in_order() -> None:
    text = _render(_report())
    ordered = [
        "uncommitted changes in the working tree (default)",
        "src/app.ts",
        "README.md (not TypeScript or JavaScript)",
        "dist/index.js (default:build-output)",
        "No checks were run in this build.",
        "No related context was gathered in this build.",
        "src/app.ts:4-7",
        "src/app.ts:9",
        "0 blocking / 1 important / 1 nit",
        "Verdict:",
    ]
    positions = [text.index(fragment) for fragment in ordered]
    assert positions == sorted(positions), text


def test_finding_fields_are_all_shown() -> None:
    text = _render(_report())
    for fragment in ("important", "error-handling", "The [catch] block swallows the error.", "diff hunk 0",
                     "nit", "maintainability", "unverified: style judgement"):
        assert fragment in text


def test_degradations_and_no_judgement_wording() -> None:
    report = _report(
        findings=[],
        degradations=[{"source": "CF-6", "code": "provider-error", "detail": "connection refused"}],
        verdict="no-judgement",
        run={**_report().run.model_dump(by_alias=True), "completionStatus": "provider-error"},
    )
    text = _render(report)
    assert "CF-6" in text and "provider-error" in text and "connection refused" in text
    assert "No review was performed" in text
    assert "no findings" not in text.lower()


def test_many_exclusions_collapse_to_a_count() -> None:
    summary = _report().change_summary.model_dump(by_alias=True)
    summary["excluded"] = [{"path": f"dist/{i}.js", "rule": "default:build-output"} for i in range(11)]
    text = _render(_report(changeSummary=summary))
    assert "11 paths excluded" in text and "dist/10.js" not in text


def test_json_round_trips_the_same_report() -> None:
    report = _report()
    text = to_json(report)
    assert text.endswith("\n")
    assert ReviewReport.model_validate(json.loads(text)) == report


# --- the third exclusion reason in the terminal (spec 003 FR-014, FR-021, T041) --------------------------------------


def _with_excluded(*entries: tuple[str, str]) -> ReviewReport:
    summary = _report().change_summary.model_dump(by_alias=True)
    summary["excluded"] = [{"path": path, "rule": rule} for path, rule in entries]
    return _report(changeSummary=summary)


def test_a_rule_scope_exclusion_renders_with_its_path_and_its_reason() -> None:
    """The new value needs no new rendering — it prints beside its path like the other two."""
    text = _render(_with_excluded(("src/ui/widget.ts", RULES_NO_SCOPE_MATCH)))
    assert "src/ui/widget.ts" in text and RULES_NO_SCOPE_MATCH in text


def test_the_summary_says_how_many_files_no_rule_covered() -> None:
    """contracts/rule-scope.md §4: a reviewer sees it without opening the JSON."""
    text = _render(
        _with_excluded(
            ("src/ui/widget.ts", RULES_NO_SCOPE_MATCH),
            ("src/ui/other.ts", RULES_NO_SCOPE_MATCH),
            ("dist/index.js", "default:build-output"),
        )
    )
    assert "of which 2 files no loaded review rule applies to." in text
    assert "Excluded (3):" in text


def test_the_count_is_singular_for_one_file() -> None:
    text = _render(_with_excluded(("src/ui/widget.ts", RULES_NO_SCOPE_MATCH)))
    assert "of which 1 file no loaded review rule applies to." in text


def test_no_count_is_printed_when_no_rule_set_anything_aside() -> None:
    text = _render(_with_excluded(("dist/index.js", "default:build-output")))
    assert "loaded review rule" not in text


def test_a_rule_scope_exclusion_is_not_rendered_as_a_degradation() -> None:
    """contracts/rule-scope.md §3. Nothing failed — a configured exclusion is not a degradation either."""
    report = _with_excluded(("src/ui/widget.ts", RULES_NO_SCOPE_MATCH))
    assert report.degradations == []
    assert "Degradation" not in _render(report)
