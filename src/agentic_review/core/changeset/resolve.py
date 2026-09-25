"""Resolving a scope into a ``ChangeSet`` (FR-10.3a, research R-4, R-5).

| Scope | Comparison |
|---|---|
| working-tree (default) | ``HEAD`` ↔ working tree, plus untracked files that are not ignored |
| staged | ``HEAD`` ↔ index (feature 001, User Story 4) |
| range | merge-base(base, HEAD) ↔ ``HEAD`` (feature 001, User Story 4) |

An unborn ``HEAD`` compares against the empty tree.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from agentic_review.core.changeset._git import GitError, GitNotFound, run_git, run_git_bytes, succeeds

__all__ = ["GitError", "GitNotFound", "head_is_unborn", "locate_repository", "ref_exists", "resolve"]
from agentic_review.core.changeset.diff_parser import (
    changed_line_ranges,
    parse_name_status,
    parse_numstat,
    split_patch,
    synthesise_added_file,
)
from agentic_review.core.changeset.exclusion import classify
from agentic_review.core.changeset.model import ChangedFile, ChangeSet, ScopeRequest, language_for
from agentic_review.core.findings.report import ChangeType, ExcludedPath, ResolvedScope

_DIFF_FLAGS = ("--no-color", "--no-ext-diff", "--no-textconv")
_BINARY_SNIFF_BYTES = 8000  # git's own heuristic: a NUL byte in the first 8,000 bytes


def locate_repository(cwd: Path) -> Path | None:
    """The repository root containing ``cwd``, or None. Raises ``GitNotFound`` if git is not installed."""
    try:
        output = run_git(cwd, "rev-parse", "--show-toplevel")
    except GitError as error:
        if error.returncode == -1:
            raise
        return None
    return Path(output.strip())


def ref_exists(repo_root: Path, ref: str) -> bool:
    if not ref or ref.startswith("-"):
        return False
    return succeeds(repo_root, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")


def head_is_unborn(repo_root: Path) -> bool:
    return not ref_exists(repo_root, "HEAD")


def _empty_tree(repo_root: Path) -> str:
    return run_git(repo_root, "hash-object", "-t", "tree", "--stdin", stdin=b"").strip()


def resolve(
    repo_root: Path,
    scope: ScopeRequest,
    exclude: Sequence[str],
    *,
    was_defaulted: bool,
) -> ChangeSet:
    if scope.kind != "working-tree":
        raise NotImplementedError(f"the {scope.kind} scope arrives with User Story 4")

    base = _empty_tree(repo_root) if head_is_unborn(repo_root) else "HEAD"
    entries = parse_name_status(run_git(repo_root, "diff", "--name-status", "-z", "-M", *_DIFF_FLAGS, base))
    numstat = parse_numstat(run_git(repo_root, "diff", "--numstat", "-z", "-M", *_DIFF_FLAGS, base))
    untracked = [p for p in run_git(repo_root, "ls-files", "--others", "--exclude-standard", "-z").split("\0") if p]

    configured = tuple(exclude)
    excluded: list[ExcludedPath] = []
    kept: list[tuple[ChangeType, str, str | None]] = []
    for change_type, path, previous in [*entries, *(("added", p, None) for p in untracked)]:
        rule = classify(path, configured)
        if rule is not None:
            excluded.append(ExcludedPath(path=path, rule=rule))
        else:
            kept.append((change_type, path, previous))

    tracked = {path for _, path, _ in entries}
    needs_patch = any(
        path in tracked and change_type != "deleted" and language_for(path) != "other" and numstat.get(path) is not None
        for change_type, path, _ in kept
    )
    hunks_by_path = (
        split_patch(
            run_git(repo_root, "diff", "-M", "-U3", *_DIFF_FLAGS, "--src-prefix=a/", "--dst-prefix=b/", base)
        )
        if needs_patch
        else {}
    )

    files: list[ChangedFile] = []
    for change_type, path, previous in kept:
        if path in tracked:
            counts = numstat.get(path)
            is_binary = counts is None
            added, removed = counts or (0, 0)
            hunks = tuple(hunks_by_path.get(path, ()))
        else:
            data = (repo_root / path).read_bytes()
            is_binary = b"\0" in data[:_BINARY_SNIFF_BYTES]
            synthesised = None if is_binary else synthesise_added_file(data.decode("utf-8", "replace"))
            hunks = (synthesised,) if synthesised else ()
            added, removed = (synthesised.new_count if synthesised else 0), 0
        language = language_for(path)
        if change_type == "deleted" or is_binary or language == "other":
            hunks = ()
        files.append(
            ChangedFile(
                path=path,
                change_type=change_type,
                previous_path=previous,
                language=language,
                is_binary=is_binary,
                changed_line_ranges=changed_line_ranges(hunks),
                hunks=hunks,
                added_lines=added,
                removed_lines=removed,
            )
        )

    files.sort(key=lambda f: f.path)
    excluded.sort(key=lambda e: e.path)
    count = len(files)
    description = (
        f"uncommitted changes in the working tree{' (default)' if was_defaulted else ''}"
        f" · {count} file{'' if count == 1 else 's'}"
    )
    return ChangeSet(
        repo_root=repo_root,
        scope=ResolvedScope(kind="working-tree", was_defaulted=was_defaulted, description=description),
        files=tuple(files),
        excluded=tuple(excluded),
    )


def read_worktree_bytes(repo_root: Path, path: str) -> bytes:
    return (repo_root / path).read_bytes()


def read_blob_bytes(repo_root: Path, spec: str) -> bytes:
    _, data = run_git_bytes(repo_root, "show", spec)
    return data
