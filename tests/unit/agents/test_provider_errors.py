"""Provider failures come back inside the outcome — FR-11.2 (spec 001 FR-020); research R-9, R-10, R-17."""

from __future__ import annotations

from dataclasses import replace

import httpx
import openai
import pytest

from agentic_review.core.findings.port import ReviewedFile, RunMaterial
from tests.conftest import CANARY_KEY
from tests.unit.agents.conftest import CONTEXT, PortFactory
from tests.support.report_assertions import assert_no_canary
from tests.support.scripted_chat_model import ai_reply, finding_call

_REQUEST = httpx.Request("POST", "https://example.invalid/v1/chat/completions")
_LEAKY = f"request with Authorization: Bearer {CANARY_KEY} failed"


def _status(code: int) -> openai.APIStatusError:
    response = httpx.Response(status_code=code, request=_REQUEST)
    return openai.APIStatusError(_LEAKY, response=response, body=None)


def _rate_limited() -> openai.RateLimitError:
    return openai.RateLimitError(_LEAKY, response=httpx.Response(status_code=429, request=_REQUEST), body=None)


FAILURES = {
    "connection": lambda: [openai.APIConnectionError(message=_LEAKY, request=_REQUEST)],
    "timeout": lambda: [openai.APITimeoutError(request=_REQUEST)],
    "4xx-refusal": lambda: [_status(403)],
    "5xx": lambda: [_status(503)],
    "429-after-retry": lambda: [_rate_limited(), _rate_limited()],
    "httpx": lambda: [httpx.ConnectError(_LEAKY, request=_REQUEST)],
    "content-filter": lambda: [ai_reply([finding_call()], finish_reason="content_filter")],
}


@pytest.mark.parametrize("failure", FAILURES, ids=list(FAILURES))
def test_each_provider_failure_is_a_provider_error(make_port: PortFactory, failure: str) -> None:
    port, _ = make_port(FAILURES[failure](), rateLimitRetrySeconds=0)
    outcome = port.review(CONTEXT)  # never raises

    assert outcome.findings == ()
    assert outcome.completion_status == "provider-error"
    assert outcome.degradations[-1].source == "CF-6" and outcome.degradations[-1].code == "provider-error"
    assert {d.code for d in outcome.degradations} == {"provider-error"}
    assert_no_canary(*(d.detail for d in outcome.degradations))
    assert outcome.tool_calls_total == 0


def test_a_status_error_names_its_status_code(make_port: PortFactory) -> None:
    port, _ = make_port([_status(404)])
    outcome = port.review(CONTEXT)
    assert "404" in outcome.degradations[0].detail


def test_a_content_filtered_reply_is_not_processed(make_port: PortFactory) -> None:
    port, _ = make_port([ai_reply([finding_call()], finish_reason="content_filter")])
    outcome = port.review(CONTEXT)
    assert "content_filter" in outcome.degradations[0].detail
    assert outcome.findings == ()


def test_provider_error_in_the_repair_turn_keeps_accepted_findings(make_port: PortFactory) -> None:
    first = [finding_call(), finding_call(startLine=99, endLine=99)]
    port, model = make_port([ai_reply(first), openai.APIConnectionError(message=_LEAKY, request=_REQUEST)])
    outcome = port.review(CONTEXT)

    assert model.call_count == 2
    assert [f.id for f in outcome.findings] == ["f-1"]
    assert outcome.completion_status == "emitted"
    assert {d.code for d in outcome.degradations} == {"provider-error", "invalid-model-output"}
    assert_no_canary(*(d.detail for d in outcome.degradations))


def test_provider_error_in_a_coverage_repair_keeps_accepted_findings(make_port: PortFactory) -> None:
    two_files = replace(
        CONTEXT,
        material=RunMaterial(
            reviewed_files={
                "src/app.ts": ReviewedFile(line_count=40, hunk_count=2),
                "src/other.ts": ReviewedFile(line_count=10, hunk_count=1),
            }
        ),
    )
    port, _ = make_port([ai_reply([finding_call()]), openai.APITimeoutError(request=_REQUEST)])
    outcome = port.review(two_files)

    assert outcome.completion_status == "emitted"
    assert {d.code for d in outcome.degradations} == {"provider-error", "incomplete-file-coverage"}
