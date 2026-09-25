"""Reading `.agentic-review.yml` (research R-8, contracts/config.md).

Failures are loud and field-precise: an unknown field, an invalid value, a duplicate key or a syntax error stops the run
naming the file and the dotted field path (FR-1.2d). PyYAML silently keeps the last of two duplicate keys, so the
document is composed and checked for duplicates before it is loaded.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from agentic_review.core.config.settings import Settings

_FOOTER = "Nothing was reviewed. Fix the field above and re-run."


class ConfigError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


@dataclass(frozen=True)
class LoadedSettings:
    settings: Settings
    ignored_settings: tuple[str, ...]
    scope_from_file: bool


def load_settings(path: Path, *, explicit: bool, display_name: str | None = None) -> LoadedSettings:
    name = display_name or str(path)
    if not path.is_file():
        if explicit:
            raise ConfigError(f"Error in {name}\n  the configuration file does not exist\n{_FOOTER}")
        return LoadedSettings(Settings(), (), scope_from_file=False)

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise ConfigError(f"Error in {name}\n  the file could not be read: {error}\n{_FOOTER}") from error

    try:
        _reject_duplicate_keys(yaml.compose(text, Loader=yaml.SafeLoader), [])
        data = yaml.safe_load(text)
    except _DuplicateKey as error:
        raise ConfigError(f"Error in {name}\n  {error.path}: duplicate key ({error.where})\n{_FOOTER}") from None
    except yaml.YAMLError as error:
        mark = getattr(error, "problem_mark", None)
        where = f"line {mark.line + 1}, column {mark.column + 1}" if mark else "unknown position"
        problem = getattr(error, "problem", None) or "invalid YAML"
        raise ConfigError(f"Error in {name}\n  {where}: {problem}\n{_FOOTER}") from None

    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ConfigError(f"Error in {name}\n  the top level must be a mapping of settings\n{_FOOTER}")

    try:
        settings = Settings.model_validate(data)
    except ValidationError as error:
        lines = [f"  {'.'.join(str(part) for part in e['loc']) or '(top level)'}: {e['msg']}" for e in error.errors()]
        raise ConfigError("\n".join([f"Error in {name}", *lines, _FOOTER])) from None

    return LoadedSettings(settings, _ignored_settings(data), scope_from_file="scope" in data)


class _DuplicateKey(Exception):
    def __init__(self, path: str, where: str) -> None:
        super().__init__(path)
        self.path = path
        self.where = where


def _reject_duplicate_keys(node: yaml.Node | None, path: list[str]) -> None:
    if isinstance(node, yaml.MappingNode):
        seen: set[str] = set()
        for key_node, value_node in node.value:
            key = str(key_node.value)
            child = [*path, key]
            if key in seen:
                mark = key_node.start_mark
                raise _DuplicateKey(".".join(child), f"line {mark.line + 1}, column {mark.column + 1}")
            seen.add(key)
            _reject_duplicate_keys(value_node, child)
    elif isinstance(node, yaml.SequenceNode):
        for item in node.value:
            _reject_duplicate_keys(item, path)


def _ignored_settings(data: dict[str, Any]) -> tuple[str, ...]:
    """Dotted paths set in the file for capabilities this build does not have (FR-1.2d; Docs/design/04-contracts.md §7)."""
    paths: list[str] = []

    def leaves(value: Any, prefix: str) -> None:
        if isinstance(value, dict) and value:
            for key, child in value.items():
                leaves(child, f"{prefix}.{key}")
        else:
            paths.append(prefix)

    for section in ("context", "checks"):
        if section in data:
            leaves(data[section], section)
    agent = data.get("agent")
    if isinstance(agent, dict) and agent.get("investigationTools") is True:
        paths.append("agent.investigationTools")
    return tuple(paths)
