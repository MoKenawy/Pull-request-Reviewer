"""Finding fingerprint — position-independent by design (research R-23, ADR-0005).

No line, column or text goes in. Without an enclosing symbol (feature 004 adds it and moves to ``fp2``), two findings
of the same category in one file share a fingerprint. v1 does not deduplicate (FR-5.5 is v2), so that is acceptable.
"""

from __future__ import annotations

import hashlib

from agentic_review.core.findings.model import FindingDraft

ALGORITHM = "fp1"


def fingerprint(draft: FindingDraft) -> str:
    material = "\0".join((ALGORITHM, draft.file, draft.category, draft.rule_id or ""))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:12]
