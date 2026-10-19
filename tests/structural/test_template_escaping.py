"""FR-10.4d: autoescape is not negotiable, and the template is shipped package data.

import-linter sees imports; it cannot see a `|safe` in a template, a dynamic import, or a resource reached by path
arithmetic. These AST and text checks cover that gap, as `test_git_confinement.py` does for subprocess arguments.
"""

from __future__ import annotations

import ast
import re
from importlib.resources import files
from pathlib import Path

from agentic_review.core.output.html import TEMPLATE_NAME, TEMPLATE_PACKAGE

SRC = Path(__file__).resolve().parents[2] / "src" / "agentic_review"
OUTPUT = SRC / "core" / "output"
TEMPLATE = OUTPUT / "templates" / "report.html.j2"


def _template_text() -> str:
    return TEMPLATE.read_text(encoding="utf-8")


def _template_markup() -> str:
    """The template with its ``{# ... #}`` comments removed.

    The comment block documents these rules by naming the things it forbids, and a ``|safe`` inside a Jinja comment
    is inert. What matters is the markup that renders.
    """
    return re.sub(r"\{#.*?#\}", "", _template_text(), flags=re.DOTALL)


def test_the_template_is_where_the_renderer_looks_for_it() -> None:
    assert TEMPLATE.is_file()
    assert TEMPLATE_PACKAGE == "agentic_review.core.output"
    assert TEMPLATE_NAME == "templates/report.html.j2"


def test_the_template_resolves_through_importlib_resources() -> None:
    # The runtime path, so this is the inclusion check that matters: it is how the renderer reads the file whether
    # the package is installed as a directory or as a zip.
    resource = files(TEMPLATE_PACKAGE).joinpath(TEMPLATE_NAME)
    assert resource.is_file()
    assert resource.read_text(encoding="utf-8") == _template_text()


def test_the_template_never_marks_anything_safe() -> None:
    text = _template_markup()
    for forbidden in ("|safe", "| safe", "{% autoescape", "Markup", "safe }}"):
        assert forbidden not in text, forbidden


def test_the_template_fetches_nothing_and_runs_nothing() -> None:
    text = _template_markup()
    for forbidden in ("<script", "http://", "https://", "@import", "<iframe", "<object", "<embed", "javascript:"):
        assert forbidden not in text, forbidden


def test_the_template_never_dumps_a_model() -> None:
    # Run metadata reaches the template as view.run_rows, an explicit allow-list. Iterating a model here would let
    # a field added to RunMetadata later appear in a published document without anyone choosing to publish it.
    text = _template_markup()
    for forbidden in ("model_dump", ".items()", "environ", "__dict__", "__class__"):
        assert forbidden not in text, forbidden


def _file_dunder_uses(tree: ast.AST) -> list[int]:
    return sorted({node.lineno for node in ast.walk(tree) if isinstance(node, ast.Name) and node.id == "__file__"})


def test_the_check_detects_a_file_dunder_use_but_not_a_mention_in_a_docstring() -> None:
    assert _file_dunder_uses(ast.parse("from pathlib import Path\nPath(__file__).parent\n")) == [2]
    assert _file_dunder_uses(ast.parse('"""Never read a resource relative to __file__."""\n')) == []


def test_no_module_under_core_output_reaches_a_file_by_path() -> None:
    # `Path(__file__).parent` is the idiom that breaks in a zipped distribution, and this is the precedent the
    # resolver bundle inherits (technical_stack.md §3.1). A docstring saying so is not a use of it.
    offenders = []
    for path in OUTPUT.rglob("*.py"):
        for line in _file_dunder_uses(ast.parse(path.read_text(encoding="utf-8"))):
            offenders.append(f"{path.relative_to(SRC).as_posix()}:{line}")
    assert offenders == [], f"core/output reaches a file by path instead of importlib.resources: {offenders}"


def _jinja_imports(tree: ast.AST) -> list[int]:
    lines = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            lines += [node.lineno for alias in node.names if alias.name.split(".")[0] in {"jinja2", "markupsafe"}]
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] in {"jinja2", "markupsafe"}:
                lines.append(node.lineno)
        elif isinstance(node, ast.Call):
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
            if name == "import_module" and node.args:
                first = node.args[0]
                if isinstance(first, ast.Constant) and str(first.value).split(".")[0] in {"jinja2", "markupsafe"}:
                    lines.append(node.lineno)
    return lines


def test_the_check_detects_both_an_import_and_a_dynamic_one() -> None:
    assert _jinja_imports(ast.parse("from jinja2 import Environment\n")) == [1]
    assert _jinja_imports(ast.parse('import importlib\nimportlib.import_module("jinja2")\n')) == [2]


def test_only_core_output_imports_jinja2() -> None:
    # Contract 8 in pyproject.toml says the same thing about static imports; this also catches a dynamic one.
    offenders = []
    for path in SRC.rglob("*.py"):
        if OUTPUT in path.parents:
            continue
        for line in _jinja_imports(ast.parse(path.read_text(encoding="utf-8"))):
            offenders.append(f"{path.relative_to(SRC).as_posix()}:{line}")
    assert offenders == [], f"Jinja2 is imported outside core/output: {offenders}"
