"""The one repair turn — FR-5.6c (spec 001 FR-016); research R-14, contracts/emit-finding.md "The repair turn"."""

from __future__ import annotations

import json

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from agentic_review.agents.review_reporting_agent import REPAIR_MESSAGE
from tests.unit.agents.conftest import CONTEXT, PortFactory
from tests.support.scripted_chat_model import ai_reply, finding_call, invalid_json_call

CONTRACT_REPAIR_MESSAGE = (
    "One or more emit_finding calls were rejected; the reasons are in the tool results. "
    "Re-emit only the rejected findings, corrected. Do not repeat accepted findings. "
    "Reply without a tool call when done."
)


def test_the_repair_message_is_the_contract_wording() -> None:
    assert REPAIR_MESSAGE == CONTRACT_REPAIR_MESSAGE


def test_one_rejected_call_earns_a_repair_turn_with_the_whole_conversation(make_port: PortFactory) -> None:
    rejected = finding_call(startLine=99, endLine=99)
    first = ai_reply([rejected])
    port, model = make_port([first, ai_reply([finding_call()])])
    outcome = port.review(CONTEXT)

    assert model.call_count == 2
    sent = model.received[1]
    assert [type(m) for m in sent] == [SystemMessage, HumanMessage, AIMessage, ToolMessage, HumanMessage]
    assert sent[0].content == CONTEXT.instructions
    assert sent[2].tool_calls == first.tool_calls
    assert sent[3].tool_call_id == rejected["id"] and json.loads(sent[3].content)["status"] == "error"
    assert sent[4].content == CONTRACT_REPAIR_MESSAGE

    assert [f.turn_index for f in outcome.findings] == [1]
    assert outcome.repair_turns == 1
    assert outcome.completion_status == "emitted" and outcome.degradations == ()
    assert outcome.tool_calls_total == 2


def test_a_second_rejection_with_nothing_accepted_is_invalid_model_output(make_port: PortFactory) -> None:
    bad = finding_call(startLine=99, endLine=99)  # past the end of src/app.ts (40 lines)
    port, model = make_port([ai_reply([bad]), ai_reply([finding_call(startLine=99, endLine=99)])])
    outcome = port.review(CONTEXT)

    assert model.call_count == 2
    assert outcome.findings == ()
    assert outcome.completion_status == "invalid-model-output"
    assert [(d.source, d.code) for d in outcome.degradations] == [("CF-6", "invalid-model-output")]


def test_a_repair_reply_with_no_call_leaves_the_rejection_uncorrected(make_port: PortFactory) -> None:
    port, _ = make_port([ai_reply([finding_call(startLine=99, endLine=99)]), ai_reply(content="Sorry, never mind.")])
    outcome = port.review(CONTEXT)

    assert outcome.completion_status == "invalid-model-output"
    assert [d.code for d in outcome.degradations] == ["invalid-model-output"]


def test_a_failed_repair_after_accepted_findings_is_emitted_with_the_degradation(make_port: PortFactory) -> None:
    """Partial acceptance (spec 001 D-4): the accepted finding is a judgement, so the run is not no-judgement."""
    port, _ = make_port([ai_reply([finding_call(), finding_call(startLine=99, endLine=99)]), ai_reply()])
    outcome = port.review(CONTEXT)

    assert [f.id for f in outcome.findings] == ["f-1"]
    assert outcome.completion_status == "emitted"
    assert [d.code for d in outcome.degradations] == ["invalid-model-output"]


def test_mixed_valid_and_invalid_calls_accept_the_valid_ones_immediately(make_port: PortFactory) -> None:
    calls = [finding_call(severity="nit"), finding_call(startLine=99, endLine=99), finding_call(severity="blocking")]
    port, _ = make_port([ai_reply(calls, invalid_tool_calls=[invalid_json_call()]), ai_reply([finding_call()])])
    outcome = port.review(CONTEXT)

    assert [(f.id, f.severity, f.turn_index) for f in outcome.findings] == [
        ("f-1", "nit", 0),
        ("f-2", "blocking", 0),
        ("f-3", "important", 1),
    ]
    assert outcome.degradations == ()


def test_repair_is_taken_at_most_once(make_port: PortFactory) -> None:
    bad = finding_call(startLine=99, endLine=99)
    # Only two replies are scripted: a third model call would fail the stand-in.
    port, model = make_port([ai_reply([bad]), ai_reply([finding_call(startLine=99, endLine=99)])])
    outcome = port.review(CONTEXT)

    assert model.call_count == 2
    assert outcome.repair_turns == 1
    repair_nudges = [m for m in port.last_transcript if isinstance(m, HumanMessage)][1:]
    assert len(repair_nudges) == 1
