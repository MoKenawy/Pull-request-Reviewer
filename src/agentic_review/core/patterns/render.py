"""Rendering the library into the prompt's static prefix (FR-006, FR-007, FR-008, contracts/rules-file.md §4).

Three properties are contractual: each identifier appears **verbatim**, because the model is asked to cite it;
each rule's declared scope appears **with** that rule, so the model can tell which files it covers; and the block
is **byte-identical** for a given library across different change sets, which is what makes it part of a static
prefix at all. Everything else about the wording is free to change — changing it is how prompt quality gets
improved once feature 007 can measure whether it did (plan 003/D-8).

What this module does *not* do is tell the model how to use the rules. That sentence belongs in the instructions
(``core.assembly.prompt``), so it exists once rather than twice.
"""

from __future__ import annotations

from agentic_review.core.patterns.model import PatternLibrary, PatternRule

RULES_HEADING = "## Review rules"
"""The block's first line. Part of the system message, never the user message (research R-2)."""


def rules_block(library: PatternLibrary) -> str:
    """The whole library as text, ordered by identifier. Empty string for an empty library — no bare heading."""
    if not library.rules:
        return ""
    sections = [RULES_HEADING, *(_rule(rule) for rule in library.rules)]
    return "\n\n".join(sections)


def _rule(rule: PatternRule) -> str:
    lines = [
        f"### {rule.id}",
        rule.title,
        f"Category: {rule.category} · default severity: {rule.default_severity}",
        f"Applies to: {_scope(rule)}",
        "",
        "Wrong:",
        _fenced(rule.wrong),
        "Correct:",
        _fenced(rule.correct),
    ]
    return "\n".join(lines).rstrip()


def _scope(rule: PatternRule) -> str:
    include = ", ".join(rule.applies_when.include)
    if not rule.applies_when.exclude:
        return include
    return f"{include} — except {', '.join(rule.applies_when.exclude)}"


def _fenced(example: str) -> str:
    return f"```ts\n{example.strip()}\n```"
