"""One report every output surface renders, so the surfaces are compared against the same document.

It was `tests/unit/output/test_render.py::_report`, inline, when the terminal was the only renderer. It moved here
when the HTML rendering arrived (SRS FR-10.4d): a template is iterated against this, never against a review run,
which is what keeps template work free of provider calls.
"""

from __future__ import annotations

from typing import Any

from agentic_review.core.findings.report import ReviewReport


def report(**overrides: Any) -> ReviewReport:
    """The canonical two-finding report. Keyword arguments replace top-level keys, by alias."""
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
