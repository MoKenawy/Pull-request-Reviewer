"""The JSON report (FR-8.2a, FR-10.4b). It is serialised from the same ``ReviewReport`` the terminal renders (FR-10.4a)."""

from __future__ import annotations

from agentic_review.core.findings.report import ReviewReport


def to_json(report: ReviewReport) -> str:
    return report.model_dump_json(by_alias=True, indent=2) + "\n"
