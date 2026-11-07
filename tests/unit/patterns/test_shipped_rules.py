"""The five rules that ship with the tool — spec 003 FR-002, FR-016, SC-001, SC-005; SRS FR-6.3a.

Five is a **floor that proves the mechanism**, not a product-grade rule set; breadth is v2 (SRS FR-6.3). So these
tests check that each rule is well formed and that the set's *scopes* behave, and they say nothing at all about
whether the rules are good ones. Whether they improve a review is feature 007's question (Principle VI).
"""

from __future__ import annotations

from typing import get_args

import pytest

from agentic_review.core.findings.model import Category, Severity
from agentic_review.core.patterns import load_library
from agentic_review.core.patterns.model import PatternLibrary

LIBRARY = load_library()


def test_the_shipped_library_loads_with_no_configuration_at_all() -> None:
    """SC-001. A fresh install reviews with rules, offline, with no repository configuration."""
    assert LIBRARY.source == "shipped"
    assert len(LIBRARY.rules) >= 5, "SRS FR-6.3a requires at least five shipped rules"


def test_every_shipped_rule_carries_everything_a_rule_owes() -> None:
    for rule in LIBRARY.rules:
        assert rule.id and rule.id == rule.id.strip()
        assert rule.title.strip() and "\n" not in rule.title
        assert rule.category in get_args(Category)
        assert rule.default_severity in get_args(Severity)
        assert rule.wrong.strip(), f"{rule.id} has no wrong example"
        assert rule.correct.strip(), f"{rule.id} has no correct example"
        assert rule.wrong.strip() != rule.correct.strip(), f"{rule.id}'s examples are the same code"
        assert rule.applies_when.include, f"{rule.id} declares no scope"


def test_shipped_identifiers_are_unique_and_sorted() -> None:
    ids = [rule.id for rule in LIBRARY.rules]
    assert len(ids) == len(set(ids))
    assert ids == sorted(ids), "the library orders by identifier; the rendered block depends on it (SC-004)"


def test_the_shipped_rules_cover_more_than_one_category() -> None:
    # Not a quality claim — a set of five rules all in one category would make the drop behaviour untestable.
    assert len({rule.id for rule in LIBRARY.rules}) >= 5
    assert len({rule.category for rule in LIBRARY.rules}) >= 3


# --- the scopes, which are the part with a user-visible failure mode (T033) ------------------------------------------


def _in_scope(library: PatternLibrary, path: str) -> list[str]:
    """Which rules cover ``path``. Uses CF-1's matcher, the only one in the system (research R-3)."""
    from agentic_review.core.changeset.exclusion import glob_to_regex

    covered = []
    for rule in library.rules:
        include = any(glob_to_regex(p).fullmatch(path) for p in rule.applies_when.include)
        exclude = any(glob_to_regex(p).fullmatch(path) for p in rule.applies_when.exclude)
        if include and not exclude:
            covered.append(rule.id)
    return covered


@pytest.mark.parametrize("path", ["src/thing.ts", "src/app.tsx", "src/util.js", "lib/helper.ts"])
def test_the_union_of_the_shipped_scopes_covers_an_ordinary_source_file(path: str) -> None:
    """research R-9's first guardrail: narrow means narrow *within* TS/JS, never narrower.

    If the union missed an ordinary source file the tool would review less than its user expects, and would say so
    only in the excluded list.
    """
    assert _in_scope(LIBRARY, path), f"no shipped rule covers {path}"


@pytest.mark.parametrize(
    "path",
    ["src/thing.test.ts", "src/thing.spec.ts", "src/components/Button.test.tsx", "src/__tests__/thing.ts"],
)
def test_at_least_one_shipped_rule_applies_to_a_test_file(path: str) -> None:
    """FR-016 / SC-005, and research R-9's sharper guardrail.

    Every other shipped rule excludes test files as production-code rules. Without one scoped *to* them, a
    test-only change would match no rule and be set aside entirely — while the instructions explicitly ask for
    findings about an existing test weakened. That is a shipped-data decision with a user-visible failure mode,
    which is why it is a requirement and not a convention.
    """
    assert _in_scope(LIBRARY, path), f"a test-only change touching {path} would be set aside"


def test_a_test_file_is_covered_although_most_rules_exclude_it() -> None:
    """The live form of AC-18's second clause: one rule excludes it, another includes it, and it is in scope.

    This is what makes the pooling bug a real failure rather than a hypothetical one — a pooled implementation of
    the scope predicate would drop every test file the shipped library ships a rule *for*.
    """
    path = "src/thing.test.ts"
    excluders = [rule.id for rule in LIBRARY.rules if path in _excluded_by(rule, path)]
    assert excluders, "no shipped rule excludes test files, so this test no longer guards anything"
    assert _in_scope(LIBRARY, path), "a pooled exclusion would have dropped it"


def _excluded_by(rule: object, path: str) -> list[str]:
    from agentic_review.core.changeset.exclusion import glob_to_regex

    patterns = rule.applies_when.exclude  # type: ignore[attr-defined]
    return [path for pattern in patterns if glob_to_regex(pattern).fullmatch(path)]


def test_a_non_typescript_file_is_covered_by_nothing_and_that_is_not_this_librarys_concern() -> None:
    """A ``README.md`` never reaches the scope question: it is already out as a non-reviewed language, and keeps
    that reason (research R-4). Asserted here so nobody "fixes" the scopes to cover it."""
    assert _in_scope(LIBRARY, "README.md") == []
    assert _in_scope(LIBRARY, "package.json") == []
