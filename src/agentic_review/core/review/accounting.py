"""Counting a review's tool calls and tokens (research R-13, FR-8.2d)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentic_review.core.findings.fingerprint import fingerprint
from agentic_review.core.findings.model import Finding, FindingDraft
from agentic_review.core.findings.schema import SCHEMA_VERSION


@dataclass
class CallAccounting:
    tool_calls_total: int = 0
    tool_calls_emission: int = 0
    tool_calls_investigation: int = 0  # always 0: investigation tools arrive with feature 005
    repair_turns: int = 0
    findings: list[Finding] = field(default_factory=list)
    tokens_in: int | None = None
    tokens_out: int | None = None

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
