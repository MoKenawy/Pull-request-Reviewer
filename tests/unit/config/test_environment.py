"""The model and endpoint read from the environment — defaults → file → environment → CLI flags (05 §4.1).

The file stays the project's choice and the environment the developer's, so an override wins over the file and a
bad value fails as loudly as a bad field in the file (FR-1.2d).
"""

from __future__ import annotations

import pytest

from agentic_review.core.config.environment import (
    BASE_URL_ENV_VAR,
    MODEL_ENV_VAR,
    AgentOverrides,
    agent_overrides,
    apply_agent_overrides,
)
from agentic_review.core.config.loader import ConfigError
from agentic_review.core.config.settings import DEFAULT_BASE_URL, DEFAULT_MODEL, AgentSettings, Settings


def test_an_absent_variable_is_not_an_override() -> None:
    assert agent_overrides({}) == AgentOverrides(model=None, base_url=None)
    assert agent_overrides({}).is_empty


@pytest.mark.parametrize("value", ["", "   "])
def test_a_blank_variable_is_not_an_override(value: str) -> None:
    """A `.env` file written as `AGENTIC_REVIEW_MODEL=` must behave exactly as if the line were absent."""
    assert agent_overrides({MODEL_ENV_VAR: value, BASE_URL_ENV_VAR: value}).is_empty


def test_surrounding_whitespace_is_ignored() -> None:
    assert agent_overrides({MODEL_ENV_VAR: "  gpt-4o-mini\n"}).model == "gpt-4o-mini"


def test_nothing_set_leaves_the_settings_object_untouched() -> None:
    settings = Settings()
    assert apply_agent_overrides(settings, agent_overrides({})) is settings


def test_the_environment_supplies_the_model_and_the_endpoint() -> None:
    env = {MODEL_ENV_VAR: "qwen/qwen3-coder-480b", BASE_URL_ENV_VAR: "https://integrate.api.nvidia.com/v1"}
    agent = apply_agent_overrides(Settings(), agent_overrides(env)).agent
    assert agent.model == "qwen/qwen3-coder-480b"
    assert agent.base_url == "https://integrate.api.nvidia.com/v1"


def test_the_environment_wins_over_the_file() -> None:
    from_file = Settings(agent=AgentSettings(model="from-file", base_url="https://from-file.example/v1"))
    agent = apply_agent_overrides(from_file, agent_overrides({MODEL_ENV_VAR: "from-env"})).agent
    assert agent.model == "from-env"
    assert agent.base_url == "https://from-file.example/v1", "a variable that is not set overrides nothing"


def test_one_override_leaves_every_other_agent_field_alone() -> None:
    from_file = Settings(agent=AgentSettings(tool_call_ceiling=7, temperature=0.5))
    agent = apply_agent_overrides(from_file, agent_overrides({BASE_URL_ENV_VAR: "http://localhost:11434/v1"})).agent
    assert (agent.tool_call_ceiling, agent.temperature) == (7, 0.5)
    assert agent.model == DEFAULT_MODEL


def test_the_rest_of_the_settings_survive() -> None:
    from_file = Settings(exclude=["**/*.generated.ts"], scope="staged")
    resolved = apply_agent_overrides(from_file, agent_overrides({MODEL_ENV_VAR: "from-env"}))
    assert (resolved.exclude, resolved.scope) == (["**/*.generated.ts"], "staged")


def test_an_endpoint_that_is_not_an_http_url_fails_naming_the_variable() -> None:
    with pytest.raises(ConfigError) as caught:
        apply_agent_overrides(Settings(), agent_overrides({BASE_URL_ENV_VAR: "integrate.api.nvidia.com"}))
    message = caught.value.message
    assert BASE_URL_ENV_VAR in message
    assert "must be an http:// or https:// URL" in message
    assert "Nothing was reviewed." in message


def test_the_default_endpoint_is_still_the_default_when_the_environment_is_silent() -> None:
    assert apply_agent_overrides(Settings(), agent_overrides({})).agent.base_url == DEFAULT_BASE_URL
