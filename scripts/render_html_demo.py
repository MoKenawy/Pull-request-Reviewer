"""Render the HTML report without running a review — SRS FR-10.4d.

Template work costs no provider calls and needs no repository. With no argument it renders the canonical two-finding
report the test suite uses; given a path, it renders a JSON report written earlier by ``review --json PATH``.

    uv run python scripts/render_html_demo.py
    uv run python scripts/render_html_demo.py r.json --out r.html
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))  # so tests.support is importable when running from a checkout

from agentic_review.core.output.html import render_html  # noqa: E402
from agentic_review.core.output.load import ReportNotLoadable, load_report  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", nargs="?", type=Path, help="a JSON report; omit for the built-in sample")
    parser.add_argument("--out", type=Path, default=Path("review-report.html"), help="where to write the HTML")
    parser.add_argument("--title", default=None)
    arguments = parser.parse_args()

    if arguments.report is None:
        from tests.support.report_factory import report as sample

        document = sample()
        source = "the built-in sample report"
    else:
        try:
            document = load_report(arguments.report.read_text(encoding="utf-8"))
        except OSError as error:
            print(f"could not read {arguments.report}: {error}", file=sys.stderr)
            return 1
        except ReportNotLoadable as error:
            print(f"{arguments.report}: {error}", file=sys.stderr)
            return 1
        source = str(arguments.report)

    arguments.out.write_text(render_html(document, title=arguments.title), encoding="utf-8", newline="\n")
    print(f"Wrote {arguments.out} from {source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
