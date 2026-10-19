"""Turning a provider failure into a degradation (FR-11.2, research R-9, R-10).

Every failure the provider client can raise — connection, timeout, a 4xx refusal, a 429 that survived its retry, a
5xx, a raw ``httpx`` error — and a reply stopped with ``finish_reason == "content_filter"`` becomes one
``provider-error`` degradation (source ``CF-6``). The review step never raises for these (data-model §5).

A provider's message can echo request details, so a detail is always passed through ``redact`` before it is stored,
and is cut short: it is for a person to read, not a log to replay.
"""

from __future__ import annotations

import httpx
import openai

from agentic_review.core.config.redact import redact
from agentic_review.core.findings.report import Degradation

PROVIDER_ERRORS: tuple[type[BaseException], ...] = (openai.APIError, httpx.HTTPError)
"""What ``call_model`` catches. ``openai.APIError`` covers every status, connection and timeout error of the client."""

_SOURCE = "CF-6"
_CODE = "provider-error"
_MESSAGE_LIMIT = 300


def to_degradation(exc: BaseException, secret: str | None) -> Degradation:
    kind = type(exc).__name__
    status = getattr(exc, "status_code", None)
    label = f"{kind}, HTTP {status}" if status is not None else kind
    # Redacted before it is cut short: a cut through the middle of the secret would leave a prefix no redaction finds.
    message = redact(" ".join(str(exc).split()), secret)
    if len(message) > _MESSAGE_LIMIT:
        message = message[:_MESSAGE_LIMIT] + "…"
    detail = f"The provider request failed ({label}): {message or 'no message'}. No reply was received for this turn."
    return Degradation(source=_SOURCE, code=_CODE, detail=detail)


def content_filter_degradation() -> Degradation:
    detail = (
        "The provider stopped the reply with finish_reason 'content_filter'; the reply was discarded unprocessed, "
        "so any finding in it was not recorded."
    )
    return Degradation(source=_SOURCE, code=_CODE, detail=detail)


def rate_limit_degradation(wait_seconds: float, *, gave_up: bool) -> Degradation:
    """Never carries the provider's own message: it can echo request details we must not repeat (research R-9)."""
    if gave_up:
        detail = (
            f"The provider returned 429 (rate limited) twice for one turn, {wait_seconds:g}s apart; that turn was "
            "abandoned without a reply. Earlier turns' findings, if any, stand."
        )
    else:
        detail = f"The provider returned 429 (rate limited); retrying after {wait_seconds:g}s succeeded."
    return Degradation(source=_SOURCE, code=_CODE, detail=detail)
