"""The terminal summary (FR-8.1b, contracts/cli.md "Terminal summary").

The only module under ``core/`` that imports Rich (import contract 1). ``core/pipeline/`` never imports it; the CLI
does. Everything shown is read from the ``ReviewReport``; nothing is recomputed here (FR-10.4a), and the wording it
shares with the other renderings comes from ``view.py`` rather than being repeated.
"""

from __future__ import annotations

from rich.console import Console
from rich.text import Text

from agentic_review.core.findings.model import Finding
from agentic_review.core.findings.report import ReviewReport
from agentic_review.core.output.view import (
    NO_CHECKS_LINE,
    NO_CONTEXT_LINE,
    NO_TOOL_CALL_LINE,
    NOT_REVIEWED_REASONS,
    evidence_line,
    line_span,
    severity_counts,
    verdict_sentence,
)

EXCLUDED_SHOWN = 10
_SEVERITY_STYLE = {"blocking": "bold red", "important": "yellow", "nit": "cyan"}


def render_terminal(report: ReviewReport, console: Console) -> None:
    summary = report.change_summary

    def line(text: str = "", style: str | None = None) -> None:
        console.print(Text(text, style=style or ""), highlight=False, soft_wrap=True)

    line(f"Scope: {summary.scope.description}", "bold")

    reviewed = [f for f in summary.files if f.reviewed]
    listed = [f for f in summary.files if not f.reviewed]
    line(f"Reviewed ({len(reviewed)}):")
    for f in reviewed:
        renamed = f" (renamed from {f.previous_path})" if f.previous_path else ""
        line(f"  {f.path}{renamed}")
    if listed:
        line(f"Listed, not reviewed ({len(listed)}):")
        for f in listed:
            line(f"  {f.path} ({NOT_REVIEWED_REASONS[f.not_reviewed_reason or 'deleted']})")
    if summary.excluded:
        if len(summary.excluded) > EXCLUDED_SHOWN:
            line(f"Excluded: {len(summary.excluded)} paths excluded; the JSON report lists each with its rule.")
        else:
            line(f"Excluded ({len(summary.excluded)}):")
            for excluded in summary.excluded:
                line(f"  {excluded.path} ({excluded.rule})")

    line()
    line(NO_CHECKS_LINE, "dim")
    line(NO_CONTEXT_LINE, "dim")
    line()

    for finding in report.findings:
        _finding(line, finding)

    counts = severity_counts(report.findings)
    line(f"Findings: {counts['blocking']} blocking / {counts['important']} important / {counts['nit']} nit")

    for degradation in report.degradations:
        line(f"Degradation [{degradation.source}] {degradation.code}: {degradation.detail}", "yellow")

    if report.run.completion_status == "no-tool-call":
        line(NO_TOOL_CALL_LINE, "yellow")
    line(verdict_sentence(report), "bold")


def _finding(line, finding: Finding) -> None:  # noqa: ANN001 - the local printer
    line(f"{finding.file}:{line_span(finding)}  {finding.severity}  {finding.category}", _SEVERITY_STYLE[finding.severity])
    line(f"  {finding.rationale}")
    line(f"  evidence: {evidence_line(finding)}")
    if finding.rule_id:
        line(f"  rule: {finding.rule_id}")
    line()
