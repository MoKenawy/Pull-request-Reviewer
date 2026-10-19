"""Preflight: everything that can stop a run is checked before any change is resolved or any model is called.

Checks run in the order of contracts/cli.md "Preflight messages" and stop at the first failure (FR-9.3 — partial:
the test-script prerequisite arrives in feature 002 — AC-9).

| # | Check | For a pull request (``--pr``) |
|---|---|---|
| 1 | Inside a git repository | The URL is a GitHub pull request URL — no repository is needed |
| 2 | Configuration valid | Only ``--config`` or the defaults: never a file from the pull request (FR-10.3d) |
| 3 | Scope arguments coherent | ``--pr`` excludes ``--scope`` and ``--head`` |
| 4 | Credential available | The same |
| 5 | Named refs exist | The pull request is opened — the only step that uses the network, and so the last |

The ``staged`` scope and its checks arrive with User Story 4.

Check 4 establishes that a credential **can** be found; it does not hand the credential on. ``PreflightOk`` becomes
pipeline state, and pipeline state is what every tracer attached to the graph receives and ships, so the value is
looked up again by the one step that gives it to the model client.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agentic_review.core.changeset.pull_request import (
    OpenedPullRequest,
    PullRequestError,
    PullRequestSource,
    parse_pull_request_url,
)
from agentic_review.core.changeset.resolve import GitNotFound, have_merge_base, locate_repository, ref_exists
from agentic_review.core.config.credentials import CredentialProblem, CredentialSources, find_credential
from agentic_review.core.config.loader import ConfigError, LoadedSettings, load_settings
from agentic_review.core.config.redact import redact
from agentic_review.core.config.settings import Settings

CONFIG_FILE_NAME = ".agentic-review.yml"
_FOOTER = "Nothing was reviewed."


@dataclass(frozen=True)
class PreflightFailure:
    message: str
    """Already redacted. The CLI prints it to stderr."""


@dataclass(frozen=True)
class PreflightOk:
    repo_root: Path | None
    """None when the change comes from a pull request: there is no repository on this machine."""
    loaded: LoadedSettings
    """No credential here, deliberately: see the module docstring."""
    pull_request: OpenedPullRequest | None = None
    """Opened by check 5. Whoever holds this must ``close`` it when the run is over."""


def _scope_arguments_problem(kind: str, base: str | None, head: str | None) -> str | None:
    if kind == "range":
        if base is None:
            return f"The range scope needs a base to compare with: add --base REF.\n{_FOOTER}"
        return None
    if base is not None:
        return f"--base is only used with the range scope or with --pr; the scope here is {kind}.\n{_FOOTER}"
    if head is not None:
        return f"--head is only used with the range scope; the scope here is {kind}.\n{_FOOTER}"
    return None


def _range_refs_problem(repo_root: Path, base: str, head: str | None) -> str | None:
    hint = "Name an existing branch, tag or commit."
    if not ref_exists(repo_root, base):
        return f"The range base {base!r} does not exist in {repo_root}.\n{_FOOTER} {hint}"
    if head is None:
        if not ref_exists(repo_root, "HEAD"):
            return f"{repo_root} has no commits yet, so there is no range to review.\n{_FOOTER}"
    elif not ref_exists(repo_root, head):
        return f"The range head {head!r} does not exist in {repo_root}.\n{_FOOTER} {hint}"
    if not have_merge_base(repo_root, base, head or "HEAD"):
        return f"{base!r} and {head or 'HEAD'!r} share no history, so there is no range to review.\n{_FOOTER}"
    return None


def preflight(
    cwd: Path,
    config_path: Path | None,
    sources: CredentialSources,
    *,
    scope: str | None = None,
    base: str | None = None,
    head: str | None = None,
    pr: str | None = None,
    pull_requests: PullRequestSource | None = None,
) -> PreflightFailure | PreflightOk:
    secret = sources.from_env.reveal() if sources.from_env is not None else None

    def fail(message: str) -> PreflightFailure:
        return PreflightFailure(redact(message, secret))

    # 1 · a repository, or a pull request URL
    pull_request_ref = None
    repo_root: Path | None = None
    if pr is not None:
        pull_request_ref = parse_pull_request_url(pr)
        if pull_request_ref is None:
            return fail(
                f"--pr: {pr!r} is not a GitHub pull request URL.\n"
                f"Expected https://github.com/<owner>/<repo>/pull/<number>.\n{_FOOTER}"
            )
    else:
        try:
            repo_root = locate_repository(cwd)
        except GitNotFound:
            return fail(f"git was not found on PATH, so no repository could be located.\n{_FOOTER}")
        if repo_root is None:
            return fail(
                f"{cwd} is not inside a git repository.\n"
                f"{_FOOTER} Run the review from inside the repository you want reviewed."
            )

    # 2 · configuration — never read from a pull request, whose author could redirect the provider URL (FR-10.3d)
    try:
        if config_path is not None:
            loaded = load_settings(config_path, explicit=True, display_name=str(config_path))
        elif repo_root is not None:
            loaded = load_settings(repo_root / CONFIG_FILE_NAME, explicit=False, display_name=CONFIG_FILE_NAME)
        else:
            loaded = LoadedSettings(Settings(), (), scope_from_file=False)
    except ConfigError as error:
        return fail(error.message)

    # 3 · scope arguments coherent
    kind = "pull-request"
    if pull_request_ref is not None:
        if scope is not None:
            return fail(f"--pr selects the pull-request scope by itself; remove --scope.\n{_FOOTER}")
        if head is not None:
            return fail(f"--head cannot be used with --pr: the head is the pull request itself.\n{_FOOTER}")
    else:
        kind = scope or loaded.settings.scope
        problem = _scope_arguments_problem(kind, base, head)
        if problem is not None:
            return fail(problem)

    # 4 · credential
    credential = find_credential(sources, repo_root)
    if isinstance(credential, CredentialProblem):
        return fail(credential.message)

    # 5 · named refs exist — for a pull request, the only step that reaches the network
    if pull_request_ref is not None:
        if pull_requests is None:
            return fail(f"No pull-request source is configured, so {pull_request_ref.url} cannot be read.\n{_FOOTER}")
        try:
            opened = pull_requests.open(pull_request_ref, base=base)
        except PullRequestError as error:
            return fail(error.message)
        return PreflightOk(repo_root=None, loaded=loaded, pull_request=opened)

    assert repo_root is not None
    if kind == "range":
        assert base is not None
        problem = _range_refs_problem(repo_root, base, head)
        if problem is not None:
            return fail(problem)

    return PreflightOk(repo_root=repo_root, loaded=loaded)
