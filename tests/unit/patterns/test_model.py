"""The rule types — data-model §2, spec 003 FR-002, FR-003, FR-004.

What is tested here is *shape*. Path patterns are deliberately not syntax-checked (see ``test_library.py``'s
``test_a_pattern_that_matches_nothing_is_not_an_error``): the dialect's translator accepts any string, so there
are no invalid patterns, only patterns that match nothing.
"""

from __future__ import annotations

from typing import Any, get_args

import pytest
from pydantic import ValidationError

from agentic_review.core.findings.model import Category, Severity
from agentic_review.core.patterns.model import PathScope, PatternLibrary, PatternRule


def _locs(model: type[PathScope] | type[PatternRule], data: dict[str, Any]) -> list[tuple[Any, ...]]:
    with pytest.raises(ValidationError) as caught:
        model.model_validate(data)
    return [error["loc"] for error in caught.value.errors()]


def _messages(model: type[PathScope] | type[PatternRule], data: dict[str, Any]) -> str:
    with pytest.raises(ValidationError) as caught:
        model.model_validate(data)
    return str(caught.value)


# --- PathScope (T004) ------------------------------------------------------------------------------------------


def test_path_scope_defaults_to_every_file_at_every_depth() -> None:
    scope = PathScope()
    assert scope.include == ("**/*",)
    assert scope.exclude == ()


def test_an_empty_include_list_is_rejected_rather_than_meaning_nothing() -> None:
    # A rule that can never apply is certainly a mistake, and carrying it would make the library's size a lie.
    assert ("include",) in _locs(PathScope, {"include": []})
    assert "must name at least one pattern" in _messages(PathScope, {"include": []})


@pytest.mark.parametrize("pattern", ["/src/**", "src\\**", "src\\api\\handler.ts", ""])
def test_a_pattern_that_is_absolute_windows_separated_or_empty_is_rejected(pattern: str) -> None:
    message = _messages(PathScope, {"include": [pattern]})
    assert ("include", 0) in _locs(PathScope, {"include": [pattern]})
    assert "expected a repo-relative POSIX pattern" in message


def test_exclude_entries_are_validated_the_same_way_but_the_list_may_be_empty() -> None:
    assert PathScope(include=("**/*.ts",), exclude=()).exclude == ()
    assert ("exclude", 0) in _locs(PathScope, {"include": ["**/*.ts"], "exclude": ["/dist/**"]})


def test_unknown_keys_on_a_scope_are_errors() -> None:
    assert ("excludes",) in _locs(PathScope, {"include": ["**/*.ts"], "excludes": ["x"]})


def test_a_scope_is_frozen() -> None:
    scope = PathScope()
    with pytest.raises(ValidationError):
        scope.include = ("**/*.ts",)  # type: ignore[misc]


# --- PatternRule (T005) ----------------------------------------------------------------------------------------


def _rule(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "id": "no-unawaited-promise",
        "title": "A promise created inside try is not awaited",
        "category": "error-handling",
        "defaultSeverity": "blocking",
        "wrong": "void save(record);",
        "correct": "await save(record);",
    }
    data.update(overrides)
    return data


def test_a_well_formed_rule_validates_and_defaults_to_the_permissive_scope() -> None:
    rule = PatternRule.model_validate(_rule())
    assert rule.id == "no-unawaited-promise"
    assert rule.category == "error-handling" and rule.default_severity == "blocking"
    assert rule.applies_when == PathScope()


@pytest.mark.parametrize("field", ["id", "title", "category", "defaultSeverity", "wrong", "correct"])
def test_every_field_but_the_scope_is_required(field: str) -> None:
    data = _rule()
    del data[field]
    assert (field,) in _locs(PatternRule, data)


@pytest.mark.parametrize("bad", ["No Unawaited", "no_unawaited_promise", "no--unawaited", "-leading", "trailing-"])
def test_a_non_slug_identifier_is_rejected(bad: str) -> None:
    assert "expected a slug like 'no-unawaited-promise'" in _messages(PatternRule, _rule(id=bad))


def test_a_category_outside_the_finding_models_vocabulary_is_rejected_by_name() -> None:
    # One definition, not two: the vocabulary is imported from core/findings/, never restated here.
    assert "'perf' is not a category" in _messages(PatternRule, _rule(category="perf"))
    assert set(get_args(Category)) >= {"error-handling", "correctness", "test-evidence"}


def test_a_severity_outside_the_finding_models_vocabulary_is_rejected_by_name() -> None:
    assert "'critical' is not a severity" in _messages(PatternRule, _rule(defaultSeverity="critical"))
    assert set(get_args(Severity)) == {"blocking", "important", "nit"}


@pytest.mark.parametrize("field", ["wrong", "correct", "title"])
def test_an_empty_example_or_title_is_rejected(field: str) -> None:
    assert (field,) in _locs(PatternRule, _rule(**{field: "   "}))


def test_a_title_spanning_two_lines_is_rejected() -> None:
    assert "must be a single line" in _messages(PatternRule, _rule(title="first\nsecond"))


def test_unknown_keys_on_a_rule_are_errors_so_a_misspelt_scope_is_not_silently_permissive() -> None:
    assert ("appliesWen",) in _locs(PatternRule, _rule(appliesWen={"include": ["src/**"]}))


def test_a_rule_is_frozen() -> None:
    rule = PatternRule.model_validate(_rule())
    with pytest.raises(ValidationError):
        rule.id = "other"  # type: ignore[misc]


# --- PatternLibrary (T007) -------------------------------------------------------------------------------------


def _named(identifier: str, **overrides: Any) -> PatternRule:
    return PatternRule.model_validate(_rule(id=identifier, **overrides))


def test_a_library_holds_its_rules_sorted_by_identifier_whatever_order_they_arrived_in() -> None:
    library = PatternLibrary(rules=(_named("zebra"), _named("apple"), _named("mango")), source="test")
    assert [rule.id for rule in library.rules] == ["apple", "mango", "zebra"]


def test_a_librarys_identifiers_are_what_a_finding_is_validated_against() -> None:
    library = PatternLibrary(rules=(_named("apple"), _named("mango")), source="test")
    assert library.ids == frozenset({"apple", "mango"})


def test_scope_globs_leave_the_package_as_plain_builtin_string_tuples() -> None:
    # The seam that keeps core/changeset/ from importing core/patterns/ (research R-3, import contract 6).
    library = PatternLibrary(
        rules=(
            _named("api", appliesWhen={"include": ["src/api/**"], "exclude": ["**/*.test.ts"]}),
            _named("everything"),
        ),
        source="test",
    )
    assert library.scope_globs == ((("src/api/**",), ("**/*.test.ts",)), (("**/*",), ()))
    for include, exclude in library.scope_globs:
        assert type(include) is tuple and type(exclude) is tuple
        assert all(type(pattern) is str for pattern in (*include, *exclude))


def test_a_library_is_frozen() -> None:
    library = PatternLibrary(rules=(_named("apple"),), source="test")
    with pytest.raises(Exception):  # noqa: B017 - FrozenInstanceError; the point is that it cannot be reassigned
        library.source = "other"  # type: ignore[misc]
