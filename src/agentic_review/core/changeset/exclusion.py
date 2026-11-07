"""Exclusion globs over repo-relative POSIX paths (FR-3.5, research R-6).

``**`` matches zero or more whole segments; ``*`` and ``?`` stay within one segment; a pattern with no ``/`` matches at
any depth (the gitignore convention). Configured patterns are always added to the defaults, never substituted for them.

**This module is the only path-pattern matcher in the system.** Since feature 003 there is a second source of
exclusion at the same stage — the rule library's declared scopes (SRS FR-6.1a) — and it reuses the dialect below
rather than bringing its own. ``core/patterns/`` carries those scopes as data and evaluates none of them; they
arrive here as plain tuples of strings, which is the seam that keeps the two sibling capabilities from importing
each other (research R-3, import contract 6, ``tests/structural/test_pattern_dialect_confinement.py``).
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from functools import lru_cache

RuleScope = tuple[tuple[str, ...], tuple[str, ...]]
"""One rule's ``(include, exclude)`` patterns. Plain builtins: the rule types never cross this boundary."""

DEFAULT_EXCLUSIONS: dict[str, tuple[str, ...]] = {
    "dependencies": ("node_modules/**", "**/node_modules/**", "vendor/**", "bower_components/**"),
    "build-output": ("dist/**", "build/**", "out/**", "coverage/**", ".next/**", ".nuxt/**", ".turbo/**"),
    "generated": ("**/*.generated.*", "**/*.gen.ts", "**/__generated__/**"),
    "minified": ("**/*.min.js", "**/*.min.mjs", "**/*.map"),
    "lockfile": ("package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb"),
}


@lru_cache(maxsize=512)
def glob_to_regex(pattern: str) -> re.Pattern[str]:
    pattern = pattern.strip().lstrip("/")
    if "/" not in pattern:
        pattern = f"**/{pattern}"
    segments = pattern.split("/")
    parts: list[str] = []
    for index, segment in enumerate(segments):
        last = index == len(segments) - 1
        if segment == "**":
            parts.append(".*" if last else "(?:[^/]+/)*")
            continue
        translated = "".join(
            "[^/]*" if char == "*" else "[^/]" if char == "?" else re.escape(char) for char in segment
        )
        parts.append(translated if last else f"{translated}/")
    return re.compile("".join(parts))


def classify(path: str, configured: Sequence[str]) -> str | None:
    """The rule that excludes ``path``, or None. Defaults are checked first, so a default rule wins a tie."""
    for rule, patterns in DEFAULT_EXCLUSIONS.items():
        if any(glob_to_regex(p).fullmatch(path) for p in patterns):
            return f"default:{rule}"
    for pattern in configured:
        if glob_to_regex(pattern).fullmatch(path):
            return f"config:{pattern}"
    return None


def in_any_rule_scope(path: str, scopes: Sequence[RuleScope]) -> bool:
    """Whether any loaded rule applies to ``path`` — the review scope FR-6.1a defines.

    ``any(include) and not any(exclude)`` **per rule**, then unioned over the rules. The exclusions must not be
    pooled: a rule that skips ``**/*.test.ts`` narrows *itself*, and must not remove test files from the scope of
    a rule written for them. AC-18's second clause exists to rule that mistake out, and so does the first test in
    ``tests/unit/changeset/test_rule_scope.py``.

    An empty ``scopes`` puts every file in scope: with no rule loaded there is no rule to fail to match, which is
    what stops an unloaded library from producing a correct-but-useless empty review.
    """
    if not scopes:
        return True
    return any(
        any(glob_to_regex(pattern).fullmatch(path) for pattern in include)
        and not any(glob_to_regex(pattern).fullmatch(path) for pattern in exclude)
        for include, exclude in scopes
    )
