"""Counting a review's tool calls and tokens, and holding the tool-call ceiling (research R-13, FR-8.2d, FR-5.7)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentic_review.core.findings.fingerprint import fingerprint
from agentic_review.core.findings.model import Finding, FindingDraft
from agentic_review.core.findings.schema import SCHEMA_VERSION


@dataclass
class CallAccounting:
    ceiling: int | None = None  # None = unbounded; the review port always sets agent.toolCallCeiling
    tool_calls_total: int = 0
    tool_calls_emission: int = 0
    tool_calls_investigation: int = 0  # always 0: investigation tools arrive with feature 005
    repair_turns: int = 0
    dropped_calls: int = 0  # calls denied because the ceiling was already reached; never counted in the totals
    findings: list[Finding] = field(default_factory=list)
    tokens_in: int | None = None
    tokens_out: int | None = None

    @property
    def ceiling_reached(self) -> bool:
        return self.ceiling is not None and self.tool_calls_total >= self.ceiling

    def admit_call(self) -> bool:
        """Whether the next call may be processed. A call past the ceiling is dropped, not counted (invariant 4)."""
        if self.ceiling_reached:
            self.dropped_calls += 1
            return False
        return True

    def denied_reason(self) -> str:
        return f"tool-call ceiling of {self.ceiling} reached; this call was not processed"

    def count_emission_call(self) -> None:
        # With emit_finding as the only tool, every call the model makes is an attempt to emit a finding.
        self.tool_calls_total += 1
        self.tool_calls_emission += 1

    def accept(self, draft: FindingDraft, *, turn_index: int) -> Finding:
        finding = Finding.model_validate(
            {
                **draft.model_dump(),
                "id": f"f-{len(self.findings) + 1}",
                "schema_version": SCHEMA_VERSION,
                "turn_index": turn_index,
                "fingerprint": fingerprint(draft),
            }
        )
        self.findings.append(finding)
        return finding

    def add_usage(self, usage: Any) -> None:
        if not usage:
            return
        self.tokens_in = (self.tokens_in or 0) + int(usage.get("input_tokens", 0))
        self.tokens_out = (self.tokens_out or 0) + int(usage.get("output_tokens", 0))
