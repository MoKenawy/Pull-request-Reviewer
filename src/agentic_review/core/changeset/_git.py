"""The git subprocess wrapper — the only place the product runs git (research R-3, import contract 2)."""

from __future__ import annotations

import subprocess
from pathlib import Path


class GitError(Exception):
    def __init__(self, args: tuple[str, ...], returncode: int, stderr: str) -> None:
        super().__init__(f"git {' '.join(args)} exited {returncode}: {stderr.strip()}")
        self.git_args = args
        self.returncode = returncode
        self.stderr = stderr


class GitNotFound(GitError):
    def __init__(self) -> None:
        super().__init__((), -1, "the git executable was not found on PATH")


def run_git_bytes(cwd: Path, *args: str, check: bool = True, stdin: bytes | None = None) -> tuple[int, bytes]:
    argv = ["git", "-c", "core.quotepath=off", *args]
    try:
        completed = subprocess.run(argv, cwd=cwd, shell=False, capture_output=True, input=stdin, check=False)
    except FileNotFoundError:
        raise GitNotFound() from None
    if check and completed.returncode != 0:
        raise GitError(args, completed.returncode, completed.stderr.decode("utf-8", "replace"))
    return completed.returncode, completed.stdout


def run_git(cwd: Path, *args: str, check: bool = True, stdin: bytes | None = None) -> str:
    _, output = run_git_bytes(cwd, *args, check=check, stdin=stdin)
    return output.decode("utf-8", "replace")


def succeeds(cwd: Path, *args: str) -> bool:
    returncode, _ = run_git_bytes(cwd, *args, check=False)
    return returncode == 0
