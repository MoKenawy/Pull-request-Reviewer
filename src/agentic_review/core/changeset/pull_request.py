"""Reading a public GitHub pull request into a ``ChangeSet`` (FR-10.3a as amended in SRS v1.5, FR-10.3d, ADR-0011).

Everything pull-request-specific sits behind ``PullRequestSource``. The pipeline, preflight and the CLI see only that
protocol and the ``ChangeSet`` it produces (FR-10.3c).

**``GitPullRequestSource`` is interim.** It reads the pull request with plain git — a blobless, no-checkout clone,
the ``refs/pull/<n>/head`` ref, then ``diff_branches`` — so that the scope works today with no GitHub API, no token
and no new dependency. It is meant to be replaced by a source backed by the official GitHub MCP server
(``github/github-mcp-server``), as a second implementation of the same protocol rather than a rewrite. That source
will need a GitHub token and an MCP client, so it will live outside ``core/`` (FR-5.8) and take its own ADR
(research R-25). Keep this module thin: nothing here should grow features the MCP server already provides.

Nothing from the pull request is executed and no configuration is read from it (FR-10.3d): the clone has no
working tree, so there are no files to run, no hooks and no install step.
"""

from __future__ import annotations

import os
import re
import shutil
import stat
import tempfile
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from agentic_review.core.changeset._git import GitError, GitNotFound, run_git
from agentic_review.core.changeset.model import ChangeSet
from agentic_review.core.changeset.resolve import diff_branches, have_merge_base, ref_exists
from agentic_review.core.changeset.summary import measure_new_files
from agentic_review.core.findings.report import ResolvedScope

# PLACEHOLDER - unmeasured. It bounds one clone or fetch, so a stalled network cannot hang a run.
FETCH_TIMEOUT_SECONDS = 300
WORKSPACE_PREFIX = "agentic-review-pr-"

_FOOTER = "Nothing was reviewed."
_PULL_REQUEST_URL = re.compile(
    r"^https://github\.com/"
    r"(?P<owner>[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)/"
    r"(?P<repo>[A-Za-z0-9._-]+)/"
    r"pull/(?P<number>[1-9][0-9]*)"
    r"(?:[/?#].*)?$"
)
# No credential helper and no askpass program: a public pull request needs neither, and a repository that is private
# or missing must fail rather than open a login prompt.
_NO_CREDENTIALS = ("-c", "credential.helper=", "-c", "core.askPass=")


@dataclass(frozen=True)
class PullRequestRef:
    owner: str
    repo: str
    number: int

    @property
    def slug(self) -> str:
        return f"{self.owner}/{self.repo}#{self.number}"

    @property
    def url(self) -> str:
        return f"https://github.com/{self.owner}/{self.repo}/pull/{self.number}"

    @property
    def head_ref(self) -> str:
        """The ref GitHub publishes for a pull request's head — also when the head branch lives in a fork."""
        return f"refs/pull/{self.number}/head"


def parse_pull_request_url(url: str) -> PullRequestRef | None:
    """``https://github.com/<owner>/<repo>/pull/<number>``, with anything GitHub appends after it; else None."""
    match = _PULL_REQUEST_URL.match(url.strip())
    if match is None or match["repo"] in (".", ".."):
        return None
    return PullRequestRef(match["owner"], match["repo"], int(match["number"]))


def github_clone_url(pr: PullRequestRef) -> str:
    return f"https://github.com/{pr.owner}/{pr.repo}.git"


class PullRequestError(Exception):
    """The pull request could not be read. ``message`` is ready for the user and says nothing was reviewed."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class OpenedPullRequest(Protocol):
    """A pull request that exists and can be read. ``close`` must be called once the run is over."""

    def change_set(self, exclude: Sequence[str]) -> ChangeSet: ...

    def line_counts(self, change_set: ChangeSet) -> Mapping[str, int]:
        """Line counts of the reviewable files as they are at the pull request's head."""
        ...

    def close(self) -> None: ...


class PullRequestSource(Protocol):
    def open(self, pr: PullRequestRef, *, base: str | None) -> OpenedPullRequest:
        """Reach the pull request, or raise ``PullRequestError``. ``base`` None means the default branch."""
        ...


def clone_arguments(clone_url: str, destination: Path) -> tuple[str, ...]:
    """History and trees only (``--filter=blob:none``), and no working tree (``--no-checkout``)."""
    return (
        *_NO_CREDENTIALS,
        "clone",
        "--quiet",
        "--filter=blob:none",
        "--no-checkout",
        "--",
        clone_url,
        str(destination),
    )


def discard_workspace(path: Path) -> None:
    """Remove a temporary clone. git marks pack files read-only, which Windows refuses to delete as they are."""

    def make_writable_and_retry(function: Callable[..., Any], target: str, _error: BaseException) -> None:
        os.chmod(target, stat.S_IWRITE)
        function(target)

    try:
        shutil.rmtree(path, onexc=make_writable_and_retry)
    except OSError:
        pass  # a leftover temporary directory must never fail a review


def _network_environment() -> dict[str, str]:
    env = {name: value for name, value in os.environ.items() if name not in ("GIT_ASKPASS", "SSH_ASKPASS")}
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GCM_INTERACTIVE"] = "never"
    return env


def _reason(error: GitError) -> str:
    lines = [line.strip() for line in error.stderr.splitlines() if line.strip()]
    return lines[-1] if lines else f"git exited {error.returncode}"


@dataclass(frozen=True)
class _ClonedPullRequest:
    pr: PullRequestRef
    workspace: Path
    repo_root: Path
    base_name: str
    base_rev: str
    base_was_default: bool

    def change_set(self, exclude: Sequence[str]) -> ChangeSet:
        diff = diff_branches(self.repo_root, self.base_rev, self.pr.head_ref, exclude)
        count = len(diff.files)
        description = (
            f"pull request {self.pr.slug} against {self.base_name}"
            f"{', the default branch' if self.base_was_default else ''} ({diff.commits})"
            f" · {count} file{'' if count == 1 else 's'}"
        )
        return ChangeSet(
            repo_root=self.repo_root,
            scope=ResolvedScope(
                kind="pull-request",
                base_ref=self.base_name,
                head_ref=self.pr.head_ref,
                was_defaulted=False,
                description=description,
            ),
            files=diff.files,
            excluded=diff.excluded,
        )

    def line_counts(self, change_set: ChangeSet) -> Mapping[str, int]:
        return measure_new_files(change_set)

    def close(self) -> None:
        discard_workspace(self.workspace)


class GitPullRequestSource:
    """The interim source: git transport only. See the module docstring for what replaces it."""

    def __init__(self, clone_url: Callable[[PullRequestRef], str] = github_clone_url) -> None:
        self._clone_url = clone_url

    def open(self, pr: PullRequestRef, *, base: str | None) -> OpenedPullRequest:
        workspace = Path(tempfile.mkdtemp(prefix=WORKSPACE_PREFIX))
        try:
            return self._open(pr, base, workspace)
        except BaseException:
            discard_workspace(workspace)
            raise

    def _open(self, pr: PullRequestRef, base: str | None, workspace: Path) -> _ClonedPullRequest:
        clone_url = self._clone_url(pr)
        repo_root = workspace / "repo"
        env = _network_environment()
        try:
            run_git(workspace, *clone_arguments(clone_url, repo_root), env=env, timeout=FETCH_TIMEOUT_SECONDS)
        except GitNotFound:
            raise PullRequestError(
                f"git was not found on PATH, so {pr.url} could not be fetched.\n{_FOOTER}"
            ) from None
        except GitError as error:
            raise PullRequestError(
                f"The repository of {pr.url} could not be cloned from {clone_url}.\n"
                f"  git: {_reason(error)}\n"
                f"{_FOOTER} Only public GitHub repositories can be read, and the network must be reachable."
            ) from None
        try:
            run_git(
                repo_root,
                *_NO_CREDENTIALS,
                "fetch",
                "--quiet",
                "origin",
                f"+{pr.head_ref}:{pr.head_ref}",
                env=env,
                timeout=FETCH_TIMEOUT_SECONDS,
            )
        except GitError as error:
            raise PullRequestError(
                f"Pull request #{pr.number} was not found in {pr.owner}/{pr.repo} ({pr.head_ref} could not be "
                f"fetched).\n  git: {_reason(error)}\n{_FOOTER}"
            ) from None
        # Blobs are fetched lazily by the diff; the same no-prompt rule must hold for those fetches.
        run_git(repo_root, "config", "credential.helper", "")
        run_git(repo_root, "config", "core.askPass", "")

        if base is None:
            try:
                tracking = run_git(repo_root, "symbolic-ref", "--short", "refs/remotes/origin/HEAD").strip()
            except GitError:
                raise PullRequestError(
                    f"The default branch of {pr.owner}/{pr.repo} could not be determined.\n"
                    f"{_FOOTER} Name the branch the pull request targets with --base."
                ) from None
            base_name = tracking.removeprefix("origin/")
        else:
            base_name = base
        base_rev = f"refs/remotes/origin/{base_name}"
        if not ref_exists(repo_root, base_rev):
            raise PullRequestError(
                f"The base branch {base_name!r} does not exist in {pr.owner}/{pr.repo}.\n"
                f"{_FOOTER} Name the branch the pull request targets with --base."
            )
        if not have_merge_base(repo_root, base_rev, pr.head_ref):
            raise PullRequestError(
                f"Pull request {pr.slug} shares no history with {base_name!r}, so there is no change to compare.\n"
                f"{_FOOTER}"
            )
        return _ClonedPullRequest(
            pr=pr,
            workspace=workspace,
            repo_root=repo_root,
            base_name=base_name,
            base_rev=base_rev,
            base_was_default=base is None,
        )
