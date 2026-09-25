"""The verdict is computed in core — FR-10.2, FR-10.4c, research R-17."""

from __future__ import annotations

import pytest

from agentic_review.core.findings.model import Finding
from agentic_review.core.findings.report import CompletionStatus, Verdict
from agentic_review.core.output.verdict import compute_verdict
from tests.support.scripted_chat_model import finding_args


def _finding(severity: str) -> Finding:
    return Finding.model_validate(
        {**finding_args(severity=severity), "id": "f-1", "schemaVersion": "1.0", "turnIndex": 0, "fingerprint": "0" * 12}
    )


@pytest.mark.parametrize(
    "completion,severities,verdict",
    [
        ("emitted", ["important", "nit"], "findings"),
        ("emitted", ["nit", "blocking"], "blocking"),
        ("no-tool-call", [], "no-findings"),
        ("ceiling-reached", ["important"], "findings"),
        ("ceiling-reached", ["blocking"], "blocking"),
        ("ceiling-reached", [], "no-findings"),
        ("invalid-model-output", [], "no-judgement"),
        ("provider-error", [], "no-judgement"),
        ("budget-exhausted", [], "no-judgement"),
        ("nothing-to-review", [], "nothing-to-review"),
    ],
)
def test_verdict_table(completion: CompletionStatus, severities: list[str], verdict: Verdict) -> None:
    assert compute_verdict(completion, [_finding(s) for s in severities]) == verdict
