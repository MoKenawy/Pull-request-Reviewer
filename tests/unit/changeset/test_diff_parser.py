"""Parsing git's own output — FR-10.3c, spec 001 FR-009, research R-5, R-7. Inputs are literal git output."""

from __future__ import annotations

import pytest

from agentic_review.core.changeset.diff_parser import (
    changed_line_ranges,
    parse_name_status,
    parse_numstat,
    split_patch,
    synthesise_added_file,
)
from agentic_review.core.changeset.model import language_for

NAME_STATUS = "A\0README.md\0M\0b.bin\0D\0gone.js\0R087\0old.ts\0new name.ts\0"
NUMSTAT = "1\t0\tREADME.md\0-\t-\tb.bin\0" "0\t1\tgone.js\0" "1\t0\t\0old.ts\0new name.ts\0"

PATCH = (
    "diff --git a/README.md b/README.md\n"
    "new file mode 100644\n"
    "index 0000000..bca70f3\n"
    "--- /dev/null\n"
    "+++ b/README.md\n"
    "@@ -0,0 +1 @@\n"
    "+q\n"
    "diff --git a/b.bin b/b.bin\n"
    "index 87ae6b6..22f6b3b 100644\n"
    "Binary files a/b.bin and b/b.bin differ\n"
    "diff --git a/gone.js b/gone.js\n"
    "deleted file mode 100644\n"
    "index 587be6b..0000000\n"
    "--- a/gone.js\n"
    "+++ /dev/null\n"
    "@@ -1 +0,0 @@\n"
    "-x\n"
    "diff --git a/old.ts b/new name.ts\n"
    "similarity index 87%\n"
    "rename from old.ts\n"
    "rename to new name.ts\n"
    "index f9d9a01..71ac1b5 100644\n"
    "--- a/old.ts\n"
    "+++ b/new name.ts\t\n"
    "@@ -5,3 +5,4 @@ d\n"
    " e\n"
    " f\n"
    " g\n"
    "+h\n"
    "diff --git a/src/app.ts b/src/app.ts\n"
    "index 1111111..2222222 100644\n"
    "--- a/src/app.ts\n"
    "+++ b/src/app.ts\n"
    "@@ -1,3 +1,4 @@\n"
    " one\r\n"
    "-two\r\n"
    "+two!\r\n"
    "+two and a half\r\n"
    " three\r\n"
    "@@ -20,2 +21,2 @@ function tail() {\n"
    "-  return 1\n"
    "+  return 2\n"
    "\\ No newline at end of file\n"
)


def test_name_status() -> None:
    assert parse_name_status(NAME_STATUS) == [
        ("added", "README.md", None),
        ("modified", "b.bin", None),
        ("deleted", "gone.js", None),
        ("renamed", "new name.ts", "old.ts"),
    ]


def test_numstat_marks_binary_and_uses_new_path_for_renames() -> None:
    assert parse_numstat(NUMSTAT) == {
        "README.md": (1, 0),
        "b.bin": None,
        "gone.js": (0, 1),
        "new name.ts": (1, 0),
    }


def test_split_patch_finds_every_text_file_by_its_new_path() -> None:
    hunks = split_patch(PATCH)
    assert set(hunks) == {"README.md", "gone.js", "new name.ts", "src/app.ts"}
    assert hunks["new name.ts"][0].header == "@@ -5,3 +5,4 @@ d"
    assert (hunks["new name.ts"][0].new_start, hunks["new name.ts"][0].new_count) == (5, 4)


def test_hunk_text_is_verbatim_including_crlf() -> None:
    first, second = split_patch(PATCH)["src/app.ts"]
    assert first.text == " one\r\n-two\r\n+two!\r\n+two and a half\r\n three\r\n"
    assert (first.old_start, first.old_count, first.new_start, first.new_count) == (1, 3, 1, 4)
    assert second.text.endswith("\\ No newline at end of file\n")


def test_counts_default_to_one() -> None:
    hunk = split_patch(PATCH)["README.md"][0]
    assert (hunk.old_start, hunk.old_count, hunk.new_start, hunk.new_count) == (0, 0, 1, 1)


def test_changed_line_ranges_in_new_file_coordinates() -> None:
    assert changed_line_ranges(split_patch(PATCH)["src/app.ts"]) == ((2, 3), (21, 21))


def test_synthesised_added_file() -> None:
    hunk = synthesise_added_file("a\nb\nc")
    assert hunk is not None
    assert hunk.header == "@@ -0,0 +1,3 @@"
    assert hunk.text == "+a\n+b\n+c\n\\ No newline at end of file\n"
    assert changed_line_ranges((hunk,)) == ((1, 3),)
    assert synthesise_added_file("") is None


@pytest.mark.parametrize(
    "path,language",
    [
        ("a.ts", "ts"), ("a.mts", "ts"), ("a.cts", "ts"), ("a.tsx", "tsx"),
        ("a.js", "js"), ("a.mjs", "js"), ("a.cjs", "js"), ("a.jsx", "jsx"),
        ("README.md", "other"), ("package.json", "other"), ("A.TS", "ts"),
    ],
)
def test_language_from_extension(path: str, language: str) -> None:
    assert language_for(path) == language
