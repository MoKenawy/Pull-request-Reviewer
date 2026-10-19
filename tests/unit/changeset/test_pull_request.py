"""Reading a pull request — FR-10.3a (as amended in SRS v1.5), FR-10.3d, ADR-0011, research R-25.

The remote is a local repository served over ``file://``: the real clone and fetch run, with no socket.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from agentic_review.core.changeset import pull_request as pull_request_module
from agentic_review.core.changeset.pull_request import (
    WORKSPACE_PREFIX,
    PullRequestError,
    PullRequestRef,
    clone_arguments,
    discard_workspace,
    github_clone_url,
    parse_pull_request_url,
)
from tests.support.pull_request_remote import PR, PullRequestRemote


@pytest.fixture
def remote(pull_request_remote: PullRequestRemote) -> PullRequestRemote:
    return pull_request_remote


@pytest.fixture
def temp_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Where temporary clones are made, so a test can see what is left behind."""
    root = tmp_path / "tmp"
    root.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(root))
    return root


def _workspaces(temp_root: Path) -> list[Path]:
    return sorted(temp_root.glob(f"{WORKSPACE_PREFIX}*"))


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://github.com/acme/widgets/pull/7", PullRequestRef("acme", "widgets", 7)),
        ("https://github.com/acme/widgets/pull/7/", PullRequestRef("acme", "widgets", 7)),
        ("https://github.com/acme/widgets/pull/7/files", PullRequestRef("acme", "widgets", 7)),
        ("https://github.com/acme/widgets/pull/7#discussion_r1", PullRequestRef("acme", "widgets", 7)),
        ("  https://github.com/a-b/c.d_e/pull/1234?diff=split  ", PullRequestRef("a-b", "c.d_e", 1234)),
    ],
)
def test_pull_request_urls_are_recognised(url: str, expected: PullRequestRef) -> None:
    assert parse_pull_request_url(url) == expected


@pytest.mark.parametrize(
    "url",
    [
        "",
        "acme/widgets#7",
        "https://github.com/acme/widgets",
        "https://github.com/acme/widgets/issues/7",
        "https://github.com/acme/widgets/pull/0",
        "https://github.com/acme/widgets/pull/seven",
        "https://github.com/acme/widgets/pull/7abc",
        "https://github.com/acme/../pull/7",
        "https://github.com/-acme/widgets/pull/7",
        "http://github.com/acme/widgets/pull/7",
        "https://gitlab.com/acme/widgets/pull/7",
        "https://github.com.evil.example/acme/widgets/pull/7",
        "git@github.com:acme/widgets.git",
        "--upload-pack=touch /tmp/x",
    ],
)
def test_anything_else_is_not_a_pull_request_url(url: str) -> None:
    assert parse_pull_request_url(url) is None


def test_a_pull_request_names_its_repository_ref_and_url() -> None:
    assert github_clone_url(PR) == "https://github.com/acme/widgets.git"
    assert (PR.head_ref, PR.slug, PR.url) == (
        "refs/pull/7/head",
        "acme/widgets#7",
        "https://github.com/acme/widgets/pull/7",
    )


def test_the_clone_is_blobless_has_no_checkout_and_uses_no_credentials(tmp_path: Path) -> None:
    arguments = clone_arguments("https://github.com/acme/widgets.git", tmp_path / "repo")
    assert "--filter=blob:none" in arguments and "--no-checkout" in arguments
    assert arguments[:4] == ("-c", "credential.helper=", "-c", "core.askPass=")
    assert arguments[-3:] == ("--", "https://github.com/acme/widgets.git", str(tmp_path / "repo"))


def test_git_cannot_prompt_while_fetching(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GIT_ASKPASS", "some-gui-prompt")
    monkeypatch.setenv("SSH_ASKPASS", "another-gui-prompt")
    env = pull_request_module._network_environment()
    assert env["GIT_TERMINAL_PROMPT"] == "0" and env["GCM_INTERACTIVE"] == "never"
    assert "GIT_ASKPASS" not in env and "SSH_ASKPASS" not in env


def test_open_fetches_history_without_files_or_blobs(remote: PullRequestRemote, temp_root: Path) -> None:
    opened = remote.source().open(PR, base=None)
    try:
        (workspace,) = _workspaces(temp_root)
        clone = workspace / "repo"
        assert sorted(p.name for p in clone.iterdir()) == [".git"]  # --no-checkout: nothing of the project on disk
        missing = pull_request_module.run_git(clone, "rev-list", "--objects", "--missing=print", "--all")
        assert any(line.startswith("?") for line in missing.splitlines())  # --filter=blob:none: no file contents yet
        assert pull_request_module.ref_exists(clone, "refs/pull/7/head")
    finally:
        opened.close()


def test_change_set_is_what_the_pull_request_changed_since_it_left_the_base(
    remote: PullRequestRemote, temp_root: Path
) -> None:
    opened = remote.source().open(PR, base=None)
    try:
        change_set = opened.change_set(())
        by_path = {f.path: f for f in change_set.files}
        assert set(by_path) == {".agentic-review.yml", "README.md", "src/added.ts", "src/app.ts"}
        assert "src/untouched.ts" not in by_path  # main's later commit is not the contributor's work
        assert [f.path for f in change_set.reviewable_files] == ["src/added.ts", "src/app.ts"]
        assert by_path["src/added.ts"].change_type == "added"
        assert [(e.path, e.rule) for e in change_set.excluded] == [("dist/bundle.js", "default:build-output")]

        scope = change_set.scope
        assert (scope.kind, scope.base_ref, scope.head_ref, scope.was_defaulted) == (
            "pull-request",
            "main",
            "refs/pull/7/head",
            False,
        )
        assert scope.description == (
            f"pull request acme/widgets#7 against main, the default branch "
            f"({remote.branch_point}..{remote.head_commit}) · 4 files"
        )
        assert opened.line_counts(change_set) == {"src/added.ts": 2, "src/app.ts": 21}
    finally:
        opened.close()


def test_a_named_base_is_used_instead_of_the_default_branch(remote: PullRequestRemote, temp_root: Path) -> None:
    opened = remote.source().open(PR, base="release")
    try:
        scope = opened.change_set(()).scope
        assert scope.base_ref == "release"
        assert "against release (" in scope.description and "default branch" not in scope.description
    finally:
        opened.close()


def test_close_removes_the_temporary_clone(remote: PullRequestRemote, temp_root: Path) -> None:
    opened = remote.source().open(PR, base=None)
    opened.change_set(())  # the diff fetches blobs: read-only pack files that must still be removable
    assert len(_workspaces(temp_root)) == 1
    opened.close()
    assert _workspaces(temp_root) == []


def test_an_unknown_pull_request_names_its_number(remote: PullRequestRemote, temp_root: Path) -> None:
    with pytest.raises(PullRequestError) as raised:
        remote.source().open(PullRequestRef("acme", "widgets", 99), base=None)
    message = raised.value.message
    assert "Pull request #99 was not found in acme/widgets" in message and "Nothing was reviewed." in message
    assert _workspaces(temp_root) == []


def test_an_unknown_base_names_the_branch(remote: PullRequestRemote, temp_root: Path) -> None:
    with pytest.raises(PullRequestError) as raised:
        remote.source().open(PR, base="no-such-branch")
    assert "The base branch 'no-such-branch' does not exist in acme/widgets" in raised.value.message
    assert _workspaces(temp_root) == []


def test_an_unreachable_repository_names_the_url(tmp_path: Path, temp_root: Path) -> None:
    source = pull_request_module.GitPullRequestSource(clone_url=lambda _pr: (tmp_path / "nowhere").as_uri())
    with pytest.raises(PullRequestError) as raised:
        source.open(PR, base=None)
    message = raised.value.message
    assert "https://github.com/acme/widgets/pull/7 could not be cloned" in message
    assert "Only public GitHub repositories can be read" in message and "Nothing was reviewed." in message
    assert _workspaces(temp_root) == []


def test_discard_workspace_copes_with_read_only_files_and_missing_directories(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    (workspace / "objects").mkdir(parents=True)
    packed = workspace / "objects" / "pack-1.pack"
    packed.write_bytes(b"PACK")
    packed.chmod(0o444)
    discard_workspace(workspace)
    assert not workspace.exists()
    discard_workspace(workspace)  # already gone: never an error
