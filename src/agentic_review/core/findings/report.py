"""Every run-level published (📦) type: the review report and what it embeds (data-model §2, §6).

These live in ``core/findings/`` so ``core/output/`` can build the report while importing only ``findings/``.
Capability packages produce these types; they do not own them.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import ConfigDict, Field
from pydantic.json_schema import SkipJsonSchema

from agentic_review.core.findings.model import Finding, WireModel

ScopeKind = Literal["working-tree", "staged", "range", "pull-request"]
ChangeType = Literal["added", "modified", "deleted", "renamed"]
Language = Literal["ts", "tsx", "js", "jsx", "other"]
NotReviewedReason = Literal["deleted", "binary", "not-typescript-or-javascript"]
CompletionStatus = Literal[
    "emitted",
    "nothing-to-review",
    "no-tool-call",
    "ceiling-reached",
    "budget-exhausted",
    "provider-error",
    "invalid-model-output",
]
DegradationCode = Literal[
    "no-index",
    "unresolvable-imports",
    "parse-error",
    "budget-exhausted",
    "checks-unrunnable",
    "execution-timed-out",
    "provider-error",
    "invalid-model-output",
    "no-tool-call",
    "tool-budget-exhausted",
    "incomplete-file-coverage",
]
CoreFunction = Literal["CF-1", "CF-2", "CF-3", "CF-4", "CF-5", "CF-6", "CF-7", "CF-8", "CF-9"]
Verdict = Literal["findings", "blocking", "no-findings", "no-judgement", "nothing-to-review"]


class ReportModel(WireModel):
    # Consumers must ignore unknown fields (02 §4), so published types never forbid them.
    model_config = ConfigDict(extra="ignore")


class ResolvedScope(ReportModel):
    kind: ScopeKind
    base_ref: str | None = None
    head_ref: str | None = None
    was_defaulted: bool
    description: str


class ExcludedPath(ReportModel):
    path: str
    rule: Annotated[str, Field(pattern=r"^(default|config):.+$")]


class FileSummary(ReportModel):
    path: str
    change_type: ChangeType
    previous_path: str | None = None
    language: Language
    is_binary: bool
    reviewed: bool
    not_reviewed_reason: NotReviewedReason | None = None
    hunk_count: Annotated[int, Field(ge=0)]
    added_lines: Annotated[int, Field(ge=0)]
    removed_lines: Annotated[int, Field(ge=0)]


class ChangeSummary(ReportModel):
    """The change set without diff text — what the report carries."""

    scope: ResolvedScope
    excluded: list[ExcludedPath]
    files: list[FileSummary]


class EvidenceRecord(ReportModel):
    """No checks are executed in this build; stated, not implied (research R-22)."""

    status: Literal["not-attempted"] = "not-attempted"
    checks: Annotated[list[dict[str, Any]], Field(max_length=0)] = []


class Degradation(ReportModel):
    source: CoreFunction
    code: DegradationCode
    detail: str


class Sampling(ReportModel):
    temperature: float
    seed: int | None = None


class StageDurations(ReportModel):
    """Milliseconds per stage. Only stages that ran are present (FR-8.2c, FR-11.3, SRS §8 rule 2)."""

    _omit_when_none = frozenset({"assembly", "review"})

    preflight: Annotated[int, Field(ge=0)]
    change_set: Annotated[int, Field(ge=0)]
    assembly: Annotated[int, Field(ge=0)] | SkipJsonSchema[None] = None
    review: Annotated[int, Field(ge=0)] | SkipJsonSchema[None] = None
    output: Annotated[int, Field(ge=0)]


_DEPTH_NOT_GATHERED = "null means related context was not gathered in this build"


class RunMetadata(ReportModel):
    started_at: str
    duration_ms: Annotated[int, Field(ge=0)]
    stage_durations_ms: StageDurations
    requested_depth: int | None = Field(default=None, description=_DEPTH_NOT_GATHERED)
    achieved_depth: int | None = Field(default=None, description=_DEPTH_NOT_GATHERED)
    tool_call_ceiling: Annotated[int, Field(ge=1)]
    investigation_tools_enabled: bool
    tool_calls_total: Annotated[int, Field(ge=0)]
    tool_calls_emission: Annotated[int, Field(ge=0)]
    tool_calls_investigation: Annotated[int, Field(ge=0)]
    repair_turns: Annotated[int, Field(ge=0)]
    completion_status: CompletionStatus
    emit_path: Literal["tool-call", "structured-output"] = "tool-call"
    model: str
    provider: str
    sampling: Sampling
    tokens_in: int | None = None
    tokens_out: int | None = None
    budget_limit: Annotated[int, Field(ge=1)]
    budget_hit: bool
    schema_version: str
    tool_version: str


class ReviewReport(ReportModel):
    schema_version: str
    run: RunMetadata
    change_summary: ChangeSummary
    context: Annotated[list[dict[str, Any]], Field(max_length=0)] = []
    evidence: EvidenceRecord
    findings: list[Finding]
    degradations: list[Degradation] = Field(description="Always present. An empty list asserts a clean run.")
    verdict: Verdict
