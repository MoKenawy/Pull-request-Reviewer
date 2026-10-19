"""Credential lookup — FR-1.3a, research R-9, contracts/config.md."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_review.core.config.credentials import (
    ENV_VAR,
    Credential,
    CredentialProblem,
    credential_sources,
    find_credential,
    user_credential_path,
)

SECRET = "sk-test-5d1e0c9a"


def test_environment_wins(tmp_path: Path) -> None:
    env = {ENV_VAR: SECRET, "APPDATA": str(tmp_path), "XDG_CONFIG_HOME": str(tmp_path)}
    path = user_credential_path(env)
    path.parent.mkdir(parents=True)
    path.write_text("apiKey: other\n", encoding="utf-8")
    found = find_credential(credential_sources(env), tmp_path / "repo")
    assert isinstance(found, Credential)
    assert found.reveal() == SECRET and found.source == "environment" and found.location == ENV_VAR


def test_empty_environment_value_is_absent(tmp_path: Path) -> None:
    assert isinstance(find_credential(credential_sources({ENV_VAR: "", "HOME": str(tmp_path)}), tmp_path / "repo"), CredentialProblem)


@pytest.mark.parametrize("platform,expected", [
    ("win32", ("AppData", "agentic-review", "credentials.yml")),
    ("linux", (".config", "agentic-review", "credentials.yml")),
])
def test_user_path_per_platform(tmp_path: Path, platform: str, expected: tuple[str, ...]) -> None:
    env = {"APPDATA": str(tmp_path / "AppData"), "HOME": str(tmp_path)}
    assert user_credential_path(env, platform=platform).parts[-3:] == expected


def test_xdg_config_home_is_used(tmp_path: Path) -> None:
    env = {"XDG_CONFIG_HOME": str(tmp_path / "xdg"), "HOME": str(tmp_path)}
    assert user_credential_path(env, platform="linux") == tmp_path / "xdg" / "agentic-review" / "credentials.yml"


def test_user_file_is_read(tmp_path: Path) -> None:
    env = {"APPDATA": str(tmp_path), "XDG_CONFIG_HOME": str(tmp_path)}
    path = user_credential_path(env)
    path.parent.mkdir(parents=True)
    path.write_text(f"apiKey: {SECRET}\n", encoding="utf-8")
    found = find_credential(credential_sources(env), tmp_path / "repo")
    assert isinstance(found, Credential)
    assert found.reveal() == SECRET and found.source == "user-config" and found.location == str(path)


def test_user_file_inside_repository_is_refused(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    env = {"APPDATA": str(repo / "cfg"), "XDG_CONFIG_HOME": str(repo / "cfg")}
    path = user_credential_path(env)
    path.parent.mkdir(parents=True)
    path.write_text(f"apiKey: {SECRET}\n", encoding="utf-8")
    problem = find_credential(credential_sources(env), repo)
    assert isinstance(problem, CredentialProblem)
    assert "inside the repository" in problem.message
    assert SECRET not in problem.message


def test_missing_names_both_places(tmp_path: Path) -> None:
    env = {"APPDATA": str(tmp_path), "XDG_CONFIG_HOME": str(tmp_path)}
    problem = find_credential(credential_sources(env), tmp_path / "repo")
    assert isinstance(problem, CredentialProblem)
    assert ENV_VAR in problem.message
    assert str(user_credential_path(env)) in problem.message
    assert "Nothing was reviewed" in problem.message


def test_credential_never_prints_its_value() -> None:
    credential = Credential(SECRET, source="environment", location=ENV_VAR)
    assert SECRET not in repr(credential) and SECRET not in str(credential) and SECRET not in f"{credential}"


def test_with_no_local_repository_the_user_file_is_read(tmp_path: Path) -> None:
    # A pull request is reviewed without a repository on this machine: there is nothing the file could be inside.
    env = {"APPDATA": str(tmp_path), "XDG_CONFIG_HOME": str(tmp_path)}
    path = user_credential_path(env)
    path.parent.mkdir(parents=True)
    path.write_text(f"apiKey: {SECRET}\n", encoding="utf-8")
    found = find_credential(credential_sources(env), None)
    assert isinstance(found, Credential) and found.reveal() == SECRET
