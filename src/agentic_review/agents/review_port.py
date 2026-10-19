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
from langchain_core.tools import tool

from agentic_review.agents.review_reporting_agent import build_review_graph, finish, start_run
from agentic_review.core.config.credentials import Credential
from agentic_review.core.config.settings import AgentSettings
from agentic_review.core.findings.port import ReviewContext, ReviewOutcome
from agentic_review.core.findings.schema import TOOL_DESCRIPTION, TOOL_NAME, tool_schema

MAX_RETRIES = 2  # PLACEHOLDER - provider retry count, labelled per Principle VI (research R-10)


# The parameters are the generated JSON schema, not FindingDraft itself: LangChain would send a Pydantic
# args_schema with snake_case names and un-inlined refs, and the model must see the camelCase wire shape (R-11).
@tool(TOOL_NAME, args_schema=tool_schema(), description=TOOL_DESCRIPTION)
def emit_finding(**finding: Any) -> str:
    # Declared for binding only. The review graph never executes it: validate_calls answers every call itself,
    # because validation needs this run's material (reviewed files, hunk counts), which a tool body cannot see.
    raise NotImplementedError("emit_finding calls are validated by the review graph, never executed")


def provider_for(base_url: str) -> str:
    """The report's ``provider``: the base URL's host (research R-10)."""
    return urlparse(base_url).hostname or base_url


class LangGraphReviewPort:
    def __init__(self, settings: AgentSettings, chat_model: BaseChatModel, *, secret: str | None = None) -> None:
        self._settings = settings
        # emit_finding is the only tool, and no tool_choice is ever set: the model is never forced to call (FR-5.10).
        # `max_retries` above already covers the provider client's own short-backoff retries; this is the one
        # longer, configurable wait-and-retry on top of that, scoped to a single turn (research R-10).
        # `secret` only redacts provider messages inside the graph; the port keeps no reference to it.
        self._graph = build_review_graph(
            chat_model.bind_tools([emit_finding]),
            rate_limit_retry_seconds=settings.rate_limit_retry_seconds,
            secret=secret,
        )
        self.provider = provider_for(settings.base_url)
        self.last_transcript: list[BaseMessage] = []

    def review(self, context: ReviewContext) -> ReviewOutcome:
        run = start_run(context, ceiling=self._settings.tool_call_ceiling)
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
    return LangGraphReviewPort(settings, chat_model, secret=credential.reveal())
