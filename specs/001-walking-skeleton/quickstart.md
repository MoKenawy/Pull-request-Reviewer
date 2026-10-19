# Quickstart: Validating the Walking Skeleton

**Feature**: [spec.md](./spec.md) · **Plan**: [plan.md](./plan.md)

How to prove feature 001 works, from a clean checkout. The steps come in three groups. **A** and **B** need no
credential and no network. **C** needs a real provider key and is the only group that does.

Shapes and rules are not repeated here. See [contracts/cli.md](./contracts/cli.md),
[contracts/review-report.md](./contracts/review-report.md), [contracts/emit-finding.md](./contracts/emit-finding.md),
and [contracts/config.md](./contracts/config.md).

---

## Prerequisites

| | Needed for |
|---|---|
| `git` on `PATH` | Everything, because the tool reviews git repositories |
| `uv` ≥ 0.11 | Environment and running commands |
| CPython 3.12 (`uv python install 3.12` if absent) | Everything |
| A NVIDIA NIM API key in `AGENTIC_REVIEW_API_KEY` | **Group C only** |

Node and `tree-sitter` are **not** needed for this feature.

## Setup

```bash
uv sync                      # creates .venv from uv.lock, installs dev dependencies
uv run agentic-review --version
```

Expected: `agentic-review 0.1.0 (report schema 1.0)`.

---

## A · Offline automated checks (SC-006)

```bash
uv run lint-imports          # structural contracts 1, 2, 3, 6
uv run pytest                # structural + unit + integration, stand-in model, network blocked
```

Expected: all contracts **KEPT**, and all tests pass, with no `AGENTIC_REVIEW_API_KEY` set and the network
disconnected. To confirm nothing reaches the network, run once with Wi-Fi off.

What the suite covers, so a reviewer can check it against the spec:

| Suite | Proves |
|---|---|
| `tests/structural/` | FR-030: Rich, git, LangChain/LangGraph confined; nothing imports `cli/`; layers hold |
| `tests/unit/changeset/` | Scope semantics, diff and hunk parsing, renames, binary files, untracked files, exclusion globs (SC-009) |
| `tests/unit/config/` | Defaults, per-field merge, unknown and duplicate keys, ignored-settings notice, credential lookup and refusal |
| `tests/unit/findings/` | Shape and reference validation, rejection reasons, tool schema = generated schema, fingerprint stability |
| `tests/unit/assembly/` | Diff passed verbatim; the "no checks / no context" statement; budget refusal with no partial diff |
| `tests/unit/agent/` | No `tool_choice`; one tool bound; repair turn at most once; ceiling counting; `denied` beyond ceiling |
| `tests/unit/output/` | Verdict table; terminal and JSON built from the same report; report invariants |
| `tests/integration/` | Every acceptance scenario in Stories 1–5 and every edge case, through `run_review` and the CLI |

The integration suite asserts across **every** scenario that: each report validates against
`agentic-review schema` using `jsonschema` (SC-002); the planted canary key appears in 0 bytes of output
(SC-007); every stage that ran has a duration (SC-008); and preflight failures called the stand-in model 0
times (SC-004).

---

## B · Manual end-to-end against a scratch repository, still offline

This checks the paths that need no model: preflight, scope resolution, nothing-to-review, and the schema command.

```bash
mkdir /tmp/ar-demo && cd /tmp/ar-demo && git init -q && git commit -q --allow-empty -m init
```

| # | Do | Expect |
|---|---|---|
| B1 | `uv run --project <repo> agentic-review schema` from **outside** any repository, with no key set | A JSON Schema on stdout, exit **0** (FR-028) |
| B2 | `agentic-review review` in `/tmp` (not a repository) | stderr names the directory, stdout empty, exit **3** |
| B3 | In `ar-demo`, with no key set: `agentic-review review` | stderr names `AGENTIC_REVIEW_API_KEY` and the user credential path, exit **3** |
| B4 | `export AGENTIC_REVIEW_API_KEY=dummy`; write `agent: {toolCallCeling: 5}` (misspelt) to `.agentic-review.yml`; run `review` | stderr names `agent.toolCallCeling`, exit **3** |
| B5 | Remove the config file. Run `review --scope range --base nope`, then `review --commit nope` | Each time, stderr names `nope`, exit **3** (`--commit` is not offered until User Story 4) |
| B5a | `review --pr acme/widgets#7`, then (with network) `review --pr https://github.com/<no-such-owner>/<no-such-repo>/pull/1` | First: stderr says it is not a pull request URL. Second: stderr names the repository; **no login prompt appears**. Both exit **3** |
| B6 | Create `README.md` and `dist/a.js` only; run `review --json` | stdout is one JSON document with `completionStatus: "nothing-to-review"`; `dist/a.js` is under `excluded` with `default:build-output`; `README.md` is listed as not reviewed; exit **0**; the dummy key made no network call |

With the dummy key, any scenario that reaches the model is expected to produce a **provider-error** report and exit
**2**, never a crash and never exit 0. Running `review` after adding a `.ts` file checks this (spec US2-AS1).

---

## C · With a real provider (SC-001, S-1)

### C1 · S-1: does the model call the tool? Run this **before** the output and CLI work is finished.

```bash
uv run python scripts/s1_tool_calling_probe.py --runs 50 --model meta/llama-3.3-70b-instruct
```

Expected: `specs/001-walking-skeleton/s1-results.md` is written, recording per-run counts of valid,
schema-rejected, reference-rejected, invalid-JSON and no-call outcomes, repair success, tokens and latency.
**No pass mark is set.** The maintainer reads the figures and decides the default model and whether FR-5.6b's
fallback is pulled forward (research R-21). Record the one-line summary in `Docs/technical_stack.md` §7.

### C2 · SC-001: one command on a public TypeScript repository

```bash
git clone --depth 50 <a small public TypeScript repository> demo && cd demo
# make a small, deliberately flawed edit to one .ts file, then:
git add -A
uv run --project <repo> agentic-review review --scope staged --json report.json
```

Expected:

- The terminal shows the scope `staged changes` (not defaulted), the reviewed file, **"No checks were run in this
  build"** and **"No related context was gathered in this build"**, the findings, counts, and the verdict.
- `report.json` validates against `agentic-review schema`.
- The exit code matches the verdict (0 or 1).
- No setup beyond the key was needed.

If the model returns no findings, the report says `no-tool-call`. That is the expected, honest outcome described
in plan gap **D-5**, not a failure of this check.
