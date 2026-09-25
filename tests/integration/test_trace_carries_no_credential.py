"""No tracer attached to the graphs can see the provider credential (SC-007, technical_stack.md §3.9).

A LangChain tracer — Langfuse, LangSmith, anything registered as a callback — receives every node's input and output
state, every chat-model call and every reply, and ships them serialised. This test attaches a capturing handler the
same way a globally configured tracer attaches itself (a configure hook, not a parameter of ``run_review``), then
serialises everything it received with Langfuse's own serialiser and scans it for the planted credential.

It guards the rule that the environment and the credential are never graph state: they reach the one place that
needs them — preflight, and the review node that builds the model client — without passing through the state.
"""

from __future__ import annotations

import json
from contextvars import ContextVar
from pathlib import Path
from typing import Any

import pytest
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.tracers.context import register_configure_hook
from langfuse._utils.serializer import EventSerializer  # the serialiser the Langfuse tracer ships payloads with

from agentic_review.agents.pipeline_agent import ReviewRequest, Reviewed, run_review
from agentic_review.agents.review_port import build_review_port
from tests.conftest import CANARY_KEY
from tests.support.repo_builder import RepoBuilder
from tests.support.scripted_chat_model import ScriptedChatModel, ai_reply, finding_call


class _Capture(BaseCallbackHandler):
    def __init__(self) -> None:
        self.payloads: list[tuple[str, Any]] = []
        self.chain_names: list[str] = []

    def on_chain_start(self, serialized: Any, inputs: Any, **kwargs: Any) -> None:
        self.chain_names.append(kwargs.get("name") or "")
        self.payloads.append(("chain_start", {"serialized": serialized, "inputs": inputs, **kwargs}))

    def on_chain_end(self, outputs: Any, **kwargs: Any) -> None:
        self.payloads.append(("chain_end", {"outputs": outputs, **kwargs}))

    def on_chat_model_start(self, serialized: Any, messages: Any, **kwargs: Any) -> None:
        self.payloads.append(("chat_model_start", {"serialized": serialized, "messages": messages, **kwargs}))

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        self.payloads.append(("llm_end", {"response": response, **kwargs}))


_capture: ContextVar[_Capture | None] = ContextVar("agentic_review_test_capture", default=None)
register_configure_hook(_capture, inheritable=True)

ENV_SECRET = "sk-lf-envcanary-4b1d"
"""Any other secret in the process environment — a tracer key, another provider's key — must not travel either."""


@pytest.fixture
def repo(tmp_path: Path) -> RepoBuilder:
    builder = RepoBuilder(tmp_path / "repo").init()
    builder.write("src/app.ts", "export const a = 1;\n")
    builder.commit("initial")
    builder.write("src/app.ts", "export const a = 2;\n")
    return builder


def test_no_tracer_payload_carries_a_secret(repo: RepoBuilder, canary_env: dict[str, str]) -> None:
    env = {**canary_env, "SOME_OTHER_SECRET": ENV_SECRET}
    model = ScriptedChatModel([ai_reply([finding_call(startLine=1, endLine=1)])])
    handler = _Capture()

    token = _capture.set(handler)
    try:
        result = run_review(
            ReviewRequest(cwd=repo.root),
            env=env,
            port_factory=lambda settings, credential: build_review_port(settings, credential, chat_model=model),
        )
    finally:
        _capture.reset(token)

    assert isinstance(result, Reviewed), result
    # Not vacuous: the tracer saw both graphs' nodes and the model call.
    assert {"preflight", "review_agent", "call_model"} <= set(handler.chain_names)
    assert any(kind == "chat_model_start" for kind, _ in handler.payloads)

    for kind, payload in handler.payloads:
        shipped = json.dumps(payload, cls=EventSerializer)
        assert CANARY_KEY not in shipped, f"the provider credential reached a tracer in a {kind} payload"
        assert ENV_SECRET not in shipped, f"the process environment reached a tracer in a {kind} payload"
