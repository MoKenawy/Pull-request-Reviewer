# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current state

**Feature 001, the walking skeleton, is built** (User Story 1 complete; `specs/001-walking-skeleton/tasks.md` tracks the rest). `src/agentic_review/` has 41 Python modules — CLI, pipeline, and the CF-1/CF-4/CF-5/CF-6/CF-7/CF-9 core functions; CF-2, CF-3 and CF-8 are not built yet (features 004, 002, 003). 207 tests run offline in about 20 seconds, plus 5 import-linter structural contracts and a GitHub Actions CI matrix on Python 3.12/3.13, Linux and Windows.

**Commands** (Python ≥3.12, via [uv](https://docs.astral.sh/uv/)):

```
uv sync                                          # install
uv run pytest                                    # full suite; -k or a path to narrow
uv run lint-imports                              # the 5 structural contracts; what CI runs
uv run --env-file .env agentic-review review      # run the tool itself
```

On Windows, `uv run lint-imports` can fail with *"uv trampoline failed to canonicalize script path."* Fall back to:

```
uv run python -c "from importlinter.cli import lint_imports_command; lint_imports_command()"
```

`Docs/operation_guidelines.md` is the full how-to-install/run/troubleshoot guide; it describes what the code does today, not the specification.

The work is an **agentic code reviewer**: a local CLI that reviews a TypeScript/JavaScript change set by parsing it, running the repository's own tests and type-check, and passing that evidence to a single model pass that emits schema-validated findings. Only the `review` command is implemented; `regression` and `schema` are not built.

## Document authority — read this before editing any doc

Exactly one document defines what to build at any time. The hierarchy is strict:

| Document | Authority |
|---|---|
| `Docs/agentic-code-review-srs-v1.md` | **Normative.** The build target. Wins on any disagreement. |
| `Docs/technical_stack.md` | **Normative for technology selection only** — which library, which protocol, which layout. Subordinate to the SRS: it never relaxes a requirement. If a library cannot satisfy one, the library is wrong. |
| `Docs/adr/*.md` | Normative *where cited by* the v1 SRS. |
| `Docs/design/` | **How the system is put together** — components, types, behaviour, contracts. Subordinate to the SRS and the stack doc; introduces no requirement and no library. Start at `Docs/design/README.md`. |
| `specs/001-walking-skeleton/` | The Spec Kit feature spec, plan and tasks that implement a slice of the v1 SRS. Its own `FR-0NN` identifiers are feature-local — see the traceability table in `spec.md` for how they map onto the SRS's `FR-x.y` identifiers. Never write an `FR-0NN` bare outside `specs/001-walking-skeleton/`. |
| `Docs/operation_guidelines.md` | How to install, run and troubleshoot the tool today. Non-normative — describes the code, not the spec. |
| `DESIGN_BLOCKERS.md` | Repo root. Places the analysis hand-off contradicted itself or left a decision design couldn't make alone, with a response log. |
| `Docs/Draft/**` | **Non-normative.** Rationale, background, and requirements for v2/v3. |

The split between the SRS and the stack document is deliberate: the SRS says *what must be true*, the stack says *what it is built with*, and ADR-0007 says *why that stack*. Library choices move — versions get pinned, packages get swapped — and those changes belong in `technical_stack.md`, not in an append-only ADR. Reversing ADR-0007's **reasoning** still needs a new ADR.

`Docs/Draft/agentic-code-review-srs.md` is the full v1–v3 requirement catalogue and the identifier registry the ADRs cite; `Docs/Draft/mvp-scope.md` is the analysis that selected v1's scope and explains every cut. Both are historical records — they are *not* the build target, even though they read like specifications.

## Conventions that must be preserved

- **Requirement identifiers are stable and are never renumbered.** A requirement keeps its `FR-x.y` identifier across versions; a version tag says when it applies. Renumbering silently breaks cross-references in the ADRs, the harness design, and the traceability table (SRS Appendix B). Requirements introduced by the v1 baseline are marked `(new in v1)`. **In `src/` and `tests/`, a bare `FR-` identifier is always an SRS (`FR-x.y`) identifier.** A feature-local `FR-0NN` identifier (from a `specs/NNN-*/` spec) is only ever written qualified, e.g. `spec 001 FR-009` — never bare outside its own feature directory.
- **Must / Should.** Must = required for the version to be complete. Should = included if time allows; its absence does not block release.
- **ADRs are append-only.** Never edit a decision to reflect a change of mind — write a new ADR that supersedes it, and update the status table in `Docs/adr/README.md`. Status values: Proposed / Accepted / Superseded / Deprecated. ADR-0006, ADR-0007, ADR-0008 and ADR-0009 are Accepted; the other five (0001–0005) are Proposed.
- **Read ADR-0006 first, then ADR-0007, then ADR-0008 and ADR-0009.** 0006 was decided late and rescoped four earlier records (0001–0003, 0005), which were written assuming a GitHub Action was the only delivery surface. 0007, 0008 and 0009 are the records naming an implementation technology: 0007 amends one consequence of 0006 (distribution: PyPI, not npm); 0008 settles what the tool-call ceiling counts and how a review ends; 0009 declares the pipeline as a LangGraph graph and narrows FR-5.8 accordingly (see below).
- Docs cross-link with relative paths and use mermaid diagrams throughout. Moving or renaming a file under `Docs/` requires fixing the inbound links in `Docs/README.md`, `Docs/adr/README.md`, and the SRS front matter.
- `Docs/Draft/agentic-code-review-srs-ar.md` is an Arabic translation of the catalogue. Changes to the catalogue leave it stale; say so rather than silently diverging.

## Architecture the code will take

**One surface-independent core behind thin adapters** (ADR-0006). v1 builds the CLI adapter only; the GitHub Action is v3. An adapter resolves what to review, renders findings, and stores state — **it never decides what counts as a finding** (FR-10.2).

Orchestration is a **fixed pipeline owned by our code**, not by the model (ADR-0001). Nine core-function blocks, `CF-1` through `CF-9`, each owning a disjoint set of requirements. Since ADR-0009 the fixed order is a **declared LangGraph graph**, and since ADR-0010 it lives in `agents/pipeline_agent.py` — the **main agent** — one node per phase, including CF-2, CF-3 and CF-8, which are pass-through nodes until their features land:

```
preflight (CF-9) → resolve_change_set (CF-1) → parse_and_context (CF-2, stub)
  → execute_checks (CF-3, stub) → load_patterns (CF-8, stub) → assemble_context (CF-4)
  → review (CF-6, the only model step) → build_report (CF-5 → CF-7)
```

The graph is acyclic. CF-6's own graph — the **review reporting agent**, `agents/review_reporting_agent.py`, reached through `ReviewPort` — is the only place a cycle may occur: the repair-turn edge back to `call_model`. It is invoked as an ordinary call, **not** added as a LangGraph subgraph, because the model it binds is unknown until `preflight` has run (ADR-0010 records why, so nobody re-derives it).

**Where code goes** (ADR-0010): `agents/` holds anything that declares a graph or builds a provider client; `core/` is framework-free and every module in it is callable as an ordinary function. If you are adding a module, that distinction decides its directory.

Two commands, one core: a `review` command producing findings, and a `regression` command producing a catch rate over a curated defect corpus.

### The load-bearing constraints

These are the ones that make v2 and v3 additions rather than rewrites. Treat a change that violates one as a design change requiring an ADR, not a refactor:

- **FR-2.6e** — no consumer branches on which `RelatedContextProvider` implementation served a request. v1 ships a parser-backed provider serving depths 0–1; v2 adds an index-backed one behind the same frozen signature (SRS §4.2.2).
- **FR-5.6a** — findings enter the system *only* through an `emit_finding` tool call validated against the finding-model schema at the call boundary. Model prose is never parsed for findings (ADR-0004).
- **FR-5.7** — v1's agent completes a review in a single model pass. Step ceiling is zero; `emit_finding` is the only tool. Raising it later is configuration, not restructuring.
- **FR-4.6** — the agent cannot trigger check execution. Checks run once per invocation, before the review pass (ADR-0002).
- **FR-10.3c** — the change set is a files-and-hunks structure independent of how it was resolved. This is the seam the v3 Action adapter substitutes into.
- **FR-11.2** — a review is produced under *every* failure mode (checks unrunnable, context over budget, provider error, budget exhausted), reporting the degradation. A silent failure is indistinguishable from a clean review.
- **FR-5.8** *(amended in v1.2 by ADR-0009, renamed in v1.3 by ADR-0010)* — the agent framework is confined to the **`agents/` package**. **No package under `core/` may import LangGraph, LangChain or openai**, and every core function stays callable as an ordinary function without them; the pipeline graph itself must stay acyclic, with CF-6 the only step where a cycle may occur. This is what keeps ADR-0001's "our code owns orchestration" true now that a framework is in the repository.
- **FR-2.6g** — the resolver sidecar's absence degrades and reports; it never fails an invocation. An optional prerequisite must not quietly become a required one.

`Docs/agentic-code-review-srs-v1.md` §6 lists sixteen acceptance criteria (AC-1…AC-16; AC-13/14 added in v1.1, AC-15/16 later). AC-5 and AC-7 are flagged as the ones to defend under schedule pressure; AC-8, AC-10 and AC-12 are the cheap structural checks on the constraints above. AC-10's import-contract wording was updated alongside FR-5.8 in v1.2.

### Planned stack and environment

Summary only — **`Docs/technical_stack.md` is the authority**, and carries the sidecar protocol, repository layout, import contracts, dependency inventory, and the version pins. Decided in **ADR-0007** (Accepted). **The host language is not the target language:** the harness is Python; the code it reviews is TypeScript.

- **Python** with `tree-sitter` bindings as a native extension, distributed as a **PyPI package** with a console entry point (`uv tool install` / `pipx`). OS/Python-version support is a distribution contract.
- **LangChain** for the provider interface, tool binding (FR-5.6a) and structured output (FR-5.6b); **LangGraph confined to `agents/`** (FR-5.8, amended v1.2 by ADR-0009, renamed v1.3 by ADR-0010) — every package under `core/` stays plain Python, callable without the framework. At ceiling zero the review step is a one-node graph, which is what makes FR-5.7's "configuration, not restructuring" literally true.
- **A bundled Node resolver sidecar** answers depth-1 module resolution from the TypeScript compiler's own algorithm (FR-2.6f). Started at most once per invocation, shipped as package data, never fetched at review time. Node is a runtime prerequisite for authoritative depth 1 and **never** for installation — its absence degrades and reports (FR-2.6g, AC-12). The sidecar is private to CF-2; nothing outside it may know it exists.
- **Pydantic** for the finding model, so the type, the JSON Schema (FR-0.4) and the `emit_finding` tool schema come from one definition — SRS §5 requires "one definition, not two".
- **Typer + Rich** for CF-7, **pytest** for the CF-8 regression corpus.
- Checks run as **subprocesses through the reviewed project's own toolchain** (FR-4.7). The harness never imports the project's dependencies, and never asks the project to install its own.

Config lives in `.agentic-review.yml` at the repository root, with documented defaults and loud (never silent) validation failure. The provider credential comes from the environment or user-level config — never hard-coded, never committed. Default provider is the NVIDIA NIM free tier, reached through an OpenAI-compatible client so a swap is a base URL and a model name.

The binding constraint is **latency, not cost**: a developer waiting at a prompt abandons the tool. How long is too long is deliberately not stated — an earlier "10–30 seconds" estimate was withdrawn in SRS v1.1 as unmeasured and now sits as TBD-2, to be set from real MVP usage.

### Build order

`Docs/agentic-code-review-srs-v1.md` Appendix A gives the recommended construction sequence: walking skeleton (CF-1 → CF-5 → CF-7), then evidence (CF-3), then **measurement (CF-8)**, then context quality (CF-2, CF-4), then hardening. Measurement is deliberately third, not last — after it, every subsequent change can be evaluated rather than argued about.

## Known gap to state honestly

v1 proves the pipeline works end to end; it does **not** yet prove the project's thesis. At context depth 1 the reviewer can judge whether a change is internally sound, not whether it violates an assumption held by a caller it never looked at. v1 also serves the *author* before they push, not the reviewer clearing a queue named as the primary persona in the problem definition. Both are stated in SRS §2.5 and §9 (R-1, R-5) and are meant to be restated whenever v1 is demonstrated.

## git-mentor skill

`git-mentor` (`SKILL.md` plus `references/`) is a Claude Code skill for commit planning, history review, Git recovery, and PR descriptions, at `.claude/skills/git-mentor/`. It is untracked because `.gitignore` ignores `.claude/*` — by design, not accident. Its hard rules apply when doing Git work here: never assume repository state without inspecting it, never assign one file to two commits, use Conventional Commits with scopes, and feed multi-line commit messages on stdin via a heredoc matching the invoking shell — PowerShell's `@'...'@` leaks its delimiters when used from the Bash tool.
