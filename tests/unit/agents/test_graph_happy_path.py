"""The review step on its main path — FR-5.6a, FR-5.9, FR-5.10, FR-11.3, AC-16; research R-13, R-14, R-16."""

from __future__ import annotations

import json
from dataclasses import replace

import httpx
import openai
from langchain_core.messages import HumanMessage, ToolMessage

from agentic_review.core.config.settings import DEFAULT_MODEL
from agentic_review.core.findings.port import ReviewedFile, RunMaterial
from agentic_review.core.findings.schema import SCHEMA_VERSION
from tests.unit.agents.conftest import CONTEXT, PortFactory
from tests.support.scripted_chat_model import ai_reply, finding_call, invalid_json_call


def rate_limit_error() -> openai.RateLimitError:
    response = httpx.Response(status_code=429, request=httpx.Request("POST", "https://example.invalid/v1"))
    return openai.RateLimitError("rate limited", response=response, body=None)


# CONTEXT reviews a single file, so it can never go missing: these tests need a second reviewed file to leave out.
TWO_FILE_CONTEXT = replace(
    CONTEXT,
    material=RunMaterial(
        reviewed_files={
            "src/app.ts": ReviewedFile(line_count=40, hunk_count=2),
            "src/other.ts": ReviewedFile(line_count=10, hunk_count=1),
        }
    ),
)


def test_two_valid_calls_become_two_findings(make_port: PortFactory) -> None:
    calls = [finding_call(severity="important"), finding_call(severity="nit", startLine=3, endLine=5)]
    port, model = make_port([ai_reply(calls, usage=(1200, 80))])
    outcome = port.review(CONTEXT)

    assert model.call_count == 1
    assert [f.id for f in outcome.findings] == ["f-1", "f-2"]
    assert [f.severity for f in outcome.findings] == ["important", "nit"]
    assert all(f.turn_index == 0 and f.schema_version == SCHEMA_VERSION for f in outcome.findings)
    assert all(len(f.fingerprint) == 12 for f in outcome.findings)
    assert outcome.completion_status == "emitted" and outcome.degradations == ()
    assert (outcome.tool_calls_total, outcome.tool_calls_emission, outcome.tool_calls_investigation) == (2, 2, 0)
    assert outcome.repair_turns == 0
    assert (outcome.tokens_in, outcome.tokens_out) == (1200, 80)
    assert outcome.model == DEFAULT_MODEL and outcome.provider == "integrate.api.nvidia.com"

    observations = [m for m in port.last_transcript if isinstance(m, ToolMessage)]
    assert [m.tool_call_id for m in observations] == [c["id"] for c in calls]
    assert [json.loads(m.content) for m in observations] == [
        {"status": "ok", "reason": None, "content": "accepted as f-1"},
        {"status": "ok", "reason": None, "content": "accepted as f-2"},
    ]


def test_prose_is_discarded_and_no_call_is_recorded(make_port: PortFactory) -> None:
    prose = 'I found one issue: {"file": "src/app.ts", "startLine": 1, "endLine": 1, "severity": "blocking"}'
    port, _ = make_port([ai_reply(content=prose)])
    outcome = port.review(CONTEXT)
    assert outcome.findings == ()
    assert outcome.completion_status == "no-tool-call"
    assert [(d.source, d.code) for d in outcome.degradations] == [("CF-6", "no-tool-call")]
    assert outcome.tool_calls_total == 0


def test_tokens_are_none_when_not_reported(make_port: PortFactory) -> None:
    port, _ = make_port([ai_reply([finding_call()])])
    outcome = port.review(CONTEXT)
    assert (outcome.tokens_in, outcome.tokens_out) == (None, None)


def test_rejected_and_invalid_json_calls_get_error_observations(make_port: PortFactory) -> None:
    calls = [finding_call(), finding_call(file="src/nope.ts")]
    bad_json = invalid_json_call()
    port, _ = make_port([ai_reply(calls, invalid_tool_calls=[bad_json]), ai_reply()])
    outcome = port.review(CONTEXT)

    assert [f.id for f in outcome.findings] == ["f-1"]
    assert outcome.tool_calls_total == 3 and outcome.tool_calls_emission == 3
    by_id = {m.tool_call_id: json.loads(m.content) for m in port.last_transcript if isinstance(m, ToolMessage)}
    assert by_id[calls[1]["id"]]["status"] == "error"
    assert by_id[calls[1]["id"]]["reason"].startswith("file: 'src/nope.ts' was not part of this review")
    assert by_id[bad_json["id"]] == {"status": "error", "reason": "arguments: not valid JSON", "content": None}


def test_missing_file_coverage_earns_one_repair_turn(make_port: PortFactory) -> None:
    """A reviewed file no call ever named owes a repair turn (FR-5.6c, DB-17), same as a rejected call."""
    first_turn = [finding_call(file="src/app.ts")]
    second_turn = [finding_call(file="src/other.ts", startLine=3, endLine=5)]
    port, model = make_port([ai_reply(first_turn), ai_reply(second_turn)])
    outcome = port.review(TWO_FILE_CONTEXT)

    assert model.call_count == 2
    assert outcome.repair_turns == 1
    assert [f.id for f in outcome.findings] == ["f-1", "f-2"]
    assert [f.turn_index for f in outcome.findings] == [0, 1]
    assert outcome.completion_status == "emitted" and outcome.degradations == ()

    nudges = [m for m in port.last_transcript if isinstance(m, HumanMessage)]
    assert len(nudges) == 2  # the original user message, then the repair nudge
    assert "src/other.ts" in nudges[-1].content and "last turn" in nudges[-1].content


def test_missing_file_coverage_repair_is_capped_at_one(make_port: PortFactory) -> None:
    """Coverage still incomplete after the one repair turn is reported, not retried again."""
    first_turn = [finding_call(file="src/app.ts")]
    port, model = make_port([ai_reply(first_turn), ai_reply()])  # repair turn reports nothing more
    outcome = port.review(TWO_FILE_CONTEXT)

    assert model.call_count == 2
    assert outcome.repair_turns == 1
    assert [f.id for f in outcome.findings] == ["f-1"]
    assert outcome.completion_status == "emitted"
    assert [(d.source, d.code) for d in outcome.degradations] == [("CF-6", "incomplete-file-coverage")]
    assert "src/other.ts" in outcome.degradations[0].detail


def test_full_coverage_in_the_first_turn_needs_no_repair(make_port: PortFactory) -> None:
    calls = [finding_call(file="src/app.ts"), finding_call(file="src/other.ts")]
    port, model = make_port([ai_reply(calls)])
    outcome = port.review(TWO_FILE_CONTEXT)

    assert model.call_count == 1
    assert outcome.repair_turns == 0
    assert outcome.degradations == ()


def test_rate_limit_is_retried_once_then_succeeds(make_port: PortFactory) -> None:
    """Only the failed turn's call is redone: the same conversation, no findings lost, no turn skipped."""
    port, model = make_port([rate_limit_error(), ai_reply([finding_call()])], rate_limit_retry_seconds=0)
    outcome = port.review(CONTEXT)

    assert model.call_count == 2
    assert [f.id for f in outcome.findings] == ["f-1"]
    assert outcome.completion_status == "emitted"
    assert [(d.source, d.code) for d in outcome.degradations] == [("CF-6", "provider-error")]
    assert "retrying after" in outcome.degradations[0].detail and "abandoned" not in outcome.degradations[0].detail


def test_rate_limit_gives_up_after_one_retry_with_no_prior_findings(make_port: PortFactory) -> None:
    port, model = make_port([rate_limit_error(), rate_limit_error()], rate_limit_retry_seconds=0)
    outcome = port.review(CONTEXT)

    assert model.call_count == 2  # the original attempt and the one retry; no third attempt
    assert outcome.findings == ()
    assert outcome.completion_status == "provider-error"
    assert [(d.source, d.code) for d in outcome.degradations] == [("CF-6", "provider-error")]
    assert "abandoned" in outcome.degradations[0].detail


def test_rate_limit_in_repair_turn_keeps_earlier_findings(make_port: PortFactory) -> None:
    """A 429 that survives its retry on the repair turn does not erase turn 0's already-accepted findings."""
    first_turn = [finding_call(file="src/app.ts")]  # leaves src/other.ts uncovered, so a repair turn is owed
    port, model = make_port(
        [ai_reply(first_turn), rate_limit_error(), rate_limit_error()], rate_limit_retry_seconds=0
    )
    outcome = port.review(TWO_FILE_CONTEXT)

    assert model.call_count == 3
    assert [f.id for f in outcome.findings] == ["f-1"]
    assert outcome.completion_status == "emitted"  # turn 0's finding is real; not overridden by the later 429
    codes = {(d.source, d.code) for d in outcome.degradations}
    assert codes == {("CF-6", "provider-error"), ("CF-6", "incomplete-file-coverage")}
