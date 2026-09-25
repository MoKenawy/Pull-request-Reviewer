"""Terminal and JSON from one report — FR-8.1b, FR-10.4a, contracts/cli.md "Terminal summary"."""

from __future__ import annotations

import json
from typing import Any

from rich.console import Console

from agentic_review.core.findings.report import ReviewReport
from agentic_review.core.output.json_out import to_json
from agentic_review.core.output.terminal import render_terminal


def _report(**overrides: Any) -> ReviewReport:
    document: dict[str, Any] = {
        "schemaVersion": "1.0",
        "run": {
            "startedAt": "2026-09-17T10:04:11Z", "durationMs": 20,
            "stageDurationsMs": {"preflight": 1, "changeSet": 2, "assembly": 3, "review": 4, "output": 5},
            "toolCallCeiling": 25, "investigationToolsEnabled": False,
            "toolCallsTotal": 2, "toolCallsEmission": 2, "toolCallsInvestigation": 0, "repairTurns": 0,
            "completionStatus": "emitted", "model": "m", "provider": "p", "sampling": {"temperature": 0},
            "budgetLimit": 20000, "budgetHit": False, "schemaVersion": "1.0", "toolVersion": "0.1.0",
        },
        "changeSummary": {
            "scope": {"kind": "working-tree", "wasDefaulted": True,
                      "description": "uncommitted changes in the working tree (default) · 2 files"},
            "excluded": [{"path": "dist/index.js", "rule": "default:build-output"}],
            "files": [
                {"path": "src/app.ts", "changeType": "modified", "language": "ts", "isBinary": False,
                 "reviewed": True, "hunkCount": 1, "addedLines": 2, "removedLines": 1},
                {"path": "README.md", "changeType": "modified", "language": "other", "isBinary": False,
                 "reviewed": False, "notReviewedReason": "not-typescript-or-javascript",
                 "hunkCount": 0, "addedLines": 1, "removedLines": 0},
            ],
        },
        "evidence": {},
        "findings": [
            {"id": "f-1", "schemaVersion": "1.0", "turnIndex": 0, "fingerprint": "a" * 12, "file": "src/app.ts",
             "startLine": 4, "endLine": 7, "severity": "important", "category": "error-handling",
             "rationale": "The [catch] block swallows the error.", "evidence": {"kind": "diff", "file": "src/app.ts", "hunkIndex": 0}},
            {"id": "f-2", "schemaVersion": "1.0", "turnIndex": 0, "fingerprint": "b" * 12, "file": "src/app.ts",
             "startLine": 9, "endLine": 9, "severity": "nit", "category": "maintainability",
             "rationale": "Name is unclear.", "evidence": {"kind": "unverified", "reason": "style judgement"}},
        ],
        "degradations": [],
        "verdict": "findings",
    }
    document.update(overrides)
    return ReviewReport.model_validate(document)


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
