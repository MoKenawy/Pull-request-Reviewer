"""Preflight: everything that can stop a run is checked before any change is resolved or any model is called.

Checks run in the order of contracts/cli.md "Preflight messages" and stop at the first failure (FR-9.3 — partial:
the test-script prerequisite arrives in feature 002 — AC-9).
Implemented here: 1 (inside a git repository), 2 (configuration valid), 4 (credential available). Checks 3 and 5
(scope arguments, range base) arrive with User Story 3.

Check 4 establishes that a credential **can** be found; it does not hand the credential on. ``PreflightOk`` becomes
pipeline state, and pipeline state is what every tracer attached to the graph receives and ships, so the value is
looked up again by the one step that gives it to the model client.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agentic_review.core.changeset.resolve import GitNotFound, locate_repository
from agentic_review.core.config.credentials import CredentialProblem, CredentialSources, find_credential
from agentic_review.core.config.loader import ConfigError, LoadedSettings, load_settings
from agentic_review.core.config.redact import redact

CONFIG_FILE_NAME = ".agentic-review.yml"


@dataclass(frozen=True)
class PreflightFailure:
    message: str
    """Already redacted. The CLI prints it to stderr."""


@dataclass(frozen=True)
class PreflightOk:
    repo_root: Path
    loaded: LoadedSettings
    """No credential here, deliberately: see the module docstring."""


def preflight(cwd: Path, config_path: Path | None, sources: CredentialSources) -> PreflightFailure | PreflightOk:
    secret = sources.from_env.reveal() if sources.from_env is not None else None

    def fail(message: str) -> PreflightFailure:
        return PreflightFailure(redact(message, secret))

    try:
        repo_root = locate_repository(cwd)
    except GitNotFound:
        return fail("git was not found on PATH, so no repository could be located.\nNothing was reviewed.")
    if repo_root is None:
        return fail(
            f"{cwd} is not inside a git repository.\n"
            "Nothing was reviewed. Run the review from inside the repository you want reviewed."
        )

    explicit = config_path is not None
    path = config_path if config_path is not None else repo_root / CONFIG_FILE_NAME
    try:
        loaded = load_settings(path, explicit=explicit, display_name=str(path) if explicit else CONFIG_FILE_NAME)
    except ConfigError as error:
        return fail(error.message)

    credential = find_credential(sources, repo_root)
    if isinstance(credential, CredentialProblem):
        return fail(credential.message)

    return PreflightOk(repo_root=repo_root, loaded=loaded)
