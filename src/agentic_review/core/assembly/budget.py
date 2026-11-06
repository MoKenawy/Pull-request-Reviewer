"""The context budget — CF-4 is its sole owner (research R-15).

The estimate is ``ceil(characters / 3)``. It is an **estimate**, not a tokenizer count: the model's tokenizer is not
available locally, and dividing by 3 overestimates relative to typical BPE tokenizers for code, so a diff near the
limit is refused before the provider would truncate it rather than after.

An estimate over ``budget.maxTokens`` is refused as ``BudgetExhausted``: no partial diff is ever built (FR-2.5b).
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class BudgetExhausted:
    """What ``assemble`` returns instead of a prompt when the whole prompt would not fit (FR-11.2, data-model §4)."""

    estimated_tokens: int
    limit: int
    fixed_section_tokens: int = 0
    """The static prefix's share — the instructions plus the whole rule library.

    Carried so that the degradation can say *what is taking the room*. A static prefix raises every prompt's
    floor, which is the one new way a change set that used to fit can start being refused (research R-8). Zero
    when no library was given, which is what every run did before feature 003.
    """


def estimate_tokens(text: str) -> int:
    return math.ceil(len(text) / 3)
