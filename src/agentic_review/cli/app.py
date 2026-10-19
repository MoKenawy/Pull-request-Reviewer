"""The command-line adapter (contracts/cli.md). It translates flags, streams and exit codes, and decides nothing
about findings (FR-10.2). Nothing imports this package (import contract 6).
"""

from __future__ import annotations

import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from agentic_review.cli.exit_codes import EXIT_PREFLIGHT, exit_code_for
from agentic_review.core.output.html import render_html
from agentic_review.core.output.json_out import to_json
from agentic_review.core.output.load import ReportNotLoadable, load_report
from agentic_review.core.output.terminal import render_terminal
from agentic_review.core.pipeline.preflight import PreflightFailure
from agentic_review.agents.pipeline_agent import ReviewRequest, run_review

app = typer.Typer(add_completion=False, no_args_is_help=True, help="Review a TypeScript/JavaScript change set.")

# Only the scopes this build resolves are offered (contracts/cli.md: a flag arrives with what gives it meaning).
# The pull-request scope is selected by --pr, not by --scope.
OFFERED_SCOPES = ("working-tree", "range")

STDOUT_NOT_OFFERED = (
    "{flag}: writing the report to stdout is not available in this build; give {flag} a path. (spec 001 T092)"
)
"""The optional-value form of --json, its stream switch and the `schema` command are still T092."""


@app.callback()
def _root() -> None:
    """Review a TypeScript/JavaScript change set."""


def _could_not_start(message: str) -> typer.Exit:
    # Checked here rather than by Click, whose usage error exits 2 — the code for "no judgement", not "could not
    # start" (contracts/cli.md "Exit codes").
    typer.echo(f"{message}\nNothing was reviewed.", err=True)
    return typer.Exit(EXIT_PREFLIGHT)


def _checked_output_path(path: Path | None, flag: str) -> Path | None:
    """Refuse an unusable output path *before* the review runs, so a typo never costs a provider call."""
    if path is None:
        return None
    if str(path) == "-":
        raise _could_not_start(STDOUT_NOT_OFFERED.format(flag=flag))
    if path.is_dir():
        raise _could_not_start(f"{flag}: {path} is a directory; give it a file path.")
    parent = path.parent if str(path.parent) else Path(".")
    if not parent.is_dir():
        raise _could_not_start(f"{flag}: the directory {parent} does not exist.")
    return path


def _write(path: Path, text: str) -> None:
    # An explicit newline: without it Windows writes \r\n, and contracts/cli.md requires \n for a report file.
    path.write_text(text, encoding="utf-8", newline="\n")


@app.command()
def review(
    scope: Annotated[
        str | None,
        typer.Option(
            "--scope",
            metavar="|".join(OFFERED_SCOPES),
            help="What to review; overrides the config file's scope. Default: working-tree.",
        ),
    ] = None,
    base: Annotated[
        str | None,
        typer.Option(
            "--base", metavar="REF", help="With --scope range: the ref to compare with. With --pr: its base branch."
        ),
    ] = None,
    head: Annotated[
        str | None,
        typer.Option("--head", metavar="REF", help="With --scope range: the ref to review instead of HEAD."),
    ] = None,
    pr: Annotated[
        str | None,
        typer.Option(
            "--pr",
            metavar="URL",
            help="Review a public GitHub pull request, https://github.com/OWNER/REPO/pull/N. Needs no local repository.",
        ),
    ] = None,
    config: Annotated[
        Path | None,
        typer.Option("--config", metavar="PATH", help="Configuration file to use instead of .agentic-review.yml."),
    ] = None,
    ceiling: Annotated[
        int | None,
        typer.Option(
            "--ceiling", metavar="N", help="Tool-call ceiling for this run (at least 1); overrides agent.toolCallCeiling."
        ),
    ] = None,
    json_path: Annotated[
        Path | None,
        typer.Option("--json", metavar="PATH", help="Write the JSON report to PATH, overwriting it."),
    ] = None,
    html_path: Annotated[
        Path | None,
        typer.Option("--html", metavar="PATH", help="Write an HTML rendering of the same report to PATH."),
    ] = None,
) -> None:
    """Review uncommitted changes, a branch range (--scope range --base REF), or a pull request (--pr URL)."""
    if ceiling is not None and ceiling < 1:
        raise _could_not_start(f"--ceiling: must be an integer of at least 1, got {ceiling}.")
    if scope is not None and scope not in OFFERED_SCOPES:
        offered = " or ".join(OFFERED_SCOPES)
        raise _could_not_start(f"--scope: {scope!r} is not available in this build; choose {offered}.")
    json_path = _checked_output_path(json_path, "--json")
    html_path = _checked_output_path(html_path, "--html")
    request = ReviewRequest(
        cwd=Path.cwd(), scope=scope, base=base, head=head, pr=pr, config_path=config, ceiling=ceiling
    )
    result = run_review(request, env=os.environ)
    if isinstance(result, PreflightFailure):
        typer.echo(result.message, err=True)
        raise typer.Exit(EXIT_PREFLIGHT)
    if json_path is not None:
        _write(json_path, to_json(result.report))
    if html_path is not None:
        _write(html_path, render_html(result.report))
    render_terminal(result.report, Console())
    raise typer.Exit(exit_code_for(result.report.verdict))


@app.command()
def render(
    report: Annotated[
        Path,
        typer.Argument(metavar="REPORT", help="A JSON report written earlier by `review --json PATH`."),
    ],
    html_path: Annotated[
        Path,
        typer.Option("--html", metavar="PATH", help="Where to write the HTML rendering."),
    ],
) -> None:
    """Re-render a saved JSON report as HTML, without reviewing anything."""
    # Needs no repository, no config and no credential, and makes no judgement — so it never exits 1 or 2. A
    # verdict read out of a file on disk is not this run's outcome, and a stale report must not set a CI status
    # (contracts/cli.md "render").
    checked = _checked_output_path(html_path, "--html")
    assert checked is not None  # the option is required, so it is never None here
    try:
        text = report.read_text(encoding="utf-8")
    except OSError as error:
        raise _could_not_start(f"REPORT: could not read {report}: {error.strerror or error}.") from error
    try:
        loaded = load_report(text)
    except ReportNotLoadable as error:
        raise _could_not_start(f"REPORT: {report}: {error}") from error
    _write(checked, render_html(loaded))
    typer.echo(f"Wrote {checked}")
    raise typer.Exit(0)


def _reject_json_to_stdout(argv: Sequence[str]) -> str | None:
    """The message for a bare ``--json`` or ``--json -``, or None.

    Click would reject a value-less option with its own usage error, which exits 2 — the code for "no judgement"
    rather than "could not start". This runs before Click sees argv. It is deliberately **not** ``normalise_argv``:
    that name belongs to T092 and rewrites argv to ``--json -``, which this build does not offer.
    """
    for index, token in enumerate(argv):
        if token not in ("--json", "--html"):
            continue
        following = argv[index + 1] if index + 1 < len(argv) else None
        if following is None or following == "-" or following.startswith("-"):
            return STDOUT_NOT_OFFERED.format(flag=token)
    return None


def main() -> None:
    message = _reject_json_to_stdout(sys.argv[1:])
    if message is not None:
        print(f"{message}\nNothing was reviewed.", file=sys.stderr)
        raise SystemExit(EXIT_PREFLIGHT)
    app()
