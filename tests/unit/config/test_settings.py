"""The configuration model — data-model §7, FR-1.2b–d, FR-1.3a."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from agentic_review.core.config.settings import DEFAULT_BASE_URL, DEFAULT_MODEL, Settings


def test_defaults() -> None:
    settings = Settings()
    assert settings.schema_version == 1
    assert settings.scope == "working-tree"
    assert settings.exclude == []
    assert settings.context.depth == 1 and settings.context.node == "node"
    assert settings.checks.tests.command is None and settings.checks.tests.timeout_seconds == 120
    assert settings.agent.tool_call_ceiling == 25
    assert settings.agent.investigation_tools is False
    assert settings.agent.model == DEFAULT_MODEL
    assert settings.agent.base_url == DEFAULT_BASE_URL  # the two constants are where the endpoint is chosen
    assert settings.agent.temperature == 0
    assert settings.agent.request_timeout_seconds == 60
    assert settings.agent.rate_limit_retry_seconds == 60
    assert settings.budget.max_tokens == 200000
    assert settings.patterns.rules is None  # spec 003 FR-024: absent is not an error and reports nothing


def _error_locs(data: dict[str, Any]) -> list[tuple[Any, ...]]:
    with pytest.raises(ValidationError) as caught:
        Settings.model_validate(data)
    return [e["loc"] for e in caught.value.errors()]


@pytest.mark.parametrize(
    "data,loc",
    [
        ({"schemaVersion": 2}, ("schemaVersion",)),
        ({"agent": {"toolCallCeling": 5}}, ("agent", "toolCallCeling")),
        ({"context": {"deep": 2}}, ("context", "deep")),
        ({"checks": {"lint": {}}}, ("checks", "lint")),
        ({"budget": {"maxTokens": 0}}, ("budget", "maxTokens")),
        ({"agent": {"toolCallCeiling": 0}}, ("agent", "toolCallCeiling")),
        ({"agent": {"temperature": 2.5}}, ("agent", "temperature")),
        ({"agent": {"rateLimitRetrySeconds": -1}}, ("agent", "rateLimitRetrySeconds")),
        ({"agent": {"baseUrl": "ftp://example.com"}}, ("agent", "baseUrl")),
        ({"checks": {"tests": {"command": []}}}, ("checks", "tests", "command")),
        ({"scope": "everything"}, ("scope",)),
        ({"apiKey": "sk-123"}, ("apiKey",)),
        ({"agent": {"apiKey": "sk-123"}}, ("agent", "apiKey")),
        ({"patterns": {"rule": "./review-rules.yml"}}, ("patterns", "rule")),
        ({"patterns": {"rules": "./x.yml", "extra": 1}}, ("patterns", "extra")),
    ],
)
def test_invalid_or_unknown_fields_are_named(data: dict[str, Any], loc: tuple[Any, ...]) -> None:
    assert loc in _error_locs(data)


def test_a_configured_rules_path_validates_and_stays_a_path(tmp_path: Path) -> None:
    """spec 003 FR-024. The first Path-typed setting; resolution against the repository root is preflight's."""
    relative = Settings.model_validate({"patterns": {"rules": "./review-rules.yml"}})
    assert relative.patterns.rules == Path("review-rules.yml")
    absolute = Settings.model_validate({"patterns": {"rules": str(tmp_path / "r.yml")}})
    assert absolute.patterns.rules == tmp_path / "r.yml"


def test_no_field_can_hold_a_credential() -> None:
    names = str(Settings.model_json_schema(by_alias=True)).lower()
    for word in ("apikey", "api_key", "token\"", "secret", "password", "credential"):
        assert word not in names
