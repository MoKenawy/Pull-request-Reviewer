"""The chat agent's wire check — the graph ``langgraph.json`` serves to the web UI."""

from __future__ import annotations

import json
from pathlib import Path

from langchain_core.messages import AIMessage, HumanMessage

from agentic_review.agents import chat_agent
from agentic_review.agents.chat_agent import WIRE_CHECK_REPLY, graph

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_a_message_is_answered_with_the_wire_check_reply() -> None:
    state = graph.invoke({"messages": [HumanMessage(content="hello")]})
    asked, answered = state["messages"]
    assert isinstance(asked, HumanMessage) and asked.content == "hello"  # the conversation is kept, not replaced
    assert isinstance(answered, AIMessage) and answered.content == WIRE_CHECK_REPLY


def test_langgraph_json_names_this_graph() -> None:
    # The server loads the graph by path; a renamed module or variable would only fail when the server starts.
    served = json.loads((REPO_ROOT / "langgraph.json").read_text(encoding="utf-8"))["graphs"]["review_chat"]
    path, _, variable = served.rpartition(":")
    assert (REPO_ROOT / path).resolve() == Path(chat_agent.__file__).resolve()
    assert getattr(chat_agent, variable) is graph
