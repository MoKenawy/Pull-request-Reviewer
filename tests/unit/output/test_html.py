"""The HTML report from one report — FR-10.4d, FR-10.4a, research R-16, contracts/cli.md "render"."""

from __future__ import annotations

from typing import Any

import pytest
from jinja2 import UndefinedError, StrictUndefined

from agentic_review.core.findings.report import ReviewReport, Verdict
from agentic_review.core.output import html as html_module
from agentic_review.core.output.html import render_html
from agentic_review.core.output.view import NO_TOOL_CALL_LINE, VERDICT_SENTENCES, run_rows
from tests.support.report_factory import report

# Words a zero-finding run must never be described with (research R-16, gap D-5). A review that found nothing is
# not a review that found nothing wrong, and the HTML is the surface most likely to be read as a verdict on quality.
FORBIDDEN_REASSURANCE = ("passed", "clean", "no issues", "looks good", "all clear", "success")


def _run(**overrides: Any) -> dict[str, Any]:
    """The factory report's run metadata as a wire document, with keys replaced."""
    return {**report().run.model_dump(by_alias=True), **overrides}


def test_the_document_is_one_self_contained_html_file() -> None:
    document = render_html(report())
    assert document.startswith("<!DOCTYPE html>")
    assert document.endswith("\n") and not document.endswith("\n\n")
    assert '<html lang="en">' in document
    assert document.count("<style>") == 1
    assert "<script" not in document
    assert "http://" not in document and "https://" not in document
    assert "@import" not in document


def test_required_sections_in_order() -> None:
    document = render_html(report())
    ordered = [
        "uncommitted changes in the working tree (default)",
        VERDICT_SENTENCES["findings"],
        "0 blocking / 1 important / 1 nit",
        "Degradations",
        'id="f-1"',
        'id="f-2"',
        "Change summary",
        "dist/index.js",
        "Run metadata",
    ]
    positions = [document.index(fragment) for fragment in ordered]
    assert positions == sorted(positions), document


def test_every_finding_field_is_shown() -> None:
    document = render_html(report())
    for fragment in (
        "src/app.ts:4-7", "important", "error-handling", "The [catch] block swallows the error.", "diff hunk 0",
        "src/app.ts:9", "nit", "maintainability", "unverified: style judgement",
    ):
        assert fragment in document, fragment


def test_the_same_strings_as_the_terminal_describe_checks_and_context() -> None:
    document = render_html(report())
    assert "No checks were run in this build." in document
    assert "No related context was gathered in this build." in document


def test_findings_are_anchored_by_id_and_never_by_fingerprint() -> None:
    document = render_html(report())
    assert 'id="f-1"' in document and 'id="f-2"' in document
    assert 'id="aaaaaaaaaaaa"' not in document and 'id="bbbbbbbbbbbb"' not in document


def test_two_findings_sharing_a_fingerprint_still_get_distinct_anchors() -> None:
    # The fingerprint is sha256("fp1\0file\0category\0rule_id")[:12], so two same-category findings in one file
    # collide, and v1 does not deduplicate. An anchor built from it would be a duplicate id.
    findings = [dict(f) for f in report().model_dump(by_alias=True)["findings"]]
    for finding in findings:
        finding["fingerprint"] = "c" * 12
        finding["category"] = "maintainability"
    document = render_html(report(findings=findings))
    assert 'id="f-1"' in document and 'id="f-2"' in document
    assert document.count('id="c' + "c" * 11 + '"') == 0


def test_model_authored_prose_is_escaped_and_never_executed() -> None:
    findings = [dict(f) for f in report().model_dump(by_alias=True)["findings"]]
    findings[0]["rationale"] = "<script>alert(1)</script>"
    document = render_html(
        report(
            findings=findings,
            degradations=[{"source": "CF-6", "code": "provider-error", "detail": '" onerror="alert(1)'}],
            verdict="no-judgement",
            run=_run(completionStatus="provider-error"),
        )
    )
    assert "<script" not in document
    assert "&lt;script&gt;" in document
    assert 'onerror="alert' not in document


def test_a_hostile_file_path_cannot_escape_an_attribute() -> None:
    findings = [dict(f) for f in report().model_dump(by_alias=True)["findings"]]
    findings[0]["file"] = 'src/a".ts'
    findings[0]["evidence"] = {"kind": "diff", "file": 'src/a".ts', "hunkIndex": 0}
    summary = report().change_summary.model_dump(by_alias=True)
    summary["files"][0]["path"] = 'src/a".ts'
    summary["scope"]["description"] = 'working tree "><img src=x>'
    document = render_html(report(findings=findings, changeSummary=summary))
    assert "<img" not in document
    assert "&#34;" in document
    assert document.count("<style>") == 1 and "<script" not in document


def test_a_no_tool_call_run_is_never_shown_as_clean() -> None:
    document = render_html(
        report(
            findings=[],
            degradations=[{"source": "CF-6", "code": "no-tool-call", "detail": "the model replied with prose"}],
            verdict="no-findings",
            run=_run(completionStatus="no-tool-call", toolCallsTotal=0, toolCallsEmission=0),
        )
    )
    assert NO_TOOL_CALL_LINE in document
    lowered = document.lower()
    for word in FORBIDDEN_REASSURANCE:
        assert word not in lowered, word


def test_no_run_is_ever_described_with_reassuring_words() -> None:
    lowered = render_html(report()).lower()
    for word in FORBIDDEN_REASSURANCE:
        assert word not in lowered, word


@pytest.mark.parametrize("verdict", ["findings", "blocking", "no-findings", "no-judgement", "nothing-to-review"])
def test_each_verdict_gets_its_own_sentence(verdict: Verdict) -> None:
    document = render_html(report(verdict=verdict))
    assert VERDICT_SENTENCES[verdict] in document
    for other, sentence in VERDICT_SENTENCES.items():
        if other != verdict:
            assert sentence not in document, other


def test_no_judgement_says_no_review_was_performed_and_never_no_findings() -> None:
    document = render_html(
        report(
            findings=[],
            degradations=[{"source": "CF-6", "code": "provider-error", "detail": "connection refused"}],
            verdict="no-judgement",
            run=_run(completionStatus="provider-error"),
        )
    )
    assert "No review was performed" in document
    assert "no findings" not in document.lower()


def test_degradations_are_listed_with_source_code_and_detail() -> None:
    document = render_html(
        report(
            findings=[],
            degradations=[{"source": "CF-6", "code": "provider-error", "detail": "connection refused"}],
            verdict="no-judgement",
            run=_run(completionStatus="provider-error"),
        )
    )
    assert "CF-6" in document and "provider-error" in document and "connection refused" in document


def test_an_empty_degradation_list_says_so_without_claiming_anything_about_quality() -> None:
    document = render_html(report())
    assert "No degradation was recorded." in document


def test_absent_stage_durations_are_omitted_rather_than_rendered_as_none() -> None:
    document = render_html(
        report(
            findings=[],
            verdict="nothing-to-review",
            run=_run(
                completionStatus="nothing-to-review",
                stageDurationsMs={"preflight": 1, "changeSet": 2, "output": 3},
            ),
        )
    )
    assert "None" not in document
    assert "assembly" not in document and ">review<" not in document


def test_all_exclusions_are_listed_even_past_the_terminal_cut_off() -> None:
    # The deliberate inverse of test_render.py::test_many_exclusions_collapse_to_a_count. A terminal has a height;
    # a document does not, and a collapsed HTML report would be strictly worse than the JSON it makes readable.
    summary = report().change_summary.model_dump(by_alias=True)
    summary["excluded"] = [{"path": f"dist/{i}.js", "rule": "default:build-output"} for i in range(11)]
    document = render_html(report(changeSummary=summary))
    assert "dist/10.js" in document
    assert "paths excluded;" not in document


def test_run_metadata_is_shown_from_the_allow_list() -> None:
    document = render_html(report())
    for label, value in run_rows(report().run):
        assert label in document, label
        assert value in document, value


def test_absent_optional_run_fields_are_worded_rather_than_blank() -> None:
    document = render_html(report())
    assert "not reported" in document  # tokens in/out and the seed
    assert "not gathered in this build" in document  # context depth


def test_the_title_can_be_given_and_otherwise_names_the_scope() -> None:
    assert "Code review" in render_html(report())
    assert "Release 4.2 review" in render_html(report(), title="Release 4.2 review")


def test_the_same_report_renders_identically_twice() -> None:
    # Nothing in the renderer may read the clock, the environment, the cwd or any file but its template: that is
    # what lets `render` reproduce byte-for-byte what `review --html` wrote.
    assert render_html(report()) == render_html(report())


def test_the_footer_says_the_json_report_is_authoritative() -> None:
    assert "the JSON report is authoritative" in render_html(report())


def test_the_environment_escapes_by_default_and_is_strict_about_unknown_names() -> None:
    environment = html_module._environment()
    assert environment.autoescape is True
    assert environment.undefined is StrictUndefined
    with pytest.raises(UndefinedError):
        environment.from_string("{{ nope }}").render()


def test_a_report_with_no_findings_and_no_degradations_still_renders() -> None:
    document = render_html(report(findings=[], verdict="no-findings"))
    assert isinstance(document, str) and document.startswith("<!DOCTYPE html>")
    assert VERDICT_SENTENCES["no-findings"] in document


def test_the_renderer_accepts_any_report_the_factory_can_build() -> None:
    assert isinstance(render_html(ReviewReport.model_validate(report().model_dump(by_alias=True))), str)
