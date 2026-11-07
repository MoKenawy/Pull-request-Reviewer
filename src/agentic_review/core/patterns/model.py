"""The rule types — ``PathScope``, ``PatternRule``, ``PatternLibrary`` (data-model §2, FR-002, FR-003, FR-004).

``Category`` and ``Severity`` are **imported** from ``core.findings``, never restated. SRS §5 asks for one
definition rather than two, and feature 007's catch predicate compares a finding's category with an expectation's
— a second vocabulary here would be a silent scoring bug there.

Validation covers *shape*: non-empty, POSIX-separated, not absolute, a slug identifier, a known category. It
deliberately stops short of checking that a path pattern is well formed, because the dialect's translator in
``core.changeset.exclusion`` accepts any string: there are no invalid patterns, only patterns that match nothing.
Nobody should build a pattern validator, least of all in this package, which evaluates nothing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Annotated, Any, get_args

from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict
from pydantic.alias_generators import to_camel
from pydantic_core import PydanticCustomError

from agentic_review.core.findings.model import Category, Severity

DEFAULT_INCLUDE: tuple[str, ...] = ("**/*",)
"""A rule that declares no scope applies to every file, at every depth — the harmless default."""

_SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
_CATEGORIES = frozenset(get_args(Category))
_SEVERITIES = frozenset(get_args(Severity))


def _pattern(value: str) -> str:
    """Shape only: repo-relative, POSIX-separated, non-empty. Whether it matches anything is not our business."""
    if not value.strip() or value.startswith("/") or "\\" in value:
        raise PydanticCustomError(
            "path_pattern",
            "'{value}': expected a repo-relative POSIX pattern",
            {"value": value},
        )
    return value


def _at_least_one(value: tuple[str, ...]) -> tuple[str, ...]:
    if not value:
        # An empty include is an error, not a rule that applies to nothing: a rule that can never apply is
        # certainly a mistake, and carrying it silently would make the library's size misleading.
        raise PydanticCustomError("too_short", "must name at least one pattern")
    return value


def _slug(value: str) -> str:
    if not _SLUG.fullmatch(value):
        raise PydanticCustomError(
            "slug",
            "'{value}': expected a slug like 'no-unawaited-promise'",
            {"value": value},
        )
    return value


def _single_line(value: str) -> str:
    if not value.strip():
        raise PydanticCustomError("non_empty", "must not be empty")
    if "\n" in value.strip():
        raise PydanticCustomError("single_line", "must be a single line")
    return value


def _non_empty(value: str) -> str:
    if not value.strip():
        raise PydanticCustomError("non_empty", "must not be empty")
    return value


def _in_vocabulary(kind: str, allowed: frozenset[str]) -> Any:
    def check(value: Any) -> Any:
        if isinstance(value, str) and value not in allowed:
            raise PydanticCustomError(kind, "'{value}' is not a " + kind, {"value": value})
        return value

    return check


PathPattern = Annotated[str, AfterValidator(_pattern)]


class _RuleModel(BaseModel):
    """``camelCase`` in the file, ``snake_case`` in Python; unknown keys are errors; frozen."""

    model_config = ConfigDict(
        extra="forbid",
        alias_generator=to_camel,
        validate_by_name=True,
        validate_by_alias=True,
        frozen=True,
    )


class PathScope(_RuleModel):
    """Which files a rule applies to. The union of the library's scopes is the review scope (FR-6.1a)."""

    include: Annotated[tuple[PathPattern, ...], AfterValidator(_at_least_one)] = DEFAULT_INCLUDE
    exclude: tuple[PathPattern, ...] = ()


class PatternRule(_RuleModel):
    """One "wrong versus correct" rule, identified by a slug a finding may cite (FR-6.2a)."""

    id: Annotated[str, AfterValidator(_slug)]
    title: Annotated[str, AfterValidator(_single_line)]
    category: Annotated[Category, BeforeValidator(_in_vocabulary("category", _CATEGORIES))]
    default_severity: Annotated[Severity, BeforeValidator(_in_vocabulary("severity", _SEVERITIES))]
    """A default, not a verdict: a finding's severity stays the model's to choose. Nothing here overrides it."""
    wrong: Annotated[str, AfterValidator(_non_empty)]
    correct: Annotated[str, AfterValidator(_non_empty)]
    applies_when: PathScope = PathScope()


@dataclass(frozen=True)
class PatternLibrary:
    """Every rule the run will show the model, in identifier order.

    Sorting is not tidiness: the rendered block must be byte-identical across runs over different change sets
    (spec 003 SC-004), and a stable order is the whole of that.
    """

    rules: tuple[PatternRule, ...]
    source: str
    """Which files it came from. Reaches the invocation trace (FR-028), never the published report."""

    def __post_init__(self) -> None:
        object.__setattr__(self, "rules", tuple(sorted(self.rules, key=lambda rule: rule.id)))

    @property
    def ids(self) -> frozenset[str]:
        """What a finding's ``ruleId`` is validated against (FR-010, FR-019)."""
        return frozenset(rule.id for rule in self.rules)

    @property
    def scope_globs(self) -> tuple[tuple[tuple[str, ...], tuple[str, ...]], ...]:
        """``(include, exclude)`` per rule, as plain builtin string tuples.

        This is the seam that keeps CF-1 from importing this package: the change-set resolver owns the matcher and
        receives only patterns (research R-3, enforced by import contract 6).
        """
        return tuple((rule.applies_when.include, rule.applies_when.exclude) for rule in self.rules)
