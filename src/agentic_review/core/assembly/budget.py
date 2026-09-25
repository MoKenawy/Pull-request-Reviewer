"""The context budget — CF-4 is its sole owner (research R-15).

The estimate is ``ceil(characters / 3)``. It is an **estimate**, not a tokenizer count: the model's tokenizer is not
available locally, and dividing by 3 overestimates relative to typical BPE tokenizers for code, so a diff near the
limit is refused before the provider would truncate it rather than after.
"""

from __future__ import annotations

import math


def estimate_tokens(text: str) -> int:
    return math.ceil(len(text) / 3)
