"""AGENTIC_REVIEW_MODEL and AGENTIC_REVIEW_BASE_URL reach the provider client and the report (05 §4.1).

The unit tests hold the resolution order; this holds the wiring: what the environment says is what the review step
binds and what the report says it used, so a developer who switches provider in `.env` can see that it took.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from agentic_review.agents.pipeline_agent import ReviewRequest, Reviewed, run_review
from agentic_review.cli.app import app
from agentic_review.cli.exit_codes import EXIT_PREFLIGHT
from agentic_review.core.config.environment import BASE_URL_ENV_VAR, MODEL_ENV_VAR
from agentic_review.core.config.settings import AgentSettings
from tests.support.repo_builder import RepoBuilder
from tests.support.scripted_chat_model import ScriptedChatModel, ai_reply, finding_call


@pytest.fixture
def repo(tmp_path: Path) -> RepoBuilder:
    builder = RepoBuilder(tmp_path / "repo").init()
    builder.write("src/app.ts", "export const a = 1;\n").commit("initial")
    builder.write("src/app.ts", "export const a = 2;\n")
    return builder


def test_the_environment_chooses_the_model_the_review_step_binds(
    repo: RepoBuilder, canary_env: dict[str, str]
) -> None:
    from agentic_review.agents.review_port import build_review_port

    bound: list[AgentSettings] = []

    def factory(settings: AgentSettings, credential: object) -> object:
        bound.append(settings)
        script = [ai_reply([finding_call(file="src/app.ts")])]
        return build_review_port(settings, credential, chat_model=ScriptedChatModel(script))  # type: ignore[arg-type]

    env = {**canary_env, MODEL_ENV_VAR: "qwen/qwen3-coder-480b", BASE_URL_ENV_VAR: "https://nim.example/v1"}
    result = run_review(ReviewRequest(cwd=repo.root), env=env, port_factory=factory)  # type: ignore[arg-type]

    assert isinstance(result, Reviewed), result
    assert [(s.model, s.base_url) for s in bound] == [("qwen/qwen3-coder-480b", "https://nim.example/v1")]
    assert result.report.run.model == "qwen/qwen3-coder-480b"
    assert result.report.run.provider == "nim.example", "the provider is the endpoint's host"


def test_an_unusable_endpoint_in_the_environment_stops_the_cli_before_any_model_call(
    repo: RepoBuilder, canary_env: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(repo.root)
    monkeypatch.setenv(BASE_URL_ENV_VAR, "nim.example/v1")
    result = CliRunner().invoke(app, ["review"])
    assert result.exit_code == EXIT_PREFLIGHT
    assert BASE_URL_ENV_VAR in result.output
