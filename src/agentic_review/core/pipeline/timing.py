"""Stage timing: every stage that runs records its duration on every run (FR-11.3, SRS §8 rule 2).

Durations are recorded, never compared against a latency value (Principle VI).
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager


class StageTimer:
    def __init__(self, clock: Callable[[], float]) -> None:
        self._clock = clock
        self.durations_ms: dict[str, int] = {}

    @contextmanager
    def stage(self, name: str) -> Iterator[None]:
        started = self._clock()
        try:
            yield
        finally:
            self.durations_ms[name] = max(0, round((self._clock() - started) * 1000))
