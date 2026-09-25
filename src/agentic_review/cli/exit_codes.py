"""Verdict → exit code. The verdict is computed in core; this is only a lookup table (FR-10.4c)."""

from __future__ import annotations

from agentic_review.core.findings.report import Verdict

EXIT_PREFLIGHT = 3
"""Could not start. No report is written."""

_EXIT_CODES: dict[Verdict, int] = {
    "findings": 0,
    "no-findings": 0,
    "nothing-to-review": 0,
    "blocking": 1,
    "no-judgement": 2,
}


def exit_code_for(verdict: Verdict) -> int:
    return _EXIT_CODES[verdict]
