"""The rules block — contracts/rules-file.md §4, FR-008.

The rendering is not a wire format and may change without a version bump; improving its wording is how prompt
quality gets improved once feature 007 can measure whether it did. Three properties *are* contractual — each
identifier verbatim, each scope beside its rule, and byte-identity for a given library — and they are what this
file tests. No test here asserts the block fits inside a token count: the budget it would be measured against is
an acknowledged placeholder (constitution Principle VI).
"""

from __future__ import annotations

from typing import Any

from agentic_review.core.patterns.model import PatternLibrary, PatternRule
from agentic_review.core.patterns.render import RULES_HEADING, rules_block


def _rule(identifier: str, **overrides: Any) -> PatternRule:
    data: dict[str, Any] = {
        "id": identifier,
        "title": "the " + identifier + " rule",
        "category": "correctness",
        "defaultSeverity": "important",
        "wrong": "// wrong " + identifier,
        "correct": "// correct " + identifier,
    }
    data.update(overrides)
    return PatternRule.model_validate(data)


def _library(*rules: PatternRule) -> PatternLibrary:
    return PatternLibrary(rules=rules, source="test")


def test_the_block_is_byte_identical_for_the_same_library() -> None:
    library = _library(_rule("alpha"), _rule("beta"))
    assert rules_block(library) == rules_block(library)
    assert rules_block(library) == rules_block(_library(_rule("beta"), _rule("alpha")))


def test_rules_are_rendered_in_identifier_order() -> None:
    block = rules_block(_library(_rule("zebra"), _rule("alpha"), _rule("mango")))
    assert block.index("alpha") < block.index("mango") < block.index("zebra")


def test_every_identifier_appears_verbatim_because_the_model_is_asked_to_cite_it() -> None:
    block = rules_block(_library(_rule("no-unawaited-promise"), _rule("widened-return-type")))
    assert "no-unawaited-promise" in block and "widened-return-type" in block


def test_each_rules_declared_scope_is_stated_next_to_it() -> None:
    scoped = _rule("api", appliesWhen={"include": ["src/api/**"], "exclude": ["**/*.test.ts"]})
    block = rules_block(_library(scoped))
    assert "src/api/**" in block and "**/*.test.ts" in block


def test_a_rule_with_no_declared_scope_says_so_rather_than_saying_nothing() -> None:
    assert "**/*" in rules_block(_library(_rule("everywhere")))


def test_the_block_carries_its_heading_both_examples_and_the_rules_own_vocabulary() -> None:
    block = rules_block(_library(_rule("alpha")))
    assert RULES_HEADING in block
    assert "// wrong alpha" in block and "// correct alpha" in block
    assert "correctness" in block and "important" in block


def test_an_empty_library_renders_nothing_rather_than_an_empty_heading() -> None:
    assert rules_block(_library()) == ""
