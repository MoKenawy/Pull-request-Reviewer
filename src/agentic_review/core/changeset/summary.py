"""What leaves the change-set package for the report and for validation (data-model §2, research R-5)."""

from __future__ import annotations

from collections.abc import Mapping

from agentic_review.core.changeset.model import ChangedFile, ChangeSet
from agentic_review.core.changeset.resolve import read_blob_bytes, read_worktree_bytes
from agentic_review.core.findings.report import ChangeSummary, FileSummary, NotReviewedReason


def _not_reviewed_reason(changed: ChangedFile) -> NotReviewedReason | None:
    if changed.change_type == "deleted":
        return "deleted"
    if changed.is_binary:
        return "binary"
    if changed.language == "other":
        return "not-typescript-or-javascript"
    return None


def summarise(change_set: ChangeSet) -> ChangeSummary:
    """The change set without diff text."""
    return ChangeSummary(
        scope=change_set.scope,
        excluded=list(change_set.excluded),
        files=[
            FileSummary(
                path=f.path,
                change_type=f.change_type,
                previous_path=f.previous_path,
                language=f.language,
                is_binary=f.is_binary,
                reviewed=f.is_reviewable,
                not_reviewed_reason=_not_reviewed_reason(f),
                hunk_count=len(f.hunks),
                added_lines=f.added_lines,
                removed_lines=f.removed_lines,
            )
            for f in change_set.files
        ],
    )


def _reviewed_bytes(change_set: ChangeSet, path: str) -> bytes:
    """The file as it is in the version under review: on disk, or the head commit's blob."""
    scope = change_set.scope
    if scope.kind == "working-tree":
        return read_worktree_bytes(change_set.repo_root, path)
    if scope.kind in ("range", "pull-request") and scope.head_ref is not None:
        return read_blob_bytes(change_set.repo_root, f"{scope.head_ref}:{path}")
    raise NotImplementedError(f"measuring the {scope.kind} scope arrives with User Story 4")


def measure_new_files(change_set: ChangeSet) -> Mapping[str, int]:
    """Line counts of the version under review, for reviewable files only — the line-range check in FR-5.6a call
    validation (contracts/emit-finding.md)."""
    counts: dict[str, int] = {}
    for changed in change_set.reviewable_files:
        data = _reviewed_bytes(change_set, changed.path)
        counts[changed.path] = data.count(b"\n") + (0 if not data or data.endswith(b"\n") else 1)
    return counts
