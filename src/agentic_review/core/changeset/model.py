"""The change set — files and hunks, independent of the scope that produced it (FR-10.3c, data-model §2).

``ChangeSet`` 🔒 is what v3's Action adapter will produce by other means, so it carries nothing git-specific.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from agentic_review.core.findings.report import ChangeType, ExcludedPath, Language, ResolvedScope, ScopeKind

_LANGUAGES: dict[str, Language] = {
    ".ts": "ts",
    ".mts": "ts",
    ".cts": "ts",
    ".tsx": "tsx",
    ".js": "js",
    ".mjs": "js",
    ".cjs": "js",
    ".jsx": "jsx",
}


def language_for(path: str) -> Language:
    return _LANGUAGES.get(PurePosixPath(path).suffix.lower(), "other")


@dataclass(frozen=True)
class Hunk:
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    header: str
    text: str
    """The hunk body exactly as git produced it. What is stored is what is sent (02 §3.1)."""


@dataclass(frozen=True)
class ChangedFile:
    path: str
    change_type: ChangeType
    previous_path: str | None
    language: Language
    is_binary: bool
    changed_line_ranges: tuple[tuple[int, int], ...]
    hunks: tuple[Hunk, ...]
    added_lines: int
    removed_lines: int

    @property
    def is_reviewable(self) -> bool:
        return self.change_type != "deleted" and not self.is_binary and self.language != "other"


@dataclass(frozen=True)
class ScopeRequest:
    kind: ScopeKind
    base: str | None = None
    head: str | None = None
    """``range`` only; None means ``HEAD``."""


@dataclass(frozen=True)
class ChangeSet:
    repo_root: Path
    scope: ResolvedScope
    files: tuple[ChangedFile, ...]
    """Every changed, non-excluded path, reviewable or not."""
    excluded: tuple[ExcludedPath, ...]

    @property
    def reviewable_files(self) -> tuple[ChangedFile, ...]:
        return tuple(f for f in self.files if f.is_reviewable)
