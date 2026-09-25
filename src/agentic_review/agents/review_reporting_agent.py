"""The review reporting agent — CF-6's graph, the one step that calls a model (research R-12, R-13, R-14, R-17,
data-model §5, ADR-0010).

A subagent of the main pipeline agent: invoked from its ``review`` node through ``ReviewPort``, never added to it
as a LangGraph subgraph (ADR-0010 records why). This is the only graph in the system with a cycle.

Four nodes, one per phase: ``call_model`` sends the conversation; ``validate_calls`` validates each tool call in
order and answers every call with exactly one structured observation; ``record_coverage`` checks which reviewed
files this turn's calls named, cumulative across turns; ``decide_repair`` owes the **one** repair turn (FR-5.6c)
when the first pass owed one — a rejected call, or a reviewed file that no call ever named — carrying only what went
wrong, and is where the conditional edge back to ``call_model`` lives. No checkpointer: state is built fresh for
every review (FR-5.1).

``call_model`` also retries once, after a configurable wait, on a 429 from the provider (FR-11.2/research R-10's
provider-error mapping, narrowed to the one case with a well-known fix: wait). The retry is scoped to **that**
model call alone — earlier turns already in ``run.messages`` are untouched, so a 429 on a repair turn does not
repeat the first turn's call, let alone restart the review.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypedDict

import openai
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.runnables import Runnable
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agentic_review.core.review.accounting import CallAccounting
from agentic_review.core.assembly.prompt import user_message
from agentic_review.core.findings.model import ToolObservation
from agentic_review.core.findings.port import ReviewContext
from agentic_review.core.findings.report import CompletionStatus, Degradation
from agentic_review.core.findings.validation import Accepted, Rejected, invalid_json_rejection, validate_call

NO_TOOL_CALL_DETAIL = (
    "The model replied without calling emit_finding. With emit_finding as its only tool, this build cannot tell a "
    "change with nothing to report from a model that did not use the finding tool."
)

MAX_REPAIR_TURNS = 5  # capped at one, outside the tool-call ceiling (FR-5.6c, DB-17): a turn, not a call.
DEFAULT_RATE_LIMIT_RETRY_SECONDS = 60  # AgentSettings.rate_limit_retry_seconds' default, mirrored here for callers
_RATE_LIMIT_SOURCE = "CF-6"
_RATE_LIMIT_CODE = "provider-error"


@dataclass
class ReviewRun:
    context: ReviewContext
    messages: list[BaseMessage]
    accounting: CallAccounting = field(default_factory=CallAccounting)
    turn_index: int = 0
    calls_by_turn: list[int] = field(default_factory=list)
    rejected_by_turn: list[int] = field(default_factory=list)
    missing_files_by_turn: list[frozenset[str]] = field(default_factory=list)
    named_files: set[str] = field(default_factory=set)  # cumulative across turns, not just the latest one
    degradations: list[Degradation] = field(default_factory=list)
    provider_gave_up: bool = False  # a turn's call_model exhausted its one rate-limit retry and got nothing back


class ReviewState(TypedDict):
    run: ReviewRun


def build_review_graph(
    bound_model: Runnable[Any, BaseMessage] | BaseChatModel,
    *,
    rate_limit_retry_seconds: float = DEFAULT_RATE_LIMIT_RETRY_SECONDS,
    sleep: Callable[[float], None] = time.sleep,
) -> CompiledStateGraph:
    def call_model(state: ReviewState) -> ReviewState:
        run = state["run"]
        try:
            reply = bound_model.invoke(run.messages)
        except openai.RateLimitError:
            sleep(rate_limit_retry_seconds)
            try:
                reply = bound_model.invoke(run.messages)
            except openai.RateLimitError:
                run.provider_gave_up = True
                run.degradations.append(_rate_limit_degradation(rate_limit_retry_seconds, gave_up=True))
                return {"run": run}
            run.degradations.append(_rate_limit_degradation(rate_limit_retry_seconds, gave_up=False))
        if not isinstance(reply, AIMessage):
            reply = AIMessage(content=str(getattr(reply, "content", "")))
        run.messages.append(reply)
        run.accounting.add_usage(reply.usage_metadata)
        return {"run": run}

    def route_after_call(state: ReviewState) -> str:
        return "end" if state["run"].provider_gave_up else "validate_calls"

    def validate_calls(state: ReviewState) -> ReviewState:
        run = state["run"]
        reply = run.messages[-1]
        assert isinstance(reply, AIMessage)
        calls = 0
        rejected = 0
        for call in reply.tool_calls:
            calls += 1
            run.accounting.count_emission_call()
            args = call["args"]
            if isinstance(args, dict) and isinstance(args.get("file"), str):
                # Counted on sight, whether or not the call is later accepted: naming a file is what "covered" it,
                # not getting it right (FR-5.6c owes a repair for a rejected call regardless).
                run.named_files.add(args["file"])
            result = validate_call(call["name"], args, run.context.material)
            if isinstance(result, Accepted):
                finding = run.accounting.accept(result.draft, turn_index=run.turn_index)
                observation = ToolObservation(status="ok", content=f"accepted as {finding.id}")
            else:
                rejected += 1
                observation = ToolObservation(status="error", reason=result.reason)
            run.messages.append(_observation_message(observation, call.get("id")))
        for invalid in reply.invalid_tool_calls:
            calls += 1
            rejected += 1
            run.accounting.count_emission_call()
            observation = ToolObservation(status="error", reason=invalid_json_rejection().reason)
            run.messages.append(_observation_message(observation, invalid.get("id")))
        run.calls_by_turn.append(calls)
        run.rejected_by_turn.append(rejected)
        return {"run": run}

    def record_coverage(state: ReviewState) -> ReviewState:
        run = state["run"]
        # Coverage is cumulative across turns: a file named in an earlier turn counts even if this turn is silent.
        missing = frozenset(run.context.material.reviewed_files) - run.named_files
        run.missing_files_by_turn.append(missing)
        return {"run": run}

    def decide_repair(state: ReviewState) -> ReviewState:
        run = state["run"]
        calls = run.calls_by_turn[-1]
        rejected = run.rejected_by_turn[-1]
        missing = run.missing_files_by_turn[-1]
        # A wholly silent turn is the model's (ambiguous, but distinct) "nothing to report" signal — handled by
        # NO_TOOL_CALL_DETAIL in finish() below — not a coverage gap this repair turn exists to close.
        if calls and run.accounting.repair_turns < MAX_REPAIR_TURNS and (rejected or missing):
            run.accounting.repair_turns += 1
            run.turn_index += 1
            run.messages.append(_repair_message(rejected, missing))
        return {"run": run}

    def route_after_repair(state: ReviewState) -> str:
        run = state["run"]
        # A repair turn was just requested (one message appended, no reply to it processed yet): go collect it.
        # `calls_by_turn` grows by one per processed reply, so this is true for exactly one pass through the edge.
        owed = run.accounting.repair_turns > 0 and len(run.calls_by_turn) <= run.accounting.repair_turns
        return "call_model" if owed else "end"

    graph = StateGraph(ReviewState)
    graph.add_node("call_model", call_model)
    graph.add_node("validate_calls", validate_calls)
    graph.add_node("record_coverage", record_coverage)
    graph.add_node("decide_repair", decide_repair)
    graph.set_entry_point("call_model")
    graph.add_conditional_edges("call_model", route_after_call, {"validate_calls": "validate_calls", "end": END})
    graph.add_edge("validate_calls", "record_coverage")
    graph.add_edge("record_coverage", "decide_repair")
    graph.add_conditional_edges("decide_repair", route_after_repair, {"call_model": "call_model", "end": END})
    return graph.compile()


def _rate_limit_degradation(wait_seconds: float, *, gave_up: bool) -> Degradation:
    """Never carries the provider's own message: it can echo request details we must not repeat (research R-9)."""
    if gave_up:
        detail = (
            f"The provider returned 429 (rate limited) twice for one turn, {wait_seconds:g}s apart; that turn was "
            "abandoned without a reply. Earlier turns' findings, if any, stand."
        )
    else:
        detail = f"The provider returned 429 (rate limited); retrying after {wait_seconds:g}s succeeded."
    return Degradation(source=_RATE_LIMIT_SOURCE, code=_RATE_LIMIT_CODE, detail=detail)


def _repair_message(rejected: int, missing: frozenset[str]) -> HumanMessage:
    """The one repair turn's nudge (FR-5.6c, DB-17): carries only what went wrong, not the diff again — it is
    already in the conversation. This is still the model's last turn: no further repair follows it.
    """
    parts = []
    if rejected:
        parts.append(
            f"{rejected} of your emit_finding call(s) above were rejected; see their observation for why. "
            "If you still believe those are real problems, correct and resubmit them now."
        )
    if missing:
        listed = ", ".join(sorted(missing))
        parts.append(
            f"No emit_finding call named these reviewed file(s): {listed}. Look at them again. Call emit_finding "
            "now for any problem you find there; if you are confident there is nothing worth reporting in a file, "
            "leave it uncalled."
        )
    parts.append("This is the last turn: after this reply, nothing further you find can be recorded.")
    return HumanMessage(content=" ".join(parts))


def _observation_message(observation: ToolObservation, call_id: str | None) -> ToolMessage:
    return ToolMessage(content=json.dumps(observation.model_dump(mode="json")), tool_call_id=call_id or "")


def start_run(context: ReviewContext) -> ReviewRun:
    return ReviewRun(
        context=context,
        messages=[
            SystemMessage(content=context.instructions),
            HumanMessage(content=user_message(context.material_statement, context.diff_section)),
        ],
    )


def finish(run: ReviewRun) -> tuple[CompletionStatus, list[Degradation]]:
    """Completion status and degradations at END (research R-16, R-17).

    A rate limit that survived its retry (``provider_gave_up``) only overrides the status when nothing was
    accepted before it happened: a 429 on the repair turn after turn 0's findings were already accepted still
    reports as ``emitted`` — those findings are real — carrying the degradation appended in ``call_model``, not a
    fabricated completion below that would suppress them (FR-11.2, research R-10/R-17's documented repair-turn case).
    """
    degradations = list(run.degradations)
    accepted = len(run.accounting.findings)
    if run.calls_by_turn and run.calls_by_turn[0] == 0:
        degradations.append(Degradation(source="CF-6", code="no-tool-call", detail=NO_TOOL_CALL_DETAIL))
        return "no-tool-call", degradations
    rejected = sum(run.rejected_by_turn)
    if rejected:
        degradations.append(
            Degradation(
                source="CF-6",
                code="invalid-model-output",
                detail=f"{rejected} emit_finding call(s) could not be validated; {accepted} finding(s) were accepted.",
            )
        )
        if accepted == 0:
            return "invalid-model-output", degradations
    if run.missing_files_by_turn and run.missing_files_by_turn[-1]:
        listed = ", ".join(sorted(run.missing_files_by_turn[-1]))
        degradations.append(
            Degradation(
                source="CF-6",
                code="incomplete-file-coverage",
                detail=f"No emit_finding call, accepted or rejected, ever named: {listed}.",
            )
        )
    if run.provider_gave_up and accepted == 0:
        return "provider-error", degradations
    return "emitted", degradations
