"""Rule scope as review scope — SRS FR-6.1a / **AC-18**, spec 003 FR-011, FR-012, FR-014, FR-017.

CF-1 owns the matcher; the rule library owns the patterns and evaluates nothing (research R-3). So the predicate
lives here, beside the glob dialect it reuses, and receives plain tuples of pattern strings.

**The first test in this file is the one that matters.** The obvious implementation of the predicate is wrong, and
AC-18's second clause exists only to rule it out.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_review.core.changeset.exclusion import RuleScope, in_any_rule_scope
from agentic_review.core.changeset.model import ScopeRequest
from agentic_review.core.changeset.resolve import resolve
from agentic_review.core.findings.report import RULES_NO_SCOPE_MATCH
from tests.support.repo_builder import RepoBuilder

PRODUCTION = (("**/*.ts",), ("**/*.test.ts",))
"""A production-code rule: all TypeScript, except tests."""

TESTS_ONLY = (("**/*.test.ts",), ())
"""A rule written *for* test files — the shipped library has one, and FR-016 requires it."""


def test_a_file_one_rule_excludes_and_another_includes_is_in_scope() -> None:
    """**AC-18 clause 2.** The pooling bug, and the only purpose of this test.

    A pooled implementation — ``any(include over all rules) and not any(exclude over all rules)`` — passes every
    other test in this file and fails this one. It would let the production-code rule's ``**/*.test.ts`` exclusion
    remove test files from the scope of the rule written for them, which the shipped library ships (research R-9).

    Exclusions are evaluated **per rule, then unioned**: one rule's exclusions narrow that rule and nothing else.
    """
    scopes: tuple[RuleScope, ...] = (PRODUCTION, TESTS_ONLY)
    assert in_any_rule_scope("src/thing.test.ts", scopes) is True
    # And the pooled reading of the same two rules, spelled out, so the difference is on the record:
    pooled_include = any(True for _ in (PRODUCTION[0], TESTS_ONLY[0]))
    pooled_exclude = "**/*.test.ts" in PRODUCTION[1]
    assert pooled_include and pooled_exclude, "the pooled reading would have dropped it"


# --- the predicate's other three properties (T038) ------------------------------------------------------------------


def test_a_file_outside_every_include_is_out_of_scope() -> None:
    assert in_any_rule_scope("src/thing.py", (PRODUCTION, TESTS_ONLY)) is False
    assert in_any_rule_scope("docs/guide.ts", ((("src/**",), ()),)) is False


def test_an_empty_scope_list_puts_every_file_in_scope() -> None:
    """With no rules loaded there is no rule to fail to match, so nothing is excluded on this ground.

    This is what keeps an unloaded library from producing a correct-but-useless empty review (data-model §4).
    """
    assert in_any_rule_scope("src/thing.ts", ()) is True
    assert in_any_rule_scope("anything/at/all.xyz", ()) is True


def test_the_permissive_default_matches_at_every_depth() -> None:
    permissive: tuple[RuleScope, ...] = ((("**/*",), ()),)
    for path in ("a.ts", "src/a.ts", "a/b/c/d/e.ts", "src/deep/nested/thing.tsx"):
        assert in_any_rule_scope(path, permissive) is True


def test_a_rule_that_excludes_everything_it_includes_covers_nothing() -> None:
    assert in_any_rule_scope("src/a.ts", ((("**/*.ts",), ("**/*.ts",)),)) is False


def test_matching_is_case_sensitive_like_the_configured_exclusions() -> None:
    """FR-017: the same dialect and the same case sensitivity as FR-3.5's patterns, so one answer, not two."""
    assert in_any_rule_scope("src/Thing.TS", ((("**/*.ts",), ()),)) is False
    assert in_any_rule_scope("src/thing.ts", ((("**/*.ts",), ()),)) is True


@pytest.mark.parametrize(
    "path,scopes,expected",
    [
        ("src/api/handler.ts", ((("src/api/**",), ()),), True),
        ("src/ui/widget.ts", ((("src/api/**",), ()),), False),
        ("thing.config.ts", ((("*.config.ts",), ()),), True),  # no separator: not anchored
        ("src/deep/thing.config.ts", ((("*.config.ts",), ()),), True),
        ("src/api/handler.ts", ((("src/api/handler.ts",), ()),), True),
    ],
)
def test_patterns_match_repo_relative_posix_paths(path: str, scopes: tuple[RuleScope, ...], expected: bool) -> None:
    """Paths reaching the predicate are always repo-relative and POSIX-separated, on Windows too: git reports
    them that way and ``ChangeSet`` stores them that way (FR-10.3c)."""
    assert in_any_rule_scope(path, scopes) is expected


def test_the_reason_keeps_the_source_colon_detail_shape_of_the_other_two() -> None:
    """FR-014 / research R-5. The schema's pattern stays a rule rather than a list of exceptions."""
    assert RULES_NO_SCOPE_MATCH == "rules:no-scope-match"
    source, _, detail = RULES_NO_SCOPE_MATCH.partition(":")
    assert source == "rules" and detail


# --- the ordering: three mechanisms, three distinguishable explanations (T039, research R-4) -------------------------


def test_the_ordering_keeps_each_mechanisms_own_reason(tmp_path: Path) -> None:
    """A changed ``README.md`` must be reported as *not a reviewed language*, never as *no rule applies*, and a file
    a configured pattern already excluded must keep **that** reason. No competition over one path (FR-014).

    Rule scope is asked only about files that would otherwise be reviewed, which is why it is applied last and
    gated on ``ChangedFile.is_reviewable``.
    """
    repo = RepoBuilder(tmp_path / "repo").init()
    repo.write("src/app.ts", "export const a = 1;\n")
    repo.write("README.md", "# demo\n")
    repo.write("src/skipme.ts", "export const b = 2;\n")
    repo.write("src/ui/widget.ts", "export const c = 3;\n")
    repo.commit("initial")
    repo.write("src/app.ts", "export const a = 2;\n")
    repo.write("README.md", "# demo\nmore\n")
    repo.write("src/skipme.ts", "export const b = 3;\n")
    repo.write("src/ui/widget.ts", "export const c = 4;\n")

    api_only: tuple[RuleScope, ...] = ((("src/app.ts",), ()),)
    change_set = resolve(
        repo.root,
        ScopeRequest(kind="working-tree"),
        ["src/skipme.ts"],
        was_defaulted=True,
        rule_scopes=api_only,
    )

    by_path = {excluded.path: excluded.rule for excluded in change_set.excluded}
    # 1 · a configured exclusion keeps its own reason, and never reaches the scope question
    assert by_path["src/skipme.ts"] == "config:src/skipme.ts"
    # 2 · a reviewable file no rule covers gets the new reason
    assert by_path["src/ui/widget.ts"] == RULES_NO_SCOPE_MATCH
    # 3 · a non-reviewed language is not in `excluded` at all: it stays in `files`, with its own reason
    assert "README.md" not in by_path
    readme = next(f for f in change_set.files if f.path == "README.md")
    assert readme.language == "other" and not readme.is_reviewable
    assert [f.path for f in change_set.reviewable_files] == ["src/app.ts"]


def test_with_no_scopes_every_reviewable_file_survives(tmp_path: Path) -> None:
    """The behaviour before feature 003, and what an unloaded library must still produce."""
    repo = RepoBuilder(tmp_path / "repo").init()
    repo.write("src/a.ts", "export const a = 1;\n")
    repo.write("src/b.ts", "export const b = 1;\n")
    repo.commit("initial")
    repo.write("src/a.ts", "export const a = 2;\n")
    repo.write("src/b.ts", "export const b = 2;\n")

    change_set = resolve(repo.root, ScopeRequest(kind="working-tree"), [], was_defaulted=True)
    assert {f.path for f in change_set.reviewable_files} == {"src/a.ts", "src/b.ts"}
    assert change_set.excluded == ()


def test_a_deleted_or_binary_file_is_never_relabelled_as_a_rule_scope_exclusion(tmp_path: Path) -> None:
    repo = RepoBuilder(tmp_path / "repo").init()
    repo.write("src/gone.ts", "export const gone = 1;\n")
    repo.write("src/kept.ts", "export const kept = 1;\n")
    repo.commit("initial")
    (repo.root / "src" / "gone.ts").unlink()
    repo.write("src/kept.ts", "export const kept = 2;\n")

    narrow: tuple[RuleScope, ...] = ((("src/kept.ts",), ()),)
    change_set = resolve(repo.root, ScopeRequest(kind="working-tree"), [], was_defaulted=True, rule_scopes=narrow)
    gone = next(f for f in change_set.files if f.path == "src/gone.ts")
    assert gone.change_type == "deleted" and not gone.is_reviewable
    assert all(excluded.path != "src/gone.ts" for excluded in change_set.excluded)
