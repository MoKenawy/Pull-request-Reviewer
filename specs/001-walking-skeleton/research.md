# Research: Walking Skeleton — Review a Change, Diff Only

**Feature**: [spec.md](./spec.md) · **Plan**: [plan.md](./plan.md) · **Date**: 2026-09-17

Phase 0 output. Each entry: **Decision**, **Rationale**, **Alternatives considered**. Entries marked
**verified** were checked against installed libraries in a throwaway environment on 2026-09-17;
everything else is reasoning from the normative documents.

Nothing here adds or relaxes a requirement. Where the documents are silent, the decision is marked
**design gap** and listed in [plan.md](./plan.md#design-gaps-raised-by-this-plan) for write-back.

---

## R-1 · Python version and project tooling

- **Decision**: `requires-python = ">=3.12"`. Project managed with **uv** (`uv sync`, `uv run`,
  `uv.lock` committed). Build backend **hatchling**. Tested on CPython 3.12 (locally, Windows) and in
  CI on 3.12 and 3.13, Linux and Windows.
- **Rationale**: 3.12 is installed on the maintainer's machine (`uv python list`) and supported by
  every dependency below. The stack mandates a PyPI wheel with a console entry point (§3.1); hatchling
  handles package data, which the resolver bundle will need in feature 004. FR-10.6 defers a formal
  support matrix to v2. v1 only has to say what it was tested on, and the CI matrix is that
  statement.
- **Alternatives**: 3.13 floor (gets `PurePath.full_match` for `**` globs, but drops a Python the
  maintainer already has, to save about 20 lines, see R-6); `uv_build` backend (newer, and less proven
  with package data); Poetry (a second lockfile format for no gain over uv).

## R-2 · Dependencies and version pins

- **Decision**: runtime `pydantic`, `pyyaml`, `typer`, `rich`, `langchain-core`, `langchain-openai`,
  `langgraph`. Dev `pytest`, `import-linter`, `jsonschema`. **Exact pins live in `uv.lock`** and are
  recorded in `Docs/technical_stack.md` §7 **in the commit that first installs them** (stack §7 rule).
  Resolved on 2026-09-17 for Python 3.12 (**verified** with `uv pip compile`): pydantic 2.13.5 ·
  pyyaml 6.0.3 · typer 0.27.2 · rich 15.0.0 · langchain-core 1.6.3 · langchain-openai 1.6.2 ·
  langgraph 1.2.11 · openai 3.14.1 (transitive) · pytest 9.1.1 · import-linter 2.15 · jsonschema 4.26.0.
- **Rationale**: every dependency is named in stack §2 except `jsonschema`. The spec needs it to
  prove SC-002 (every report validates against the *published* schema), using an independent
  validator instead of the Pydantic model validating itself. It is dev-only. `langchain-openai`
  is the OpenAI-compatible client, not a vendor package (stack §6).
- **Not installed in 001**: `tree-sitter` (004 · SRS Appendix A: "step 1 needs neither `tree-sitter` nor
  the resolver sidecar"), Node tooling for the sidecar (004).
- **Alternatives**: `langchain-nvidia-ai-endpoints`, rejected by stack §6 as vendor-specific.
  `pathspec` for exclusion globs, rejected as one more runtime dependency for about 20 lines of code
  (R-6). `platformdirs` for the user config path, rejected for the same reason (R-9). `pytest-socket` for offline
  enforcement, rejected because a 10-line conftest fixture does the same (R-19).

## R-3 · How git is reached, and how that is confined

- **Decision**: invoke the **`git` CLI through `subprocess.run([...], shell=False)`** from a single
  private module, `core/changeset/_git.py`. No git library. Confinement (FR-030, stack contract 2) is
  enforced by **two** checks: an import-linter contract forbidding any package but `core.changeset`
  from importing `agentic_review.core.changeset._git`, **and** an AST structural test failing if any
  module outside `core/changeset/` passes a literal `"git"` as the first element of an argv to
  `subprocess`.
- **Rationale**: the developer already has git, since they are in a repository. GitPython also shells out to
  git; pygit2 adds a native wheel (the same install risk as S-2, for no gain). import-linter sees
  imports, not subprocess arguments, so the AST test covers the gap. Preflight needs "is this a
  repository?" and "does this base exist?". Both are exposed as functions of `core/changeset/`
  (`locate_repository`, `ref_exists`) so the pipeline never touches git itself.
- **Alternatives**: GitPython (another layer over the same CLI, and a new dependency); pygit2
  (native build risk, and libgit2 behaviour differs from the user's git on attributes and filters).

## R-4 · What each scope means

- **Decision**:

  | Scope | Git comparison | Notes |
  |---|---|---|
  | `working-tree` (default) | `HEAD` ↔ working tree (`git diff HEAD`), **plus untracked files not ignored** (`git ls-files --others --exclude-standard`), each treated as `added` | "Uncommitted changes" includes a new file the developer has not `git add`-ed yet |
  | `staged` | `HEAD` ↔ index (`git diff --cached`) | |
  | `range` | merge-base(`base`, `head`) ↔ `head` (`git diff base...head`); `head` is `HEAD` unless `--head` names another ref *(nameable since 2026-10-09, SRS v1.5)* | "What this branch changed since it left `base`" — the same comparison a PR makes, which is the seam v3 substitutes (FR-10.3c). Naming the head lets a branch be reviewed without checking it out |
  | `pull-request` *(added 2026-10-09, SRS v1.5)* | merge-base(base branch, `refs/pull/<n>/head`) ↔ `refs/pull/<n>/head`, in a temporary clone | The `range` comparison, run on a repository fetched for the purpose. Selected by `--pr URL`. See [R-25](#r-25--reading-a-pull-request-added-2026-10-09-srs-v15-adr-0011) |
  | `commit` *(added 2026-10-09, SRS v1.4)* | first parent of `REF` ↔ `REF` (`git diff REF^1 REF`); git's empty tree ↔ `REF` when `REF` is a root commit | "What this one commit introduced." Selected by `--commit REF`. The working tree and the index play no part: uncommitted edits are not reviewed, and no untracked file is read |

  An **unborn `HEAD`** (a repository with no commits) compares against git's empty tree for
  `working-tree` and `staged`; `range` against an unborn `HEAD` is a preflight failure naming the problem.
  `ResolvedScope` records `base_ref` as given and `head_ref` as given, or `"HEAD"`. The one-line description
  carries the abbreviated commit IDs they resolved to. A base and a head with no common history have no
  three-dot diff, so that too is a preflight failure.

  For **`commit`**: `REF` is anything that resolves to a commit (`REF^{commit}` — an ID, a branch, a tag,
  `HEAD~2`); one that does not is a preflight failure naming the ref, which also covers a repository
  with no commits. A **merge commit** is compared with its first parent, and the description says so.
  `ResolvedScope` records `head_ref` as given and leaves `base_ref` empty, because the user named no
  base; the description carries the abbreviated IDs of the commit and of the parent it was compared with.
- **Rationale**: FR-10.3a names the scopes but not their git semantics. Excluding untracked files
  would silently skip the most common new-file case. The spec's Story 1 is "edited some files and has not
  committed", and silence is what Principle V forbids. Two-dot (`base..HEAD`) would pull in unrelated
  commits merged to `base` after the branch point and review them as the developer's work.
- **Design gap**: `Docs/design/02-domain-model.md` §3.1 defines the scopes' names, not their
  comparisons. **D-7** in the plan; **D-11** for the `commit` scope; **D-13** for the `pull-request` scope.
- **Alternatives**: `git diff` without `HEAD`, which reviews only unstaged edits and so contradicts "uncommitted".
  Leaving untracked files out, and listing them as "not reviewed", which is honest but wrong for the default
  user. Two-dot range, rejected above. For a single commit: expressing it as a `range` whose base is
  `REF^` and whose head is `REF` (no new scope kind, but the report would call one commit a range, and
  `head_ref` would stop being always `HEAD`); refusing merge commits (a preflight failure for
  something git can answer); a combined diff against every parent (not a files-and-hunks change set).
- **Checks and the working tree (D-12)**: checks and parsing read the working tree. Under `commit` the
  working tree need not hold the reviewed version, and the same is already true of `staged` and of a
  `range` with uncommitted edits. **Decided 2026-10-09 for `commit`: checks are not run** and are
  recorded as skipped (SRS FR-4.8, built by 002). The other two scopes, and related context under
  `commit`, are left to 002 and 004. Nothing in 001 reads the working tree for these scopes — line
  counts come from the blobs (R-5) — so 001 is unaffected.

## R-5 · Reading the diff

- **Decision**: all git calls use `-c core.quotepath=off` and `--no-color --no-ext-diff --no-textconv`.
  Two calls per tracked comparison:
  1. `diff --name-status -z -M` → change type, previous path for renames.
  2. `diff --numstat -z -M` → binary detection (`-\t-`) and line counts.
  3. `diff -M -U3 -- <paths>` → the patch, split into files on `diff --git` headers and into hunks
     on `@@` headers.

  Untracked files are read from disk: binary if they contain a NUL byte in the first 8,000 bytes (git's
  own heuristic), otherwise synthesised as one hunk `@@ -0,0 +1,N @@` with every line prefixed `+`.
  Output is decoded as UTF-8 with `errors="replace"`. **`Hunk.text` is kept byte-for-byte as decoded**,
  including CRLF, so the text sent to the model equals the text stored (02 §3.1). `changed_line_ranges`
  are computed from `+` lines in new-file coordinates.
- **Rationale**: `-z` avoids quoting problems with unusual paths on every OS. Git already emits POSIX
  separators, which satisfies the repo-relative-POSIX-path rule without conversion. Rename detection (`-M`) gives
  the spec's "reviewed under its new path; previous path recorded".
- **Line counts** for FR-013's "line range must fall inside that file" come from the version under
  review: the working-tree file, the index blob (`git show :path`), the `HEAD` blob, or the named
  commit's blob (`git show REF:path`). They are exposed as
  `measure_new_files(change_set) -> dict[path, int]` in `core/changeset/` rather than as a new
  `ChangeSet` field, because `ChangeSet` is frozen (FR-10.3c) and the v3 producer should not inherit an
  obligation the interface does not state.
- **Alternatives**: a unidiff parsing library (a dependency to parse a format git controls exactly);
  storing a line-count field on `ChangedFile` (widens a frozen interface).

## R-6 · Exclusions

- **Decision**: glob patterns over repo-relative POSIX paths. `**` matches zero or more whole segments,
  `*` and `?` stay within one segment, and a pattern with no `/` matches at any depth (gitignore
  convention). They are translated to regular expressions by a small in-house function with unit tests. **Default list**
  (documented in [contracts/config.md](./contracts/config.md)), each entry tagged with its rule name:

  | Rule | Patterns |
  |---|---|
  | `default:dependencies` | `node_modules/**`, `**/node_modules/**`, `vendor/**`, `bower_components/**` |
  | `default:build-output` | `dist/**`, `build/**`, `out/**`, `coverage/**`, `.next/**`, `.nuxt/**`, `.turbo/**` |
  | `default:generated` | `**/*.generated.*`, `**/*.gen.ts`, `**/__generated__/**` |
  | `default:minified` | `**/*.min.js`, `**/*.min.mjs`, `**/*.map` |
  | `default:lockfile` | `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `bun.lockb` |

  Configured patterns are recorded as `config:<pattern>`. Defaults are applied first, and **configured
  patterns are always added to the defaults, never substituted for them** (FR-008, SC-009). A renamed file is
  excluded if its **new** path matches.
- **Rationale**: FR-3.5 requires a documented default list and exclusion at resolution time.
  Recording the rule name gives the spec's "listed as excluded, with the rule that excluded it".
- **Alternatives**: `fnmatch` (does not treat `/` specially, so `dist/*` would match nested paths
  inconsistently); `pathspec` (R-2).

## R-7 · Which files are reviewable

- **Decision**: language from extension: `.ts .mts .cts` → `ts`; `.tsx` → `tsx`;
  `.js .mjs .cjs` → `js`; `.jsx` → `jsx`; anything else → `other`. A file is **reviewable** when it is
  not excluded, not deleted, not binary, and its language is not `other`. Non-reviewable changed files
  stay in `ChangeSet.files` with no hunks and appear in the change summary (FR-009).
- **Rationale**: 02 §3.1 fixes the language vocabulary. `.mts`/`.cts`/`.mjs`/`.cjs` are ordinary
  module-format variants of the same languages.

## R-8 · Configuration loading

- **Decision**: `yaml.safe_load` via a loader subclass that **rejects duplicate keys**, then a Pydantic
  model with `extra="forbid"` on every section, camelCase aliases, and defaults held in the model. The
  **whole** schema from `Docs/design/04-contracts.md` §7 is modelled (FR-003). A validation failure
  is rendered as the file path, a dotted field path, and the message, followed by "Nothing was reviewed",
  then exit 3 (05 §4.2). Resolution order: built-in defaults → file → CLI flags, per field (05 §4.1).
  One additive field is proposed: `agent.requestTimeoutSeconds` (placeholder, see R-10).
- **Rationale**: PyYAML silently keeps the last of two duplicate keys, which is exactly the silent fallback
  FR-1.2d forbids. `extra="forbid"` makes a misspelt key an error (spec Assumptions). Error messages
  come from Pydantic's own field locations, so they are field-precise by construction (stack §3.9).
- **Settings for unbuilt capabilities** (`context.*`, `checks.*`, `agent.investigationTools: true`)
  are validated, have no effect, and produce **one** stderr notice listing the dotted paths that were set.
  It goes in the terminal only, because an ignored setting is neither a finding nor a degradation.
- **Alternatives**: `pydantic-settings` (its strength is environment-variable merging, which is the one
  thing the repository config must *not* do for the credential); ruamel.yaml (round-trip editing is
  not needed).

## R-9 · The credential

- **Decision**: looked up in order: (1) environment variable `AGENTIC_REVIEW_API_KEY`
  (04 §7); (2) user-level file `agentic-review/credentials.yml` under `%APPDATA%` on Windows,
  `$XDG_CONFIG_HOME` or `~/.config` elsewhere, holding `apiKey: ...`. If the resolved user-level path lies
  **inside the repository root**, it is refused with a message (FR-1.3a: "never from a file
  committed to the repository"). The repository config schema has **no** credential field.
  Missing → preflight message naming both places, exit 3.
- **Redaction**: the key is held in a `SecretStr`-style wrapper whose `repr`/`str` are masked. Every
  degradation detail and stderr message passes through one `redact(text, secret)` function before it
  is stored. SC-007 is tested with a planted canary key across every integration scenario, scanning
  stdout, stderr, the report file and captured log records.
- **Rationale**: FR-004 / FR-1.3a. The user-level path is computed with `os.environ` and `pathlib`
  instead of `platformdirs` (R-2).
- **Verified**: an `openai.APITimeoutError` raised by `ChatOpenAI` did not include the planted key in
  its message. That is one case, not a guarantee, which is why redaction is applied regardless.

## R-10 · Provider client

- **Decision**: `langchain_openai.ChatOpenAI(base_url=agent.baseUrl, model=agent.model,
  api_key=..., temperature=agent.temperature, timeout=agent.requestTimeoutSeconds, max_retries=2)`,
  constructed **only** inside `core/agent/`. Defaults: `baseUrl = https://integrate.api.nvidia.com/v1`
  (NVIDIA NIM, SRS §2.3). `model` default is a **placeholder pending S-1** (R-21), labelled as such in
  the config documentation. The initial candidate is `meta/llama-3.3-70b-instruct`.
  `requestTimeoutSeconds = 60` and `max_retries = 2` are **placeholders**, labelled as such (Principle VI).
  The report's `provider` is the base URL's host.
- **Error mapping** → `provider-error` degradation (FR-020): any `openai.APIError` subclass
  (connection, timeout, status incl. 4xx refusal and 429), `httpx.HTTPError`, and a response with
  `finish_reason == "content_filter"`. **Verified**: an unreachable endpoint surfaces as
  `OpenAITimeoutError → openai.APITimeoutError → APIConnectionError → APIError`.
- **Rationale**: stack §3.6. FR-0.3 reduces to a base URL and a model name.
- **Alternatives**: `init_chat_model` (indirection with no second provider to justify it).

## R-11 · The `emit_finding` tool schema

- **Decision**: generated from `FindingDraft.model_json_schema(by_alias=True)` at import time, then
  **mechanically transformed** by one function that inlines `$ref`/`$defs` and removes Pydantic's
  `title` noise. Name `emit_finding`, description from 04 §4.1. Bound with
  `chat.bind_tools([tool])` and **no `tool_choice`** (FR-5.10). A test asserts that the bound runnable's
  kwargs carry no `tool_choice`, and that the schema sent equals the transform applied to the model's schema.
- **Verified**: Pydantic 2.13 emits the discriminated evidence union as `$defs` + `$ref` + `oneOf`
  with a discriminator mapping. `bind_tools` without `tool_choice` sets no `tool_choice` kwarg.
- **Rationale**: "one definition, not two" (SRS §5, Principle IV) holds because the tool schema is a
  pure function of the model. Inlining avoids known failures of some OpenAI-compatible backends on
  `$ref` inside tool parameters. S-1 exercises the real endpoint with the real schema.
- **Alternatives**: hand-writing the JSON from 04 §4.1 (two definitions); LangChain's
  `convert_to_openai_tool(FindingDraft)` (uses the Pydantic field names unless configured, and hides
  the transform we need to test).

## R-12 · The review step's graph

- **Decision**: a LangGraph `StateGraph` with two nodes:
  `call_model` → `process_calls`, and a **conditional edge** `process_calls → call_model` taken only when
  a repair turn is owed (`rejected > 0 and repair_turns == 0 and ceiling not reached`). Otherwise the
  edge goes to `END`. No checkpointer; state is built fresh per review (FR-5.1 isolation). Investigation
  (005) adds a second condition on the **same** edge. It does not restructure the graph.
- **Rationale**: FR-5.6c's repair turn needs a second model call, so the v1 default graph cannot be
  "one node, no cycle" as stack §3.6 and SRS §2.1 describe. Both were written before FR-5.6c existed.
  The edge exists but is traversable at most once, and FR-5.7's "configuration, not restructuring"
  still holds.
- **Design gap**: stack §3.6 table row "FR-5.7 — a graph with one node and no cycle" predates the
  repair turn. **D-6** in the plan, **out of scope for 001** (maintainer decision, 2026-09-17): the
  graph is built as decided here, and the stack document's wording is left for a later edit. This is a wording correction to a technology document, not a
  reversal of ADR-0007's reasoning.
- **Alternatives**: an acyclic `call → process → repair_call → process_repair → END` (duplicates the
  processing node, and investigation would still need a cycle later); a plain Python loop (would put
  the framework in CF-6 for nothing, and move the seam FR-5.7 relies on).

## R-13 · Counting against the ceiling

- **Decision**:
  - Every tool call the model makes, in the first turn **and** the repair turn, increments
    `toolCallsTotal`. `emit_finding` calls also increment `toolCallsEmission`. `toolCallsInvestigation` is always
    0 in 001.
  - The repair **turn** increments `repairTurns` and consumes **no** ceiling slot (FR-016).
  - Calls are processed in the order they appear. When `toolCallsTotal` equals the ceiling, further
    calls in that reply are **not processed**. Each gets a `denied` observation reason, since the call was understood and
    not permitted (FR-5.9). This makes `denied` reachable in 001.
  - `completionStatus = ceiling-reached` whenever the ceiling was reached. **Additionally**, if calls
    were dropped, a `tool-budget-exhausted` degradation records how many (02 §3.5).
  - If the ceiling is reached, no repair turn is taken. Rejected calls then produce
    `invalid-model-output`.
- **Rationale**: FR-5.7 counts every call. DB-17/FR-5.6c exempt the *turn*. The split between the
  `ceiling-reached` completion status and the `tool-budget-exhausted` degradation is 02 §3.5's: using the
  whole allowance is not damage, but losing findings is.
- **Note**: the `denied` observation in a reply that is never answered is still recorded in the run's
  counters. It is only sent to the model if a repair turn follows, which cannot happen once the ceiling is reached.

## R-14 · Validating a call

- **Decision**: validation lives in `core/findings/validation.py` as a pure function
  `validate_call(args: object, material: RunMaterial) -> Accepted | Rejected`, in two layers:
  1. **Shape**: `FindingDraft.model_validate(args)`. Pydantic's error locations are rendered as
     `field.path: message`.
  2. **Reference** (spec FR-013, gap D-1): `file` must be a reviewed file; `1 ≤ startLine ≤ endLine
     ≤ line count`; `evidence.kind == "diff"` must name a reviewed file and, if `hunkIndex` is given, a hunk
     that exists; `evidence.kind in {"check", "context"}` → rejected ("no checks were run in this
     review" / "no related context was gathered in this review"); `ruleId` present → **discarded**, and the
     finding accepted without it *(changed 2026-10-09 — it was a rejection, and cost a real finding its one
     repair turn; see contracts/emit-finding.md "Discarded fields")*.

  LangChain's `AIMessage.invalid_tool_calls` (arguments that are not valid JSON) are counted as calls and
  rejected with reason `arguments: not valid JSON`. A call naming any tool other than `emit_finding` is
  rejected with `status: error`, reason `unknown tool`.
  **Every** tool call receives a `ToolMessage` carrying its observation, because the OpenAI-compatible protocol
  requires one per `tool_call_id` before the next assistant turn.
- **Repair turn content**: the original messages, the assistant reply, one observation per call
  (accepted ones `ok`), and a short user message: "Some calls were rejected. Re-emit only the rejected
  findings, corrected. Reply without a tool call when done."
- **Partial success** (spec Edge Cases, D-4): valid calls are accepted immediately. After a failed repair,
  if **any** finding was accepted, the run is `emitted` with an `invalid-model-output` degradation (exit 0/1).
  If none was, it is `invalid-model-output` (exit 2).
- **Alternatives**: validating references only after the review (the model would lose its one correction
  chance); rejecting a whole reply for one bad call (throws away valid findings, which contradicts ADR-0004).

## R-15 · The context limit (FR-019)

- **Decision**: CF-4 (`core/assembly/`) estimates tokens as **`ceil(len(text) / 3)`** characters-per-token
  over the full assembled prompt (instructions, the "no checks / no context" statement, and every
  reviewable file's hunks). If the estimate exceeds `budget.maxTokens`, CF-4 returns `budget-exhausted`
  (source `CF-4`) instead of a prompt. The review stage is skipped, completion is `budget-exhausted`, and the exit is 2. No
  partial diff is ever built. `budget.maxTokens` defaults to **20000, a TBD-3 placeholder** standing in for
  "the configured model's window less a reply reserve" (SRS §8), which an OpenAI-compatible endpoint
  does not report. The estimator is labelled as an estimate.
- **Rationale**: CF-4 is the sole budget owner (DB-05). Dividing by 3 overestimates relative to typical
  BPE tokenisers for code, so a diff near the limit is refused before it is truncated by the provider,
  not after. The model's tokenizer is not available locally, and `tiktoken` counts for a different vocabulary.
- **Alternatives**: `tiktoken` (wrong vocabulary for NIM models, and a precise-looking wrong number is worse
  than a stated estimate); asking the provider (no such endpoint).

## R-16 · Zero findings and "no tool call" — a contradiction in the spec

- **Finding**: with `emit_finding` as the **only** tool, a model that reviewed the change and found nothing
  replies without a tool call. So does a model that never used the tool. **The two produce the same reply.**
  So at v1's default:
  - every run with zero findings is a `no-tool-call` run (FR-018 requires recording it);
  - spec **US2-AS7** ("a clean run with no findings and no damage carries an empty degradation list")
    and **SC-003's "clean"** outcome, if clean means zero findings, **cannot occur with a real model**.
  - ADR-0008 decision 2 says the benefit of `finish_review` "is obtainable by observing whether **any** call was
    made". That is true only when investigation tools exist. With investigation off, it is not.
- **Provisional decision** (keeps the spec's own Assumption: "No tool call and no findings → completed with a
  degradation, exit 0"):
  - zero findings + no call → `completionStatus: no-tool-call`, degradation `no-tool-call` (CF-6),
    verdict `no-findings`, exit 0. The terminal says plainly: *"No findings. The model made no tool call,
    so this build cannot tell a change with nothing to report from a model that did not use the
    finding tool."*
  - US2-AS7 is tested as **"a run with accepted findings and no damage carries an empty degradation
    list"**. SC-003's "clean" is read as "reviewed, non-blocking findings, no damage".
- **Decided 2026-09-17 (maintainer): reword.** The provisional decision above stands. Spec Story 2 (scenarios 4
  and 7) and SC-003 were reworded to what this build can distinguish. ADR-0008 is not reopened. **D-5** in the plan.
- **Mitigation that needs no decision**: S-1 (R-21) measures whether the model calls the tool when a defect
  **is** planted. That is the only evidence that a zero-finding run means anything.

## R-17 · Verdict, completion status, exit code

- **Decision**: the verdict is computed in `core/output/verdict.py` (Principle III), and the CLI maps it to an
  integer.

  | Situation | `completionStatus` | Degradations (001) | `verdict` | Exit |
  |---|---|---|---|---|
  | Findings, none blocking | `emitted` | — | `findings` | 0 |
  | ≥1 blocking finding | `emitted` | — | `blocking` | 1 |
  | Zero findings, no call | `no-tool-call` | `no-tool-call` | `no-findings` | 0 |
  | Ceiling reached | `ceiling-reached` | `tool-budget-exhausted` if calls dropped | by findings | 0/1 |
  | Repair failed, some accepted | `emitted` | `invalid-model-output` | by findings | 0/1 |
  | Repair failed, none accepted | `invalid-model-output` | `invalid-model-output` | `no-judgement` | 2 |
  | Provider unreachable / refuses | `provider-error` | `provider-error` | `no-judgement` | 2 |
  | Diff over the limit | `budget-exhausted` | `budget-exhausted` | `no-judgement` | 2 |
  | Nothing reviewable | `nothing-to-review` | — | `nothing-to-review` | 0 |
  | Preflight failure | *(no report)* | — | — | 3 |

  If a provider error occurs **during the repair turn** after findings were accepted, the result is `emitted`
  with a `provider-error` degradation, exit 0/1, following the same rule as D-4: judgement was made.
- **Rationale**: FR-023 and FR-10.4c's four outcomes. SC-003 requires every row to differ in at
  least one of exit code, completion status and degradation list, and the table meets that (subject to D-5).
- **Vocabulary**: `completionStatus` extends 02 §3.6's enum with `nothing-to-review` and `no-tool-call` (spec
  D-3). `verdict` values are new, because design never fixed them. 01 §4's `clean`/`degraded` are not used: `clean`
  would overclaim under R-16, and `degraded` hides whether a blocking finding exists. Both are listed as a
  write-back in plan D-8.

## R-18 · Output streams and `--json [PATH]`

- **Decision**:
  - `--json` with no value → the report on **stdout** and nothing else. The Rich summary goes to **stderr**.
  - `--json PATH` → the report is written to `PATH` (UTF-8, `\n` line endings), and the summary goes to stdout.
  - No `--json` → the summary goes to stdout.
  - Preflight failure → message on stderr, nothing on stdout, exit 3.
  - Rich `Console` auto-detects TTY and honours `NO_COLOR`. Non-TTY output is plain text.
- **Verified**: **Typer 0.27.2 rejects an option whose value is optional** (`--json` → "Option '--json'
  requires an argument"), while Click 8.5 accepts it with `is_flag=False, flag_value="-"`. To keep
  the documented contract `--json [PATH]` (04 §6) without leaving Typer, `cli/` normalises argv before
  dispatch: a bare `--json` (at the end of argv, or followed by a token beginning with `-`) becomes `--json -`,
  and `-` means stdout. This is tested directly.
- **Alternatives**: a separate `--json-file PATH` (changes a 📦 stable contract); dropping Typer for
  Click (a stack change for one option); an explicit `--json -` only (changes the contract).

## R-19 · Offline tests with a stand-in model

- **Decision**:
  - **Stand-in model**: `tests/support/scripted_chat_model.py`, a subclass of LangChain's
    `GenericFakeChatModel` that overrides `bind_tools` to record the tools and kwargs and return
    itself. It replays a scripted list of `AIMessage`s (with `tool_calls`, `invalid_tool_calls`,
    `usage_metadata`), can raise a scripted `openai.APIError`, and counts invocations. It is injected through
    `agent.build_review_port(..., chat_model=...)`.
    **Verified**: `GenericFakeChatModel.bind_tools` raises `NotImplementedError`, so the subclass is needed.
  - **Fixture repositories** are built in `tmp_path` by `tests/support/repo_builder.py` using the git CLI
    (`git init`, commits, staging, untracked files, renames, binary files, `dist/` files).
  - **Offline guarantee**: an autouse fixture patches `socket.socket.connect` to raise, so any
    accidental network use fails the test. The credential is set to a **planted canary** in every
    integration test (SC-007).
  - **Clock**: the pipeline takes an injectable monotonic clock, so stage durations are asserted present and
    non-negative, never compared against a latency value (Principle VI).
- **Rationale**: Principle VII and 06 §4. Using the real LangGraph adapter with a scripted chat model
  means the repair, ceiling and no-call logic is exercised as shipped, not by a fake port that bypasses it.
- **Alternatives**: a fake `ReviewPort` for the matrix tests (it would skip the logic under test; kept
  only for pipeline tests of preflight and nothing-to-review, where the agent must not be called);
  recorded HTTP cassettes (need a key to record, and are brittle across `openai` releases).

## R-20 · Structural checks on every commit

- **Decision**: import-linter contracts in `pyproject.toml` (`[tool.importlinter]`) for the packages
  this feature creates:
  1. `rich` forbidden outside `agentic_review.cli` and `agentic_review.core.output`
  2. `agentic_review.core.changeset._git` forbidden outside `agentic_review.core.changeset`
     (+ the AST test from R-3)
  3. `langchain_core`, `langchain_openai`, `langgraph`, `openai` forbidden outside `agentic_review.core.agent`
  6. A **layers** contract: `cli` > `core.pipeline` > `core.agent` > `core.assembly | core.output` >
     `core.changeset` > `core.findings | core.config`, which also enforces "nothing imports `cli/`" and "capabilities do not
     import each other".

  Forbidden contracts 1–3 set **`allow_indirect_imports = true`**. The requirement is that no module
  outside the package *imports* the dependency (FR-5.8, AC-10). The pipeline must still be able to call
  `core/agent/`, which imports LangChain, and the CLI must be able to import the Rich renderer. Rich is
  confined to `core/output/terminal.py`, which `core/pipeline/` never imports, so the pipeline stays
  free of Rich even indirectly.

  Contracts **4 and 5** (resolver path, concrete context provider) are **not** added, because their packages do
  not exist until 004 (Principle VII: contracts are enabled in the feature that creates the packages).
  They run as `uv run lint-imports`, **and** as a pytest test so a plain `pytest` also fails on a
  violation. A CI workflow (`.github/workflows/ci.yml`) runs both on every push and pull request,
  with no secrets.
- **Rationale**: FR-030, AC-10 (partial), stack §4. CI is how "on every commit" is made true rather than
  intended, and running with no secrets proves SC-006 continuously.
- **Alternatives**: a local pre-commit hook only (skippable, and not visible to reviewers).

## R-21 · S-1, run early

- **Decision**: `scripts/s1_tool_calling_probe.py`, run manually with a real key once `core/agent/`
  exists (early in implementation, **before** the output and CLI work). Protocol from stack §7: a fixed
  fixture diff with one planted defect, the real assembled prompt and real tool schema, **50 runs** per
  candidate model at temperature 0. It records, per run: calls made, valid, schema-rejected,
  reference-rejected, invalid JSON, no call at all, whether the repair turn fixed it, tokens, and latency. The raw
  results go to `specs/001-walking-skeleton/s1-results.md`, and a summary line goes to `Docs/technical_stack.md` §7.
- **Decision rule**: none is set here. The figures go to the maintainer, who decides (a) the default
  model and (b) whether FR-5.6b's fallback must be pulled forward. A threshold chosen now would be a
  placeholder justifying a decision, which Principle VI forbids.
- **Rationale**: stack §7 and 06 §6 call S-1 "the cheapest test in the plan and it gates the most". It is
  outside the pytest suite because it needs a key and network (Principle VII).

## R-22 · Schema versioning and the empty sections

- **Decision**: `SCHEMA_VERSION = "1.0"`, hand-set in `core/findings/schema.py` and stamped on the report
  and every finding. `toolVersion` comes from `importlib.metadata.version("agentic-review")`.
  In 001, `evidence = {"status": "not-attempted", "checks": []}` and `context = []`, with
  `run.requestedDepth = null` and `run.achievedDepth = null` documented as "related context not gathered".
  `checks` and `context` are typed with `maxItems: 0` in schema 1.0, and 002 and 004 widen them with a minor
  bump. The published schema states "consumers must ignore unknown fields" (02 §4).
- **Rationale**: FR-026 wants "no checks executed" and "context not gathered" stated rather than implied.
  Keeping `context` an array and `evidence` an object preserves 04 §5's shape, so later features add fields
  rather than change shapes (additive = minor, 02 §4).
- **Alternatives**: `requestedDepth: 0` (claims depth 0 was served, which is false); omitting the sections
  (absence asserts nothing, 04 §5).

## R-23 · Finding identity

- **Decision**: `id = "f-<n>"` in order of acceptance. `turnIndex` is 0 for the first turn and 1 for the repair turn.
  `fingerprint = sha256("fp1\0" + file + "\0" + category + "\0" + (ruleId or ""))[:12]`: no line, column,
  or text (ADR-0005). The `fp1` prefix versions the algorithm. **004** adds the enclosing symbol and
  bumps it to `fp2`.
- **Rationale**: the fingerprint is required by 02 §3.4, and position independence by ADR-0005. Without CF-2
  there is no enclosing symbol, so two findings of the same category in one file share a fingerprint.
  That is acceptable because v1 does not deduplicate (FR-5.5 is v2), and it is stated, not hidden.

## R-24 · Unexpected internal errors

- **Decision**: failures the spec names are handled as degradations. Anything else after preflight
  is a **defect**. The CLI catches it at the top level, prints a one-line message and the report path if one was
  written, and exits **2** ("no judgement made"). It never exits 0. The traceback is shown only with
  `AGENTIC_REVIEW_DEBUG=1`, after redaction.
- **Rationale**: FR-10.4c fixes four outcomes, and a fifth exit code would change a stable contract. Exit 0 would
  let a crash read as a review, which Principle V forbids.

## R-25 · Reading a pull request *(added 2026-10-09; SRS v1.5, ADR-0011)*

- **Decision**: a pull request is read with git alone, into a temporary directory, and never checked out.

  ```
  git clone --filter=blob:none --no-checkout https://github.com/<owner>/<repo>.git <tmp>/repo
  git fetch origin +refs/pull/<n>/head:refs/pull/<n>/head
  git diff <base>...refs/pull/<n>/head          # the same three-dot diff as the range scope (R-4)
  ```

  | Question | Answer |
  |---|---|
  | How is the pull request named? | By URL: `https://github.com/<owner>/<repo>/pull/<n>`, with anything GitHub appends after it. Nothing else is accepted — the string becomes a git argument, so it is matched strictly, not parsed loosely |
  | Where does its head come from? | `refs/pull/<n>/head`, which GitHub publishes for every pull request, including those opened from forks. No branch name is needed |
  | What is the base? | The repository's default branch (`refs/remotes/origin/HEAD`), unless `--base` names another. **git cannot know which branch a pull request targets**; the scope line says which base was used and whether it was the default |
  | What is downloaded? | Commits and trees (`--filter=blob:none`). File contents are fetched only for the files the diff touches, when the diff asks for them |
  | What is written to disk? | Only `.git`. `--no-checkout` means no working tree: no project file exists as a file, so nothing can be run, no hook fires and nothing is installed (SRS FR-10.3d) |
  | Where does configuration come from? | `--config PATH`, or the defaults. Never from the pull request, and never from the directory the command was run in (SRS FR-10.3d) |
  | Can git ask for a login? | No. `-c credential.helper= -c core.askPass=`, `GIT_TERMINAL_PROMPT=0`, `GCM_INTERACTIVE=never`, and `GIT_ASKPASS`/`SSH_ASKPASS` removed. GitHub answers a missing repository with a login challenge; without this, a mistyped URL hangs at a prompt |
  | What if it cannot be read? | A preflight failure (exit 3) naming the URL, the pull request number or the base. It is check 5, the last, so a missing credential never costs a clone |
  | What happens to the clone? | Removed when the run ends, in a `finally`. git marks pack files read-only, which Windows will not delete as they are; removal makes them writable first |
  | How long may it take? | One clone or fetch is bounded by a timeout — **a placeholder**, labelled as one in the code. No decision rests on its value |

- **The seam**: all of this is behind `PullRequestSource` ([contracts/internal-seams.md](./contracts/internal-seams.md) §2a).
  Preflight, the pipeline and the CLI see a `ChangeSet` and line counts, and nothing that would reveal how they
  were obtained.
- **Interim, by decision.** This reader is hand-written plumbing for something the official GitHub MCP server
  (`github/github-mcp-server`) already provides. It is to be replaced by a `PullRequestSource` backed by that
  server — a second implementation, not a rewrite. That is **not** built here and needs its own ADR, because it
  brings a GitHub token (an exception to FR-10.1, and a second credential under FR-1.3a), an MCP client that may
  not live under `core/` (FR-5.8) and must be named in `technical_stack.md`, and reach into private repositories.
  Until then this module stays thin: no feature the MCP server already has.
- **Rationale**: it needs nothing the tool does not already require — git — and it cannot execute the pull
  request, which is the exposure ADR-0003 exists for. Three-dot semantics come for free from R-4.
- **Tests stay offline** (SC-006): a fixture repository served over `file://`, with `uploadpack.allowFilter` set
  and a `refs/pull/7/head` ref, lets the real clone, fetch and lazy blob fetch run with no socket. The pull
  request's commits exist only under that ref, as for a fork.
- **One observation, not a target** (Principle VI): on 2026-10-09 a five-file pull request in a small public
  TypeScript repository was opened, diffed and measured in about four seconds on the maintainer's machine. No
  decision here depends on that figure.
- **Alternatives**: the GitHub REST API (knows the true base, but needs a token to be usable, and puts a GitHub
  client in the dependency list — ADR-0011 option B); the `gh` CLI (a second prerequisite, and a logged-in one);
  downloading the pull request's `.diff` over HTTPS (no line counts for validation, and an HTTP client in
  `core/changeset/`); a shallow clone (`--depth`) (no merge base, so no three-dot diff); a full clone (downloads
  every version of every file to read a handful).
