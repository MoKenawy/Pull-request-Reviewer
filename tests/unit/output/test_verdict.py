"""The verdict is computed in core — FR-10.2, FR-10.4c, research R-17."""

from __future__ import annotations

import pytest

from agentic_review.core.findings.model import Finding
from agentic_review.core.findings.report import CompletionStatus, Verdict
from agentic_review.core.findings.schema import SCHEMA_VERSION
from agentic_review.core.output.verdict import compute_verdict
from agentic_review.cli.exit_codes import exit_code_for
from tests.support.scripted_chat_model import finding_args


def _finding(severity: str) -> Finding:
    return Finding.model_validate(
        {**finding_args(severity=severity), "id": "f-1", "schemaVersion": SCHEMA_VERSION, "turnIndex": 0, "fingerprint": "0" * 12}
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


def test_an_empty_review_scope_is_its_own_verdict_at_exit_zero() -> None:
    """spec 003 FR-015, SC-003; contracts/rule-scope.md §5.

    Assert the **verdict**, not the exit code alone: 0 is shared with a clean review, and the verdict is what tells
    "found nothing" from "never looked" apart (AC-7, AC-13, AC-16). Exit 2 is the *no judgement* case — a provider
    error, an exhausted budget — and nothing failed here, so this is not that.
    """
    assert compute_verdict("nothing-to-review", []) == "nothing-to-review"
    assert compute_verdict("no-tool-call", []) == "no-findings"
    assert exit_code_for("nothing-to-review") == 0
    assert exit_code_for("no-findings") == 0
    assert exit_code_for("no-judgement") == 2
