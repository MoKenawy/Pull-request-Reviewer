"""The verdict, computed in core — never in the command-line layer (FR-10.2, FR-10.4c, research R-17)."""

from __future__ import annotations

from collections.abc import Sequence

from agentic_review.core.findings.model import Finding
from agentic_review.core.findings.report import CompletionStatus, Verdict

_NO_JUDGEMENT: frozenset[CompletionStatus] = frozenset({"provider-error", "invalid-model-output", "budget-exhausted"})


def compute_verdict(completion: CompletionStatus, findings: Sequence[Finding]) -> Verdict:
    if completion == "nothing-to-review":
        return "nothing-to-review"
    if completion in _NO_JUDGEMENT:
        return "no-judgement"
    if any(f.severity == "blocking" for f in findings):
        return "blocking"
    return "findings" if findings else "no-findings"
