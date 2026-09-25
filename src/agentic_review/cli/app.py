"""The command-line adapter (contracts/cli.md). It translates flags, streams and exit codes, and decides nothing about
findings (FR-10.2). Nothing imports this package (import contract 6).
"""

from __future__ import annotations

import os
from pathlib import Path

import typer
from rich.console import Console

from agentic_review.cli.exit_codes import EXIT_PREFLIGHT, exit_code_for
from agentic_review.core.output.terminal import render_terminal
from agentic_review.core.pipeline.preflight import PreflightFailure
from agentic_review.agents.pipeline_agent import ReviewRequest, run_review

app = typer.Typer(add_completion=False, no_args_is_help=True, help="Review a TypeScript/JavaScript change set.")


@app.callback()
def _root() -> None:
    """Review a TypeScript/JavaScript change set."""


@app.command()
def review() -> None:
    """Review the uncommitted changes in the working tree."""
    result = run_review(ReviewRequest(cwd=Path.cwd()), env=os.environ)
    if isinstance(result, PreflightFailure):
        typer.echo(result.message, err=True)
        raise typer.Exit(EXIT_PREFLIGHT)
    render_terminal(result.report, Console())
    raise typer.Exit(exit_code_for(result.report.verdict))


def main() -> None:
    app()
