"""Call validation against the shape and against this run's material — FR-5.6a, FR-5.9, gap D-1.

Reason strings are asserted exactly: contracts/emit-finding.md fixes them so the model can act on them.
"""

from __future__ import annotations

from typing import Any

import pytest

from agentic_review.core.findings.port import ReviewedFile, RunMaterial
from agentic_review.core.findings.validation import (
    Accepted,
    Rejected,
    invalid_json_rejection,
    validate_call,
)
from tests.support.scripted_chat_model import finding_args

MATERIAL = RunMaterial(
    reviewed_files={
        "src/app.ts": ReviewedFile(line_count=40, hunk_count=2),
        "src/util.js": ReviewedFile(line_count=10, hunk_count=1),
    }
)


def _reason(args: Any, name: str = "emit_finding") -> str:
    result = validate_call(name, args, MATERIAL)
    assert isinstance(result, Rejected), result
    return result.reason


def test_valid_call_is_accepted() -> None:
    result = validate_call("emit_finding", finding_args(startLine=3, endLine=40), MATERIAL)
    assert isinstance(result, Accepted)
    assert result.draft.end_line == 40


def test_unknown_tool() -> None:
    assert _reason(finding_args(), name="read_file") == "name: unknown tool 'read_file'; the only tool is emit_finding"


def test_invalid_json() -> None:
    assert invalid_json_rejection().reason == "arguments: not valid JSON"


def test_shape_failure_names_the_field() -> None:
    assert _reason(finding_args(severity="critical")) == (
        "severity: Input should be 'blocking', 'important' or 'nit'"
    )


def test_nested_shape_failure_uses_the_json_path() -> None:
    reason = _reason(finding_args(evidence={"kind": "diff", "file": "src/app.ts", "hunkIndex": -1}))
    assert reason.startswith("evidence.hunkIndex: ")


def test_several_failures_are_joined() -> None:
    reason = _reason(finding_args(severity="critical", category="style"))
    assert reason.startswith("severity: ") and "; category: " in reason


def test_file_not_reviewed() -> None:
    args = finding_args(file="src/other.ts", evidence={"kind": "unverified", "reason": "diff only"})
    assert _reason(args) == (
        "file: 'src/other.ts' was not part of this review; reviewed files: src/app.ts, src/util.js"
    )


def test_nested_failures_have_one_reason_per_field() -> None:
    reason = _reason(finding_args(ruleId=5, evidence={"kind": "diff", "file": "src/app.ts", "hunkIndex": "x"}))
    assert reason == "ruleId: Input should be a valid string; evidence.hunkIndex: Input should be a valid integer"


def test_reference_failures_on_several_fields_are_joined() -> None:
    assert _reason(finding_args(file="src/other.ts")) == (
        "file: 'src/other.ts' was not part of this review; reviewed files: src/app.ts, src/util.js; "
        "evidence.file: 'src/other.ts' was not part of this review"
    )


def test_end_beyond_file() -> None:
    assert _reason(finding_args(startLine=1, endLine=41)) == "endLine: 41 is past the end of 'src/app.ts' (40 lines)"


def test_end_before_start() -> None:
    assert _reason(finding_args(startLine=9, endLine=2)) == "endLine: must be greater than or equal to startLine"


def test_diff_evidence_names_unreviewed_file() -> None:
    reason = _reason(finding_args(evidence={"kind": "diff", "file": "README.md"}))
    assert reason == "evidence.file: 'README.md' was not part of this review"


def test_hunk_out_of_range() -> None:
    reason = _reason(finding_args(evidence={"kind": "diff", "file": "src/app.ts", "hunkIndex": 2}))
    assert reason == "evidence.hunkIndex: 'src/app.ts' has hunks 0–1"


def test_check_evidence_is_rejected_when_no_checks_ran() -> None:
    reason = _reason(finding_args(evidence={"kind": "check", "checkId": "tests"}))
    assert reason == "evidence.kind: no checks were run in this review; cite the diff or mark the finding unverified"


def test_context_evidence_is_rejected_when_no_context_was_gathered() -> None:
    reason = _reason(finding_args(evidence={"kind": "context", "file": "src/b.ts", "startLine": 1, "endLine": 2}))
    assert reason == (
        "evidence.kind: no related context was gathered in this review; cite the diff or mark the finding unverified"
    )


def test_rule_id_is_rejected_when_no_rules_are_loaded() -> None:
    assert _reason(finding_args(ruleId="R-001")) == "ruleId: no pattern rules are loaded in this review; omit ruleId"


@pytest.mark.parametrize("args", ["not an object", None, ["a"]])
def test_non_object_arguments_are_rejected(args: Any) -> None:
    assert _reason(args).startswith("arguments: ")


def test_unverified_evidence_is_accepted() -> None:
    result = validate_call("emit_finding", finding_args(evidence={"kind": "unverified", "reason": "diff only"}), MATERIAL)
    assert isinstance(result, Accepted)
