"""The context limit — FR-2.5b, FR-11.2 (spec 001 FR-019); research R-15. Over budget is refused, never truncated."""

from __future__ import annotations

from agentic_review.core.assembly.budget import BudgetExhausted
from agentic_review.core.assembly.prompt import assemble
from agentic_review.core.config.settings import BudgetSettings
from agentic_review.core.findings.port import ReviewContext
from tests.unit.assembly.test_prompt import CHANGE_SET

LINE_COUNTS = {"src/app.ts": 40, "lib/new.js": 31}


def _estimate() -> int:
    context = assemble(CHANGE_SET, LINE_COUNTS, BudgetSettings())
    assert isinstance(context, ReviewContext)
    return context.estimated_tokens


def test_an_estimate_above_the_limit_is_budget_exhausted() -> None:
    estimate = _estimate()
    result = assemble(CHANGE_SET, LINE_COUNTS, BudgetSettings(max_tokens=estimate - 1))
    assert result == BudgetExhausted(estimated_tokens=estimate, limit=estimate - 1)
    assert not isinstance(result, ReviewContext)  # no partial prompt is ever built


def test_an_estimate_at_the_limit_is_accepted() -> None:
    estimate = _estimate()
    result = assemble(CHANGE_SET, LINE_COUNTS, BudgetSettings(max_tokens=estimate))
    assert isinstance(result, ReviewContext)
    assert result.estimated_tokens == estimate
