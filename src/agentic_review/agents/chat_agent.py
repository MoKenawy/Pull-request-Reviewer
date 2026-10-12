"""The chat agent — the graph the web UI talks to. Experimental: no ADR and no stack entry cover it yet.

It is an adapter in ADR-0006's sense: it will resolve what to review and render the result, and it never decides
what counts as a finding (FR-10.2).

The main agent's graph cannot be served to a chat UI as it is. Its state is ``{"run": PipelineRun}`` — one mutable
object holding callables, with no ``messages`` key — and a chat runtime reads and writes ``messages``. So the UI gets
a graph of its own, chat-shaped, which will call ``run_review`` as an ordinary function.

**Today this is a wire check.** The one node answers with a fixed line: no model is called, no credential is read
and nothing is reviewed. It exists so the LangGraph server and the frontend can be proven to reach each other.

``langgraph.json`` at the repository root names ``graph`` below; ``langgraph dev`` serves it.
"""

from __future__ import annotations

from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, AnyMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph

WIRE_CHECK_REPLY = "The review chat is connected. Reviewing from the chat is not wired yet."


class ChatState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def _reply(state: ChatState) -> dict[str, list[AnyMessage]]:
    return {"messages": [AIMessage(content=WIRE_CHECK_REPLY)]}


def build_chat_graph() -> CompiledStateGraph:
    graph = StateGraph(ChatState)
    graph.add_node("reply", _reply)
    graph.set_entry_point("reply")
    graph.add_edge("reply", END)
    return graph.compile()


graph = build_chat_graph()
