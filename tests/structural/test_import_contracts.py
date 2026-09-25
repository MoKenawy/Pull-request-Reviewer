"""FR-5.8, FR-10.2, AC-10 (partial) / research R-20: the import-linter contracts also fail a plain ``pytest`` run."""

from __future__ import annotations

import os
from pathlib import Path

from importlinter.cli import lint_imports

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_every_import_contract_is_kept() -> None:
    previous = Path.cwd()
    os.chdir(PROJECT_ROOT)
    try:
        exit_code = lint_imports(config_filename=str(PROJECT_ROOT / "pyproject.toml"), no_cache=True)
    finally:
        os.chdir(previous)
    assert exit_code == 0, "an import-linter contract is broken; run `uv run lint-imports` for details"
