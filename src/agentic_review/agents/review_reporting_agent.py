"""The review reporting agent — CF-6's graph, the one step that calls a model (research R-12, R-13, R-14, R-17,
data-model §5, ADR-0010).

A subagent of the main pipeline agent: invoked from its ``review`` node through ``ReviewPort``, never added to it
as a LangGraph subgraph (ADR-0010 records why). This is the only graph in the system with a cycle.

Four working nodes, one per phase, between pass-through ``start`` and ``end`` nodes kept for tracing: ``call_model`` sends the conversation; ``validate_calls`` admits each tool call against
the ceiling, validates it in order, and answers every call with exactly one structured observation;
``record_coverage`` checks which reviewed files this turn's calls named, cumulative across turns; ``decide_repair``
owes the **one** repair turn (FR-5.6c) when the first pass owed one — a rejected call, or a reviewed file that no
call ever named — and the ceiling was not reached, and is where the conditional edge back to ``call_model`` lives.
No checkpointer: state is built fresh for every review (FR-5.1).

``call_model`` catches every provider failure (FR-11.2, research R-10) and a reply stopped by the provider's content
filter, records a ``provider-error`` degradation, and ends the graph: ``review()`` never raises for them. A 429 is
first retried once after a configurable wait — the one failure with a well-known fix. The retry is scoped to
**that** model call alone: earlier turns already in ``run.messages`` are untouched, so a 429 on a repair turn does
not repeat the first turn's call, let alone restart the review.

The completion status and degradations are derived at the end by ``finish``, following the state machine of
data-model §5 and research R-17.
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
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agentic_review.agents.provider_errors import (
    PROVIDER_ERRORS,
    content_filter_degradation,
    rate_limit_degradation,
    to_degradation,
)
from agentic_review.core.assembly.prompt import user_message
from agentic_review.core.findings.model import ToolObservation
from agentic_review.core.findings.port import ReviewContext
from agentic_review.core.findings.report import CompletionStatus, Degradation
from agentic_review.core.findings.validation import Accepted, invalid_json_rejection, validate_call
from agentic_review.core.review.accounting import CallAccounting

NO_TOOL_CALL_DETAIL = (
    "The model replied without calling emit_finding. With emit_finding as its only tool, this build cannot tell a "
    "change with nothing to report from a model that did not use the finding tool."
)

REPAIR_MESSAGE = (
    "One or more emit_finding calls were rejected; the reasons are in the tool results. "
    "Re-emit only the rejected findings, corrected. Do not repeat accepted findings. "
    "Reply without a tool call when done."
)
"""The fixed repair nudge of contracts/emit-finding.md "The repair turn". Edited there first, never only here."""

MAX_REPAIR_TURNS = 1  # at most one, outside the tool-call ceiling (FR-5.6c, DB-17): a turn, not a call.
DEFAULT_RATE_LIMIT_RETRY_SECONDS = 60  # AgentSettings.rate_limit_retry_seconds' default, mirrored here for callers


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
    provider_failed: bool = False  # a turn's call_model got no usable reply; the graph ends there


class ReviewState(TypedDict):
    run: ReviewRun


def build_review_graph(
    bound_model: Runnable[Any, BaseMessage] | BaseChatModel,
    *,
    rate_limit_retry_seconds: float = DEFAULT_RATE_LIMIT_RETRY_SECONDS,
    sleep: Callable[[float], None] = time.sleep,
    secret: str | None = None,
) -> CompiledStateGraph:
    """``secret`` is only ever used to redact provider messages. It is captured here, never put in graph state,
    which is what a tracer serialises.
    """

    def invoke(run: ReviewRun) -> BaseMessage | None:
        """One turn's model call. ``None`` means the provider failed; the degradation is already recorded."""
        try:
            return bound_model.invoke(run.messages)
        except openai.RateLimitError:
            pass
        except PROVIDER_ERRORS as exc:
            run.degradations.append(to_degradation(exc, secret))
            return None
        sleep(rate_limit_retry_seconds)
        try:
            reply = bound_model.invoke(run.messages)
        except openai.RateLimitError:
            run.degradations.append(rate_limit_degradation(rate_limit_retry_seconds, gave_up=True))
            return None
        except PROVIDER_ERRORS as exc:
            run.degradations.append(to_degradation(exc, secret))
            return None
        run.degradations.append(rate_limit_degradation(rate_limit_retry_seconds, gave_up=False))
        return reply

    def call_model(state: ReviewState) -> ReviewState:
        run = state["run"]
        reply = invoke(run)
        if reply is None:
            run.provider_failed = True
            return {"run": run}
        if not isinstance(reply, AIMessage):
            reply = AIMessage(content=str(getattr(reply, "content", "")))
        run.accounting.add_usage(reply.usage_metadata)
        if reply.response_metadata.get("finish_reason") == "content_filter":
            # Tokens were spent, so they are counted; the reply itself is not processed.
            run.degradations.append(content_filter_degradation())
            run.provider_failed = True
            return {"run": run}
        run.messages.append(reply)
        return {"run": run}

    def route_after_call(state: ReviewState) -> str:
        return "end" if state["run"].provider_failed else "validate_calls"

    def validate_calls(state: ReviewState) -> ReviewState:
        run = state["run"]
        reply = run.messages[-1]
        assert isinstance(reply, AIMessage)
        calls = 0
        rejected = 0
        for call in reply.tool_calls:
            if not run.accounting.admit_call():
                # Understood and not permitted (FR-5.9): answered, so the protocol stays whole, but not processed.
                denied = ToolObservation(status="denied", reason=run.accounting.denied_reason())
                run.messages.append(_observation_message(denied, call.get("id")))
                continue
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
                content = f"accepted as {finding.id}"
                if result.note:
                    content = f"{content}; {result.note}"
                observation = ToolObservation(status="ok", content=content)
            else:
                rejected += 1
                observation = ToolObservation(status="error", reason=result.reason)
            run.messages.append(_observation_message(observation, call.get("id")))
        for invalid in reply.invalid_tool_calls:
            if not run.accounting.admit_call():
                denied = ToolObservation(status="denied", reason=run.accounting.denied_reason())
                run.messages.append(_observation_message(denied, invalid.get("id")))
                continue
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
        # Once the ceiling is reached no repair is taken: nothing the model sent back could be processed (R-13).
        owed = rejected or missing
        if calls and owed and run.accounting.repair_turns < MAX_REPAIR_TURNS and not run.accounting.ceiling_reached:
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

    def passthrough(state: ReviewState) -> ReviewState:
        return state

    graph = StateGraph(ReviewState)
    # `start` and `end` do no work: they give every trace one entry span and one exit span, whichever of the two
    # exit paths (provider failure, or no repair owed) the run took.
    graph.add_node("start", passthrough)
    graph.add_node("call_model", call_model)
    graph.add_node("validate_calls", validate_calls)
    graph.add_node("record_coverage", record_coverage)
    graph.add_node("decide_repair", decide_repair)
    graph.add_node("end", passthrough)
    graph.add_edge(START, "start")
    graph.add_edge("start", "call_model")
    graph.add_conditional_edges("call_model", route_after_call, {"validate_calls": "validate_calls", "end": "end"})
    graph.add_edge("validate_calls", "record_coverage")
    graph.add_edge("record_coverage", "decide_repair")
    graph.add_conditional_edges("decide_repair", route_after_repair, {"call_model": "call_model", "end": "end"})
    graph.add_edge("end", END)
    return graph.compile()


def _repair_message(rejected: int, missing: frozenset[str]) -> HumanMessage:
    """The one repair turn's nudge (FR-5.6c, DB-17): carries only what went wrong, not the diff again — it is
    already in the conversation. For rejected calls it is exactly ``REPAIR_MESSAGE``; the coverage part is this
    build's addition for a reviewed file no call named, and says this is the model's last turn.
    """
    parts = []
    if rejected:
        parts.append(REPAIR_MESSAGE)
    if missing:
        listed = ", ".join(sorted(missing))
        parts.append(
            f"No emit_finding call named these reviewed file(s): {listed}. Look at them again. Call emit_finding "
            "now for any problem you find there; if you are confident there is nothing worth reporting in a file, "
            "leave it uncalled. This is the last turn: after this reply, nothing further you find can be recorded."
        )
    return HumanMessage(content=" ".join(parts))


def _observation_message(observation: ToolObservation, call_id: str | None) -> ToolMessage:
    return ToolMessage(content=json.dumps(observation.model_dump(mode="json")), tool_call_id=call_id or "")


def start_run(context: ReviewContext, *, ceiling: int | None = None) -> ReviewRun:
    return ReviewRun(
        context=context,
        messages=[
            SystemMessage(content=context.instructions),
            HumanMessage(content=user_message(context.material_statement, context.diff_section)),
        ],
        accounting=CallAccounting(ceiling=ceiling),
    )


def _uncorrected_rejections(run: ReviewRun) -> int:
    """Rejected calls the model never corrected (data-model §5 ``RepairFailed``, contracts/emit-finding.md).

    Without a processed repair reply — none was owed, the ceiling forbade one, or the provider failed on it — the
    first turn's rejections stand. A repair reply with no call leaves them standing too: it is ``RepairFailed``,
    never ``NoCall``. Otherwise what counts is what the repair reply itself got rejected.
    """
    first_rejected = run.rejected_by_turn[0]
    if len(run.calls_by_turn) < 2 or run.calls_by_turn[1] == 0:
        return first_rejected
    return run.rejected_by_turn[1]


def finish(run: ReviewRun) -> tuple[CompletionStatus, list[Degradation]]:
    """Completion status and degradations at END (data-model §5, research R-13, R-16, R-17).

    A provider failure only decides the status when nothing was accepted before it happened: a failure on the
    repair turn after turn 0's findings were accepted still reports as ``emitted`` — those findings are real —
    carrying the degradation appended in ``call_model`` (FR-11.2, research R-17's documented repair-turn case).
    The same rule holds for uncorrected rejections (D-4): with any finding accepted, a judgement was made.
    """
    degradations = list(run.degradations)
    accounting = run.accounting
    accepted = len(accounting.findings)
    if not run.calls_by_turn:  # the first turn got no usable reply
        return "provider-error", degradations
    if run.calls_by_turn[0] == 0:
        degradations.append(Degradation(source="CF-6", code="no-tool-call", detail=NO_TOOL_CALL_DETAIL))
        return "no-tool-call", degradations
    if accounting.dropped_calls:
        degradations.append(
            Degradation(
                source="CF-6",
                code="tool-budget-exhausted",
                detail=(
                    f"The tool-call ceiling of {accounting.ceiling} was reached; {accounting.dropped_calls} further "
                    "call(s) were denied and not processed, so any finding in them was not recorded."
                ),
            )
        )
    uncorrected = _uncorrected_rejections(run)
    if uncorrected:
        degradations.append(
            Degradation(
                source="CF-6",
                code="invalid-model-output",
                detail=(
                    f"{uncorrected} emit_finding call(s) were rejected and not corrected; "
                    f"{accepted} finding(s) were accepted."
                ),
            )
        )
    if run.missing_files_by_turn and run.missing_files_by_turn[-1]:
        listed = ", ".join(sorted(run.missing_files_by_turn[-1]))
        degradations.append(
            Degradation(
                source="CF-6",
                code="incomplete-file-coverage",
                detail=f"No emit_finding call, accepted or rejected, ever named: {listed}.",
            )
        )
    if accepted == 0:
        if run.provider_failed:
            return "provider-error", degradations
        if uncorrected:
            return "invalid-model-output", degradations
    if accounting.ceiling_reached:
        return "ceiling-reached", degradations
    return "emitted", degradations
