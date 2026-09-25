"""Builds git fixture repositories in a temporary directory (research R-19).

This is test tooling. It runs git directly, which the product code may do only inside ``core/changeset/``.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


class RepoBuilder:
    def __init__(self, root: Path) -> None:
        self.root = root
        root.mkdir(parents=True, exist_ok=True)

    def git(self, *args: str) -> str:
        completed = subprocess.run(
            ["git", *args], cwd=self.root, shell=False, capture_output=True, check=False
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"git {' '.join(args)} failed: {completed.stderr.decode('utf-8', 'replace')}"
            )
        return completed.stdout.decode("utf-8", "replace")

    def init(self) -> RepoBuilder:
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Fixture Author")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "core.autocrlf", "false")
        self.git("config", "commit.gpgsign", "false")
        return self

    def write(self, path: str, text: str) -> RepoBuilder:
        return self.write_bytes(path, text.encode("utf-8"))

    def write_bytes(self, path: str, data: bytes) -> RepoBuilder:
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return self

    def stage(self, *paths: str) -> RepoBuilder:
        self.git("add", "--", *(paths or (".",)))
        return self

    def commit(self, message: str = "commit") -> RepoBuilder:
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", message)
        return self

    def commit_staged(self, message: str = "commit") -> RepoBuilder:
        self.git("commit", "-q", "--allow-empty", "-m", message)
        return self

    def rename(self, old: str, new: str) -> RepoBuilder:
        (self.root / new).parent.mkdir(parents=True, exist_ok=True)
        self.git("mv", old, new)
        return self

    def delete(self, path: str) -> RepoBuilder:
        (self.root / path).unlink()
        return self

    def branch(self, name: str) -> RepoBuilder:
        self.git("branch", name)
        return self

    def checkout(self, name: str, *, create: bool = False) -> RepoBuilder:
        self.git("checkout", "-q", *(["-b"] if create else []), name)
        return self
