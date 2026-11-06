# Quickstart — Validating Feature 003

**Feature**: [spec.md](./spec.md) · **Date**: 2026-11-06

How to see this feature working, and how to tell it apart from the build before it. Everything here runs offline except the last section, which is optional and costs a free-tier request.

## Prerequisites

```bash
uv sync
```

No provider credential is needed for anything in §1–§4. On Windows, use `uv run python -m pytest` and the `importlinter.cli` form if the `uv run` shims fail, per `CLAUDE.md`.

---

## 1 · The shipped library loads

```bash
uv run python -c "from agentic_review.core.patterns import load_library; lib = load_library(); print(lib.source, len(lib.rules)); [print(' ', r.id, r.category, r.applies_when.include) for r in lib.rules]"
```

**Expect**: the source reported as the shipped set, **at least five** rules, each with a category and a declared scope. At least one scope should name a test-file pattern — that is [FR-016](./spec.md), and it is the guardrail that keeps a test-only change from being set aside.

## 2 · Every rule reaches the prompt, identically

```bash
uv run python -m pytest tests/unit/assembly/test_prompt.py -q
```

**Expect**: the rules block in the **system** message and not the user message; the block byte-identical across two different change sets; the whole-prompt estimate including it. That byte-identity is [SC-004](./spec.md) and the precondition for any prompt caching — which is *unverified* for our provider and must not be claimed as a latency win.

## 3 · A finding names its rule, and an unknown rule is rejected

```bash
uv run python -m pytest tests/unit/findings tests/integration -k "rule" -q
```

**Expect**: a finding citing a loaded rule keeps its identifier in the terminal, the JSON and the HTML; a finding citing an identifier the model was not shown is rejected with that identifier named; a finding citing nothing is accepted unchanged. Together these are **AC-4** — see [research R-12](./research.md#r-12--ac-4-is-verified-offline-and-claimed) for why that is the whole of it without a corpus.

## 4 · Rule scope decides what gets reviewed

The behaviour **AC-18** exists for. Against a fixture repository with two changed TypeScript files, one of which no rule covers:

```bash
uv run python -m pytest tests/integration -k "rule_scope" -q
```

**Expect**, and each of these is a separate assertion:

| | |
|---|---|
| The covered file | in the diff the model was given |
| The uncovered file | **absent** from that diff, and present in the report's excluded list with the reason `rules:no-scope-match` |
| A file one rule excludes and another includes | **reviewed** — the pooled-exclusion bug, caught |
| A non-TypeScript file | still reported as *not a reviewed language*, **not** as a rule-scope exclusion |
| The degradation list | **empty.** Nothing failed; a scope exclusion is not a degradation |
| When nothing is left in scope | the run completes, says nothing was reviewed, calls the model **zero** times, and the verdict is **`nothing-to-review`** at exit 0 — its own verdict, not *reviewed and found nothing* |

To see it by hand rather than through the suite, point the configuration at a deliberately narrow rules file:

```bash
uv run --env-file .env agentic-review review --json report.json
```

With `patterns.rules` naming a file whose only rule is scoped to `src/api/**`, a change touching `src/ui/widget.ts` is set aside, and `report.json` says so with its reason.

## 5 · A project's own rules are added, not substituted

```bash
uv run python -m pytest tests/integration -k "user_rules" -q
```

**Expect**: the configured rule in the prompt **alongside** all five shipped rules — none displaced ([SC-008](./spec.md)); a configured identifier colliding with a shipped one failing by name; a malformed rules file stopping at preflight with the file and field named, **exit 3**, zero provider calls.

## 6 · The structure still holds

```bash
uv run lint-imports
uv run python -m pytest -q
```

**Expect**: the layering contract passing with the new package in it — `core/changeset/` importing `core/patterns/` is a **violation**, which is what keeps the glob-list seam honest ([research R-3](./research.md#r-3--cf-1-evaluates-the-globs-core-patterns-carries-them-as-data)) — and the whole suite green, offline, with no credential.

---

## 7 · Optional: did a real model actually cite a rule?

Not part of the suite, and not required for AC-4. One review against the free tier, in the shape of the existing tool-calling probe:

```bash
uv run --env-file .env agentic-review review --json real-report.json
```

**Expect**: nothing in particular. Whether a real model cites rules, and how often, is a *measurement* — and measurement is feature 007. Recording one observation here is fine; concluding anything from it is not (constitution Principle VI). Mind the daily free-tier request budget.
