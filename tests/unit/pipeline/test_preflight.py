"""Preflight for the range and pull-request scopes — FR-9.3, AC-9, FR-10.3a/d (SRS v1.5), contracts/cli.md.

The rest of preflight's contract (spec 001 tasks T079) arrives with User Story 3; this covers what the range and
pull-request scopes added.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

import pytest

from agentic_review.core.changeset.model import ChangeSet
from agentic_review.core.changeset.pull_request import PullRequestError, PullRequestRef
from agentic_review.core.config.credentials import ENV_VAR, CredentialSources, credential_sources
from agentic_review.core.pipeline.preflight import PreflightFailure, PreflightOk, preflight
from tests.support.repo_builder import RepoBuilder

PR_URL = "https://github.com/acme/widgets/pull/7"
SECRET = "sk-test-41c07fa2"


class StubOpened:
    def change_set(self, exclude: Sequence[str]) -> ChangeSet:
        raise AssertionError("preflight never resolves a change")

    def line_counts(self, change_set: ChangeSet) -> Mapping[str, int]:
        raise AssertionError("preflight never resolves a change")

    def close(self) -> None:
        pass


class StubSource:
    """Records how it was asked; never touches git or the network."""

    def __init__(self, error: str | None = None) -> None:
        self.error = error
        self.calls: list[tuple[PullRequestRef, str | None]] = []

    def open(self, pr: PullRequestRef, *, base: str | None) -> StubOpened:
        self.calls.append((pr, base))
        if self.error is not None:
            raise PullRequestError(self.error)
        return StubOpened()


@pytest.fixture
def sources(tmp_path: Path) -> CredentialSources:
    return credential_sources({ENV_VAR: SECRET, "APPDATA": str(tmp_path / "user"), "HOME": str(tmp_path / "user")})


@pytest.fixture
def no_credential(tmp_path: Path) -> CredentialSources:
    return credential_sources({"APPDATA": str(tmp_path / "user"), "XDG_CONFIG_HOME": str(tmp_path / "user")})


@pytest.fixture
def repo(tmp_path: Path) -> RepoBuilder:
    builder = RepoBuilder(tmp_path / "repo").init()
    builder.write("src/app.ts", "export const a = 1;\n").commit("initial")
    builder.checkout("feature", create=True)
    builder.write("src/app.ts", "export const a = 2;\n").commit("feature work")
    builder.checkout("main")
    return builder


def _message(result: PreflightFailure | PreflightOk) -> str:
    assert isinstance(result, PreflightFailure), result
    assert "Nothing was reviewed." in result.message
    return result.message


# --- the range scope ------------------------------------------------------------------------------------------------


def test_range_with_an_existing_base_and_head_passes(repo: RepoBuilder, sources: CredentialSources) -> None:
    result = preflight(repo.root, None, sources, scope="range", base="main", head="feature")
    assert isinstance(result, PreflightOk) and result.repo_root is not None and result.pull_request is None


def test_range_named_by_the_config_file_needs_a_base_too(repo: RepoBuilder, sources: CredentialSources) -> None:
    repo.write(".agentic-review.yml", "scope: range\n")
    assert "--base REF" in _message(preflight(repo.root, None, sources))


def test_range_without_a_base_names_the_option(repo: RepoBuilder, sources: CredentialSources) -> None:
    assert "add --base REF" in _message(preflight(repo.root, None, sources, scope="range"))


@pytest.mark.parametrize("option,arguments", [("--base", {"base": "main"}), ("--head", {"head": "feature"})])
def test_range_options_are_rejected_for_another_scope(
    repo: RepoBuilder, sources: CredentialSources, option: str, arguments: dict[str, str]
) -> None:
    message = _message(preflight(repo.root, None, sources, **arguments))
    assert message.startswith(f"{option} is only used with the range scope") and "working-tree" in message


def test_an_unknown_base_names_the_ref(repo: RepoBuilder, sources: CredentialSources) -> None:
    message = _message(preflight(repo.root, None, sources, scope="range", base="nope"))
    assert "The range base 'nope' does not exist" in message


def test_an_unknown_head_names_the_ref(repo: RepoBuilder, sources: CredentialSources) -> None:
    message = _message(preflight(repo.root, None, sources, scope="range", base="main", head="ghost"))
    assert "The range head 'ghost' does not exist" in message


def test_a_ref_that_looks_like_an_option_is_not_a_ref(repo: RepoBuilder, sources: CredentialSources) -> None:
    message = _message(preflight(repo.root, None, sources, scope="range", base="--output=/tmp/x"))
    assert "does not exist" in message


def test_refs_with_no_common_history_cannot_be_compared(repo: RepoBuilder, sources: CredentialSources) -> None:
    repo.git("checkout", "-q", "--orphan", "island")
    repo.write("src/island.ts", "export const i = 1;\n").commit("unrelated root")
    message = _message(preflight(repo.root, None, sources, scope="range", base="main", head="island"))
    assert "share no history" in message


def test_range_in_a_repository_with_no_commits_is_refused(tmp_path: Path, sources: CredentialSources) -> None:
    empty = RepoBuilder(tmp_path / "empty").init()
    message = _message(preflight(empty.root, None, sources, scope="range", base="main"))
    assert "The range base 'main' does not exist" in message


def test_range_from_a_branch_with_no_commits_is_refused(repo: RepoBuilder, sources: CredentialSources) -> None:
    repo.git("checkout", "-q", "--orphan", "blank")
    message = _message(preflight(repo.root, None, sources, scope="range", base="main"))
    assert "has no commits yet" in message


def test_the_credential_is_checked_before_any_ref(repo: RepoBuilder, no_credential: CredentialSources) -> None:
    message = _message(preflight(repo.root, None, no_credential, scope="range", base="nope"))
    assert ENV_VAR in message and "nope" not in message


# --- the pull-request scope -----------------------------------------------------------------------------------------


def test_a_pull_request_needs_no_repository(tmp_path: Path, sources: CredentialSources) -> None:
    source = StubSource()
    result = preflight(tmp_path, None, sources, pr=PR_URL, pull_requests=source)
    assert isinstance(result, PreflightOk)
    assert result.repo_root is None and result.pull_request is not None
    assert source.calls == [(PullRequestRef("acme", "widgets", 7), None)]


def test_the_base_branch_is_passed_to_the_source(tmp_path: Path, sources: CredentialSources) -> None:
    source = StubSource()
    preflight(tmp_path, None, sources, pr=PR_URL, base="release", pull_requests=source)
    assert source.calls == [(PullRequestRef("acme", "widgets", 7), "release")]


def test_a_malformed_url_is_named_before_anything_is_fetched(tmp_path: Path, sources: CredentialSources) -> None:
    source = StubSource()
    message = _message(preflight(tmp_path, None, sources, pr="acme/widgets#7", pull_requests=source))
    assert "'acme/widgets#7' is not a GitHub pull request URL" in message
    assert "https://github.com/<owner>/<repo>/pull/<number>" in message
    assert source.calls == []


@pytest.mark.parametrize("option,arguments", [("--scope", {"scope": "range"}), ("--head", {"head": "feature"})])
def test_options_that_contradict_a_pull_request_are_rejected(
    tmp_path: Path, sources: CredentialSources, option: str, arguments: dict[str, str]
) -> None:
    source = StubSource()
    message = _message(preflight(tmp_path, None, sources, pr=PR_URL, pull_requests=source, **arguments))
    assert option in message and "--pr" in message
    assert source.calls == []


def test_a_missing_credential_never_costs_a_fetch(tmp_path: Path, no_credential: CredentialSources) -> None:
    source = StubSource()
    message = _message(preflight(tmp_path, None, no_credential, pr=PR_URL, pull_requests=source))
    assert ENV_VAR in message
    assert source.calls == []


def test_a_pull_request_that_cannot_be_read_is_a_preflight_failure(tmp_path: Path, sources: CredentialSources) -> None:
    source = StubSource(error=f"Pull request #7 was not found, said a remote echoing {SECRET}.\nNothing was reviewed.")
    message = _message(preflight(tmp_path, None, sources, pr=PR_URL, pull_requests=source))
    assert "Pull request #7 was not found" in message
    assert SECRET not in message  # redacted like every other preflight message


def test_configuration_is_never_read_from_the_working_directory_for_a_pull_request(
    repo: RepoBuilder, sources: CredentialSources
) -> None:
    # Run from inside an unrelated repository whose own file is invalid: it is not this review's configuration.
    repo.write(".agentic-review.yml", "agent:\n  toolCallCeling: 5\n")
    result = preflight(repo.root, None, sources, pr=PR_URL, pull_requests=StubSource())
    assert isinstance(result, PreflightOk)
    assert result.loaded.settings.agent.tool_call_ceiling == 25 and not result.loaded.scope_from_file


def test_an_explicit_config_file_is_used_for_a_pull_request(tmp_path: Path, sources: CredentialSources) -> None:
    config = tmp_path / "mine.yml"
    config.write_text("agent:\n  toolCallCeiling: 3\n", encoding="utf-8")
    result = preflight(tmp_path, config, sources, pr=PR_URL, pull_requests=StubSource())
    assert isinstance(result, PreflightOk) and result.loaded.settings.agent.tool_call_ceiling == 3

    config.write_text("agent:\n  toolCallCeling: 3\n", encoding="utf-8")
    source = StubSource()
    message = _message(preflight(tmp_path, config, sources, pr=PR_URL, pull_requests=source))
    assert "agent.toolCallCeling" in message and source.calls == []
