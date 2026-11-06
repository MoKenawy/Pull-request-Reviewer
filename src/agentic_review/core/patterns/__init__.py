"""CF-8's rule library — the rules as **data**, and nothing that evaluates them.

This package carries path patterns; it never matches a path against one. The glob dialect lives in
``core.changeset.exclusion`` and stays there: ``core/patterns/`` and ``core/changeset/`` are sibling Layer-1
capabilities, so neither may import the other (import contract 6). A rule's declared scope therefore leaves
this package as plain builtin string tuples — ``PatternLibrary.scope_globs`` — and CF-1 does the matching
(research R-3).

The public surface is re-exported below so a caller never has to know which module a name lives in; the
quickstart's ``from agentic_review.core.patterns import load_library`` is the contract for that.
"""

from __future__ import annotations

from agentic_review.core.patterns.library import PatternLibraryError, load_library
from agentic_review.core.patterns.model import PathScope, PatternLibrary, PatternRule
from agentic_review.core.patterns.render import rules_block

__all__ = [
    "PathScope",
    "PatternLibrary",
    "PatternLibraryError",
    "PatternRule",
    "load_library",
    "rules_block",
]
