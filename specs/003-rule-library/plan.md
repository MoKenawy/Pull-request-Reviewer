# Implementation Plan: Rule Library — Scoped Rules in a Static Prompt

**Branch**: `003-rule-library` | **Date**: 2026-11-06 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/003-rule-library/spec.md`

**Authority**: [`Docs/agentic-code-review-srs-v1.md`](../../Docs/agentic-code-review-srs-v1.md) **v1.8** is normative — it gained FR-6.1a and AC-18 for this feature before the spec was written. [`Docs/technical_stack.md`](../../Docs/technical_stack.md) is normative for technology selection only; this plan introduces no technology, so it needs no amendment ([research R-1](./research.md#r-1--rule-files-are-yaml-package-data-under-core-patternsrules)). [`Docs/design/`](../../Docs/design/) says how the system is put together — principally [`02-domain-model.md`](../../Docs/design/02-domain-model.md) §3.8 for the rule types and [`01-logical-architecture.md`](../../Docs/design/01-logical-architecture.md) §3 for the layering. Rules: [`.specify/memory/constitution.md`](../../.specify/memory/constitution.md). This plan selects from those documents and adds no requirement; where it disagrees with them, it is wrong.

---

## Summary

Give the reviewer a library of named, path-scoped rules; put the whole library in the static part of every prompt; let the union of the rules' scopes decide which changed files are worth reviewing; and make every finding that came from a rule say which one.

**Technical approach.**

- A new Layer-1 capability package holds the rules as **data** — types, a loader over YAML package data, and a renderer. It evaluates no globs.
- **Preflight loads and validates** the library, because it is the only stage that may stop a run and because CF-1 needs the scopes before it resolves the change set.
- **CF-1 evaluates the scopes**, reusing the glob dialect it already owns, and records a file no rule covers as excluded with a new third reason.
- **Our code appends the rules block** to whatever the instructions turn out to be, so a prompt-store failure can never drop the library.
- The attribution seam **already exists in the code and is deliberately empty**: the run's set of shown rule identifiers, the validation branch for an unknown identifier, and the rendering of a finding's rule are all written. This feature fills them in, which is why the smallest part of the work is the part the acceptance criterion names.

---

## Technical Context

**Language/Version**: Python ≥ 3.12 (3.12 and 3.13 in CI) — unchanged.

**Primary Dependencies**: Pydantic for the rule types; PyYAML for parsing; `importlib.resources` for package data. **All three are already in use. No dependency is added** — [R-1](./research.md#r-1--rule-files-are-yaml-package-data-under-core-patternsrules).

**Storage**: none. Rule documents are package data in the wheel, plus one optional file in the reviewed repository.

**Testing**: pytest, offline, with the existing scripted stand-in model; `import-linter` for the structural contracts. Four existing contracts are extended in this feature — [R-10](./research.md#r-10--four-existing-import-contracts-are-extended-no-new-contract-is-added).

**Target Platform**: the existing CLI — Linux and Windows, Python 3.12/3.13.

**Project Type**: single Python package with a console entry point. The host language is not the target language: the harness is Python, the reviewed code is TypeScript.

**Performance Goals**: none stated, and none may be invented — the latency figure is an acknowledged open item. One real effect to report rather than target: a static prefix **raises every prompt's floor**, so a change set that fitted before may now exhaust the budget. That is reported, never silent — [R-8](./research.md#r-8--the-budget-counts-the-rules-block-and-gains-one-constant-per-section-allocation-stays-with-004).

**Constraints**: `core/` stays framework-free; capabilities never import each other, which is what forces the plain-glob-list seam; design introduces no technology; the published report's schema takes a **minor** version bump for the new exclusion reason.

**Scale/Scope**: five shipped rules plus one optional configured file. Five user stories, 28 functional requirements, 8 success criteria. Two acceptance criteria completed: AC-4 and AC-18.

---

## Constitution Check

*GATE: must pass before Phase 0. Re-checked after Phase 1 below.*

| # | Principle | Gate | Status |
|---|---|---|---|
| I | The Documents Decide | The feature selects SRS identifiers and adds none. The one piece of new observable behaviour — rule scope deciding what is reviewed — was taken to the SRS **first** and became FR-6.1a/AC-18 in v1.8; the spec cites them rather than inventing them. Five design corrections found along the way were written back to the design documents, not settled inside the spec | ✅ Pass |
| II | Our Code Owns Orchestration | The pipeline's order, nodes and edges are unchanged; `load_patterns` stops being a pass-through but stays where it is. The one new edge — the *nothing reviewed* short-circuit this feature inherits from 001's T087 — is conditional and keeps the graph **acyclic**. No step outside the review step branches on model output. The framework stays in `agents/` | ✅ Pass |
| III | One Core, Thin Adapters | The CLI gains nothing; the verdict stays in core. The change set remains a files-and-hunks structure independent of **how it was resolved** — rule scope is review policy applied to every scope alike, not a property of the resolver. The pull-request source's interface widens by one parameter, which is recorded as a design gap rather than done quietly | ✅ Pass |
| IV | Findings Enter Through One Door | `emit_finding` stays the only door and the only tool. A rule identifier is validated **at the call boundary** against the identifiers the run actually showed the model; an unknown one is rejected like a malformed call. No prose is parsed. One definition: the rule types import the finding model's category and severity vocabularies rather than restating them. Nothing forces a tool call | ✅ Pass |
| V | Never Silent | A file set aside for want of a rule is recorded with a reason **distinguishable** from a configured exclusion and from a non-reviewed language. An empty review scope completes, says nothing was reviewed, and is never clean. A malformed library halts at preflight — the one stage permitted to stop a run — naming the file and the field. A rule-scope exclusion is **not** dressed as a degradation, and a test asserts the degradation list is empty | ✅ Pass |
| VI | Measure, Do Not Argue | No task is justified by a quality claim: whether these rules improve review is **007's** question. The prompt-cache benefit is stated as unverified. No test asserts the library fits inside a token ceiling, because that ceiling is an acknowledged placeholder. Catch rate is not claimed, and nothing here reports one | ✅ Pass |
| VII | Offline, Structural, Fast Tests | Every test runs offline, with no credential and the scripted stand-in. The new package's layering is enforced **in this feature**: contract 6 gains it as a sibling of the change-set package, which makes the import this plan forbids a contract violation rather than a convention. Three forbidden-dependency contracts gain it as a source module | ✅ Pass |

**Engineering constraints**: no new dependency, so no stack-table row, inventory row or version pin is owed ([R-1](./research.md#r-1--rule-files-are-yaml-package-data-under-core-patternsrules)). Package data is read through `importlib.resources`, never by path arithmetic from `__file__`. ✅

**Gate result: PASS.** No violations, so Complexity Tracking is empty.

---

## Project Structure

### Documentation (this feature)

```
specs/003-rule-library/
    spec.md                  # what and why, with the SRS traceability
    plan.md                  # this file
    research.md              # R-1 … R-12, the decisions and their alternatives
    data-model.md            # the types, their validation, the deltas to existing ones
    quickstart.md            # how to see it working, and how to tell it from the build before
    checklists/
        requirements.md      # spec quality, re-validated after clarification
    contracts/
        rules-file.md        # the rule document format, its sources, and every failure message
        rule-scope.md        # the scope predicate, the new report reason, the empty-scope outcome
```

### Source Code (repository root)

```
src/agentic_review/
    core/
        patterns/            # NEW · CF-8 · a Layer-1 capability, data only
            model.py         #   PathScope, PatternRule, PatternLibrary
            library.py       #   load + validate, shipped and configured
            render.py        #   the rules block, deterministic and ordered by id
            rules/           #   NEW · package data · the five shipped rules, YAML
        changeset/
            exclusion.py     # CHANGED · the scope predicate joins the glob dialect it reuses
            resolve.py       # CHANGED · scopes applied at resolution, after reviewability
            pull_request.py  # CHANGED · the source interface widens by one parameter
            model.py         # CHANGED · the third exclusion reason
        assembly/
            prompt.py        # CHANGED · the rules block appended after the instructions
            budget.py        # CHANGED · the fixed section's constant; the estimate covers the block
        findings/
            model.py         # CHANGED · the rule-identifier field's prompt-visible description
            schema.py        # CHANGED · schema version 1.0 → 1.1
            report.py        # CHANGED · the excluded-path reason admits the new source
        config/
            settings.py      # CHANGED · one key naming a file of additional rules
        pipeline/
            preflight.py     # CHANGED · loads and validates the library; exit 3 on a bad one
    agents/
        pipeline_agent.py    # CHANGED · load_patterns renders and publishes; the T087 edge
tests/
    unit/patterns/           # NEW · the loader, its failures, the renderer
    unit/changeset/          # CHANGED · the scope predicate, including the pooling-bug test
    integration/             # CHANGED · rule scope, empty scope, rules in the prompt, user rules
    structural/              # CHANGED · the four extended contracts, plus a dialect-confinement test
pyproject.toml               # CHANGED · import contracts 1, 2, 6, 8
```

**Structure Decision**: the existing layout, plus one package the layout document already reserved. `core/patterns/` is a Layer-1 capability beside the change-set package, so the two **may not import each other** — which is precisely why the scopes travel as plain string tuples and the glob dialect stays where it already lives. The corpus directory the layout also reserves stays empty: it belongs to feature 007.

---

## Phase 0 — Research (complete)

[research.md](./research.md) records twelve decisions. The five that shape everything downstream:

| | |
|---|---|
| [R-1](./research.md) | YAML package data, read through `importlib.resources` — **no new dependency**, so the stack document is untouched |
| [R-2](./research.md) | Our code appends the rules block. Putting rules in the managed prompt would let a fetch timeout silently drop the whole library |
| [R-3](./research.md) | CF-1 evaluates; patterns carries data. Forced by the layering, enforced by contract 6 |
| [R-4](./research.md) | Rule scope applies **after** reviewability, so a non-TS file keeps its honest reason |
| [R-5](./research.md) | `rules:no-scope-match`, and the project's first schema bump |

## Phase 1 — Design (complete)

[data-model.md](./data-model.md) gives the three new types, their validation, the predicate, and the six deltas to existing types. [contracts/rules-file.md](./contracts/rules-file.md) is what a project author writes against, down to each failure message. [contracts/rule-scope.md](./contracts/rule-scope.md) is the observable behaviour: the predicate's four properties, the new report reason, the terminal line, and the empty-scope outcome. [quickstart.md](./quickstart.md) is how to see it all working offline.

### Suggested build order within the feature

1. `core/patterns/` — types, then loader, then renderer. Testable alone, imports nothing of ours but the finding model's vocabularies.
2. The five shipped rules as package data, with the test that the shipped library loads and has at least five rules each carrying both examples.
3. The configuration key and its validation, then preflight's load. Exit 3 on a bad file, with no provider call.
4. The scope predicate in the change-set package, **with the pooling-bug test first**.
5. Applying it at resolution: the third reason, the report's schema bump, the terminal count.
6. The *nothing reviewed* short-circuit — 001's T087 — and its conditional edge.
7. The prompt: the block appended, the estimate covering it, the fixed-section constant.
8. Attribution: publish the identifiers, rewrite the rule-identifier field's description, update the schema test.
9. The import contracts, and the dialect-confinement test.
10. Republish the managed system prompt so its instructions mention rules. **Not a code change, and easy to forget** — without it, every run with the store configured shows rules the instructions never reference.

Steps 1–3 are independent of 4–6. Step 7 needs 1; step 8 needs 3.

---

## Design gaps raised by this plan

- **D-6 — the pull-request source's interface widens.** The scopes have to reach every change-set path, including the pull-request one, so that source's method takes one more parameter. ADR-0011 names that interface as the seam a future implementation substitutes into, so widening it is a recorded decision rather than a refactor. The parameter is additive with a default, and nothing pull-request-specific changes.
- **D-7 — how much of the library the trace should carry.** The run's state is serialised by every attached tracer, so putting the whole library on it ships five rules' worth of code examples into each trace at every node transition. It carries no secret and at five rules it is bounded, so this plan starts there for traceability. If it proves heavy the fallback is a cached loader with only the identifiers and the scopes on the state — [R-7](./research.md).
- **D-8 — the rules block's rendering is deliberately not a wire format.** Three properties are contractual: each identifier appears verbatim, each scope appears with its rule, and the block is byte-identical for a given library. Everything else about the wording is free to change, because changing it is how prompt quality gets improved once 007 can measure whether it did.

---

## Post-design constitution re-check

Re-run after Phase 1, since the design added the schema bump, the T087 edge and the interface widening — none of which existed at the first gate.

| Principle | Re-check |
|---|---|
| I | The schema bump follows the versioning rule the design document already states (an added value is minor, the version is hand-set). No requirement was added; FR-6.1a was already in the SRS before design began. ✅ |
| II | The T087 edge is conditional and the graph stays acyclic; a test asserts there is no back edge. ✅ |
| III | The widened pull-request interface is additive with a default, and recorded as **D-6** rather than done quietly. ✅ |
| IV | Importing the category and severity vocabularies rather than restating them is what keeps "one definition" true once feature 007 compares a finding's category with an expectation's. ✅ |
| V | Three exclusion reasons, all distinguishable; the ordering decision in [R-4](./research.md) exists precisely so the least honest of them cannot win. ✅ |
| VI | The one number this feature could have invented — a token ceiling for the library — is explicitly forbidden a test, because the budget it would be measured against is a placeholder. ✅ |
| VII | Four contracts extended here, not later; a structural test also catches the glob dialect being copied into the new package, which the layering contract alone would not see. ✅ |

**Gate result after design: PASS.**

## Complexity Tracking

No constitutional violations, so this table is empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| — | — | — |
