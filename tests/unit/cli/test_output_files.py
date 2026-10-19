"""Output paths are refused before the review runs — FR-10.4d, spec 001 FR-025, contracts/cli.md "Streams"."""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from agentic_review.cli.app import _reject_json_to_stdout, app


@pytest.mark.parametrize(
    "argv",
    [
        ["review", "--json"],
        ["review", "--html"],
        ["review", "--json", "-"],
        ["review", "--json", "--pr", "https://example.invalid/x"],
        ["review", "--html", "--scope", "range"],
    ],
)
def test_a_value_less_output_flag_is_refused_before_click_sees_it(argv: list[str]) -> None:
    # Click's own usage error exits 2, which means "no judgement" — not "could not start" (contracts/cli.md).
    message = _reject_json_to_stdout(argv)
    assert message is not None
    assert "not available in this build" in message


@pytest.mark.parametrize(
    "argv",
    [["review", "--json", "out.json"], ["review", "--html", "out.html"], ["review"], ["render", "r.json"]],
)
def test_an_output_flag_with_a_path_passes_the_guard(argv: list[str]) -> None:
    assert _reject_json_to_stdout(argv) is None


def test_the_guard_names_the_flag_it_refused() -> None:
    assert "--html" in (_reject_json_to_stdout(["review", "--html"]) or "")
    assert "--json" in (_reject_json_to_stdout(["review", "--json"]) or "")


def test_json_dash_exits_three_rather_than_clicks_two() -> None:
    result = CliRunner().invoke(app, ["review", "--json", "-"])
    assert result.exit_code == 3, result.output
    assert "Nothing was reviewed." in result.stderr


def test_an_output_path_in_a_missing_directory_exits_three_before_the_review_runs(
    monkeypatch: pytest.MonkeyPatch, tmp_path: object
) -> None:
    # No stand-in model is installed, so reaching the pipeline at all would raise rather than exit 3.
    import agentic_review.agents.pipeline_agent as pipeline_agent

    def never_called(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("the review ran despite an unusable output path")

    monkeypatch.setattr(pipeline_agent, "run_review", never_called)
    monkeypatch.setattr("agentic_review.cli.app.run_review", never_called)
    result = CliRunner().invoke(app, ["review", "--html", "nowhere-at-all/r.html"])
    assert result.exit_code == 3, result.output
    assert "nowhere-at-all" in result.stderr


def test_an_output_path_that_is_a_directory_exits_three(monkeypatch: pytest.MonkeyPatch, tmp_path: object) -> None:
    def never_called(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("the review ran despite an unusable output path")

    monkeypatch.setattr("agentic_review.cli.app.run_review", never_called)
    result = CliRunner().invoke(app, ["review", "--json", str(tmp_path)])
    assert result.exit_code == 3, result.output
    assert "is a directory" in result.stderr
