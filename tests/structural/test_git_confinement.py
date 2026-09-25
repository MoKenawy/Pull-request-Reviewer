"""FR-10.3c / research R-3: only ``core/changeset/`` runs git.

import-linter sees imports, not subprocess arguments, so this AST check covers the gap: no module outside
``core/changeset/`` may call a ``subprocess`` function with the literal ``"git"`` as the first argv element.
"""

from __future__ import annotations

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src" / "agentic_review"
CHANGESET = SRC / "core" / "changeset"
SUBPROCESS_FUNCTIONS = {"run", "Popen", "call", "check_call", "check_output"}


def _git_calls(tree: ast.AST) -> list[int]:
    lines = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
        if name not in SUBPROCESS_FUNCTIONS:
            continue
        argv = node.args[0]
        if isinstance(argv, (ast.List, ast.Tuple)) and argv.elts:
            first = argv.elts[0]
            if isinstance(first, ast.Constant) and first.value == "git":
                lines.append(node.lineno)
    return lines


def test_the_check_detects_a_git_call() -> None:
    assert _git_calls(ast.parse('import subprocess\nsubprocess.run(["git", "status"])\n')) == [2]


def test_no_git_invocation_outside_changeset() -> None:
    offenders = []
    for path in SRC.rglob("*.py"):
        if CHANGESET in path.parents:
            continue
        for line in _git_calls(ast.parse(path.read_text(encoding="utf-8"))):
            offenders.append(f"{path.relative_to(SRC)}:{line}")
    assert offenders == [], f"git is run outside core/changeset: {offenders}"
