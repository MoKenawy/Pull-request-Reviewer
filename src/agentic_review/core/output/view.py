"""What the renderings say, and the derivations they share — FR-10.4a, FR-10.4d, research R-16.

Everything here is read from the ``ReviewReport``; nothing is recomputed (FR-10.4a). Counting findings by severity
and formatting a line span are presentation, not judgement — the terminal has done both since the walking skeleton.

The wording lives here rather than in each renderer because the research R-16 caveat is CF-7's most load-bearing
sentence, and a second copy of it is what rots when one surface is reworded. FR-10.4a's "not produced
independently" is about derivation, and wording is derivation.
"""

from __future__ import annotations

from collections.abc import Sequence

from agentic_review.core.findings.model import DiffEvidence, Finding, UnverifiedEvidence
from agentic_review.core.findings.report import ReviewReport, RunMetadata, Verdict

NO_TOOL_CALL_LINE = (
    "No findings. The model made no tool call, so this build cannot tell a change with nothing to report from a "
    "model that did not use the finding tool."
)
"""Research R-16 (gap D-5): a zero-finding run is never presented as a clean review."""

NO_CHECKS_LINE = "No checks were run in this build."
NO_CONTEXT_LINE = "No related context was gathered in this build."

SEVERITY_ORDER: tuple[str, ...] = ("blocking", "important", "nit")

NOT_REVIEWED_REASONS = {
    "deleted": "deleted",
    "binary": "binary",
    "not-typescript-or-javascript": "not TypeScript or JavaScript",
}

VERDICT_SENTENCES: dict[Verdict, str] = {
    "blocking": "Verdict: blocking. At least one finding is blocking.",
    "findings": "Verdict: findings, none blocking.",
    "no-findings": "Verdict: no findings were accepted.",
    "no-judgement": "Verdict: no judgement. No review was performed; see the degradations above.",
    "nothing-to-review": "Verdict: nothing to review.",
}

_NOT_REPORTED = "not reported"
_NOT_GATHERED = "not gathered in this build"

_STAGE_LABELS: tuple[tuple[str, str], ...] = (
    ("preflight", "preflight"),
    ("change_set", "change set"),
    ("assembly", "assembly"),
    ("review", "review"),
    ("output", "output"),
)


def verdict_sentence(report: ReviewReport) -> str:
    return VERDICT_SENTENCES[report.verdict]


def line_span(finding: Finding) -> str:
    if finding.start_line == finding.end_line:
        return str(finding.start_line)
    return f"{finding.start_line}-{finding.end_line}"


def evidence_line(finding: Finding) -> str:
    evidence = finding.evidence
    if isinstance(evidence, DiffEvidence):
        cited = "diff" if evidence.hunk_index is None else f"diff hunk {evidence.hunk_index}"
        if evidence.file != finding.file:
            cited += f" of {evidence.file}"
        return cited
    if isinstance(evidence, UnverifiedEvidence):
        return f"unverified: {evidence.reason}"
    return evidence.kind


def severity_counts(findings: Sequence[Finding]) -> dict[str, int]:
    return {severity: sum(1 for f in findings if f.severity == severity) for severity in SEVERITY_ORDER}


def stage_rows(run: RunMetadata) -> list[tuple[str, int]]:
    """The stages that ran, in pipeline order.

    ``assembly`` and ``review`` are absent from the report when they did not run (``StageDurations``
    omits them), so they are dropped here rather than rendered as ``None`` by a template.
    """
    durations = run.stage_durations_ms
    rows = []
    for field, label in _STAGE_LABELS:
        value = getattr(durations, field)
        if value is not None:
            rows.append((label, value))
    return rows


def run_rows(run: RunMetadata) -> list[tuple[str, str]]:
    """Run metadata as label/value pairs — an explicit allow-list, never an iteration over the model.

    This is the control that keeps the HTML from growing a field nobody chose to publish. A future addition to
    ``RunMetadata`` — a provider base URL, anything the GitHub work brings — cannot reach a rendering without a
    deliberate edit here. The base URL the API key is sent to is not in the report at all; it lives in config.
    """
    depth = (
        _NOT_GATHERED
        if run.requested_depth is None and run.achieved_depth is None
        else f"{run.requested_depth} requested, {run.achieved_depth} achieved"
    )
    return [
        ("started at", run.started_at),
        ("duration", f"{run.duration_ms} ms"),
        ("completion status", run.completion_status),
        ("model", run.model),
        ("provider", run.provider),
        ("temperature", str(run.sampling.temperature)),
        ("seed", _NOT_REPORTED if run.sampling.seed is None else str(run.sampling.seed)),
        ("context depth", depth),
        ("tool-call ceiling", str(run.tool_call_ceiling)),
        ("investigation tools", "enabled" if run.investigation_tools_enabled else "disabled"),
        ("tool calls", f"{run.tool_calls_total} total, {run.tool_calls_emission} emitting, "
                       f"{run.tool_calls_investigation} investigating"),
        ("repair turns", str(run.repair_turns)),
        ("emit path", run.emit_path),
        ("tokens in", _NOT_REPORTED if run.tokens_in is None else str(run.tokens_in)),
        ("tokens out", _NOT_REPORTED if run.tokens_out is None else str(run.tokens_out)),
        ("budget", f"{run.budget_limit} limit, {'hit' if run.budget_hit else 'not hit'}"),
        ("report schema", run.schema_version),
        ("tool version", run.tool_version),
    ]
