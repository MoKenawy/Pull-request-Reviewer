"""The change summary and line counts — data-model §2, research R-5."""

from __future__ import annotations

from pathlib import Path

from agentic_review.core.changeset.model import ScopeRequest
from agentic_review.core.changeset.resolve import resolve
from agentic_review.core.changeset.summary import measure_new_files, summarise
from tests.support.repo_builder import RepoBuilder


def test_summary_and_line_counts(tmp_path: Path) -> None:
    repo = RepoBuilder(tmp_path / "repo").init()
    repo.write("src/app.ts", "a\nb\n").write("src/gone.js", "x\n").write("README.md", "r\n")
    repo.write_bytes("logo.bin", b"\0\1")
    repo.commit("initial")
    repo.write("src/app.ts", "a\nb\nc\nd")  # no trailing newline: 4 lines
    repo.delete("src/gone.js").write("README.md", "r\ns\n").write_bytes("logo.bin", b"\0\2")
    repo.write("dist/out.js", "built\n")

    change_set = resolve(repo.root, ScopeRequest(kind="working-tree"), (), was_defaulted=True)
    summary = summarise(change_set)

    files = {f.path: f for f in summary.files}
    assert files["src/app.ts"].reviewed and files["src/app.ts"].not_reviewed_reason is None
    assert (files["src/app.ts"].hunk_count, files["src/app.ts"].added_lines) == (1, 2)
    assert files["src/gone.js"].not_reviewed_reason == "deleted"
    assert files["logo.bin"].not_reviewed_reason == "binary"
    assert files["README.md"].not_reviewed_reason == "not-typescript-or-javascript"
    assert files["README.md"].hunk_count == 0 and files["README.md"].added_lines == 1
    assert [(e.path, e.rule) for e in summary.excluded] == [("dist/out.js", "default:build-output")]
    assert summary.scope == change_set.scope

    dumped = summary.model_dump_json(by_alias=True)
    assert "@@" not in dumped and "hunks" not in dumped

    assert measure_new_files(change_set) == {"src/app.ts": 4}
