"""The HTML report (FR-10.4d). The only module under ``core/`` that imports Jinja2 (import contract 8).

Autoescape is on and is not optional. A finding's rationale and a degradation's detail are prose a model wrote
about a repository nobody vouched for, and a file path or a branch name is attacker-chosen under ``--pr``. Of the
three renderings only this one is opened by a browser, which executes what it is handed.

Everything shown is read from the report; nothing is recomputed here (FR-10.4a). Nothing reads the clock, the
environment, the working directory or any file but the template, so rendering a saved report reproduces what the
review wrote, byte for byte (contracts/cli.md "render").
"""

from __future__ import annotations

from functools import lru_cache
from importlib.resources import files

from jinja2 import Environment, StrictUndefined

from agentic_review.core.findings.report import ReviewReport
from agentic_review.core.output import view

TEMPLATE_PACKAGE = "agentic_review.core.output"
TEMPLATE_NAME = "templates/report.html.j2"


def render_html(report: ReviewReport, *, title: str | None = None) -> str:
    """One self-contained HTML document, ending in a single newline as ``to_json`` does."""
    summary = report.change_summary
    document = _environment().from_string(_template_text()).render(
        title=title or f"Code review — {summary.scope.description}",
        report=report,
        run=report.run,
        summary=summary,
        scope=summary.scope,
        reviewed=[f for f in summary.files if f.reviewed],
        listed=[f for f in summary.files if not f.reviewed],
        findings=[
            {
                "id": finding.id,
                "file": finding.file,
                "span": view.line_span(finding),
                "severity": finding.severity,
                "category": finding.category,
                "rationale": finding.rationale,
                "evidence": view.evidence_line(finding),
                "rule_id": finding.rule_id,
                "turn_index": finding.turn_index,
                "fingerprint": finding.fingerprint,
            }
            for finding in report.findings
        ],
        counts=view.severity_counts(report.findings),
        severity_order=view.SEVERITY_ORDER,
        verdict_sentence=view.verdict_sentence(report),
        no_tool_call_line=view.NO_TOOL_CALL_LINE if report.run.completion_status == "no-tool-call" else None,
        no_checks_line=view.NO_CHECKS_LINE,
        no_context_line=view.NO_CONTEXT_LINE,
        not_reviewed_reasons=view.NOT_REVIEWED_REASONS,
        stage_rows=view.stage_rows(report.run),
        run_rows=view.run_rows(report.run),
    )
    return document.rstrip("\n") + "\n"


@lru_cache(maxsize=1)
def _environment() -> Environment:
    return Environment(
        autoescape=True,  # literally, not select_autoescape: one template, and it is HTML
        undefined=StrictUndefined,  # a renamed field is a loud failure in a test, not a blank cell in a report
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


@lru_cache(maxsize=1)
def _template_text() -> str:
    # Through importlib.resources, never path arithmetic from __file__: that breaks in a zipped distribution, and
    # this is the precedent the resolver bundle follows (technical_stack.md §3.1).
    return files(TEMPLATE_PACKAGE).joinpath(TEMPLATE_NAME).read_text(encoding="utf-8")
