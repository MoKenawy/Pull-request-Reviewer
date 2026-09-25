"""Suite-wide guarantees: no network, no real credential, no leakage from the developer's environment.

Research R-19; spec SC-006 (offline) and SC-007 (the planted canary appears in no output).
"""

from __future__ import annotations

import socket

import pytest

CANARY_KEY = "ar-canary-9f3b2c7d51e84a06"
"""A planted credential. Every integration test scans every output for it (SC-007)."""


class NetworkBlocked(RuntimeError):
    pass


@pytest.fixture(autouse=True)
def _block_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def refuse(*_args: object, **_kwargs: object) -> None:
        raise NetworkBlocked("network access is blocked in the test suite")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket.socket, "connect_ex", refuse)


@pytest.fixture(autouse=True)
def _isolate_environment(monkeypatch: pytest.MonkeyPatch, tmp_path_factory: pytest.TempPathFactory) -> None:
    home = tmp_path_factory.mktemp("userhome")
    for name in ("AGENTIC_REVIEW_API_KEY", "AGENTIC_REVIEW_DEBUG", "XDG_CONFIG_HOME", "NO_COLOR"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("APPDATA", str(home / "AppData" / "Roaming"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(home / ".config"))
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    # Fixture repositories must not inherit the machine's git configuration (autocrlf, hooks, signing).
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(home / ".gitconfig-none"))


@pytest.fixture
def canary_env(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """Sets the planted credential and returns the environment mapping to hand to the pipeline."""
    import os

    monkeypatch.setenv("AGENTIC_REVIEW_API_KEY", CANARY_KEY)
    return dict(os.environ)
