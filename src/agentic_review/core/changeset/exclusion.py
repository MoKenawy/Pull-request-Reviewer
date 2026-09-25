"""Exclusion globs over repo-relative POSIX paths (FR-3.5, research R-6).

``**`` matches zero or more whole segments; ``*`` and ``?`` stay within one segment; a pattern with no ``/`` matches at
any depth (the gitignore convention). Configured patterns are always added to the defaults, never substituted for them.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from functools import lru_cache

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
