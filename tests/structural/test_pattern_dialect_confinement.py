"""spec 003 FR-023 / research R-3: only ``core/changeset/`` evaluates a path pattern.

Import contract 6 catches the *import* — ``core/patterns/`` and ``core/changeset/`` are sibling Layer-1
capabilities, so neither may import the other. What it cannot catch is a copy-paste: a second glob translator
written inside ``core/patterns/``, importing nothing of ours, would keep every contract and still put the dialect
in two places, where the two would drift. So this AST check covers the gap, in the shape of
``test_git_confinement.py``: no module under ``core/patterns/`` may compile a regular expression, match a path
against one, or call a filesystem glob matcher.

``core/patterns/`` carries patterns as **data**. The one regex it is allowed is the identifier slug check in
``model.py``, which validates a rule's own ``id`` and never touches a path — that module is exempted by name,
and the exemption is the narrowest thing that works.
"""

from __future__ import annotations

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src" / "agentic_review"
PATTERNS = SRC / "core" / "patterns"
MODEL = PATTERNS / "model.py"

MATCHER_FUNCTIONS = {
    "compile",  # re.compile
    "fullmatch",
    "match",
    "search",
    "translate",  # fnmatch.translate, the other way to build a glob matcher
    "fnmatch",
    "fnmatchcase",
    "glob",
    "rglob",
    "glob_to_regex",  # the dialect's own translator, which lives in core/changeset/ and stays there
}


def _matcher_calls(tree: ast.AST) -> list[int]:
    lines = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
        if name in MATCHER_FUNCTIONS:
            lines.append(node.lineno)
    return lines


def test_the_check_detects_a_pattern_matcher() -> None:
    # The house convention: a check nobody has seen fire is a check nobody should trust.
    source = "import re\nre.compile('[^/]*').fullmatch(path)\n"
    assert _matcher_calls(ast.parse(source)) == [2, 2]


def test_no_module_under_patterns_evaluates_a_path_pattern() -> None:
    offenders = []
    for path in sorted(PATTERNS.rglob("*.py")):
        if path == MODEL:
            continue
        for line in _matcher_calls(ast.parse(path.read_text(encoding="utf-8"))):
            offenders.append(f"{path.relative_to(SRC)}:{line}")
    message = f"core/patterns/ evaluates path patterns; the dialect belongs to core/changeset/: {offenders}"
    assert offenders == [], message


def test_the_only_regex_in_the_rule_types_is_the_identifier_slug() -> None:
    """``model.py`` is exempted above, so this pins what the exemption is actually used for."""
    tree = ast.parse(MODEL.read_text(encoding="utf-8"))
    compiled = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "compile"
    ]
    assert len(compiled) == 1, "a second regex appeared in the rule types; is it matching a path?"
    assert isinstance(compiled[0].args[0], ast.Constant)
    assert "[a-z0-9]" in str(compiled[0].args[0].value), "the one permitted regex is the identifier slug"
