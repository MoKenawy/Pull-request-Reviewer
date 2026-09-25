"""The review port: what the model is given, and what the review step returns (data-model §4–§5).

The protocol lives here; its LangChain implementation lives in ``core/agent/`` (FR-5.8, FR-0.3).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Protocol

from agentic_review.core.findings.model import Finding
from agentic_review.core.findings.report import CompletionStatus, Degradation


@dataclass(frozen=True)
class ReviewedFile:
    line_count: int
    hunk_count: int


@dataclass(frozen=True)
class RunMaterial:
    """What this run actually showed the model. Finding references are validated against it (FR-5.6a)."""

    reviewed_files: Mapping[str, ReviewedFile]
    check_ids: frozenset[str] = frozenset()
    context_ranges: tuple[tuple[str, int, int], ...] = ()
    rule_ids: frozenset[str] = frozenset()


@dataclass(frozen=True)
class ReviewContext:
    instructions: str
    material_statement: str
    diff_section: str
    estimated_tokens: int
    material: RunMaterial


@dataclass(frozen=True)
class ReviewOutcome:
    findings: tuple[Finding, ...]
    completion_status: CompletionStatus
    degradations: tuple[Degradation, ...]
    tool_calls_total: int
    tool_calls_emission: int
    tool_calls_investigation: int
    repair_turns: int
    tokens_in: int | None
    tokens_out: int | None
    model: str
    provider: str
    temperature: float
    seed: int | None = None
    notes: tuple[str, ...] = field(default=())


class ReviewPort(Protocol):
    def review(self, context: ReviewContext) -> ReviewOutcome:
        """Never raises for a failure the spec names; those come back inside the outcome (Principle V)."""
        ...
