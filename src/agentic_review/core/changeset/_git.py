"""The git subprocess wrapper — the only place the product runs git (research R-3, import contract 2)."""

from __future__ import annotations

import subprocess
from collections.abc import Mapping
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


def run_git_bytes(
    cwd: Path,
    *args: str,
    check: bool = True,
    stdin: bytes | None = None,
    env: Mapping[str, str] | None = None,
    timeout: float | None = None,
) -> tuple[int, bytes]:
    """``env`` replaces the process environment when given; ``timeout`` (seconds) ends the call as a ``GitError``."""
    argv = ["git", "-c", "core.quotepath=off", *args]
    try:
        completed = subprocess.run(
            argv, cwd=cwd, shell=False, capture_output=True, input=stdin, check=False, env=env, timeout=timeout
        )
    except FileNotFoundError:
        raise GitNotFound() from None
    except subprocess.TimeoutExpired:
        raise GitError(args, -2, f"timed out after {timeout:g} seconds") from None
    if check and completed.returncode != 0:
        raise GitError(args, completed.returncode, completed.stderr.decode("utf-8", "replace"))
    return completed.returncode, completed.stdout


def run_git(
    cwd: Path,
    *args: str,
    check: bool = True,
    stdin: bytes | None = None,
    env: Mapping[str, str] | None = None,
    timeout: float | None = None,
) -> str:
    _, output = run_git_bytes(cwd, *args, check=check, stdin=stdin, env=env, timeout=timeout)
    return output.decode("utf-8", "replace")


def succeeds(cwd: Path, *args: str) -> bool:
    returncode, _ = run_git_bytes(cwd, *args, check=False)
    return returncode == 0
