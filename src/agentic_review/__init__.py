"""agentic-review: a local reviewer for TypeScript/JavaScript change sets."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("agentic-review")
except PackageNotFoundError:  # running from a source tree that was never installed
    __version__ = "0.0.0"
