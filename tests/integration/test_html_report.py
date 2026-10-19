"""The HTML report end to end — FR-10.4d, spec 001 FR-027, research R-16, SC-007.

The report written during a review and the report re-rendered from its JSON must be the same document, and the
HTML must agree with the JSON about what was found. Runs through the Typer app with the stand-in model.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import httpx
import openai
import pytest
from typer.testing import CliRunner

from agentic_review.agents import pipeline_agent
from agentic_review.agents.review_port import build_review_port
from agentic_review.cli.app import app
from agentic_review.core.output.view import NO_TOOL_CALL_LINE
from tests.conftest import CANARY_KEY
from tests.support.report_assertions import assert_no_canary, assert_valid_report
from tests.support.repo_builder import RepoBuilder
from tests.support.scripted_chat_model import ScriptedChatModel, ai_reply, finding_call

_REQUEST = httpx.Request("POST", "https://example.invalid/v1/chat/completions")

IMPORTANT_AND_NIT = [
    finding_call(severity="important", category="error-handling", startLine=2, endLine=4,
                 rationale="Doubling changes the exported contract."),
    finding_call(severity="nit", category="maintainability", startLine=7, endLine=7,
                 evidence={"kind": "unverified", "reason": "naming judgement"}, rationale="Names are opaque."),
]


@pytest.fixture
def repo(tmp_path: Path) -> RepoBuilder:
    builder = RepoBuilder(tmp_path / "repo").init()
    builder.write("src/app.ts", "".join(f"export const v{i} = {i};\n" for i in range(1, 21)))
    builder.write("README.md", "# demo\n")
    builder.commit("initial")
    builder.write("src/app.ts", "".join(f"export const v{i} = {i * 2};\n" for i in range(1, 21)))
    builder.write("README.md", "# demo\nmore\n")
    return builder


def _factory(model: ScriptedChatModel) -> Callable[..., object]:
    return lambda settings, credential: build_review_port(settings, credential, chat_model=model)


def _install(monkeypatch: pytest.MonkeyPatch, repo: RepoBuilder, script: list[object]) -> ScriptedChatModel:
    model = ScriptedChatModel(script)  # type: ignore[arg-type]
    monkeypatch.setattr(pipeline_agent, "build_review_port", _factory(model))
    monkeypatch.chdir(repo.root)
    return model


def test_review_writes_an_html_file_whose_findings_match_the_json_report(
    repo: RepoBuilder, canary_env: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    _install(monkeypatch, repo, [ai_reply(IMPORTANT_AND_NIT)])
    result = CliRunner().invoke(app, ["review", "--json", "r.json", "--html", "r.html"])
    assert result.exit_code == 0, result.output

    document = json.loads((repo.root / "r.json").read_text(encoding="utf-8"))
    assert_valid_report(document)
    html = (repo.root / "r.html").read_text(encoding="utf-8")

    assert document["findings"], "the scenario is pointless without findings"
    for finding in document["findings"]:
        assert f'id="{finding["id"]}"' in html
        assert finding["rationale"] in html
        assert finding["severity"] in html and finding["category"] in html
    assert document["changeSummary"]["scope"]["description"] in html
    # The terminal summary still owns stdout; the files are extra (contracts/cli.md "Streams").
    assert "Verdict:" in result.stdout


def test_a_saved_report_renders_to_the_same_html_as_the_run_did(
    repo: RepoBuilder, canary_env: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # One renderer, two entry points (FR-10.4d). This fails the moment anything non-deterministic — a clock, an
    # environment variable, a path — reaches the template.
    _install(monkeypatch, repo, [ai_reply(IMPORTANT_AND_NIT)])
    assert CliRunner().invoke(app, ["review", "--json", "r.json", "--html", "a.html"]).exit_code == 0

    result = CliRunner().invoke(app, ["render", "r.json", "--html", "b.html"])
    assert result.exit_code == 0, result.output
    assert (repo.root / "a.html").read_bytes() == (repo.root / "b.html").read_bytes()


def test_the_html_report_carries_no_planted_credential(
    repo: RepoBuilder, canary_env: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    _install(monkeypatch, repo, [ai_reply(IMPORTANT_AND_NIT)])
    result = CliRunner().invoke(app, ["review", "--json", "r.json", "--html", "r.html"])
    assert result.exit_code == 0, result.output
    html = repo.root / "r.html"
    # The bytes as well as the text: a credential mangled by escaping would still be recoverable from them.
    assert_no_canary(html.read_text(encoding="utf-8"), html.read_bytes(), result.stdout, result.stderr)
    assert_no_canary((repo.root / "r.json").read_text(encoding="utf-8"))


def test_a_provider_error_puts_the_credential_free_detail_in_the_html(
    repo: RepoBuilder, canary_env: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    error = openai.APIConnectionError(message=f"could not reach host (key {CANARY_KEY})", request=_REQUEST)
    _install(monkeypatch, repo, [error])
    result = CliRunner().invoke(app, ["review", "--html", "r.html"])
    assert result.exit_code == 2, result.output
    html = (repo.root / "r.html").read_text(encoding="utf-8")
    assert "No review was performed" in html
    assert "no findings" not in html.lower()
    assert_no_canary(html, (repo.root / "r.html").read_bytes())


def test_a_no_tool_call_run_is_not_shown_as_clean_in_the_html(
    repo: RepoBuilder, canary_env: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    _install(monkeypatch, repo, [ai_reply()])
    result = CliRunner().invoke(app, ["review", "--html", "r.html"])
    assert result.exit_code == 0, result.output
    html = (repo.root / "r.html").read_text(encoding="utf-8")
    assert NO_TOOL_CALL_LINE in html
    for word in ("passed", "clean", "no issues", "looks good", "all clear"):
        assert word not in html.lower(), word


def test_the_written_files_are_utf8_with_newline_endings(
    repo: RepoBuilder, canary_env: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    _install(monkeypatch, repo, [ai_reply(IMPORTANT_AND_NIT)])
    assert CliRunner().invoke(app, ["review", "--json", "r.json", "--html", "r.html"]).exit_code == 0
    for name in ("r.json", "r.html"):
        data = (repo.root / name).read_bytes()
        assert b"\r\n" not in data, name
        data.decode("utf-8")


def test_a_preflight_failure_writes_neither_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    outside = tmp_path / "not-a-repo"
    outside.mkdir()
    monkeypatch.chdir(outside)
    result = CliRunner().invoke(app, ["review", "--json", "r.json", "--html", "r.html"])
    assert result.exit_code == 3, result.output
    assert result.stdout == ""
    assert not (outside / "r.json").exists() and not (outside / "r.html").exists()


def test_html_alone_needs_no_json(
    repo: RepoBuilder, canary_env: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    _install(monkeypatch, repo, [ai_reply([finding_call(severity="blocking")])])
    result = CliRunner().invoke(app, ["review", "--html", "r.html"])
    assert result.exit_code == 1, result.output
    assert (repo.root / "r.html").is_file()
    assert not (repo.root / "r.json").exists()
