"""What the model is given — FR-2.5b (diff never truncated, material statement), research R-15."""

from __future__ import annotations

import math
from pathlib import Path

from agentic_review.core.assembly.budget import estimate_tokens
from agentic_review.core.assembly.prompt import MATERIAL_STATEMENT, assemble, prompt_text
from agentic_review.core.changeset.model import ChangedFile, ChangeSet, Hunk
from agentic_review.core.config.settings import BudgetSettings
from agentic_review.core.findings.port import ReviewContext, ReviewedFile
from agentic_review.core.findings.report import ResolvedScope

HUNK_A = Hunk(1, 2, 1, 3, header="@@ -1,2 +1,3 @@", text=" keep\r\n-old\r\n+new\r\n+added\r\n")
HUNK_B = Hunk(30, 1, 31, 1, header="@@ -30 +31 @@ function f() {", text="-  return 1\n+  return 2\n")


def _file(path: str, **overrides: object) -> ChangedFile:
    fields: dict[str, object] = dict(
        path=path, change_type="modified", previous_path=None, language="ts", is_binary=False,
        changed_line_ranges=((2, 3),), hunks=(HUNK_A, HUNK_B), added_lines=3, removed_lines=2,
    )
    fields.update(overrides)
    return ChangedFile(**fields)  # type: ignore[arg-type]


CHANGE_SET = ChangeSet(
    repo_root=Path("/repo"),
    scope=ResolvedScope(kind="working-tree", was_defaulted=True, description="uncommitted changes"),
    files=(
        _file("src/app.ts"),
        _file("lib/new.js", change_type="renamed", previous_path="src/old.js", language="js", hunks=(HUNK_B,)),
        _file("README.md", language="other", hunks=()),
        _file("src/gone.ts", change_type="deleted", hunks=()),
    ),
    excluded=(),
)


def _assemble() -> ReviewContext:
    result = assemble(CHANGE_SET, {"src/app.ts": 40, "lib/new.js": 31}, BudgetSettings())
    assert isinstance(result, ReviewContext)
    return result


def test_diff_section_is_verbatim_with_headers() -> None:
    diff = _assemble().diff_section
    assert "src/app.ts (modified)" in diff
    assert "lib/new.js (renamed, renamed from src/old.js)" in diff
    assert f"[hunk 0] {HUNK_A.header}\n{HUNK_A.text}" in diff
    assert f"[hunk 1] {HUNK_B.header}\n{HUNK_B.text}" in diff
    assert diff.index("src/app.ts (modified)") < diff.index("lib/new.js")


def test_non_reviewable_files_are_not_sent() -> None:
    diff = _assemble().diff_section
    assert "README.md" not in diff and "src/gone.ts" not in diff


def test_material_statement() -> None:
    assert MATERIAL_STATEMENT == "No checks were run. No related context was gathered."
    assert _assemble().material_statement == MATERIAL_STATEMENT


def test_instructions_name_the_only_way_to_report() -> None:
    instructions = _assemble().instructions
    for phrase in ("emit_finding", "blocking", "important", "nit", "error-handling", "unverified", "no tool call"):
        assert phrase in instructions


def test_run_material() -> None:
    material = _assemble().material
    assert dict(material.reviewed_files) == {
        "src/app.ts": ReviewedFile(line_count=40, hunk_count=2),
        "lib/new.js": ReviewedFile(line_count=31, hunk_count=1),
    }
    assert material.check_ids == frozenset() and material.context_ranges == () and material.rule_ids == frozenset()


def test_estimate_covers_the_whole_prompt() -> None:
    context = _assemble()
    text = prompt_text(context.instructions, context.material_statement, context.diff_section)
    assert context.estimated_tokens == estimate_tokens(text) == math.ceil(len(text) / 3)
