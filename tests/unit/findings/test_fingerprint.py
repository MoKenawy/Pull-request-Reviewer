"""Position-independent finding identity — research R-23, ADR-0005."""

from __future__ import annotations

import hashlib
import re

from agentic_review.core.findings.fingerprint import fingerprint
from agentic_review.core.findings.model import FindingDraft
from tests.support.scripted_chat_model import finding_args


def _draft(**fields: object) -> FindingDraft:
    return FindingDraft.model_validate(finding_args(**fields))


def test_format_and_formula() -> None:
    value = fingerprint(_draft())
    assert re.fullmatch(r"[0-9a-f]{12}", value)
    expected = hashlib.sha256("fp1\0src/app.ts\0correctness\0".encode()).hexdigest()[:12]
    assert value == expected


def test_independent_of_position_severity_and_text() -> None:
    base = fingerprint(_draft())
    assert fingerprint(_draft(startLine=7, endLine=9, severity="nit", rationale="Different words.")) == base


def test_changes_with_file_category_and_rule() -> None:
    base = fingerprint(_draft())
    assert fingerprint(_draft(file="src/util.js")) != base
    assert fingerprint(_draft(category="security")) != base
    assert fingerprint(_draft(ruleId="R-001")) != base
