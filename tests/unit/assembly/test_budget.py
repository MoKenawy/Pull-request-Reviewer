"""The context limit — FR-2.5b, FR-11.2 (spec 001 FR-019); research R-15. Over budget is refused, never truncated."""

from __future__ import annotations

from agentic_review.core.assembly.budget import BudgetExhausted, estimate_tokens
from agentic_review.core.assembly.prompt import (
    INSTRUCTIONS,
    assemble,
    fixed_section_tokens,
    system_message,
)
from agentic_review.core.config.settings import BudgetSettings
from agentic_review.core.findings.port import ReviewContext
from tests.unit.assembly.test_prompt import BLOCK, CHANGE_SET

LINE_COUNTS = {"src/app.ts": 40, "lib/new.js": 31}


def _estimate() -> int:
    context = assemble(CHANGE_SET, LINE_COUNTS, BudgetSettings())
    assert isinstance(context, ReviewContext)
    return context.estimated_tokens


def test_an_estimate_above_the_limit_is_budget_exhausted() -> None:
    estimate = _estimate()
    result = assemble(CHANGE_SET, LINE_COUNTS, BudgetSettings(max_tokens=estimate - 1))
    assert result == BudgetExhausted(
        estimated_tokens=estimate,
        limit=estimate - 1,
        fixed_section_tokens=fixed_section_tokens(INSTRUCTIONS),
    )
    assert not isinstance(result, ReviewContext)  # no partial prompt is ever built


def test_an_estimate_at_the_limit_is_accepted() -> None:
    estimate = _estimate()
    result = assemble(CHANGE_SET, LINE_COUNTS, BudgetSettings(max_tokens=estimate))
    assert isinstance(result, ReviewContext)
    assert result.estimated_tokens == estimate


# --- the fixed section (spec 003 FR-009, T020; research R-8) --------------------------------------------------------


def test_the_fixed_section_is_the_instructions_plus_the_rules() -> None:
    assert fixed_section_tokens(INSTRUCTIONS, BLOCK) == estimate_tokens(system_message(INSTRUCTIONS, BLOCK))
    assert fixed_section_tokens(INSTRUCTIONS) == estimate_tokens(INSTRUCTIONS)
    # The library raises the floor. How much is an observation, never a target: no test may assert the block fits
    # inside a token count, because the budget it would be measured against is a placeholder (Principle VI).
    assert fixed_section_tokens(INSTRUCTIONS, BLOCK) > fixed_section_tokens(INSTRUCTIONS)


def test_budget_exhaustion_carries_the_fixed_sections_share_so_the_cause_is_legible() -> None:
    estimate = _estimate()
    result = assemble(CHANGE_SET, LINE_COUNTS, BudgetSettings(max_tokens=estimate - 1), rules_block=BLOCK)
    assert isinstance(result, BudgetExhausted)
    assert result.fixed_section_tokens == fixed_section_tokens(INSTRUCTIONS, BLOCK)
    assert result.fixed_section_tokens < result.estimated_tokens
