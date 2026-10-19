"""Reading a report this tool wrote earlier — FR-10.4d, spec 001 FR-025.

The published schema tells *consumers* to ignore unknown fields, and `ReviewReport` does. What this build refuses
is a report whose declared schema version it does not read, because that is a version mismatch rather than a
tolerable addition.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from agentic_review.core.findings.schema import SCHEMA_VERSION
from agentic_review.core.output.html import render_html
from agentic_review.core.output.json_out import to_json
from agentic_review.core.output.load import ReportNotLoadable, load_report
from tests.conftest import CANARY_KEY
from tests.support.report_factory import report


def _document(**overrides: Any) -> dict[str, Any]:
    document = json.loads(to_json(report()))
    document.update(overrides)
    return document


def test_a_report_written_by_to_json_loads_back_equal() -> None:
    assert load_report(to_json(report())) == report()


def test_a_loaded_report_renders_to_the_same_html() -> None:
    # The constraint behind one renderer and two entry points (FR-10.4d).
    original = report()
    assert render_html(load_report(to_json(original))) == render_html(original)


def test_an_unknown_schema_version_is_refused_naming_both_versions() -> None:
    with pytest.raises(ReportNotLoadable) as raised:
        load_report(json.dumps(_document(schemaVersion="1.1")))
    message = str(raised.value)
    assert SCHEMA_VERSION in message and "1.1" in message


def test_malformed_json_is_refused_naming_where_it_broke() -> None:
    with pytest.raises(ReportNotLoadable) as raised:
        load_report('{"schemaVersion": "1.0",')
    message = str(raised.value)
    assert "line" in message and "column" in message


def test_something_that_is_not_an_object_is_refused() -> None:
    with pytest.raises(ReportNotLoadable):
        load_report("[]")


def test_a_document_without_a_schema_version_is_refused() -> None:
    document = _document()
    del document["schemaVersion"]
    with pytest.raises(ReportNotLoadable) as raised:
        load_report(json.dumps(document))
    assert "schemaVersion" in str(raised.value)


def test_a_document_missing_a_required_field_names_that_field() -> None:
    document = _document()
    del document["verdict"]
    with pytest.raises(ReportNotLoadable) as raised:
        load_report(json.dumps(document))
    assert "verdict" in str(raised.value)


def test_an_unknown_top_level_field_is_ignored_as_the_published_schema_requires() -> None:
    # The report's own schema description says consumers must ignore unknown fields, and `ReportModel` sets
    # extra="ignore" to match. A later build adding a field must not make its reports unreadable here.
    assert load_report(json.dumps(_document(surprise=1))) == report()


def test_an_unknown_field_inside_a_finding_s_evidence_is_refused() -> None:
    # The evidence arms are the types that still forbid extras, because an unrecognised key there means the
    # discriminated union was misread, not that the document is merely newer.
    document = _document()
    document["findings"][0]["evidence"]["surprise"] = 1
    with pytest.raises(ReportNotLoadable) as raised:
        load_report(json.dumps(document))
    assert "evidence" in str(raised.value)


def test_the_message_never_repeats_a_rejected_value() -> None:
    # A malformed report could carry a secret in a field that fails validation; the message names paths, not values.
    with pytest.raises(ReportNotLoadable) as raised:
        load_report(json.dumps(_document(verdict=CANARY_KEY)))
    assert CANARY_KEY not in str(raised.value)
    assert "verdict" in str(raised.value)
