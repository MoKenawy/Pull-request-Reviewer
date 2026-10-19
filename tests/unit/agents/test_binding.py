"""Binding rules — FR-5.7a (default off), FR-5.10, AC-16, contracts/emit-finding.md."""

from __future__ import annotations

import json

from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool

from agentic_review.core.findings.schema import TOOL_DESCRIPTION, TOOL_NAME, tool_schema
from tests.unit.agents.conftest import CONTEXT, PortFactory
from tests.support.scripted_chat_model import ai_reply


def test_exactly_one_tool_is_bound_with_the_generated_schema(make_port: PortFactory) -> None:
    port, model = make_port([ai_reply()])
    port.review(CONTEXT)
    assert model.bound_tools is not None and len(model.bound_tools) == 1
    bound = model.bound_tools[0]
    assert isinstance(bound, BaseTool)  # declared with @tool, not as a hand-built dict
    # What the provider receives: the conversion ChatOpenAI.bind_tools applies.
    function = convert_to_openai_tool(bound)["function"]
    assert function["name"] == TOOL_NAME and function["description"] == TOOL_DESCRIPTION
    # The schema's own top-level description is dropped in conversion; the tool description stands in its place.
    expected = {key: value for key, value in tool_schema().items() if key != "description"}
    assert function["parameters"] == expected


def test_the_bound_tool_carries_the_rules_for_filling_a_call(make_port: PortFactory) -> None:
    # These left the system prompt: they reach the model only through the tool definition.
    port, model = make_port([ai_reply()])
    port.review(CONTEXT)
    assert model.bound_tools is not None
    sent = json.dumps(convert_to_openai_tool(model.bound_tools[0]))
    for phrase in ("blocking", "important", "nit", "error-handling", "unverified", "[hunk i]", "Removed (-) lines"):
        assert phrase in sent


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
