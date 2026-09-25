"""Exclusions — FR-3.5, SC-009, research R-6, contracts/config.md "Default exclusion list"."""

from __future__ import annotations

import pytest

from agentic_review.core.changeset.exclusion import DEFAULT_EXCLUSIONS, classify, glob_to_regex


@pytest.mark.parametrize(
    "pattern,path,matches",
    [
        ("dist/**", "dist/index.js", True),
        ("dist/**", "dist/a/b/c.js", True),
        ("dist/**", "src/dist/index.js", False),
        ("**/node_modules/**", "packages/a/node_modules/x/index.js", True),
        ("**/node_modules/**", "node_modules/x.js", True),
        ("src/*.ts", "src/a.ts", True),
        ("src/*.ts", "src/deep/a.ts", False),
        ("src/?.ts", "src/a.ts", True),
        ("src/?.ts", "src/ab.ts", False),
        ("*.snap", "tests/__snapshots__/a.snap", True),
        ("yarn.lock", "packages/a/yarn.lock", True),
        ("**/*.generated.*", "src/api.generated.ts", True),
        ("src/a.ts", "src/a.tsx", False),
    ],
)
def test_glob_semantics(pattern: str, path: str, matches: bool) -> None:
    assert bool(glob_to_regex(pattern).fullmatch(path)) is matches


SAMPLES = {
    "dependencies": "node_modules/left-pad/index.js",
    "build-output": "dist/index.js",
    "generated": "src/__generated__/schema.ts",
    "minified": "public/app.min.js",
    "lockfile": "package-lock.json",
}


def test_every_default_rule_has_a_sample() -> None:
    assert set(SAMPLES) == set(DEFAULT_EXCLUSIONS)


@pytest.mark.parametrize("rule,path", sorted(SAMPLES.items()))
def test_default_rules_are_named(rule: str, path: str) -> None:
    assert classify(path, ()) == f"default:{rule}"


@pytest.mark.parametrize(
    "path",
    [p for patterns in DEFAULT_EXCLUSIONS.values() for p in patterns],
)
def test_every_default_pattern_is_well_formed(path: str) -> None:
    glob_to_regex(path)


def test_configured_pattern_is_named() -> None:
    assert classify("src/api.gen.js", ("src/*.gen.js",)) == "config:src/*.gen.js"
    assert classify("src/app.ts", ("src/*.gen.js",)) is None


def test_default_rule_wins_when_both_match() -> None:
    assert classify("dist/index.js", ("dist/**",)) == "default:build-output"


def test_adding_a_pattern_keeps_every_default() -> None:
    configured = ("**/*.stories.tsx",)
    for rule, path in SAMPLES.items():
        assert classify(path, configured) == f"default:{rule}"
    assert classify("src/Button.stories.tsx", configured) == "config:**/*.stories.tsx"
