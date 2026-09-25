"""Constructing the review port — the LangChain implementation of ``ReviewPort`` (research R-10, R-11).

The provider client lives here and nowhere else: the main agent declares the order, this builds the thing that
talks to a model (import contract 3b). ``agents/`` is the only package importing ``langchain_*``, ``langgraph``
or ``openai`` (FR-5.8, import contract 3, ADR-0010).
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage

from agentic_review.agents.review_reporting_agent import build_review_graph, finish, start_run
from agentic_review.core.config.credentials import Credential
from agentic_review.core.config.settings import AgentSettings
from agentic_review.core.findings.port import ReviewContext, ReviewOutcome
from agentic_review.core.findings.schema import TOOL_DESCRIPTION, TOOL_NAME, tool_schema

MAX_RETRIES = 2  # PLACEHOLDER - provider retry count, labelled per Principle VI (research R-10)


def emit_finding_tool() -> dict[str, Any]:
    return {
        "type": "function",
        "function": {"name": TOOL_NAME, "description": TOOL_DESCRIPTION, "parameters": tool_schema()},
    }


class LangGraphReviewPort:
    def __init__(self, settings: AgentSettings, chat_model: BaseChatModel) -> None:
        self._settings = settings
        # emit_finding is the only tool, and no tool_choice is ever set: the model is never forced to call (FR-5.10).
        # `max_retries` above already covers the provider client's own short-backoff retries; this is the one
        # longer, configurable wait-and-retry on top of that, scoped to a single turn (research R-10).
        self._graph = build_review_graph(
            chat_model.bind_tools([emit_finding_tool()]),
            rate_limit_retry_seconds=settings.rate_limit_retry_seconds,
        )
        self.provider = urlparse(settings.base_url).hostname or settings.base_url
        self.last_transcript: list[BaseMessage] = []

    def review(self, context: ReviewContext) -> ReviewOutcome:
        run = start_run(context)
        self._graph.invoke({"run": run})
        self.last_transcript = run.messages
        completion, degradations = finish(run)
        accounting = run.accounting
        return ReviewOutcome(
            findings=tuple(accounting.findings),
            completion_status=completion,
            degradations=tuple(degradations),
            tool_calls_total=accounting.tool_calls_total,
            tool_calls_emission=accounting.tool_calls_emission,
            tool_calls_investigation=accounting.tool_calls_investigation,
            repair_turns=accounting.repair_turns,
            tokens_in=accounting.tokens_in,
            tokens_out=accounting.tokens_out,
            model=self._settings.model,
            provider=self.provider,
            temperature=self._settings.temperature,
        )


def build_review_port(
    settings: AgentSettings,
    credential: Credential,
    *,
    chat_model: BaseChatModel | None = None,
) -> LangGraphReviewPort:
    if chat_model is None:
        from langchain_openai import ChatOpenAI

        chat_model = ChatOpenAI(
            base_url=settings.base_url,
            model=settings.model,
            api_key=credential.reveal(),
            temperature=settings.temperature,
            timeout=settings.request_timeout_seconds,
            max_retries=MAX_RETRIES,
        )
    return LangGraphReviewPort(settings, chat_model)
