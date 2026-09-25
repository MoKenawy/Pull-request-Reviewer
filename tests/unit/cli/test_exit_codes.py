"""The CLI maps a verdict computed in core to an integer — FR-10.4c, contracts/cli.md."""

from __future__ import annotations

import pytest

from agentic_review.cli.exit_codes import EXIT_PREFLIGHT, exit_code_for


@pytest.mark.parametrize(
    "verdict,code",
    [("findings", 0), ("no-findings", 0), ("nothing-to-review", 0), ("blocking", 1), ("no-judgement", 2)],
)
def test_verdict_to_exit_code(verdict: str, code: int) -> None:
    assert exit_code_for(verdict) == code  # type: ignore[arg-type]


def test_preflight_exit_code() -> None:
    assert EXIT_PREFLIGHT == 3
