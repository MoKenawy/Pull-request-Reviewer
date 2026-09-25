"""Validation of one ``emit_finding`` call: shape first, then references against this run (research R-14, gap D-1).

Pure functions with no I/O. Reason strings are fixed by contracts/emit-finding.md so the model can act on them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from agentic_review.core.findings.model import (
    CheckEvidence,
    ContextEvidence,
    DiffEvidence,
    FindingDraft,
)
from agentic_review.core.findings.port import RunMaterial
from agentic_review.core.findings.schema import TOOL_NAME

_EVIDENCE_KINDS = {"check", "context", "diff", "unverified"}


@dataclass(frozen=True)
class Accepted:
    draft: FindingDraft


@dataclass(frozen=True)
class Rejected:
    reason: str


def invalid_json_rejection() -> Rejected:
    return Rejected("arguments: not valid JSON")


def validate_call(name: str, args: object, material: RunMaterial) -> Accepted | Rejected:
    if name != TOOL_NAME:
        return Rejected(f"name: unknown tool '{name}'; the only tool is {TOOL_NAME}")
    try:
        draft = FindingDraft.model_validate(args)
    except ValidationError as error:
        return Rejected("; ".join(_render_shape_error(item) for item in error.errors()))
    problems = _reference_problems(draft, material)
    if problems:
        return Rejected("; ".join(problems))
    return Accepted(draft)


def _render_shape_error(error: Any) -> str:
    if error["type"] == "end_before_start":
        return f"endLine: {error['msg']}"
    loc = list(error["loc"])
    # A discriminated union adds the tag to the location (evidence.diff.file); the JSON path has no such segment.
    parts = [
        str(part)
        for index, part in enumerate(loc)
        if not (index > 0 and loc[index - 1] == "evidence" and part in _EVIDENCE_KINDS)
    ]
    return f"{'.'.join(parts) or 'arguments'}: {error['msg']}"


def _reference_problems(draft: FindingDraft, material: RunMaterial) -> list[str]:
    problems: list[str] = []
    reviewed = material.reviewed_files

    target = reviewed.get(draft.file)
    if target is None:
        listed = ", ".join(sorted(reviewed)) or "none"
        problems.append(f"file: '{draft.file}' was not part of this review; reviewed files: {listed}")
    elif draft.end_line > target.line_count:
        problems.append(f"endLine: {draft.end_line} is past the end of '{draft.file}' ({target.line_count} lines)")

    evidence = draft.evidence
    if isinstance(evidence, DiffEvidence):
        cited = reviewed.get(evidence.file)
        if cited is None:
            problems.append(f"evidence.file: '{evidence.file}' was not part of this review")
        elif evidence.hunk_index is not None and evidence.hunk_index >= cited.hunk_count:
            if cited.hunk_count == 0:
                problems.append(f"evidence.hunkIndex: '{evidence.file}' has no hunks; omit hunkIndex")
            else:
                problems.append(f"evidence.hunkIndex: '{evidence.file}' has hunks 0–{cited.hunk_count - 1}")
    elif isinstance(evidence, CheckEvidence):
        if not material.check_ids:
            problems.append(
                "evidence.kind: no checks were run in this review; cite the diff or mark the finding unverified"
            )
        elif evidence.check_id not in material.check_ids:
            problems.append(f"evidence.checkId: '{evidence.check_id}' was not run in this review")
    elif isinstance(evidence, ContextEvidence):
        if not material.context_ranges:
            problems.append(
                "evidence.kind: no related context was gathered in this review; "
                "cite the diff or mark the finding unverified"
            )
        elif not any(
            file == evidence.file and start <= evidence.start_line and evidence.end_line <= end
            for file, start, end in material.context_ranges
        ):
            problems.append(f"evidence: '{evidence.file}' lines {evidence.start_line}–{evidence.end_line} were not in the context given")

    if draft.rule_id is not None:
        if not material.rule_ids:
            problems.append("ruleId: no pattern rules are loaded in this review; omit ruleId")
        elif draft.rule_id not in material.rule_ids:
            problems.append(f"ruleId: '{draft.rule_id}' is not a loaded rule")

    return problems
