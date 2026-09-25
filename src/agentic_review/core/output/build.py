"""Building the review report from what the pipeline recorded (data-model §6, contracts/review-report.md)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from agentic_review.core.config.settings import AgentSettings
from agentic_review.core.findings.port import ReviewOutcome
from agentic_review.core.findings.report import (
    ChangeSummary,
    CompletionStatus,
    Degradation,
    EvidenceRecord,
    ReviewReport,
    RunMetadata,
    Sampling,
    StageDurations,
)
from agentic_review.core.findings.schema import SCHEMA_VERSION
from agentic_review.core.output.verdict import compute_verdict


def build_report(
    *,
    change_summary: ChangeSummary,
    completion: CompletionStatus,
    outcome: ReviewOutcome | None,
    degradations: Sequence[Degradation],
    agent: AgentSettings,
    provider: str,
    budget_limit: int,
    budget_hit: bool,
    started_at: str,
    duration_ms: int,
    stage_durations_ms: Mapping[str, int],
    tool_version: str,
) -> ReviewReport:
    """When no review ran, model fields carry the configured values and every counter is 0."""
    findings = list(outcome.findings) if outcome else []
    run = RunMetadata(
        started_at=started_at,
        duration_ms=duration_ms,
        stage_durations_ms=StageDurations.model_validate(dict(stage_durations_ms)),
        requested_depth=None,
        achieved_depth=None,
        tool_call_ceiling=agent.tool_call_ceiling,
        investigation_tools_enabled=False,
        tool_calls_total=outcome.tool_calls_total if outcome else 0,
        tool_calls_emission=outcome.tool_calls_emission if outcome else 0,
        tool_calls_investigation=outcome.tool_calls_investigation if outcome else 0,
        repair_turns=outcome.repair_turns if outcome else 0,
        completion_status=completion,
        emit_path="tool-call",
        model=outcome.model if outcome else agent.model,
        provider=outcome.provider if outcome else provider,
        sampling=Sampling(
            temperature=outcome.temperature if outcome else agent.temperature,
            seed=outcome.seed if outcome else None,
        ),
        tokens_in=outcome.tokens_in if outcome else None,
        tokens_out=outcome.tokens_out if outcome else None,
        budget_limit=budget_limit,
        budget_hit=budget_hit,
        schema_version=SCHEMA_VERSION,
        tool_version=tool_version,
    )
    return ReviewReport(
        schema_version=SCHEMA_VERSION,
        run=run,
        change_summary=change_summary,
        context=[],
        evidence=EvidenceRecord(),
        findings=findings,
        degradations=list(degradations),
        verdict=compute_verdict(completion, findings),
    )
