"""Parsing git's diff output into files and hunks (research R-5). Hunk text is kept verbatim."""

from __future__ import annotations

import re
from collections.abc import Iterable

from agentic_review.core.changeset.model import Hunk
from agentic_review.core.findings.report import ChangeType

_STATUS: dict[str, ChangeType] = {"A": "added", "M": "modified", "D": "deleted", "R": "renamed", "T": "modified"}
_HUNK_HEADER = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def parse_name_status(output: str) -> list[tuple[ChangeType, str, str | None]]:
    """``git diff --name-status -z -M`` → ``(change type, path, previous path)``."""
    tokens = output.split("\0")
    entries: list[tuple[ChangeType, str, str | None]] = []
    index = 0
    while index < len(tokens) and tokens[index]:
        status = tokens[index][0]
        if status in ("R", "C"):
            previous, path = tokens[index + 1], tokens[index + 2]
            entries.append(("renamed" if status == "R" else "added", path, previous if status == "R" else None))
            index += 3
        else:
            entries.append((_STATUS.get(status, "modified"), tokens[index + 1], None))
            index += 2
    return entries


def parse_numstat(output: str) -> dict[str, tuple[int, int] | None]:
    """``git diff --numstat -z -M`` → path → (added, removed), or None for a binary file."""
    tokens = output.split("\0")
    counts: dict[str, tuple[int, int] | None] = {}
    index = 0
    while index < len(tokens) and tokens[index]:
        added, removed, path = tokens[index].split("\t", 2)
        if path == "":  # a rename: the old and new paths follow as their own tokens
            path = tokens[index + 2]
            index += 3
        else:
            index += 1
        counts[path] = None if added == "-" else (int(added), int(removed))
    return counts


def _lines(text: str) -> list[str]:
    # Split on "\n" only, keeping it, so "\r" and other separators stay inside the line they belong to.
    return [line for line in re.split(r"(?<=\n)", text) if line]


def split_patch(patch: str) -> dict[str, list[Hunk]]:
    """A ``git diff`` patch → new path → hunks. Files without hunks (binary, pure renames) are absent."""
    result: dict[str, list[Hunk]] = {}
    path: str | None = None
    minus_path: str | None = None
    header: tuple[int, int, int, int, str] | None = None
    body: list[str] = []
    in_hunks = False

    def flush() -> None:
        nonlocal header, body
        if header is not None and path is not None:
            result.setdefault(path, []).append(Hunk(*header[:4], header=header[4], text="".join(body)))
        header, body = None, []

    for line in _lines(patch):
        if line.startswith("diff --git "):
            flush()
            path, minus_path, in_hunks = None, None, False
            continue
        if not in_hunks:
            content = line.rstrip("\r\n")
            if content.startswith("rename to "):
                path = content[len("rename to "):]
            elif content.startswith("--- "):
                minus_path = _strip_prefix(content[4:], "a/")
            elif content.startswith("+++ "):
                plus = _strip_prefix(content[4:], "b/")
                path = plus if plus is not None else minus_path
            elif content.startswith("@@"):
                in_hunks = True
        if in_hunks and line.startswith("@@"):
            flush()
            match = _HUNK_HEADER.match(line)
            if match is None:
                continue
            old_start, old_count, new_start, new_count = match.groups()
            header = (
                int(old_start),
                1 if old_count is None else int(old_count),
                int(new_start),
                1 if new_count is None else int(new_count),
                line.rstrip("\r\n"),
            )
        elif in_hunks and header is not None:
            body.append(line)
    flush()
    return result


def _strip_prefix(value: str, prefix: str) -> str | None:
    value = value.rstrip("\t")  # git appends a tab after a path containing a space
    if value == "/dev/null":
        return None
    return value[len(prefix):] if value.startswith(prefix) else value


def changed_line_ranges(hunks: Iterable[Hunk]) -> tuple[tuple[int, int], ...]:
    """Added lines in new-file coordinates, 1-based and inclusive, merged into ranges."""
    lines: list[int] = []
    for hunk in hunks:
        current = hunk.new_start
        for line in _lines(hunk.text):
            if line.startswith("+"):
                lines.append(current)
                current += 1
            elif line.startswith(" "):
                current += 1
    ranges: list[tuple[int, int]] = []
    for number in lines:
        if ranges and number == ranges[-1][1] + 1:
            ranges[-1] = (ranges[-1][0], number)
        else:
            ranges.append((number, number))
    return tuple(ranges)


def synthesise_added_file(text: str) -> Hunk | None:
    """One hunk for a file git does not yet track, shaped exactly as ``git diff`` would show it."""
    lines = _lines(text)
    if not lines:
        return None
    body = "".join(f"+{line}" for line in lines)
    if not body.endswith("\n"):
        body += "\n\\ No newline at end of file\n"
    count = len(lines)
    return Hunk(0, 0, 1, count, header=f"@@ -0,0 +1{'' if count == 1 else f',{count}'} @@", text=body)
