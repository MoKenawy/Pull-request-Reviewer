"""FindingDraft shape rules — data-model §3, FR-5.2, FR-5.2a–c, AC-15."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from agentic_review.core.findings.model import FindingDraft
from tests.support.scripted_chat_model import finding_args

EVIDENCE_ARMS = [
    {"kind": "check", "checkId": "tests", "failingTest": "login > rejects expired token"},
    {"kind": "context", "file": "src/b.ts", "startLine": 3, "endLine": 9},
    {"kind": "diff", "file": "src/app.ts", "hunkIndex": 0},
    {"kind": "diff", "file": "src/app.ts"},
    {"kind": "unverified", "reason": "inferred from the diff alone"},
]


@pytest.mark.parametrize("evidence", EVIDENCE_ARMS)
def test_accepts_each_evidence_arm(evidence: dict[str, Any]) -> None:
    draft = FindingDraft.model_validate(finding_args(evidence=evidence))
    assert draft.evidence.kind == evidence["kind"]


def _locs(args: dict[str, Any]) -> list[tuple[Any, ...]]:
    with pytest.raises(ValidationError) as caught:
        FindingDraft.model_validate(args)
    return [error["loc"] for error in caught.value.errors()]


def test_evidence_is_required() -> None:
    args = finding_args()
    del args["evidence"]
    assert ("evidence",) in _locs(args)


def test_unknown_field_is_rejected() -> None:
    assert ("confidence",) in _locs(finding_args(confidence=0.9))


def test_start_line_must_be_positive() -> None:
    assert ("startLine",) in _locs(finding_args(startLine=0))


def test_end_before_start_is_rejected() -> None:
    with pytest.raises(ValidationError) as caught:
        FindingDraft.model_validate(finding_args(startLine=5, endLine=4))
    assert caught.value.errors()[0]["type"] == "end_before_start"


def test_whitespace_rationale_is_rejected() -> None:
    assert ("rationale",) in _locs(finding_args(rationale="   \n"))


@pytest.mark.parametrize("field,value", [("severity", "critical"), ("category", "style")])
def test_closed_vocabularies(field: str, value: str) -> None:
    assert (field,) in _locs(finding_args(**{field: value}))


def test_unverified_needs_a_reason() -> None:
    locs = _locs(finding_args(evidence={"kind": "unverified", "reason": ""}))
    assert any(loc[0] == "evidence" and loc[-1] == "reason" for loc in locs)


def test_serialises_with_camel_case_and_omits_absent_optionals() -> None:
    draft = FindingDraft.model_validate(finding_args(evidence={"kind": "diff", "file": "src/app.ts"}))
    dumped = draft.model_dump(mode="json", by_alias=True)
    assert "startLine" in dumped and "endLine" in dumped
    assert "ruleId" not in dumped
    assert dumped["evidence"] == {"kind": "diff", "file": "src/app.ts"}
