# Feature Inventory — Planned (v1 / v2) and Candidate Features

Derived from [`agentic-code-review-srs.md`](./agentic-code-review-srs.md) (planned work) and [`tool-reference.md`](./tool-reference.md) (candidate features observed in comparable tools). Positioning context lives in [`competitive-landscape.md`](./competitive-landscape.md).

> **Updated for [ADR-0006](../adr/0006-local-cli-core-action-as-adapter.md) (Accepted).** The system is **one core reached through surface adapters**. Section 1 below is unchanged — those requirements are surface-independent — but §4 records what the decision adds, removes, and re-scopes, and the local CLI has moved from a version 2 candidate to version 1 core.
>
> **Superseded in part (2026-09-08).** GitHub integration has since been deferred to **v3** ([SRS §2.3.3](./agentic-code-review-srs.md)), so v1 is CLI-only. The version labels in §1 and §2 below are therefore **stale for the GitHub-dependent rows** — FR-1.1, FR-1.3, FR-1.4, FR-2.1, FR-7.1, FR-8.1a, FR-8.1c, FR-8.3 and FR-9.2 are now v3, and the Action-surface rows in §4.2 move with them. Complexity estimates are unaffected. For the current shape of the first increment, read [`mvp-scope.md`](./mvp-scope.md), which supersedes §5 below.

**Complexity scale** — an estimate of build effort for this project's scope, not of value:

| Level | Meaning |
|---|---|
| **Low** | Config, glue, or templating. Hours to a day. No new subsystem. |
| **Medium** | A self-contained module with real logic and tests. Days. |
| **High** | Cross-cutting subsystem, new analysis technique, or state that must persist across runs. Weeks. |
| **Very High** | Changes the product's architecture or operating model (backend, sandbox infra, multi-language). Beyond a v1/v2 budget without a rethink. |

**Priority tags** follow the SRS: **Must** = v1 core · **Should** = v1 if time allows.

---

## 1. Version 1 — planned features

### 1.1 Canonical data model (FR-0)

| # | Feature | Description | Priority | Complexity |
|---|---|---|---|---|
| FR-0.1 | Finding model | Provider-independent internal representation; the single canonical structure all findings use | Must | Medium |
| FR-0.2 | Mandatory normalization | All model output converted to the finding model; no component reads raw provider responses | Must | Medium |
| FR-0.3 | Provider-mapping seam | A new provider integrates by mapping output to the finding model, with no downstream changes | Must | Medium |
| FR-0.4 | Versioned schema | Documented schema carrying a `schema-version` field | Must | Low |

### 1.2 Trigger & integration (FR-1)

| # | Feature | Description | Priority | Complexity |
|---|---|---|---|---|
| FR-1.1 | PR-triggered Action | Runs on pull request `opened` and `synchronize` | Must | Low |
| FR-1.2a–c | Config file + defaults | Reads `.agentic-review.yml`; documented built-in defaults for absent file and missing fields | Must | Medium |
| FR-1.2d | Config validation | Malformed YAML/schema fails loudly, naming the offending field; no silent fallback | Must | Medium |
| FR-1.3 | Secret-based auth | Provider key supplied via repo/org secret, never hard-coded | Must | Low |
| FR-1.4 | Skip mechanism | Label or config flag (e.g. `skip-agentic-review`) bypasses the run | Should | Low |

### 1.3 Context gathering (FR-2)

| # | Feature | Description | Priority | Complexity |
|---|---|---|---|---|
| FR-2.1 | Checkout & diff extraction | Check out the PR branch; identify changed files and diff hunks | Must | Low |
| FR-2.2 | `tree-sitter` AST | Build ASTs for changed TS/JS files | Must | Medium |
| FR-2.3a | Import/export graph | For each modified symbol, find the files that import or export it | Must | High |
| FR-2.3b | Call-site resolution | For each modified function/method, find its direct call sites in the repo | Must | High |
| FR-2.3c | Context assembly | Include related definitions and call sites in the agent's context, within the cap | Must | Medium |
| FR-2.3d | Inclusion traceability | Record which related files were pulled in and why (imported-by / calls / called-by) | Should | Low |
| FR-2.4 | Semantic windows | Use function/class/type boundaries instead of raw line windows | Should | Medium |
| FR-2.5 | Context capping | Stay within token and runner limits, degrading gracefully when exceeded | Should | Medium |

### 1.4 Risk triage (FR-3)

| # | Feature | Description | Priority | Complexity |
|---|---|---|---|---|
| FR-3.1 | Deterministic risk tiering | Classify each PR (trivial / normal / critical) from file-path and change-type rules | Must | Medium |
| FR-3.2 | Configurable triage rules | Path globs → risk tier, so projects can mark security/core paths critical | Must | Low |
| FR-3.3 | Depth routing | Fast-track trivial changes; deeper review for critical ones | Must | Medium |
| FR-3.4 | Model selection by tier | Optionally pick a lighter or stronger model per tier | Should | Low |

### 1.5 Sandboxed execution (FR-4)

| # | Feature | Description | Priority | Complexity |
|---|---|---|---|---|
| FR-4.1 | Test-suite execution | Run the project's tests in the runner; capture pass/fail and output | Must | Medium |
| FR-4.2 | Build / type check | Run build and type checks (e.g. `tsc`) and capture results | Must | Low |
| FR-4.3 | Dependency audit | Run `npm audit` and capture findings | Should | Low |
| FR-4.4a–b | Execution time budget | Configurable budget; on timeout mark `timed-out`, skip remaining checks, still produce a review | Must | Medium |
| FR-4.5a–c | Execution record | Per-check run/skipped/errored status, results and output; exposed to the agent and to JSON output | Must | Medium |

### 1.6 Fresh-context review agent (FR-5)

| # | Feature | Description | Priority | Complexity |
|---|---|---|---|---|
| FR-5.1 | Context isolation | Review agent runs with no shared history/state with any code-writing agent | Must | Medium |
| FR-5.2 | Structured findings | Each finding carries path, line/range, severity, category, rationale, optional fix reference | Must | Medium |
| FR-5.3 | Evidence-grounded reasoning | Fold execution results (FR-4) and pattern rules (FR-6) into the findings | Must | High |
| FR-5.4 | Blocking vs. advisory | Distinguish blocking issues from non-blocking suggestions | Should | Low |
| FR-5.5 | Cross-run de-duplication | Avoid repeating duplicate/near-duplicate comments on re-runs | Should | High |
| FR-5.6 | Output conformance | Agent output validated against the finding model; FR-8 outputs derived from it | Must | High |

### 1.7 Pattern library (FR-6)

| # | Feature | Description | Priority | Complexity |
|---|---|---|---|---|
| FR-6.1 | Pattern library loader | Load configurable "wrong vs. correct" examples and project standards | Must | Medium |
| FR-6.2a | Rule attribution | Findings from a pattern rule reference that rule's identifier | Must | Low |
| FR-6.2b | Regression suite | Pattern examples with expected outcomes, runnable as a test to monitor matching behavior | Must | Medium |
| FR-6.2c | Coverage reporting | Report which rules fired, in the structured output | Should | Low |
| FR-6.3 | Default TS/JS pattern set | Ship a baseline set projects can extend or override | Should | Medium |

### 1.8 Fix suggestions (FR-7)

| # | Feature | Description | Priority | Complexity |
|---|---|---|---|---|
| FR-7.1 | Suggested-change comments | Propose fixes as review comments, using GitHub suggestion blocks for localized edits | Must | Medium |
| FR-7.2 | Advisory-only guarantee | Never commit, push, or auto-apply changes in v1 | Must | Low |
| FR-7.3 | Evidence linkage | Each suggestion links back to the finding and evidence behind it | Should | Low |

### 1.9 Output (FR-8)

| # | Feature | Description | Priority | Complexity |
|---|---|---|---|---|
| FR-8.1a–b | Single summary comment | Exactly one summary per run: risk tier, checks run and results, severity counts, verdict | Must | Medium |
| FR-8.1c | Comment update on re-run | Update the existing summary rather than posting a new one | Should | Low |
| FR-8.2a–b | JSON artifact | Serialize the finding model to schema-valid JSON (findings, severities, evidence, triage) | Must | Low |
| FR-8.3 | Non-blocking status check | Publish a check/status summarizing the outcome without blocking merges | Should | Low |
| FR-8.4 | Documented output schema | Schema documented and versioned alongside FR-0.4 | Should | Low |

### 1.10 Open-source usability (FR-9)

| # | Feature | Description | Priority | Complexity |
|---|---|---|---|---|
| FR-9.1 | Project hygiene | README, LICENSE, usage docs, example workflow file | Must | Low |
| FR-9.2 | Free-tier end-to-end run | Works on a public repo using only a hosted runner and a free model tier | Must | Medium |
| FR-9.3 | Actionable failure messages | Clear errors when prerequisites (test script, API key) are missing | Should | Low |

---

## 2. Version 2 and deferred work

Sources: SRS §2.3.2 (out of scope for v1), §5 (NFR pass), Appendix A.

| Feature | Description | Source | Complexity |
|---|---|---|---|
| Auto-applied remediation | Commit/push fixes instead of only suggesting them | Appendix A | High |
| Fix-and-verify loop | Apply a fix, re-run tests, iterate until green or give up | Appendix A | Very High |
| Secret detection | Scan the diff for leaked credentials (e.g. TruffleHog) | Appendix A | Medium |
| OWASP / SAST scanning | Security-focused static analysis beyond `npm audit` | Appendix A | Medium |
| Supply-chain & provenance analysis | Dependency provenance and supply-chain risk checks | Appendix A | High |
| Additional languages | Support beyond TS/JS (new grammars, runners, pattern sets) | §2.3.2 | High |
| Multi-provider routing & fallback | Provider chains and failover; a data-mapping task thanks to FR-0 | Appendix A | Medium |
| Config-driven provider abstraction | Provider selection as user configuration rather than a build-time choice | §2.3.2 | Medium |
| Hosted GitHub App | Webhooks, backend, persistent store — a different operating model. *Since 2026-10-03 this is the closest catalogued item to the paid hosted review service of the open-core model ([canvas §5](./003-business-model-canvas.md)); it is still unversioned and unspecified* | §2.3.2 | Very High |
| Web dashboard / analytics UI | Cross-PR trends, resolution rates, risk concentration | §2.3.2 | High |
| Non-GitHub platforms | GitLab, Bitbucket support | §2.3.2 | High |
| Multimodal / architectural-diagram analysis | Reason over or emit diagrams of architectural impact | §2.3.2 | High |
| Team governance, RBAC, audit compliance | Org-level roles, policy, audit trail | §2.3.2 | High |
| Self-hosted sandbox infrastructure | gVisor / Firecracker isolation instead of hosted runners | §2.3.2 | Very High |
| Execution isolation & untrusted-code security model | Formal guarantees for running PR code (residue of former FR-4.4) | §5 NFR | High |
| Concrete resource budgets | Max runtime, memory cap, context tokens, max PR size | §5 NFR | Medium |
| Latency / cost targets per risk tier | Per-tier performance and spend envelopes | §5 NFR | Medium |
| Quantitative success criteria | Measurable targets for the §2.1.3 criteria (incl. false-positive rate) | §5 NFR | Medium |

---

## 3. Candidate features from the tool reference

Features observed in Greptile, CodeRabbit, Qodo, Claude Code Review, Danger/DangerJS and Graphite, assessed for this project. **Fit** is a suggestion, not a commitment.

| Feature | Description | Seen in | Fit | Complexity |
|---|---|---|---|---|
| Finding verification pass | Re-check candidate findings against actual code behavior before posting, to cut false positives | Claude Code, CodeRabbit | v1 stretch — partially covered by FR-4 execution evidence | High |
| Three-level severity incl. "pre-existing" | Separate Important / Nit / Pre-existing so untouched legacy issues don't read as regressions | Claude Code | v1 — small extension of FR-5.2 | Low |
| Machine-readable comment payload | Embed parseable per-severity counts in the check-run details for `gh`/`jq` consumers | Claude Code | v1 — complements the FR-8.2 artifact | Low |
| Manual re-review trigger | `@bot review` mention in addition to open/push triggers | Claude Code | v1 — extends FR-1.1 | Low |
| Fork-PR safety policy | Run on fork PRs only by explicit request, since fork code is untrusted | Claude Code | v1 — a real security gap in the current SRS | Medium |
| In-repo review instructions file | A `REVIEW.md`-style file for severity calibration, nit caps, skip rules | Claude Code | v1 — natural companion to FR-1.2 and FR-6 | Low |
| Nit caps & re-review convergence | Bound the number of low-severity comments; converge across repeated runs | Claude Code | v1 — strengthens FR-5.5, the main anti-noise guard | Medium |
| Spend cap / budget guard | Configurable ceiling on tokens or calls per run and per month | Claude Code, Greptile credits | v1 — directly serves the $20 budget objective | Medium |
| Local CLI review mode | Review a diff on the developer's machine before opening a PR | Greptile, CodeRabbit, Claude Code | **v1 core** — adopted in [ADR-0006](../adr/0006-local-cli-core-action-as-adapter.md); see §4 | Medium |
| Dangerfile-style user rules | Let repos author executable process rules in-repo, with a plugin system for sharing | Danger | v2 — proven ergonomic model for FR-6 config UX | Medium |
| Process checks (CHANGELOG, ticket link, labels) | Deterministic PR-hygiene assertions, cheap and model-free | Danger | v2 — or compose with DangerJS instead of rebuilding | Low |
| Whole-repo index / codegraph | Persistent semantic index of the repository rather than per-run AST walks | Greptile, CodeRabbit, Qodo | v2 — a more ambitious cousin of FR-2.3; needs cross-run state | High |
| Self-learning rules from PR history | Derive coding standards from past PRs and reviewer behavior | Qodo, CodeRabbit "Learnings" | v2+ — requires persistence the Action model lacks | Very High |
| Rule effectiveness & decay metrics | Measure which rules fire usefully; surface conflicts and stale rules | Qodo | v2 — pairs with FR-6.2c coverage reporting | High |
| Business-context ingestion | Pull requirements from linked issues/PRDs to catch requirements gaps | Qodo, CodeRabbit | v2 — GitHub issue text is cheap to fetch | Medium |
| Cross-repo breaking-change detection | Flag changes that break dependent repositories | Qodo | Out of scope — needs multi-repo indexing | Very High |
| PR triage scoring & reviewer routing | Score by risk/effort/complexity and auto-assign reviewers | CodeRabbit | v2 — FR-3 already computes the risk signal | Medium |
| Semantic diff / change explainability | Explain large diffs in intent terms rather than line terms | CodeRabbit Change Stack | v2 | High |
| Conversational follow-up on comments | Reply to reviewer questions in-thread with repo context | CodeRabbit, Graphite | v2 — needs a second trigger path and thread state | High |
| One-click committable fixes | Suggestions the author accepts and commits directly | CodeRabbit, Graphite | v1 — FR-7.1 already targets suggestion blocks | Medium |
| Runtime validation of changes | Execute the changed code paths, not just the suite (Greptile "TREX") | Greptile | v2 — a deeper form of the FR-4 differentiator | Very High |
| Continuous security monitoring | Scan the default branch on a schedule, not only on PRs | CodeRabbit | Out of scope — implies a service, not an Action | High |
| Sensitive-information filters | Redact secrets/PII from context before it leaves for the provider | Graphite | v1 — cheap, and a trust prerequisite for adopters | Low |
| Data-retention posture statement | Document what is sent to the provider and what is retained | Qodo | v1 — documentation, not code | Low |
| IDE integration | Same review engine inside VS Code / JetBrains | Qodo, CodeRabbit | Out of scope for v1/v2 | High |
| Chat/Slack notifications | Push review summaries to a team channel | CodeRabbit | v2 — thin layer over the FR-8.2 JSON | Medium |
| Stacked / small-PR support | Handle a series of dependent PRs as one logical change | Graphite | Out of scope — a workflow product, not a reviewer | High |
| Self-hosting / enterprise deployment | Run the engine on adopter-controlled infrastructure | Greptile, Qodo | Already inherent — the Action is open source and forkable | Low |

---

## 4. Impact of ADR-0006 — two surfaces over one core

[ADR-0006](../adr/0006-local-cli-core-action-as-adapter.md) makes the reviewing core a local command-line tool and the GitHub Action an adapter over it. Both ship in version 1. This changes the feature set in three ways.

### 4.1 Added to version 1

| Feature | Description | Complexity |
|---|---|---|
| CLI entry point and packaging | A PyPI package with a console entry point, replacing part of the Action packaging work | Low |
| Change-scope resolution | Decide and expose what "review my changes" means: working tree, staged only, against the default branch, or since the branch point | **Medium** — ambiguous by nature, and the default silently changes what gets reviewed |
| Terminal renderer | Streaming output, progress while the model thinks, terminal-versus-pipe detection, colour, meaningful exit codes | Medium |
| Machine-readable CLI output | The same finding model serialised for scripting, mirroring the Action's JSON artifact | Low |
| Local state file | Tier-3 memory as a gitignored file instead of a hidden comment ledger | Low |
| Platform distribution | Native `tree-sitter` parser wheels per operating system and Python version, plus the bundled resolver sidecar carried as package data | **Medium–High** — the largest single new item; the Action made it free by controlling the machine |
| Resolver sidecar | A bundled script in the target language's own toolchain answering depth-1 module resolution, started once per invocation, degrading and reporting when absent (FR-2.6f, FR-2.6g) | **Medium** — a second language in the build, but confined behind one interface |
| Configuration and cache discovery | Repository-level and user-level configuration and their merge order; a cache location that behaves on every platform | Low |
| Tolerating code that does not compile | A working tree can be mid-edit; the agent must distinguish *wrong* from *unfinished* | Low–Medium |
| Quota'd execution tool | A narrow `run_single_test_file` the model may call, affordable only where dependencies are warm | Low |

### 4.2 Re-scoped, not removed

| Feature | New scope |
|---|---|
| Untrusted-code isolation and fork trigger policy | GitHub Action adapter only — no trust boundary exists locally |
| Hidden comment ledger | GitHub Action adapter only — the CLI has a filesystem |
| Suggested-change block positioning | GitHub Action adapter only — the CLI renders a patch instead |
| Summary comment lifecycle | GitHub Action adapter only |
| Pipeline-owned test execution | Binding on the Action; relaxed on the CLI, where a targeted run costs seconds rather than minutes |

### 4.3 Unchanged

The finding model, context gathering and the symbol graph, risk triage, the pattern library, the review agent and its tool surface, and the structured-output mechanism are all surface-independent. That is most of the intellectual content of section 1, and it is the point of the split.

### 4.4 Net effect on effort

Raw effort falls, but the shape matters more than the number. The work removed from the critical path — untrusted execution and the GitHub review-comment position API — is security-consequential and open-endedly fiddly. The work added is conventional command-line engineering with well-trodden solutions, apart from native-module distribution, which genuinely fails on other people's machines rather than ours.

The decisive gain is not effort at all: it is that the least estimable work in the whole plan — prompt and context tuning, which needs hundreds of qualitative iterations — moves from a four-minute continuous-integration loop to a few seconds.

---

## 5. Suggested near-term picks

Highest value per unit of complexity, drawn from §3 and §4 and consistent with the v1 scope:

0. **Change-scope resolution** (Medium) — new, and now first: nothing on the CLI can be built until "review my changes" has a defined meaning, and the choice silently determines what gets reviewed.
1. **Fork-PR safety policy** (Medium) — the SRS runs untrusted PR code in the sandbox with no stated gate. Decided in [ADR-0003](../adr/0003-untrusted-code-isolation-and-fork-triggers.md) but not yet reflected in the requirements; it closes a security gap rather than adding surface, and after [ADR-0006](../adr/0006-local-cli-core-action-as-adapter.md) it is confined to the Action adapter.
2. **Sensitive-information filtering** (Low) — small, and a precondition for adopters sending code to a third-party provider.
3. **Spend cap / budget guard** (Medium) — makes objective 6 ($20/free budget) enforceable instead of aspirational.
4. **"Pre-existing" severity + nit caps** (Low/Medium) — the cheapest available defense against the noise problem flagged in `competitive-landscape.md` §"Honest limitations".
5. **Machine-readable check-run payload** (Low) — a few lines on top of FR-8.2, and it makes the output consumable without downloading the artifact.
