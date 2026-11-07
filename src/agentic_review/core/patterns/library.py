"""Loading and validating the rule library (FR-001, FR-004, FR-025, FR-026, research R-1).

Two sources, in this order: the ``*.yml`` documents shipped as package data beside ``rules/__init__.py``, then
one optional file a project configures through ``patterns.rules``. **Configured rules are added, never
substituted** — there is no precedence order to learn, because there is no override: an identifier belongs to
exactly one rule, and a collision is an error rather than a winner (research R-6; overriding is v2).

Validation is loud and total. Every message names the file and the offending field, with the rule's index where
the identifier itself is the problem, because the author of a rules file debugs against these strings —
``specs/003-rule-library/contracts/rules-file.md`` §3 is the contract and this module is its implementation.
A malformed library stops the run at preflight, the one stage permitted to halt one (FR-005).
"""

from __future__ import annotations

from collections.abc import Iterator
from importlib import resources
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from agentic_review.core.patterns.model import PatternLibrary, PatternRule

SHIPPED_SOURCE = "shipped"
"""``PatternLibrary.source`` when no project file was configured. Reaches the trace, never the report."""

_RULES_PACKAGE = "agentic_review.core.patterns.rules"


class PatternLibraryError(Exception):
    """A rule document could not be loaded. Already a finished, user-facing message."""


def load_library(extra: Path | None = None) -> PatternLibrary:
    """The shipped rules, plus ``extra``'s if one is configured. Raises ``PatternLibraryError`` on any problem."""
    rules: list[PatternRule] = []
    origins: dict[str, str] = {}

    for document in _shipped_documents():
        _add(rules, origins, document.name, _parse(document.read_text(encoding="utf-8"), document.name), True)

    source = SHIPPED_SOURCE
    if extra is not None:
        if not extra.is_file():
            # The key is named rather than the bare path: the reader has to know which setting sent them here.
            raise PatternLibraryError(f"patterns.rules: '{extra}' does not exist")
        _add(rules, origins, extra.name, _parse(extra.read_text(encoding="utf-8"), extra.name), False)
        source = f"{SHIPPED_SOURCE} + {extra.name}"

    if not rules:
        raise PatternLibraryError("the rule library is empty: expected at least one rule")
    return PatternLibrary(rules=tuple(rules), source=source)


def _shipped_documents() -> Iterator[Traversable]:
    """The shipped documents in sorted name order, read through ``importlib.resources``.

    Never by path arithmetic from ``__file__``: the files are package data in the wheel, and this is the only
    lookup that keeps working when the package is zipped (``Docs/technical_stack.md`` §3.1).
    """
    root = resources.files(_RULES_PACKAGE)
    yield from sorted((entry for entry in root.iterdir() if entry.name.endswith(".yml")), key=lambda e: e.name)


def _parse(text: str, name: str) -> list[Any]:
    try:
        document = yaml.safe_load(text)
    except yaml.YAMLError as error:
        # safe_load, never load: a rules file is data and must not be able to construct a Python object.
        raise PatternLibraryError(f"{name}: not valid YAML: {error}") from error
    if not isinstance(document, dict) or not isinstance(document.get("rules"), list):
        raise PatternLibraryError(f"{name}: expected a mapping with a 'rules' list")
    return document["rules"]


def _add(
    rules: list[PatternRule],
    origins: dict[str, str],
    name: str,
    documents: list[Any],
    shipped: bool,
) -> None:
    for index, entry in enumerate(documents):
        where = f"{name}: rules[{index}]"
        if not isinstance(entry, dict):
            raise PatternLibraryError(f"{where}: expected a mapping")
        try:
            rule = PatternRule.model_validate(entry)
        except ValidationError as error:
            raise PatternLibraryError(f"{name}: {_first_problem(index, error)}") from error
        if rule.id in origins:
            raise PatternLibraryError(f"{where}.id: '{rule.id}' is already defined by {origins[rule.id]}")
        origins[rule.id] = "a built-in rule" if shipped else f"{name} rules[{index}]"
        rules.append(rule)


def _first_problem(index: int, error: ValidationError) -> str:
    """One problem, not all of them: the first is the one to fix, and a wall of pydantic is not a contract."""
    problem = error.errors()[0]
    return f"rules[{index}]{_path(problem['loc'])}: {_reason(problem)}"


def _path(loc: tuple[Any, ...]) -> str:
    rendered = ""
    for part in loc:
        rendered += f"[{part}]" if isinstance(part, int) else f".{part}"
    return rendered


def _reason(problem: dict[str, Any]) -> str:
    kind = problem["type"]
    if kind == "missing":
        return "required"
    if kind == "extra_forbidden":
        return "unknown field"
    # Our own validators raise PydanticCustomError, whose message is already the contract's wording. Pydantic
    # prefixes a plain ValueError with "Value error, "; strip it so no message leaks the framework.
    return str(problem["msg"]).removeprefix("Value error, ")
