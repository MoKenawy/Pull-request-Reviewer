"""What the model is given — FR-2.5b (diff never truncated, material statement), research R-15."""

from __future__ import annotations

import math
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from agentic_review.core.assembly.budget import estimate_tokens
from agentic_review.core.assembly.prompt import (
    INSTRUCTIONS,
    MATERIAL_STATEMENT,
    SYSTEM_PROMPT_NAME,
    assemble,
    load_instructions,
    prompt_text,
)
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
    for phrase in ("emit_finding", "one turn", "no tool call"):
        assert phrase in instructions


def test_instructions_leave_the_field_rules_to_the_tool() -> None:
    # Severity, evidence kinds and the example travel with the bound tool (tests/unit/agents/test_binding.py).
    for phrase in ("# Severity", "# Filling in the fields", "unverified", "hunkIndex"):
        assert phrase not in INSTRUCTIONS


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


LANGFUSE_ENV = {"LANGFUSE_PUBLIC_KEY": "pk-lf-test", "LANGFUSE_SECRET_KEY": "sk-lf-test"}


class _FakeLangfuse:
    """Stands in for ``langfuse.Langfuse``: returns ``prompt`` from ``get_prompt`` and records what was asked."""

    prompt: Any = None
    requested: list[str] = []

    def __init__(self, **_kwargs: object) -> None:
        pass

    def get_prompt(self, name: str, **_kwargs: object) -> SimpleNamespace:
        self.requested.append(name)
        return SimpleNamespace(prompt=self.prompt, version=7)


@pytest.fixture
def fake_langfuse(monkeypatch: pytest.MonkeyPatch) -> type[_FakeLangfuse]:
    _FakeLangfuse.requested = []
    monkeypatch.setattr("langfuse.Langfuse", _FakeLangfuse)
    return _FakeLangfuse


def test_without_langfuse_credentials_the_built_in_prompt_is_used() -> None:
    loaded = load_instructions({})
    assert (loaded.text, loaded.source, loaded.problem) == (INSTRUCTIONS, "built-in", None)
    assert _assemble().instructions == INSTRUCTIONS


def test_the_langfuse_system_message_is_used(fake_langfuse: type[_FakeLangfuse]) -> None:
    fake_langfuse.prompt = [{"role": "system", "content": "Review it. Use \\\nemit_finding."}]
    loaded = load_instructions(LANGFUSE_ENV)
    assert fake_langfuse.requested == [SYSTEM_PROMPT_NAME]
    assert loaded.text == "Review it. Use emit_finding."  # the copied line continuations are joined
    assert loaded.source == f"langfuse:{SYSTEM_PROMPT_NAME}@v7" and loaded.problem is None


def test_a_failed_fetch_falls_back_to_the_built_in_prompt() -> None:
    # The suite blocks the network, so the real client's fetch fails: the review must still get a prompt.
    loaded = load_instructions(LANGFUSE_ENV)
    assert loaded.text == INSTRUCTIONS and loaded.source == "built-in" and loaded.problem


def test_a_prompt_without_a_system_message_falls_back(fake_langfuse: type[_FakeLangfuse]) -> None:
    fake_langfuse.prompt = [{"role": "user", "content": "hello"}]
    loaded = load_instructions(LANGFUSE_ENV)
    assert loaded.text == INSTRUCTIONS and "no system message" in (loaded.problem or "")


def test_explicit_instructions_override_the_loaded_prompt() -> None:
    context = assemble(CHANGE_SET, {"src/app.ts": 40, "lib/new.js": 31}, BudgetSettings(), "Only this.")
    assert context.instructions == "Only this."
    text = prompt_text(context.instructions, context.material_statement, context.diff_section)
    assert context.estimated_tokens == estimate_tokens(text)
