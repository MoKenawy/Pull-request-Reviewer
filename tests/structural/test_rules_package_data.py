"""The shipped rules are package data, reached through ``importlib.resources`` — research R-1, technical_stack §3.1.

**Why this is a structural test and not the packaging test T034 describes.** T034 asks for a unit test proving
``load_library()`` works "against the installed distribution, so a wheel that forgot the package data fails here
rather than in a user's install". It cannot: the project is installed **editable** (``_editable_impl_*.pth``
points at ``src/``) and CI runs ``uv sync``, so ``importlib.resources`` resolves to the source tree both locally
and in CI. A test written that way would pass against a wheel that shipped no ``*.yml`` at all.

What *is* checkable, and is what actually prevents the failure, is the mechanism: the rules must be read through
``importlib.resources`` and never by path arithmetic from ``__file__``, because the second works in a source tree
and fails in a zipped wheel. That is the shape ``test_template_escaping.py`` already uses for the HTML template,
the project's other package-data file. Catching a wheel that genuinely forgot its data needs ``uv build`` plus
inspection of the artifact, which no task in this feature does — recorded in implementation-notes.md.
"""

from __future__ import annotations

import ast
from importlib import resources
from pathlib import Path

from agentic_review.core.patterns import load_library

SRC = Path(__file__).resolve().parents[2] / "src" / "agentic_review"
PATTERNS = SRC / "core" / "patterns"
RULES_PACKAGE = "agentic_review.core.patterns.rules"


def test_the_rules_resolve_through_importlib_resources() -> None:
    root = resources.files(RULES_PACKAGE)
    documents = [entry.name for entry in root.iterdir() if entry.name.endswith(".yml")]
    assert documents, "no rule documents are addressable as package data"
    assert len(documents) >= 1 and all(document.endswith(".yml") for document in documents)
    # And the loader actually reads them, rather than a hard-coded fallback inside the module.
    assert len(load_library().rules) >= 5


def test_the_rules_directory_is_an_addressable_package() -> None:
    # Without __init__.py, importlib.resources cannot name it, and hatchling's wheel would still contain the files.
    assert (PATTERNS / "rules" / "__init__.py").is_file()


def test_no_module_under_patterns_reaches_the_rules_by_path_arithmetic_from_dunder_file() -> None:
    offenders = []
    for path in sorted(PATTERNS.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == "__file__":
                offenders.append(f"{path.relative_to(SRC)}:{node.lineno}")
    message = (
        "core/patterns/ reaches its package data through __file__; use importlib.resources, which also works "
        f"from a zipped wheel (technical_stack.md §3.1): {offenders}"
    )
    assert offenders == [], message


def test_every_rule_document_is_yaml_and_none_is_python() -> None:
    """Rules are data. A ``.py`` under ``rules/`` other than ``__init__.py`` would mean someone made them code."""
    rules_dir = PATTERNS / "rules"
    python_files = {path.name for path in rules_dir.glob("*.py")}
    assert python_files == {"__init__.py"}, f"rules/ holds Python beyond its package marker: {python_files}"
    assert list(rules_dir.glob("*.yaml")) == [], "the loader reads *.yml only; a *.yaml file would load silently never"
