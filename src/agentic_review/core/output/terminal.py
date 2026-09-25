"""The terminal summary (FR-8.1b, contracts/cli.md "Terminal summary").

The only module under ``core/`` that imports Rich (import contract 1). ``core/pipeline/`` never imports it; the CLI does.
Everything shown is read from the ``ReviewReport``; nothing is recomputed here (FR-10.4a).
"""

from __future__ import annotations

from rich.console import Console
from rich.text import Text

from agentic_review.core.findings.model import DiffEvidence, Finding, UnverifiedEvidence
from agentic_review.core.findings.report import ReviewReport

EXCLUDED_SHOWN = 10
_REASONS = {
    "deleted": "deleted",
    "binary": "binary",
    "not-typescript-or-javascript": "not TypeScript or JavaScript",
}
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
            line(f"  {f.path} ({_REASONS[f.not_reviewed_reason or 'deleted']})")
    if summary.excluded:
        if len(summary.excluded) > EXCLUDED_SHOWN:
            line(f"Excluded: {len(summary.excluded)} paths excluded; the JSON report lists each with its rule.")
        else:
            line(f"Excluded ({len(summary.excluded)}):")
            for excluded in summary.excluded:
                line(f"  {excluded.path} ({excluded.rule})")

    line()
    line("No checks were run in this build.", "dim")
    line("No related context was gathered in this build.", "dim")
    line()

    for finding in report.findings:
        _finding(line, finding)

    counts = {severity: sum(1 for f in report.findings if f.severity == severity) for severity in _SEVERITY_STYLE}
    line(f"Findings: {counts['blocking']} blocking / {counts['important']} important / {counts['nit']} nit")

    for degradation in report.degradations:
        line(f"Degradation [{degradation.source}] {degradation.code}: {degradation.detail}", "yellow")

    line(_verdict_line(report), "bold")


def _finding(line, finding: Finding) -> None:  # noqa: ANN001 - the local printer
    span = str(finding.start_line) if finding.start_line == finding.end_line else f"{finding.start_line}-{finding.end_line}"
    line(f"{finding.file}:{span}  {finding.severity}  {finding.category}", _SEVERITY_STYLE[finding.severity])
    line(f"  {finding.rationale}")
    evidence = finding.evidence
    if isinstance(evidence, DiffEvidence):
        cited = "diff" if evidence.hunk_index is None else f"diff hunk {evidence.hunk_index}"
        if evidence.file != finding.file:
            cited += f" of {evidence.file}"
    elif isinstance(evidence, UnverifiedEvidence):
        cited = f"unverified: {evidence.reason}"
    else:
        cited = evidence.kind
    line(f"  evidence: {cited}")
    if finding.rule_id:
        line(f"  rule: {finding.rule_id}")
    line()


def _verdict_line(report: ReviewReport) -> str:
    match report.verdict:
        case "blocking":
            return "Verdict: blocking. At least one finding is blocking."
        case "findings":
            return "Verdict: findings, none blocking."
        case "no-findings":
            return "Verdict: no findings were accepted."
        case "no-judgement":
            return "Verdict: no judgement. No review was performed; see the degradations above."
        case "nothing-to-review":
            return "Verdict: nothing to review."
