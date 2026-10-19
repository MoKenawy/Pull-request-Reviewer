"""A reply with no tool call — FR-5.10 (spec 001 FR-018); research R-16, gap D-5, data-model §5."""

from __future__ import annotations

from tests.unit.agents.conftest import CONTEXT, PortFactory
from tests.support.scripted_chat_model import ai_reply, finding_call

D5_WORDING = "cannot tell a change with nothing to report from a model that did not use the finding tool"


def test_a_first_reply_with_no_call_is_no_tool_call(make_port: PortFactory) -> None:
    port, model = make_port([ai_reply(content="Looks good to me.", usage=(500, 12))])
    outcome = port.review(CONTEXT)

    assert model.call_count == 1  # no repair turn for silence
    assert outcome.completion_status == "no-tool-call"
    assert [(d.source, d.code) for d in outcome.degradations] == [("CF-6", "no-tool-call")]
    assert D5_WORDING in outcome.degradations[0].detail
    assert (outcome.tokens_in, outcome.tokens_out) == (500, 12)
    assert outcome.repair_turns == 0


def test_a_repair_reply_with_no_call_is_repair_failed_not_no_tool_call(make_port: PortFactory) -> None:
    port, _ = make_port([ai_reply([finding_call(startLine=99, endLine=99)]), ai_reply()])
    outcome = port.review(CONTEXT)

    assert outcome.completion_status == "invalid-model-output"
    assert "no-tool-call" not in {d.code for d in outcome.degradations}


def test_a_first_reply_of_only_rejected_calls_is_not_no_tool_call(make_port: PortFactory) -> None:
    bad = finding_call(startLine=99, endLine=99)  # past the end of src/app.ts (40 lines)
    port, _ = make_port([ai_reply([bad]), ai_reply([finding_call(startLine=99, endLine=99)])])
    outcome = port.review(CONTEXT)

    assert outcome.completion_status == "invalid-model-output"
    assert [d.code for d in outcome.degradations] == ["invalid-model-output"]
