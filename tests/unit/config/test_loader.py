"""Loading `.agentic-review.yml` — FR-1.2a–d, research R-8, contracts/config.md."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_review.core.config.loader import ConfigError, load_settings
from agentic_review.core.config.settings import DEFAULT_MODEL


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / ".agentic-review.yml"
    path.write_text(text, encoding="utf-8")
    return path


def test_absent_file_gives_defaults(tmp_path: Path) -> None:
    loaded = load_settings(tmp_path / ".agentic-review.yml", explicit=False)
    assert loaded.settings.agent.tool_call_ceiling == 25
    assert loaded.ignored_settings == ()
    assert loaded.scope_from_file is False


def test_empty_file_gives_defaults(tmp_path: Path) -> None:
    assert load_settings(_write(tmp_path, ""), explicit=False).settings.scope == "working-tree"


def test_per_field_merge(tmp_path: Path) -> None:
    loaded = load_settings(_write(tmp_path, "agent:\n  toolCallCeiling: 5\n"), explicit=False)
    assert loaded.settings.agent.tool_call_ceiling == 5
    assert loaded.settings.agent.model == DEFAULT_MODEL
    assert loaded.settings.budget.max_tokens == 200000


def test_scope_named_by_file_is_recorded(tmp_path: Path) -> None:
    assert load_settings(_write(tmp_path, "scope: staged\n"), explicit=False).scope_from_file is True


def _message(path: Path) -> str:
    with pytest.raises(ConfigError) as caught:
        load_settings(path, explicit=True)
    return caught.value.message


def test_unknown_field_is_named(tmp_path: Path) -> None:
    message = _message(_write(tmp_path, "agent:\n  toolCallCeling: 5\n"))
    assert ".agentic-review.yml" in message
    assert "agent.toolCallCeling" in message
    assert "Nothing was reviewed" in message


def test_invalid_value_is_named(tmp_path: Path) -> None:
    message = _message(_write(tmp_path, "agent:\n  toolCallCeiling: 0\n"))
    assert "  agent.toolCallCeiling: Input should be greater than or equal to 1" in message


def test_duplicate_key_is_an_error(tmp_path: Path) -> None:
    message = _message(_write(tmp_path, "agent:\n  model: a\n  model: b\n"))
    assert "agent.model" in message and "duplicate" in message


def test_yaml_syntax_error_names_line_and_column(tmp_path: Path) -> None:
    message = _message(_write(tmp_path, "agent:\n  model: [unclosed\n"))
    assert "line " in message and "column " in message


def test_top_level_must_be_a_mapping(tmp_path: Path) -> None:
    assert "mapping" in _message(_write(tmp_path, "- a\n- b\n"))


def test_api_key_is_an_unknown_field(tmp_path: Path) -> None:
    assert "apiKey" in _message(_write(tmp_path, "apiKey: sk-live-123\n"))


def test_explicit_missing_path_fails(tmp_path: Path) -> None:
    message = _message(tmp_path / "missing.yml")
    assert "missing.yml" in message and "does not exist" in message


def test_ignored_settings_lists_only_paths_present(tmp_path: Path) -> None:
    text = (
        "context:\n  depth: 2\n"
        "checks:\n  tests:\n    command: [npm, test]\n"
        "agent:\n  investigationTools: false\n  toolCallCeiling: 4\n"
    )
    loaded = load_settings(_write(tmp_path, text), explicit=False)
    assert loaded.ignored_settings == ("context.depth", "checks.tests.command")


def test_investigation_tools_true_is_reported(tmp_path: Path) -> None:
    loaded = load_settings(_write(tmp_path, "agent:\n  investigationTools: true\n"), explicit=False)
    assert loaded.ignored_settings == ("agent.investigationTools",)
