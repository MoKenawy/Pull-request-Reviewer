"""The range scope and the three-dot branch diff — FR-10.3a (as amended in SRS v1.5), FR-10.3c, research R-4, R-5."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_review.core.changeset.model import ChangeSet, ChangedFile, ScopeRequest
from agentic_review.core.changeset.resolve import diff_branches, have_merge_base, resolve
from agentic_review.core.changeset.summary import measure_new_files
from tests.support.repo_builder import RepoBuilder


@pytest.fixture
def repo(tmp_path: Path) -> RepoBuilder:
    """``main`` and a ``feature`` branch that left it; both have moved since. ``main`` is checked out."""
    builder = RepoBuilder(tmp_path / "repo").init()
    builder.write("src/app.ts", "export const a = 1;\nexport const b = 2;\n")
    builder.write("src/old.ts", "export const old = 1;\n" * 6)
    builder.write("src/base-only.ts", "export const base = 1;\n")
    builder.write("README.md", "# fixture\n")
    builder.commit("initial")

    builder.checkout("feature", create=True)
    builder.write("src/app.ts", "export const a = 1;\nexport const b = 3;\nexport const c = 4;\n")
    builder.rename("src/old.ts", "src/renamed.ts")
    builder.write("dist/out.js", "var built = 1;\n")
    builder.write("README.md", "# fixture\nmore\n")
    builder.commit("feature work")

    builder.checkout("main")
    builder.write("src/base-only.ts", "export const base = 2;\n")
    builder.commit("main moves on after the branch point")
    return builder


def _by_path(change_set: ChangeSet) -> dict[str, ChangedFile]:
    return {f.path: f for f in change_set.files}


def _range(repo: RepoBuilder, *, head: str | None = "feature", was_defaulted: bool = False) -> ChangeSet:
    return resolve(repo.root, ScopeRequest(kind="range", base="main", head=head), (), was_defaulted=was_defaulted)


def test_three_dot_ignores_what_the_base_did_after_the_branch_point(repo: RepoBuilder) -> None:
    files = _by_path(_range(repo))
    assert set(files) == {"src/app.ts", "src/renamed.ts", "README.md"}
    assert "src/base-only.ts" not in files  # two-dot would report it as the author's change


def test_the_head_need_not_be_checked_out(repo: RepoBuilder) -> None:
    assert repo.git("rev-parse", "--abbrev-ref", "HEAD").strip() == "main"
    changed = _by_path(_range(repo))["src/app.ts"]
    assert changed.change_type == "modified" and changed.changed_line_ranges == ((2, 3),)
    assert (changed.added_lines, changed.removed_lines) == (2, 1)


def test_head_defaults_to_the_current_head(repo: RepoBuilder) -> None:
    repo.checkout("feature")
    change_set = _range(repo, head=None)
    assert set(_by_path(change_set)) == {"src/app.ts", "src/renamed.ts", "README.md"}
    assert change_set.scope.head_ref == "HEAD"


def test_uncommitted_edits_and_untracked_files_are_not_part_of_a_range(repo: RepoBuilder) -> None:
    repo.checkout("feature")
    repo.write("src/app.ts", "export const a = 99;\n")
    repo.write("src/untracked.ts", "export const u = 1;\n")
    files = _by_path(_range(repo))
    assert "src/untracked.ts" not in files
    assert files["src/app.ts"].changed_line_ranges == ((2, 3),)


def test_rename_keeps_its_previous_path(repo: RepoBuilder) -> None:
    renamed = _by_path(_range(repo))["src/renamed.ts"]
    assert renamed.change_type == "renamed" and renamed.previous_path == "src/old.ts"


def test_exclusions_apply_to_a_range(repo: RepoBuilder) -> None:
    change_set = resolve(
        repo.root, ScopeRequest(kind="range", base="main", head="feature"), ("**/renamed.ts",), was_defaulted=False
    )
    assert {(e.path, e.rule) for e in change_set.excluded} == {
        ("dist/out.js", "default:build-output"),
        ("src/renamed.ts", "config:**/renamed.ts"),
    }
    assert set(_by_path(change_set)) == {"src/app.ts", "README.md"}


def test_scope_records_both_refs_and_the_commits_compared(repo: RepoBuilder) -> None:
    scope = _range(repo).scope
    merge_base = repo.git("merge-base", "main", "feature").strip()
    compared = f"{repo.rev_parse(merge_base, short=True)}..{repo.rev_parse('feature', short=True)}"
    assert (scope.kind, scope.base_ref, scope.head_ref, scope.was_defaulted) == ("range", "main", "feature", False)
    assert scope.description == f"changes on feature since it left main ({compared}) · 3 files"
    assert "(default)" in _range(repo, was_defaulted=True).scope.description


def test_line_counts_come_from_the_head_commit_not_the_working_tree(repo: RepoBuilder) -> None:
    repo.write("src/app.ts", "one line only\n")  # main's working tree, which a range never reads
    assert measure_new_files(_range(repo)) == {"src/app.ts": 3, "src/renamed.ts": 6}


def test_diff_branches_is_usable_on_its_own(repo: RepoBuilder) -> None:
    diff = diff_branches(repo.root, "main", "feature", ())
    assert [f.path for f in diff.files] == ["README.md", "src/app.ts", "src/renamed.ts"]
    assert [e.path for e in diff.excluded] == ["dist/out.js"]
    assert diff.head == repo.rev_parse("feature", short=True)
    assert diff.commits == f"{diff.merge_base}..{diff.head}"


def test_unrelated_histories_have_no_merge_base(repo: RepoBuilder) -> None:
    repo.git("checkout", "-q", "--orphan", "island")
    repo.write("src/island.ts", "export const i = 1;\n").commit("unrelated root")
    assert have_merge_base(repo.root, "main", "feature")
    assert not have_merge_base(repo.root, "main", "island")


def test_a_range_without_a_base_is_a_programming_error(repo: RepoBuilder) -> None:
    with pytest.raises(ValueError, match="needs a base"):
        resolve(repo.root, ScopeRequest(kind="range"), (), was_defaulted=False)
