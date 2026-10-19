"""The tool-call ceiling — FR-5.7, FR-5.9 (spec 001 FR-017); research R-13."""

from __future__ import annotations

import json

from langchain_core.messages import ToolMessage

from tests.unit.agents.conftest import CONTEXT, PortFactory
from tests.support.scripted_chat_model import ai_reply, finding_call

DENIED_REASON = "tool-call ceiling of {n} reached; this call was not processed"


def _observations(port) -> list[dict]:  # noqa: ANN001 - the port under test
    return [json.loads(m.content) for m in port.last_transcript if isinstance(m, ToolMessage)]


def test_calls_past_the_ceiling_are_denied_and_counted_as_dropped(make_port: PortFactory) -> None:
    calls = [finding_call(startLine=n, endLine=n) for n in (1, 2, 3, 4)]
    port, model = make_port([ai_reply(calls)], toolCallCeiling=2)
    outcome = port.review(CONTEXT)

    assert model.call_count == 1
    assert [f.start_line for f in outcome.findings] == [1, 2]
    assert outcome.completion_status == "ceiling-reached"
    assert (outcome.tool_calls_total, outcome.tool_calls_emission) == (2, 2)
    assert [(d.source, d.code) for d in outcome.degradations] == [("CF-6", "tool-budget-exhausted")]
    assert "2" in outcome.degradations[0].detail

    observations = _observations(port)
    assert [o["status"] for o in observations] == ["ok", "ok", "denied", "denied"]
    assert observations[2] == {"status": "denied", "reason": DENIED_REASON.format(n=2), "content": None}


def test_reaching_the_ceiling_exactly_drops_nothing(make_port: PortFactory) -> None:
    port, _ = make_port([ai_reply([finding_call(), finding_call(startLine=2, endLine=2)])], toolCallCeiling=2)
    outcome = port.review(CONTEXT)

    assert outcome.completion_status == "ceiling-reached"
    assert outcome.degradations == ()  # using the whole allowance is not damage (02 §3.5)


def test_no_repair_turn_once_the_ceiling_is_reached(make_port: PortFactory) -> None:
    calls = [finding_call(), finding_call(startLine=99, endLine=99)]
    port, model = make_port([ai_reply(calls)], toolCallCeiling=2)
    outcome = port.review(CONTEXT)

    assert model.call_count == 1
    assert outcome.repair_turns == 0
    assert outcome.completion_status == "ceiling-reached"
    assert [d.code for d in outcome.degradations] == ["invalid-model-output"]


def test_the_repair_turn_uses_no_slot_but_its_calls_do(make_port: PortFactory) -> None:
    first = [finding_call(), finding_call(startLine=99, endLine=99)]  # 2 of 3 slots; one rejected, so a repair is owed
    repair = [finding_call(startLine=2, endLine=2), finding_call(startLine=3, endLine=3)]  # only one slot left
    port, model = make_port([ai_reply(first), ai_reply(repair)], toolCallCeiling=3)
    outcome = port.review(CONTEXT)

    assert model.call_count == 2
    assert outcome.repair_turns == 1
    assert outcome.tool_calls_total == 3
    assert [(f.start_line, f.turn_index) for f in outcome.findings] == [(1, 0), (2, 1)]
    assert outcome.completion_status == "ceiling-reached"
    assert [d.code for d in outcome.degradations] == ["tool-budget-exhausted"]
    assert _observations(port)[-1]["status"] == "denied"


def test_rejected_calls_count_against_the_ceiling_and_nothing_accepted_is_no_judgement(
    make_port: PortFactory,
) -> None:
    calls = [finding_call(startLine=99, endLine=99), finding_call(startLine=99, endLine=99), finding_call()]
    port, _ = make_port([ai_reply(calls)], toolCallCeiling=2)
    outcome = port.review(CONTEXT)

    assert outcome.findings == ()
    assert outcome.completion_status == "invalid-model-output"
    assert {d.code for d in outcome.degradations} == {"invalid-model-output", "tool-budget-exhausted"}
