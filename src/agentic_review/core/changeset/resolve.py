"""Resolving a scope into a ``ChangeSet`` (FR-10.3a, research R-4, R-5).

| Scope | Comparison |
|---|---|
| working-tree (default) | ``HEAD`` ↔ working tree, plus untracked files that are not ignored |
| staged | ``HEAD`` ↔ index (feature 001, User Story 4) |
| range | merge-base(base, head) ↔ head — ``git diff base...head``; head defaults to ``HEAD`` |
| pull-request | the same three-dot diff, inside a temporary clone (``pull_request.py``) |

An unborn ``HEAD`` compares against the empty tree.

``diff_branches`` is the three-dot diff on its own: ``range`` uses it here, and the pull-request scope uses it on a
repository it fetched.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from agentic_review.core.changeset._git import GitError, GitNotFound, run_git, run_git_bytes, succeeds

__all__ = [
    "BranchDiff",
    "GitError",
    "GitNotFound",
    "diff_branches",
    "have_merge_base",
    "head_is_unborn",
    "locate_repository",
    "ref_exists",
    "resolve",
]
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


def have_merge_base(repo_root: Path, base: str, head: str) -> bool:
    """Whether ``base...head`` can be answered: two histories with no common commit have no three-dot diff."""
    return succeeds(repo_root, "merge-base", base, head)


def _empty_tree(repo_root: Path) -> str:
    return run_git(repo_root, "hash-object", "-t", "tree", "--stdin", stdin=b"").strip()


def _short(repo_root: Path, rev: str) -> str:
    return run_git(repo_root, "rev-parse", "--short", f"{rev}^{{commit}}").strip()


def _files(count: int) -> str:
    return f"{count} file{'' if count == 1 else 's'}"


def _collect(
    repo_root: Path,
    target: str,
    untracked: Sequence[str],
    exclude: Sequence[str],
) -> tuple[tuple[ChangedFile, ...], tuple[ExcludedPath, ...]]:
    """One tracked comparison (``git diff <target>``) plus any untracked files, as files and exclusions.

    ``target`` is a single revision (compared with the working tree) or ``base...head``.
    """
    entries = parse_name_status(run_git(repo_root, "diff", "--name-status", "-z", "-M", *_DIFF_FLAGS, target, "--"))
    numstat = parse_numstat(run_git(repo_root, "diff", "--numstat", "-z", "-M", *_DIFF_FLAGS, target, "--"))

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
            run_git(
                repo_root, "diff", "-M", "-U3", *_DIFF_FLAGS, "--src-prefix=a/", "--dst-prefix=b/", target, "--"
            )
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
    return tuple(files), tuple(excluded)


@dataclass(frozen=True)
class BranchDiff:
    """What ``head`` changed since it left ``base``, and the two commits that were compared."""

    files: tuple[ChangedFile, ...]
    excluded: tuple[ExcludedPath, ...]
    merge_base: str
    """Abbreviated ID of the commit the comparison starts from."""
    head: str
    """Abbreviated ID of the commit ``head`` resolved to."""

    @property
    def commits(self) -> str:
        return f"{self.merge_base}..{self.head}"


def diff_branches(repo_root: Path, base: str, head: str, exclude: Sequence[str]) -> BranchDiff:
    """``git diff base...head``: merge-base(base, head) ↔ head. The working tree and the index are not read.

    Two-dot would review commits merged into ``base`` after the branch point as the author's own work (R-4).
    """
    files, excluded = _collect(repo_root, f"{base}...{head}", (), exclude)
    merge_base = run_git(repo_root, "merge-base", base, head).strip()
    return BranchDiff(files, excluded, merge_base=_short(repo_root, merge_base), head=_short(repo_root, head))


def resolve(
    repo_root: Path,
    scope: ScopeRequest,
    exclude: Sequence[str],
    *,
    was_defaulted: bool,
) -> ChangeSet:
    if scope.kind == "working-tree":
        return _resolve_working_tree(repo_root, exclude, was_defaulted=was_defaulted)
    if scope.kind == "range":
        return _resolve_range(repo_root, scope, exclude, was_defaulted=was_defaulted)
    raise NotImplementedError(f"the {scope.kind} scope arrives with User Story 4")


def _resolve_working_tree(repo_root: Path, exclude: Sequence[str], *, was_defaulted: bool) -> ChangeSet:
    base = _empty_tree(repo_root) if head_is_unborn(repo_root) else "HEAD"
    untracked = [p for p in run_git(repo_root, "ls-files", "--others", "--exclude-standard", "-z").split("\0") if p]
    files, excluded = _collect(repo_root, base, untracked, exclude)
    description = (
        f"uncommitted changes in the working tree{' (default)' if was_defaulted else ''} · {_files(len(files))}"
    )
    return ChangeSet(
        repo_root=repo_root,
        scope=ResolvedScope(kind="working-tree", was_defaulted=was_defaulted, description=description),
        files=files,
        excluded=excluded,
    )


def _resolve_range(repo_root: Path, scope: ScopeRequest, exclude: Sequence[str], *, was_defaulted: bool) -> ChangeSet:
    if scope.base is None:
        raise ValueError("the range scope needs a base; preflight checks this before a change is resolved")
    head = scope.head or "HEAD"
    diff = diff_branches(repo_root, scope.base, head, exclude)
    description = (
        f"changes on {head} since it left {scope.base} ({diff.commits})"
        f"{' (default)' if was_defaulted else ''} · {_files(len(diff.files))}"
    )
    return ChangeSet(
        repo_root=repo_root,
        scope=ResolvedScope(
            kind="range", base_ref=scope.base, head_ref=head, was_defaulted=was_defaulted, description=description
        ),
        files=diff.files,
        excluded=diff.excluded,
    )


def read_worktree_bytes(repo_root: Path, path: str) -> bytes:
    return (repo_root / path).read_bytes()


def read_blob_bytes(repo_root: Path, spec: str) -> bytes:
    _, data = run_git_bytes(repo_root, "show", spec)
    return data
