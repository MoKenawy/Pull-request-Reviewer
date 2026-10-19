"""`render` re-renders a saved report and makes no judgement — FR-10.4d, contracts/cli.md "render"."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from agentic_review.cli.app import app
from agentic_review.core.output.html import render_html
from agentic_review.core.output.json_out import to_json
from tests.support.report_factory import report


def _saved(tmp_path: Path, **overrides: object) -> Path:
    path = tmp_path / "r.json"
    path.write_text(to_json(report(**overrides)), encoding="utf-8", newline="\n")
    return path


def test_render_writes_the_html_file_and_exits_zero(tmp_path: Path) -> None:
    out = tmp_path / "r.html"
    result = CliRunner().invoke(app, ["render", str(_saved(tmp_path)), "--html", str(out)])
    assert result.exit_code == 0, result.output
    assert out.read_text(encoding="utf-8") == render_html(report())
    assert f"Wrote {out}" in result.stdout


def test_render_reproduces_what_review_would_have_written(tmp_path: Path) -> None:
    # The constraint behind one renderer and two entry points: nothing in the template may read the clock.
    out = tmp_path / "r.html"
    CliRunner().invoke(app, ["render", str(_saved(tmp_path)), "--html", str(out)])
    assert out.read_bytes() == render_html(report()).encode("utf-8")


def test_render_needs_no_repository_no_config_and_no_credential(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The autouse _isolate_environment fixture has already removed AGENTIC_REVIEW_API_KEY.
    saved = _saved(tmp_path)
    elsewhere = tmp_path / "not-a-repo"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    result = CliRunner().invoke(app, ["render", str(saved), "--html", "out.html"])
    assert result.exit_code == 0, result.output
    assert (elsewhere / "out.html").is_file()


@pytest.mark.parametrize("verdict", ["blocking", "no-judgement"])
def test_render_does_not_map_the_verdict_onto_its_exit_code(tmp_path: Path, verdict: str) -> None:
    # `review` would exit 1 and 2 for these. `render` makes no judgement, so it exits 0.
    saved = _saved(tmp_path, verdict=verdict)
    result = CliRunner().invoke(app, ["render", str(saved), "--html", str(tmp_path / "r.html")])
    assert result.exit_code == 0, result.output


def test_render_on_a_missing_file_exits_three_naming_the_path(tmp_path: Path) -> None:
    missing = tmp_path / "nope.json"
    result = CliRunner().invoke(app, ["render", str(missing), "--html", str(tmp_path / "r.html")])
    assert result.exit_code == 3, result.output
    assert "nope.json" in result.stderr
    assert "Nothing was reviewed." in result.stderr


def test_render_on_malformed_json_exits_three_and_writes_no_file(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text('{"schemaVersion": "1.0",', encoding="utf-8")
    out = tmp_path / "r.html"
    result = CliRunner().invoke(app, ["render", str(bad), "--html", str(out)])
    assert result.exit_code == 3, result.output
    assert not out.exists()


def test_render_on_an_unknown_schema_version_exits_three_naming_both_versions(tmp_path: Path) -> None:
    document = json.loads(to_json(report()))
    document["schemaVersion"] = "1.1"
    future = tmp_path / "future.json"
    future.write_text(json.dumps(document), encoding="utf-8")
    result = CliRunner().invoke(app, ["render", str(future), "--html", str(tmp_path / "r.html")])
    assert result.exit_code == 3, result.output
    assert "1.1" in result.stderr and "1.0" in result.stderr


def test_render_on_a_directory_given_as_the_report_exits_three(tmp_path: Path) -> None:
    result = CliRunner().invoke(app, ["render", str(tmp_path), "--html", str(tmp_path / "r.html")])
    assert result.exit_code == 3, result.output


def test_render_overwrites_an_existing_output_file(tmp_path: Path) -> None:
    out = tmp_path / "r.html"
    out.write_text("stale", encoding="utf-8")
    result = CliRunner().invoke(app, ["render", str(_saved(tmp_path)), "--html", str(out)])
    assert result.exit_code == 0, result.output
    assert "stale" not in out.read_text(encoding="utf-8")


def test_render_into_a_missing_directory_exits_three_naming_the_directory(tmp_path: Path) -> None:
    out = tmp_path / "nowhere" / "r.html"
    result = CliRunner().invoke(app, ["render", str(_saved(tmp_path)), "--html", str(out)])
    assert result.exit_code == 3, result.output
    assert "nowhere" in result.stderr


def test_render_writes_the_file_with_newline_endings(tmp_path: Path) -> None:
    out = tmp_path / "r.html"
    CliRunner().invoke(app, ["render", str(_saved(tmp_path)), "--html", str(out)])
    assert b"\r\n" not in out.read_bytes()
