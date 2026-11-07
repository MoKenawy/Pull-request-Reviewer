"""Loading and validating a rule library — contracts/rules-file.md §3, FR-004, FR-026.

The error messages are part of the contract, because they are what a project author debugs against. Every one of
them names the file and the offending field, with the rule's index where the identifier itself is the problem.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from agentic_review.core.patterns.library import PatternLibraryError, load_library

_GOOD_RULE = """
  - id: no-unawaited-promise
    title: A promise created inside try is not awaited
    category: error-handling
    defaultSeverity: blocking
    wrong: |
      void save(record);
    correct: |
      await save(record);
"""


def _rules_file(tmp_path: Path, body: str, name: str = "review-rules.yml") -> Path:
    path = tmp_path / name
    path.write_text(textwrap.dedent(body), encoding="utf-8")
    return path


def _error(tmp_path: Path, body: str) -> str:
    with pytest.raises(PatternLibraryError) as caught:
        load_library(_rules_file(tmp_path, body))
    return str(caught.value)


def test_the_shipped_library_loads_with_no_configured_file() -> None:
    library = load_library()
    assert library.rules and library.source == "shipped"


def test_a_configured_file_is_read_and_its_rule_joins_the_library(tmp_path: Path) -> None:
    library = load_library(_rules_file(tmp_path, "rules:\n" + _GOOD_RULE))
    assert "no-unawaited-promise" in library.ids
    assert "review-rules.yml" in library.source and "shipped" in library.source


# --- the failure table (T008) ----------------------------------------------------------------------------------


def test_a_configured_file_that_does_not_exist_names_the_key_and_the_path(tmp_path: Path) -> None:
    with pytest.raises(PatternLibraryError) as caught:
        load_library(tmp_path / "review-rules.yml")
    message = str(caught.value)
    assert "patterns.rules:" in message and "does not exist" in message


def test_invalid_yaml_names_the_file_and_quotes_the_parser(tmp_path: Path) -> None:
    message = _error(tmp_path, "rules: [unclosed\n")
    assert message.startswith("review-rules.yml:") and "not valid YAML" in message


@pytest.mark.parametrize("body", ["[]\n", "rules: not-a-list\n", "other: {}\n", "\n"])
def test_a_top_level_that_is_not_a_mapping_with_a_rules_list_is_an_error(tmp_path: Path, body: str) -> None:
    assert "expected a mapping with a 'rules' list" in _error(tmp_path, body)


def test_a_rule_that_is_not_a_mapping_names_its_index(tmp_path: Path) -> None:
    body = "rules:\n" + _GOOD_RULE + "  - just-a-string\n"
    assert "rules[1]: expected a mapping" in _error(tmp_path, body)


def test_a_missing_required_field_is_named(tmp_path: Path) -> None:
    body = """
    rules:
      - id: no-title
        category: error-handling
        defaultSeverity: blocking
        wrong: a
        correct: b
    """
    assert "rules[0].title: required" in _error(tmp_path, body)


def test_an_unknown_key_is_named_so_a_misspelt_scope_is_not_silently_permissive(tmp_path: Path) -> None:
    body = "rules:\n" + _GOOD_RULE + "    appliesWen: {}\n"
    assert "rules[0].appliesWen: unknown field" in _error(tmp_path, body)


def test_a_bad_identifier_shows_the_value_and_the_expected_shape(tmp_path: Path) -> None:
    body = "rules:\n" + _GOOD_RULE.replace("no-unawaited-promise", "No Unawaited")
    message = _error(tmp_path, body)
    assert "rules[0].id: 'No Unawaited': expected a slug like 'no-unawaited-promise'" in message


def test_a_category_outside_the_vocabulary_is_named(tmp_path: Path) -> None:
    body = "rules:\n" + _GOOD_RULE.replace("error-handling", "perf")
    assert "rules[0].category: 'perf' is not a category" in _error(tmp_path, body)


def test_an_empty_include_list_is_named(tmp_path: Path) -> None:
    body = "rules:\n" + _GOOD_RULE + "    appliesWhen:\n      include: []\n"
    assert "rules[0].appliesWhen.include: must name at least one pattern" in _error(tmp_path, body)


def test_an_absolute_pattern_is_named_down_to_its_index(tmp_path: Path) -> None:
    body = "rules:\n" + _GOOD_RULE + "    appliesWhen:\n      include: ['/src/**']\n"
    message = _error(tmp_path, body)
    assert "rules[0].appliesWhen.include[0]: '/src/**': expected a repo-relative POSIX pattern" in message


def test_two_configured_rules_sharing_an_identifier_fail_naming_it(tmp_path: Path) -> None:
    message = _error(tmp_path, "rules:\n" + _GOOD_RULE + _GOOD_RULE)
    assert "rules[1].id: 'no-unawaited-promise' is already defined" in message


# --- the guard (T010) ------------------------------------------------------------------------------------------


def test_a_pattern_that_matches_nothing_is_not_an_error(tmp_path: Path) -> None:
    """Deliberately mapped to no requirement — it defends a decision.

    The dialect's translator accepts any string, so there is no such thing as an invalid pattern, only one that
    matches nothing. This test exists to stop someone building a pattern validator, which would have to live in
    the package that evaluates nothing (research R-3, data-model §2).
    """
    body = "rules:\n" + _GOOD_RULE + "    appliesWhen:\n      include: ['nothing/matches/this/***']\n"
    library = load_library(_rules_file(tmp_path, body))
    assert "no-unawaited-promise" in library.ids
