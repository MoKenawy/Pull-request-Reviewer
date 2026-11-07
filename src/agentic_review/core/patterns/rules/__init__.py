"""The shipped rule documents (FR-6.3a's five), as **package data** rather than as Python.

The ``*.yml`` files beside this module are read at runtime through ``importlib.resources``, never by path
arithmetic from ``__file__`` (``Docs/technical_stack.md`` §3.1). This module exists only so that the directory
is an addressable package for that lookup — it holds no code and imports nothing.

Hatchling ships every file under ``packages = ["src/agentic_review"]``, so these documents land in the wheel
with no build configuration of their own.
"""
