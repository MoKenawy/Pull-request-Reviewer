"""Assertions every integration scenario applies to its report (SC-002, SC-005, SC-007, SC-008; data-model §6)."""

from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any

from jsonschema import Draft202012Validator

from agentic_review.core.findings.report import ReviewReport
from agentic_review.core.findings.schema import report_schema
from tests.conftest import CANARY_KEY

_VALIDATOR = Draft202012Validator(report_schema())


def as_document(report: ReviewReport | str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(report, ReviewReport):
        return json.loads(report.model_dump_json(by_alias=True))
    if isinstance(report, str):
        return json.loads(report)
    return report


def assert_valid_report(report: ReviewReport | str | dict[str, Any]) -> dict[str, Any]:
    """Validate with an independent validator against the *published* schema, not the model validating itself."""
    document = as_document(report)
    errors = sorted(_VALIDATOR.iter_errors(document), key=lambda e: list(e.path))
    assert not errors, "report does not match the published schema:\n" + "\n".join(
        f"  {'/'.join(map(str, e.path))}: {e.message}" for e in errors
    )
    return document


def assert_invariants(report: ReviewReport | str | dict[str, Any]) -> None:
    doc = as_document(report)
    run, findings = doc["run"], doc["findings"]
    status = run["completionStatus"]

    has_blocking = any(f["severity"] == "blocking" for f in findings)
    assert (doc["verdict"] == "blocking") == has_blocking, "invariant 1"
    no_judgement = status in {"provider-error", "invalid-model-output", "budget-exhausted"}
    assert (doc["verdict"] == "no-judgement") == no_judgement, "invariant 2"
    if status == "nothing-to-review":
        assert findings == [] and "review" not in run["stageDurationsMs"], "invariant 3"
    assert run["toolCallsTotal"] == run["toolCallsEmission"] + run["toolCallsInvestigation"], "invariant 4"
    assert run["toolCallsTotal"] <= run["toolCallCeiling"], "invariant 4"
    assert run["repairTurns"] <= 1, "invariant 5"
    reviewed = {f["path"] for f in doc["changeSummary"]["files"] if f["reviewed"]}
    for finding in findings:
        assert finding["file"] in reviewed, "invariant 6"
        assert finding.get("evidence"), "invariant 7"


def assert_no_canary(*texts: str | bytes | None) -> None:
    for text in texts:
        if text is None:
            continue
        haystack = text.decode("utf-8", "replace") if isinstance(text, bytes) else text
        assert CANARY_KEY not in haystack, "the planted credential leaked into an output"


def assert_stage_durations(report: ReviewReport | str | dict[str, Any], expected: Iterable[str]) -> None:
    """Every stage that ran has a duration; stages that did not run have none. Values are never bounded."""
    durations = as_document(report)["run"]["stageDurationsMs"]
    assert set(durations) == set(expected)
    assert all(isinstance(value, int) and value >= 0 for value in durations.values())
