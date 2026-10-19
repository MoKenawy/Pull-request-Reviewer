"""Reading a report this tool wrote earlier — FR-10.4d, spec 001 FR-025.

Text in, model out: the filesystem belongs to ``cli/``, so this module performs no I/O and owns no path. The
declared schema version is checked before validation, so a report from a later build fails with a sentence rather
than a list of field errors that do not say what is actually wrong.
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from agentic_review.core.findings.report import ReviewReport
from agentic_review.core.findings.schema import SCHEMA_VERSION


class ReportNotLoadable(ValueError):
    """The text is not a review report this build can read. ``str(self)`` is the message shown to a user."""


def load_report(text: str) -> ReviewReport:
    try:
        document: Any = json.loads(text)
    except json.JSONDecodeError as error:
        raise ReportNotLoadable(
            f"not a JSON document: {error.msg} at line {error.lineno}, column {error.colno}."
        ) from error

    if not isinstance(document, dict):
        kind = type(document).__name__
        raise ReportNotLoadable(f"a review report is a JSON object; this document is a {kind}.")

    declared = document.get("schemaVersion")
    if declared is None:
        raise ReportNotLoadable(
            "no schemaVersion: this does not look like a review report written by this tool."
        )
    if declared != SCHEMA_VERSION:
        raise ReportNotLoadable(
            f"this build reads review-report schema {SCHEMA_VERSION}; the file declares {declared}."
        )

    try:
        return ReviewReport.model_validate(document)
    except ValidationError as error:
        # Field paths only, never the rejected values: a malformed report could carry a secret in a field that
        # failed validation, and this message is printed.
        paths = sorted({_path(problem["loc"]) for problem in error.errors()})
        raise ReportNotLoadable(
            "the document declares review-report schema "
            f"{SCHEMA_VERSION} but does not match it. Fields at fault: {', '.join(paths)}."
        ) from error


def _path(location: tuple[int | str, ...]) -> str:
    return ".".join(str(part) for part in location) or "(the document itself)"
