"""Binding rules — FR-5.7a (default off), FR-5.10, AC-16, contracts/emit-finding.md."""

from __future__ import annotations

from agentic_review.core.findings.schema import TOOL_DESCRIPTION, TOOL_NAME, tool_schema
from tests.unit.agents.conftest import CONTEXT, PortFactory
from tests.support.scripted_chat_model import ai_reply


def test_exactly_one_tool_is_bound_with_the_generated_schema(make_port: PortFactory) -> None:
    port, model = make_port([ai_reply()])
    port.review(CONTEXT)
    assert model.bound_tools is not None and len(model.bound_tools) == 1
    function = model.bound_tools[0]["function"]
    assert function["name"] == TOOL_NAME and function["description"] == TOOL_DESCRIPTION
    assert function["parameters"] == tool_schema()


def test_no_tool_choice_is_set(make_port: PortFactory) -> None:
    port, model = make_port([ai_reply()])
    port.review(CONTEXT)
    assert model.bound_kwargs is not None and "tool_choice" not in model.bound_kwargs


def test_model_receives_instructions_then_material_and_diff(make_port: PortFactory) -> None:
    port, model = make_port([ai_reply()])
    port.review(CONTEXT)
    system, user = model.received[0]
    assert system.type == "system" and system.content == CONTEXT.instructions
    assert user.type == "human"
    assert CONTEXT.material_statement in user.content and CONTEXT.diff_section in user.content
