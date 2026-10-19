# Requirement Catalogue — Agentic Code Review (v1–v3)

**Status:** Draft · **Role:** Non-normative catalogue and roadmap · **Audience:** Contributors planning beyond the current version

> ## ⚠️ This is not the build target
>
> **The authoritative specification for the version being built is [`agentic-code-review-srs-v1.md`](../agentic-code-review-srs-v1.md).** Where this document and that one differ, **that one wins**.
>
> This document is the **superset catalogue**: every requirement across v1, v2 and v3, kept in one place so that identifiers stay stable and deferred work stays visible. It is the registry the ADRs cite. It is not a specification anyone should implement from, because it describes versions that do not exist yet alongside the one that does.
>
> | If you want… | Read |
> |---|---|
> | What to build now | [`agentic-code-review-srs-v1.md`](../agentic-code-review-srs-v1.md) — normative |
> | Why v1 contains what it contains | [`mvp-scope.md`](./mvp-scope.md) — the selection analysis |
> | What comes after v1, and the requirement identifiers reserved for it | This document |

**Three amendments shaped the roadmap below.**

> **[ADR-0006](../adr/0006-local-cli-core-action-as-adapter.md) (Accepted, 2026-09-08).** The system is **one reviewing core reached through thin surface adapters**. Sections 1.3, 2.2, 2.3.1, 2.6, 3 and 4.10 reflect this. Requirements are surface-independent unless they say otherwise — see the note opening §4.

> **GitHub integration deferred to v3 (2026-09-08).** All GitHub-dependent behaviour — the Action trigger, PR comments, suggested-change blocks, status checks, and the example workflow — moves to **v3** and is listed in §2.3.3. **Requirement identifiers are unchanged**; affected requirements carry a **(v3)** tag in place of their Must/Should tag, so existing cross-references in the ADRs and design documents remain valid.

> **Design-review corrections, SRS v1.1 (2026-09-14).** The design phase found that several requirements specified a *mechanism* where they should have stated a *property*, and that three pairs contradicted each other. [`agentic-code-review-srs-v1.md`](../agentic-code-review-srs-v1.md) §10 records every change; the reasoning is in [`DESIGN_BLOCKERS.md`](../../DESIGN_BLOCKERS.md).
>
> **This catalogue is not rewritten** — it is a historical record as well as a registry, and the text below is what was catalogued on 2026-09-08. But it is the registry, so two things have to be visible here:
>
> **Identifiers reserved by v1.1**, and not to be reused for anything else:
>
> | Identifier | For |
> |---|---|
> | **FR-2.6h** | All simultaneous degradation reasons reported, not one |
> | **FR-5.2a** | Severity vocabulary |
> | **FR-5.2b** | Category vocabulary, closed set |
> | **FR-5.2c** | Evidence reference, or an explicit `unverified` marker |
> | **FR-5.6c** | One repair turn after a failed validation |
> | **FR-5.9** | Structured tool observation with `ok` / `error` / `denied` |
> | **FR-5.10** | No compelled tool call; a reply without one is termination |
> | **FR-6.2f** | A documented, line-independent rule for what counts as a catch |
> | **FR-8.2d** | Tool calls reported as a total **and** a breakdown |
> | **FR-8.2e** | Every degradation recorded in the structured output |
> | **AC-13 … AC-16** | Acceptance criteria for the above |
>
> **Identifiers whose wording changed in v1.1** — the identifier is stable, the text is not, and **v1.1's text governs**: FR-2.2, FR-2.6f, FR-2.6g, FR-3.5, FR-0.3, FR-5.7, FR-5.7a, FR-5.7b, FR-5.7c, FR-8.2a, FR-8.2b, FR-8.2c, FR-10.4c.
>
> ⚠️ **[`agentic-code-review-srs-ar.md`](./agentic-code-review-srs-ar.md) does not reflect any of this** and is stale with respect to the identifiers above.

**One later decision changes nothing below, but contradicts §2.2, and is recorded here so the contradiction is visible.**

> **Open-core business model (2026-10-03).** A business decision, recorded in [`enterpenuership/003-business-model-canvas.md`](./enterpenuership/003-business-model-canvas.md) §5: the command-line tool and its engine stay free and open source, and revenue is planned from a **paid hosted review service**. That is what §2.2 calls "out of scope entirely" and §2.3.2 lists as a hosted GitHub App.
>
> **No requirement, identifier or version is added by it.** v1–v3 remain exactly as catalogued, and the hosted service has no specification, no version and no ADR. Taking it up is a design change, not an addition: it would be the first surface that operates a server and holds server-side state, which §2.2 here, [`agentic-code-review-srs-v1.md`](../agentic-code-review-srs-v1.md) §2.1 and the reasoning of [ADR-0005](../adr/0005-cross-run-memory-as-hidden-comment-ledger.md) ("The product is deliberately **not** a hosted service") all rule out today.
>
> ⚠️ **[`agentic-code-review-srs-ar.md`](./agentic-code-review-srs-ar.md) does not reflect this note either.**

---

## 1. Introduction

### 1.1 Purpose

This document catalogues the requirements for **Agentic Code Review**, an open-source system that performs an autonomous first-pass review on code changes. It records the business case, the scope boundaries, and the full functional requirement set across the planned versions, and it is the registry from which requirement identifiers are drawn.

It is **not** the reference against which the current version is built and evaluated — that is [`agentic-code-review-srs-v1.md`](../agentic-code-review-srs-v1.md). This document's purpose is continuity: it keeps deferred work and its identifiers visible so that later versions extend a stable numbering rather than inventing a new one. Non-functional requirements are addressed in a separate pass (§5, planned).

### 1.2 Intended Audience

- **Contributors** building or extending the system — the primary readers of the functional requirements.
- **Adopters** running the CLI in their projects, and from v3 integrating the Action into their repositories — served by the scope, assumptions, and usability requirements.
- **Reviewers/maintainers** evaluating whether a change meets the specification.

Readers seeking the business rationale need only §1–§2. Readers implementing or testing should continue to the functional requirements (§4).

### 1.3 Product Scope

Agentic Code Review automates the initial review pass on pull requests so human reviewers can concentrate on high-risk changes. It gathers full repository context, executes tests and checks in an isolated sandbox, runs a review agent in a context isolated from any code-writing agent, and proposes fixes as review comments.

It is built as **one reviewing core reached through thin surface adapters**. **v1 ships a single surface: a local command-line tool** a developer runs against their own working tree, staged changes, or a branch range — specified in full in [`agentic-code-review-srs-v1.md`](../agentic-code-review-srs-v1.md). The GitHub Action — which is what addresses the review bottleneck described in §2.1.1 — is deferred to v3 (§2.3.3), and the core is structured so that it arrives as an adapter rather than a rewrite.

The system uses a single free/low-cost AI provider and emits both a human-readable summary and a structured machine-readable artifact. It targets TypeScript/JavaScript repositories. Version boundaries are in §2.3 and Appendix A.

**On the ordering.** Deferring the Action means v1 does not yet address the primary problem statement, which is a review bottleneck on pull requests. v1 is deliberately an engineering milestone rather than a product: it builds and measures the reviewing core on the surface where iteration is fastest. The product claim is made in v3, when the core reaches pull requests.

### 1.4 References

- **Normative specification for the current version — [`agentic-code-review-srs-v1.md`](../agentic-code-review-srs-v1.md)**
- Scope selection analysis — [`mvp-scope.md`](./mvp-scope.md)
- Agentic Code Review — Project Definition — [`Agentic_Code_Review_Problem_Definition_v1.md`](./Agentic_Code_Review_Problem_Definition_v1.md)
- Architecture Decision Records — [`adr/`](../adr/), in particular [ADR-0006](../adr/0006-local-cli-core-action-as-adapter.md) (Accepted), which introduced the two-surface structure
- Agent harness design — [`agent-harness-design.md`](./agent-harness-design.md)
- Non-Functional Requirements — deferred pass (planned, to become §5)

---

## 2. Overall Description

### 2.1 Business Case

#### 2.1.1 Problem Definition

AI-assisted development has sharply increased the volume and size of pull requests, outpacing the capacity of human reviewers and creating a review bottleneck. Existing automated tools address only fragments of the problem: linters catch syntax but miss semantics and cross-file dependencies; single-shot LLM reviewers give shallow line comments without executing code or understanding the wider repository, and — when the same model both writes and reviews — suffer from self-confirmation bias. There is no accessible, budget-conscious tool that performs a genuinely autonomous, context-aware, execution-backed first-pass review while keeping humans focused on the changes that actually carry risk.

#### 2.1.2 Objectives

1. **Automate the first-pass review** so human attention is reserved for high-risk changes.
2. **Ground reviews in real context and execution** — full-repo context, dependency-aware analysis, and sandboxed test/build/scan runs rather than text-only inference.
3. **Eliminate self-confirmation bias** by running the review agent in a fresh context, isolated from any code-writing agent.
4. **Triage by blast radius** — deterministically route PRs so critical changes (security, core logic) get deeper review and trivial ones (docs, dep bumps) can be fast-tracked.
5. **Propose actionable fixes** as review comments, backed by execution evidence (auto-applied remediation is deferred to v2).
6. **Operate within a $20/free budget** by using a single free/low-cost provider (e.g. NVIDIA NIM free tier), with model calls wrapped behind a thin interface so the provider can be swapped later without rearchitecting.
7. **Produce dual output** — human summaries and structured data for downstream automation.
8. **Ship as a usable open-source project** — clear docs, easy adoption, and an extensible base others can build on.

#### 2.1.3 Success Criteria

- The system runs end-to-end on a public repo using only free tiers — via the CLI in v1, via the Action from v3.
- Reviews are grounded in executed test/build results, not text inference alone.
- Findings are emitted in the canonical finding model (§4, FR-0) and serialized to schema-valid JSON.
- A new contributor can adopt the system using the shipped README and docs — the CLI in v1, and the example workflow from v3.

*(Quantitative targets for these criteria are deferred to the NFR pass.)*

### 2.2 Product Perspective

The system is self-contained, not a hosted service. **In v1 it runs on a developer's own machine**, invoking an external AI provider over the network; from v3 it also runs inside the adopter's CI on GitHub-hosted runners. It holds no persistent server-side state — review history lives in local state files in v1, and additionally in PR comments and per-run artifacts from v3. This positions the project deliberately below the complexity of a hosted GitHub App (webhooks, backend, database), which is out of scope entirely.

Internally, the two surfaces are **thin adapters over a shared core**. An adapter may resolve what to review, render findings, and store state; it may not decide what counts as a finding. This constraint is what keeps the two surfaces from becoming two reviewers ([ADR-0006](../adr/0006-local-cli-core-action-as-adapter.md)).

### 2.3 Scope Boundaries

#### 2.3.1 In Scope (v1)

**Specified in [`agentic-code-review-srs-v1.md`](../agentic-code-review-srs-v1.md) §1.2 and §4 — not restated here.**

In outline, v1 is a local CLI — written in Python, reviewing TypeScript ([ADR-0007](../adr/0007-python-harness-typescript-target.md)) — over a TS/JS change set, with `tree-sitter` parsing, related context at depths 0–1 behind a depth-parameterised interface, local execution of tests and type checks with a recorded evidence trail, a single-pass fresh-context review agent, a canonical finding model with terminal and JSON output, and a pattern library with a runnable regression harness.

Note two items this catalogue lists for the CLI surface that v1 does **not** implement, both deferred to v2: deterministic risk triage (FR-3.1–FR-3.4, replaced in v1 by a path-exclusion list) and context depths 2 and above (FR-2.3a, FR-2.3b). The full inclusion and exclusion list, with reasoning, is in [`mvp-scope.md`](./mvp-scope.md) §3 and §4.

#### 2.3.2 Out of Scope (v1)

- Automated/auto-applied remediation and fix-and-verify loops (deferred to v2)
- Languages other than TS/JS
- Hosted GitHub App with webhooks and persistent backend
- Web dashboard / analytics UI
- Non-GitHub platforms (GitLab, Bitbucket)
- Multimodal / architectural-diagram analysis — deferred
- Team governance, RBAC, audit-compliance features
- Self-hosted sandbox infrastructure (gVisor / Firecracker)
- Multi-provider routing, fallback chains, and config-driven provider abstraction

#### 2.3.3 Deferred to v3 — GitHub Integration

Everything requiring the GitHub API, the Actions runtime, or a pull request as the unit of review. These requirements keep their identifiers and are tagged **(v3)** in §4.

| Requirement | What it covers | Why it is GitHub-dependent |
|---|---|---|
| FR-1.1 | Action triggered on PR `opened` / `synchronize` | The Actions runtime and PR events |
| FR-1.3 | Authentication via repo/org secret | v1 reads the provider key from the local environment or config instead |
| FR-1.4 | Skip via label or config flag | Labels are a GitHub concept; the config flag survives in v1 under FR-1.2 |
| FR-2.1 | Check out the PR branch and identify changed files | v1 resolves a local change set instead (FR-10.3a, FR-10.3b) |
| FR-7.1 | Suggested-change blocks in review comments | A GitHub review-comment feature; v1 renders advisory findings to the terminal |
| FR-8.1a–c | The single PR summary comment and its update-in-place behaviour | PR comments |
| FR-8.3 | Non-blocking status/check run | The GitHub checks API |
| FR-9.1 *(partial)* | The example workflow file | The rest of FR-9.1 — README, LICENSE, usage docs — stays in v1 |
| FR-9.2 | End-to-end run on a public repo using a GitHub-hosted runner | v1's equivalent is an end-to-end local run on free provider tiers |

Consequences elsewhere in the document set:

- [ADR-0003](../adr/0003-untrusted-code-isolation-and-fork-triggers.md) — untrusted-code isolation and fork triggers — becomes **a v3 decision**. It has no v1 effect, because a developer reviewing their own working tree crosses no trust boundary.
- [ADR-0005](../adr/0005-cross-run-memory-as-hidden-comment-ledger.md) — the hidden comment ledger — becomes **a v3 decision**. v1 stores per-change state in a local file (FR-10.5).
- [ADR-0006](../adr/0006-local-cli-core-action-as-adapter.md) is unaffected in substance and increases in importance: the adapter seam is now what allows the Action to arrive in v3 as an addition rather than a rewrite.
- The requirement that both surfaces produce identical findings (FR-10.2) becomes testable only in v3, but the constraint it expresses — that no adapter decides what counts as a finding — binds from the first line of v1 code.

### 2.4 Stakeholders

| Stakeholder | Interest |
|---|---|
| Repository maintainers | Reduced review load; trustworthy first-pass triage |
| PR authors (human & AI-assisted) | Fast, actionable, execution-backed feedback |
| Open-source contributors | Clear, extensible codebase and requirements |
| Project maintainer | Shippable, budget-bound, maintainable v1 |

### 2.5 Assumptions & Constraints

- Budget limited to free tiers / a single ~$20 plan; no dedicated GPU or paid inference infrastructure.
- From v3, runs on free GitHub Actions compute, where execution time and resources are bounded by runner limits. In v1 it runs on the developer's own machine.
- On the CLI surface the binding constraint is developer-perceived latency rather than runner minutes, and model cost is borne per invocation by the developer — so the two surfaces are tuned against different budgets ([ADR-0006](../adr/0006-local-cli-core-action-as-adapter.md)).
- Requires repositories with a runnable test suite for execution-backed verification to add value.
- As an open-source tool, model API keys must be handled via repo/org secrets, never hard-coded.
- v1 is single-provider and single-language by deliberate scoping decision, not technical limitation.

### 2.6 Operating Environment

**CLI surface — the only surface in v1**

- **Platform:** a developer workstation — Linux, macOS, or Windows.
- **Trigger:** an explicit command; no CI, no GitHub API, and no repository credentials required.
- **Host runtime:** Python, with `tree-sitter` bindings as a native extension, LangChain for the provider interface, and LangGraph confined to the review step ([ADR-0007](../adr/0007-python-harness-typescript-target.md)).
- **Distribution:** a PyPI package with a console entry point, installed with `uv tool install` or `pipx`. Because `tree-sitter` bindings are a native extension, supported operating systems and Python versions form a distribution contract the Action surface never needed (FR-10.6).
- **Optional prerequisite:** Node.js, for the bundled resolver sidecar that answers depth-1 module resolution from the TypeScript compiler's own algorithm. Required for authoritative depth 1, never for installation; its absence degrades and is reported. Specified normatively as FR-2.6f and FR-2.6g in [`agentic-code-review-srs-v1.md`](../agentic-code-review-srs-v1.md).

**Action surface — v3 (§2.3.3)**

- **Platform:** GitHub (hosted runners, Actions, PR API).
- **Trigger events:** pull request `opened`, `synchronize`.

**All surfaces**

- **External dependency:** one AI model provider reachable over HTTPS (NVIDIA NIM free tier as default).
- **Target repositories:** TypeScript/JavaScript projects with a runnable test script.

---

## 3. Glossary

| Term | Definition |
|---|---|
| **Adapter** | A thin layer translating between a surface and the shared core: it resolves what to review, renders findings, and stores state. It never decides what counts as a finding. |
| **Agentic code review** | An automated review that gathers repository context, executes tools (tests/builds/scans), and reasons over the results — as opposed to static linting or single-shot LLM commenting. |
| **AST (Abstract Syntax Tree)** | A structured tree representation of source code used to analyze symbols, dependencies, and structure. Produced here via `tree-sitter`. |
| **Blast radius** | The potential impact scope of a change, used to assign a risk tier and route review depth. |
| **Change scope** | The answer to "which change is being reviewed?" — unambiguous on the Action surface (PR head vs. base), and a resolved choice on the CLI surface (working tree, staged, or branch range). |
| **Context Gatherer** | The component that checks out the PR, parses changed files, and assembles cross-file review context. |
| **Core (shared core)** | The surface-independent part of the system: change scoping, context gathering, triage, execution, the review agent, and the finding model. Both surfaces run the same core. |
| **Finding model (FR-0)** | The provider-independent internal representation for all review findings; the single canonical structure that downstream outputs are derived from. |
| **Fresh-context review** | Running the review agent in a context isolated from any code-writing agent, to avoid self-confirmation bias. |
| **Fresh-Context Review Agent** | The component that produces findings from the gathered context, execution evidence, and pattern library. |
| **GitHub Action** | A CI workflow unit that runs in a repository's pipeline; the primary product surface (as opposed to a hosted GitHub App), deferred to v3 (§2.3.3). |
| **Host language** | The language the system itself is written in — Python ([ADR-0007](../adr/0007-python-harness-typescript-target.md)). Distinct from the **target language** below. |
| **Module resolution** | Turning an import specifier — the string `'./auth'` or `'@app/db'` — into the file on disk it refers to. `tree-sitter` yields the specifier; resolving it requires the target language's own algorithm, which is why the resolver sidecar exists. |
| **Pattern library** | A configurable set of "wrong vs. correct" examples and project standards the agent applies when generating findings. |
| **PR (Pull Request)** | A proposed set of changes to a repository, the unit reviewed by the system. |
| **Resolver sidecar** | A bundled helper process, in the target language's own toolchain, that answers module-resolution questions for the host process. Private to the context-gathering component; started at most once per invocation, and degraded-but-reported when unavailable (FR-2.6f, FR-2.6g). |
| **Risk tier** | A deterministic classification (e.g. trivial / normal / critical) that drives review depth and optional model selection. |
| **Remediation Engine** | The component responsible for fix proposals; limited to advisory suggestions (auto-apply deferred — see Appendix A). |
| **Suggested-change block** | A GitHub review-comment feature that proposes a specific localized edit the author can accept directly. |
| **Surface** | A way a user reaches the system. v1 has one — the local CLI; the GitHub Action is added in v3. |
| **Target language** | The language of the code being reviewed — TypeScript/JavaScript. Distinct from the **host language** above; see [ADR-0007](../adr/0007-python-harness-typescript-target.md). |
| **Tool Sandbox** | The execution environment where tests, builds, and scans run: the developer's machine in v1, a GitHub-hosted runner from v3. In v1 this is always a subprocess running the project's own toolchain, never the host runtime (FR-4.7). |
| **`tree-sitter`** | An incremental parsing library used to build ASTs for dependency and structure analysis. Used from the host language via its bindings, in-process. It yields the shape of the source text; it does not resolve imports — see **module resolution**. |
| **Must / Should** | Requirement priority tags: **Must** = v1 core; **Should** = v1 if time allows. |
| **NFR** | Non-Functional Requirement (performance, isolation, cost, latency) — addressed in a separate pass. |

---

## 4. Specific Requirements (Functional)

> **Non-normative.** For requirements in the current build target, the authoritative wording — including several that this catalogue does not carry, such as the related-context interface and the per-invocation budget rules — is [`agentic-code-review-srs-v1.md`](../agentic-code-review-srs-v1.md) §4. This section exists to hold the **full identifier registry across versions**, including requirements not yet scheduled.

Requirements are written as testable "the system shall…" statements, grouped by component and mapped to the Module 2 architecture. Each is tagged **Must** or **Should**. Concrete thresholds (time/memory budgets, isolation guarantees) are deferred to §5 (NFR pass).

**Version tags.** A requirement tagged **(v3)** is deferred with GitHub integration (§2.3.3). Its identifier is retained so cross-references stay valid. Of the remainder, [`mvp-scope.md`](./mvp-scope.md) §9 records which are in v1 and which are held for v2.

**Surface applicability.** Unless a requirement names a surface, it belongs to the shared core. In v1 the CLI is the only surface, so core requirements are exercised there.

| Group | Applies to |
|---|---|
| FR-1 — Trigger & Integration | Mostly v3 (Action); FR-1.2 configuration is core and binds in v1 |
| FR-7, FR-8 — Fix suggestions and output | FR-7.1 and FR-8.1/FR-8.3 are v3 (comments, suggestion blocks, checks); FR-8.2 JSON output and FR-10.4 terminal rendering are v1 |
| FR-10 — CLI surface | v1, and the only surface until v3 |

Two further splits are recorded in the ADRs rather than here, pending an NFR pass: the isolation of untrusted PR code ([ADR-0003](../adr/0003-untrusted-code-isolation-and-fork-triggers.md), a v3 concern) and whether the review agent may itself trigger a test run ([ADR-0002](../adr/0002-pipeline-initiates-test-execution.md), forbidden on the Action, affordable on the CLI and therefore permitted in v1 under a call quota).

### 4.0 FR-0 — Canonical Data Model (the "finding model")

The single canonical structure for all review findings. Defined once here; every other requirement references FR-0 rather than redefining it.

- **FR-0.1 (Must)** The system shall define a provider-independent internal finding representation ("the finding model") as the single canonical structure for all review findings.
- **FR-0.2 (Must)** All model output shall be converted into the finding model before any downstream use; no component shall consume raw provider responses directly.
- **FR-0.3 (Must)** A new provider shall be integratable by mapping its output to the finding model without changes to downstream components.
- **FR-0.4 (Must)** The finding model shall have a documented, versioned schema carrying a schema-version field.

### 4.1 FR-1 — Trigger & Integration

- **FR-1.1 (v3)** The system shall run as a GitHub Action triggered on pull request `opened` and `synchronize` (new commits) events. *(v1 equivalent: FR-10.1, an explicitly invoked command.)*
- **FR-1.2a (Must)** The system shall read configuration from `.agentic-review.yml` at the repo root when present.
- **FR-1.2b (Must)** When the file is absent, the system shall apply a documented built-in default configuration.
- **FR-1.2c (Must)** When the file is present but a field is missing, the system shall apply that field's documented default value.
- **FR-1.2d (Must)** When the file is present but malformed (invalid YAML or schema), the system shall fail with an error message identifying the offending field, and shall not fall back silently.
- **FR-1.3 (v3)** The system shall authenticate to the model provider using a repo/org secret, never a hard-coded key. *(v1 equivalent: FR-1.3a.)*
- **FR-1.3a (Must)** The system shall read the model provider credential from the local environment or user-level configuration, never from a hard-coded key and never from a file committed to the repository.
- **FR-1.4 (v3)** The system shall allow the Action to be skipped via a label or config flag (e.g. `skip-agentic-review`). *(The config-flag half is available in v1 via FR-1.2; only the label mechanism is GitHub-dependent.)*

*(Documented default configuration values live in the config-schema appendix, not in requirement text.)*

### 4.2 FR-2 — Context Gathering

- **FR-2.1 (v3)** The system shall check out the PR branch and identify the changed files and diff hunks. *(v1 equivalent: FR-10.3a and FR-10.3b resolve a local change set into the same changed-files-and-hunks structure. Everything downstream of this point is shared.)*
- **FR-2.2 (Must)** The system shall build a `tree-sitter` AST for changed TS/JS files.
- **FR-2.3a (Must)** For each symbol modified in the diff, the system shall identify the files that import or export that symbol.
- **FR-2.3b (Must)** For each modified function or method, the system shall identify its direct call sites within the repository.
- **FR-2.3c (Must)** The system shall include the source of these related definitions and call sites in the review context passed to the agent, up to the context cap (FR-2.5).
- **FR-2.3d (Should)** The system shall record which related files were included and why (imported-by / calls / called-by), for traceability.
- **FR-2.4 (Should)** The system shall include relevant surrounding context (function/class boundaries, type definitions) rather than raw line windows.
- **FR-2.5 (Should)** The system shall cap context size to stay within model token and runner limits, degrading gracefully when exceeded.

### 4.3 FR-3 — Risk Triage (Blast Radius)

- **FR-3.1 (Must)** The system shall deterministically classify each PR into a risk tier (e.g. trivial / normal / critical) using file-path and change-type rules.
- **FR-3.2 (Must)** The triage rules shall be configurable (path globs → risk tier) so projects can mark security/core paths as critical.
- **FR-3.3 (Must)** The system shall route review depth by tier (fast-track trivial changes, deeper review for critical).
- **FR-3.4 (Should)** The system shall optionally select a lighter vs. stronger model by tier.

### 4.4 FR-4 — Sandboxed Execution

- **FR-4.1 (Must)** The system shall run the project's test suite in its execution environment — the developer's machine in v1, an isolated runner from v3 — and capture pass/fail results and output.
- **FR-4.2 (Must)** The system shall run build/type checks (e.g. `tsc`) and capture results.
- **FR-4.3 (Should)** The system shall run `npm audit` and capture its findings.
- **FR-4.4a (Must)** The system shall enforce a configurable time budget on the execution phase and terminate execution when it is exceeded.
- **FR-4.4b (Must)** On termination due to timeout, the system shall mark execution as `timed-out`, skip remaining checks, and continue to produce a review reporting the timeout.
- **FR-4.5a (Must)** The system shall record, for each check, whether it was run, skipped, or errored.
- **FR-4.5b (Must)** The system shall record each executed check's pass/fail result and captured output.
- **FR-4.5c (Must)** The system shall make this execution record available to the review agent (FR-5) and include it in the structured output (FR-8.2).

*(Isolation guarantees and specific time/resource budget values are deferred to §5, the NFR pass.)*

*(Because the harness and the reviewed project no longer share a runtime, checks are invoked through the project's own toolchain as subprocesses and the harness never imports the project's dependencies. That is stated normatively for the build target as FR-4.7 in [`agentic-code-review-srs-v1.md`](../agentic-code-review-srs-v1.md); it is a consequence of [ADR-0007](../adr/0007-python-harness-typescript-target.md), not a change to FR-4.1 or FR-4.2, which never named a runtime. FR-4.3 is likewise unaffected: `npm audit` is a property of the project under review.)*

### 4.5 FR-5 — Fresh-Context Review Agent

- **FR-5.1 (Must)** The review agent shall operate in a context isolated from any code-writing agent (no shared history/state).
- **FR-5.2 (Must)** Each finding shall contain: file path, line or line-range, severity, category, rationale, and (optionally) a suggested-fix reference — conforming to the finding model (FR-0).
- **FR-5.3 (Must)** The agent shall incorporate execution results (FR-4) and pattern-library rules (FR-6) into its findings.
- **FR-5.4 (Should)** The agent shall distinguish blocking issues from non-blocking suggestions.
- **FR-5.5 (Should)** The agent shall avoid duplicate/near-duplicate comments on unchanged findings across re-runs.
- **FR-5.6 (Must)** The agent's output shall conform to the finding model (FR-0); FR-8 outputs shall be derived from it, not produced independently by the model.

### 4.6 FR-6 — Pattern Library

- **FR-6.1 (Must)** The system shall load a configurable pattern library of "wrong vs. correct" examples and project standards.
- **FR-6.2a (Must)** When a finding is generated from a pattern-library rule, the finding shall reference the identifier of the matched rule.
- **FR-6.2b (Must)** The system shall support a regression set of pattern examples with expected outcomes, runnable as a test, so pattern-matching behavior can be verified and monitored across changes.
- **FR-6.2c (Should)** The system shall report pattern-library coverage (which rules fired) in the structured output.
- **FR-6.3 (Should)** The system shall ship a default TS/JS pattern set that projects can extend or override.

### 4.7 FR-7 — Fix Suggestions (advisory only)

- **FR-7.1 (v3)** The system shall propose fixes as review comments, using GitHub suggested-change blocks where the fix is a localized edit. *(v1 equivalent: FR-7.1a.)*
- **FR-7.1a (Should)** The system shall include a proposed replacement snippet with a finding where the fix is a localized edit, rendered in the terminal and carried in the structured output.
- **FR-7.2 (Must)** Suggestions shall be advisory only — the system shall not commit, push, or auto-apply changes.
- **FR-7.3 (Should)** Each suggestion shall link to the finding and evidence that motivated it.

### 4.8 FR-8 — Output

- **FR-8.1a (v3)** The system shall post exactly one summary comment per review run on the PR. *(v1 equivalent: FR-10.4a, one terminal summary per invocation.)*
- **FR-8.1b (Must)** The summary — a PR comment from v3, the terminal output in v1 — shall state the risk tier, the checks run and their results, the count of findings by severity, and an overall verdict.
- **FR-8.1c (v3)** On re-run, the system shall update its existing summary comment rather than post a new one.
- **FR-8.2a (Must)** The system shall serialize the finding model (FR-0) to JSON as a machine-readable artifact.
- **FR-8.2b (Must)** The JSON shall conform to the finding model's versioned schema (FR-0.4), including findings, severities, evidence/execution record, and triage result.
- **FR-8.3 (v3)** The system shall set a non-blocking status/check summarizing the review outcome. *(v1 equivalent: FR-10.4c, a documented exit code.)*
- **FR-8.4 (Should)** The structured output schema shall be documented and versioned (see FR-0.4).

### 4.9 FR-9 — Open-Source Usability

- **FR-9.1 (Must)** The system shall ship with README, LICENSE, and CLI usage documentation. *(The example workflow file is v3, with FR-1.1.)*
- **FR-9.2 (v3)** The system shall run against a public repo using only free tiers (GitHub-hosted runner + free model provider). *(v1 equivalent: FR-9.2a.)*
- **FR-9.2a (Must)** The system shall complete an end-to-end review of a public TS/JS repository on a developer machine, using only a free model provider tier.
- **FR-9.3 (Should)** The system shall provide clear failure messages when prerequisites (e.g. test script, API key) are missing.

### 4.10 FR-10 — CLI Surface

Added by [ADR-0006](../adr/0006-local-cli-core-action-as-adapter.md). The CLI is the primary development and testing surface for the shared core, and a shipped surface in its own right.

- **FR-10.1 (Must)** The system shall provide a command-line interface that reviews a local change set without requiring GitHub API access or repository credentials.
- **FR-10.2 (Must)** For an identical change set, configuration, and model, the CLI and the Action shall produce the same findings. Neither surface shall contain logic that determines whether something is a finding.
- **FR-10.3a (Must)** The CLI shall resolve the change scope from an explicit selection among: uncommitted working-tree changes, staged changes only, or a comparison against a named branch or commit.
- **FR-10.3b (Must)** The CLI shall apply a documented default change scope when none is specified, and shall state the resolved scope in its output.
- **FR-10.4a (Must)** The CLI shall render findings to the terminal, derived from the finding model (FR-0) and not produced independently.
- **FR-10.4b (Must)** The CLI shall provide machine-readable output conforming to the same versioned schema as the Action's JSON artifact (FR-8.2b).
- **FR-10.4c (Should)** The CLI shall exit with a status code reflecting the review outcome, documented and stable across versions.
- **FR-10.5 (Should)** The CLI shall persist per-change-set state locally so repeated invocations can suppress findings already reported, using the same fingerprint definition as the Action surface.
- **FR-10.6 (Should)** The system shall document the operating systems and Python versions the CLI supports — together with any minimum version of the optional Node.js runtime used by the resolver sidecar — and shall fail with a clear message on an unsupported combination. *(Reworded, not renumbered, when the host language was decided in [ADR-0007](../adr/0007-python-harness-typescript-target.md); it previously named Node.js versions, on the assumption that the harness shared a runtime with the code it reviews.)*
- **FR-10.7 (Should)** The CLI shall tolerate a working tree that does not fully parse or type-check, and shall distinguish incomplete code from defective code in its findings.

---

## 5. Non-Functional Requirements (Planned)

Deferred to a dedicated pass. Open items carried in from the functional work:

- Execution isolation guarantees and the security model for untrusted PR code (residue of former FR-4.4). **A v3 concern** — v1 executes only the developer's own code, on their own machine.
- Concrete budgets: max execution runtime, memory cap, max context tokens, max PR size handled.
- Latency / cost targets per risk tier.
- Quantitative targets for the §2.1.3 success criteria.

---

## Appendix A — Version roadmap

| Version | Contents |
|---|---|
| **v1** | **Baselined and specified in [`agentic-code-review-srs-v1.md`](../agentic-code-review-srs-v1.md).** The local CLI: change-set resolution, parsing and depth-0/1 related context, execution evidence, a single-pass review agent, the finding model, a five-rule pattern library with its regression harness, terminal and JSON output. |
| **v2** | The requirements held back from v1 — context depths 2+ behind the interface v1 establishes, risk triage, the agent tool loop, dependency audit, cross-run de-duplication, fix snippets, a broad rule set, and the platform support matrix. Enumerated in [`agentic-code-review-srs-v1.md`](../agentic-code-review-srs-v1.md) §7. |
| **v3** | **GitHub integration** (§2.3.3): the Action, PR comments, suggested-change blocks, status checks, untrusted-code isolation ([ADR-0003](../adr/0003-untrusted-code-isolation-and-fork-triggers.md)), and the cross-run comment ledger ([ADR-0005](../adr/0005-cross-run-memory-as-hidden-comment-ledger.md)). |
| **Later** | Automated/auto-applied remediation and fix-and-verify loops · advanced scanning: secret detection (e.g. TruffleHog), OWASP tooling, supply-chain / dependency-provenance analysis · languages other than TS/JS · multi-provider routing and fallback chains (note: the FR-0 finding model keeps this a data-mapping task, not a rearchitecture). |

> **Note on ordering.** GitHub integration now sits *after* the local product is complete. That is the intended sequence — build and measure the reviewing core where iteration is cheapest, then attach it to pull requests — but it does mean the primary problem statement (§2.1.1, a review bottleneck on pull requests) is not addressed until v3. See §1.3.
