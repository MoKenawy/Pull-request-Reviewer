"""The working-tree scope against real git repositories — FR-10.3a, FR-10.3c, spec 001 FR-009, research R-4, R-5."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_review.core.changeset.model import ChangeSet, ChangedFile, ScopeRequest
from agentic_review.core.changeset.resolve import head_is_unborn, locate_repository, ref_exists, resolve
from tests.support.repo_builder import RepoBuilder

WORKING_TREE = ScopeRequest(kind="working-tree")


@pytest.fixture
def repo(tmp_path: Path) -> RepoBuilder:
    builder = RepoBuilder(tmp_path / "repo").init()
    builder.write("src/app.ts", "export const a = 1;\nexport const b = 2;\n")
    builder.write("src/old.js", "module.exports = 1;\n" * 5)
    builder.write("src/gone.ts", "export {};\n")
    builder.write("README.md", "# fixture\n")
    builder.write(".gitignore", "*.log\n")
    builder.write_bytes("assets/logo.bin", b"\x89PNG\0\0\0")
    builder.commit("initial")
    return builder


def _by_path(change_set: ChangeSet) -> dict[str, ChangedFile]:
    return {f.path: f for f in change_set.files}


def test_modified_tracked_file(repo: RepoBuilder) -> None:
    repo.write("src/app.ts", "export const a = 1;\nexport const b = 3;\nexport const c = 4;\n")
    changed = _by_path(resolve(repo.root, WORKING_TREE, (), was_defaulted=True))["src/app.ts"]
    assert changed.change_type == "modified" and changed.language == "ts" and not changed.is_binary
    assert len(changed.hunks) == 1
    assert changed.changed_line_ranges == ((2, 3),)
    assert (changed.added_lines, changed.removed_lines) == (2, 1)


def test_staged_and_unstaged_edits_both_count(repo: RepoBuilder) -> None:
    repo.write("src/app.ts", "export const a = 9;\nexport const b = 2;\n").stage("src/app.ts")
    repo.write("src/old.js", "module.exports = 2;\n")
    assert set(_by_path(resolve(repo.root, WORKING_TREE, (), was_defaulted=True))) == {"src/app.ts", "src/old.js"}


def test_untracked_file_is_added_with_one_hunk(repo: RepoBuilder) -> None:
    repo.write("src/new.tsx", "export const X = () => null;\n")
    repo.write("debug.log", "ignored\n")
    files = _by_path(resolve(repo.root, WORKING_TREE, (), was_defaulted=True))
    assert "debug.log" not in files
    added = files["src/new.tsx"]
    assert added.change_type == "added" and added.language == "tsx"
    assert added.hunks[0].header == "@@ -0,0 +1 @@"
    assert added.changed_line_ranges == ((1, 1),)


def test_deleted_file_has_no_hunks(repo: RepoBuilder) -> None:
    repo.delete("src/gone.ts")
    change_set = resolve(repo.root, WORKING_TREE, (), was_defaulted=True)
    gone = _by_path(change_set)["src/gone.ts"]
    assert gone.change_type == "deleted" and gone.hunks == ()
    assert gone not in change_set.reviewable_files


def test_renamed_file_keeps_previous_path(repo: RepoBuilder) -> None:
    repo.rename("src/old.js", "lib/new.js")
    renamed = _by_path(resolve(repo.root, WORKING_TREE, (), was_defaulted=True))["lib/new.js"]
    assert renamed.change_type == "renamed" and renamed.previous_path == "src/old.js"


def test_binary_and_other_language_files_are_listed_without_hunks(repo: RepoBuilder) -> None:
    repo.write_bytes("assets/logo.bin", b"\x89PNG\0\0\1")
    repo.write("README.md", "# fixture\nmore\n")
    repo.write_bytes("src/blob.ts", b"\0\0binary ts")
    change_set = resolve(repo.root, WORKING_TREE, (), was_defaulted=True)
    files = _by_path(change_set)
    assert files["assets/logo.bin"].is_binary and files["assets/logo.bin"].hunks == ()
    assert files["src/blob.ts"].is_binary and files["src/blob.ts"].hunks == ()
    assert files["README.md"].language == "other" and files["README.md"].hunks == ()
    assert files["README.md"].added_lines == 1
    assert change_set.reviewable_files == ()


def test_excluded_paths_are_recorded_not_listed(repo: RepoBuilder) -> None:
    repo.write("dist/index.js", "built\n")
    repo.write("src/app.ts", "changed\n")
    change_set = resolve(repo.root, WORKING_TREE, ("src/*.ts",), was_defaulted=True)
    assert change_set.files == ()
    assert {(e.path, e.rule) for e in change_set.excluded} == {
        ("dist/index.js", "default:build-output"),
        ("src/app.ts", "config:src/*.ts"),
    }


def test_paths_are_repo_relative_posix_from_a_subdirectory(repo: RepoBuilder) -> None:
    repo.write("src/deep/er/x.ts", "export {};\n")
    root = locate_repository(repo.root / "src")
    assert root is not None and root.resolve() == repo.root.resolve()
    assert "src/deep/er/x.ts" in _by_path(resolve(root, WORKING_TREE, (), was_defaulted=True))


def test_scope_description(repo: RepoBuilder) -> None:
    repo.write("src/app.ts", "changed\n")
    scope = resolve(repo.root, WORKING_TREE, (), was_defaulted=True).scope
    assert scope.kind == "working-tree" and scope.was_defaulted and scope.base_ref is None
    assert scope.description == "uncommitted changes in the working tree (default) · 1 file"
    chosen = resolve(repo.root, WORKING_TREE, (), was_defaulted=False).scope
    assert chosen.description == "uncommitted changes in the working tree · 1 file"


def test_unborn_head(tmp_path: Path) -> None:
    builder = RepoBuilder(tmp_path / "fresh").init()
    builder.write("index.ts", "export {};\n")
    assert head_is_unborn(builder.root)
    files = _by_path(resolve(builder.root, WORKING_TREE, (), was_defaulted=True))
    assert files["index.ts"].change_type == "added"
    builder.stage("index.ts")
    assert _by_path(resolve(builder.root, WORKING_TREE, (), was_defaulted=True))["index.ts"].change_type == "added"


def test_repository_queries(repo: RepoBuilder, tmp_path: Path) -> None:
    outside = tmp_path / "not-a-repo"
    outside.mkdir()
    assert locate_repository(outside) is None
    assert ref_exists(repo.root, "main") and ref_exists(repo.root, "HEAD")
    assert not ref_exists(repo.root, "nope") and not ref_exists(repo.root, "--output=x")
    assert not head_is_unborn(repo.root)


def test_no_changes_gives_an_empty_change_set(repo: RepoBuilder) -> None:
    change_set = resolve(repo.root, WORKING_TREE, (), was_defaulted=True)
    assert change_set.files == () and change_set.excluded == ()
