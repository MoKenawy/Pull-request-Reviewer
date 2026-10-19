---
description: "Task list for feature 001 — Walking Skeleton"
---

# Tasks: Walking Skeleton — Review a Change, Diff Only

**Input**: Design documents from `specs/001-walking-skeleton/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)

**Tests**: **Required.** Constitution Principle VII and spec FR-030/FR-031 make tests part of the feature. Within each
phase, test tasks come first and are expected to fail until the implementation tasks after them land.

**Authority**: these tasks select from the documents above and add no requirement. A task that seems to need a
decision the documents do not make stops and reports it (Principle I) — it is not settled inside the code.

**Organization**: grouped by user story (spec.md priorities P1–P5), so each story is a testable increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency on an unfinished task)
- **[Story]**: US1…US5, mapping to spec.md User Stories 1–5
- Paths are repository-relative. Source lives in `src/agentic_review/`, tests in `tests/` (plan.md "Project Structure")

## Rules that apply to every task

- `subprocess` is always called with an argv list and `shell=False`. Only `core/changeset/_git.py` runs git.
- `langchain_*`, `langgraph` and `openai` are imported only under `agents/` (ADR-0010; was `core/agent/`). `rich` only in `core/output/terminal.py` and `cli/`.
- Placeholders (tool-call ceiling 25 · TBD-8, `budget.maxTokens` 20000 · TBD-3, request timeout 60 s, default model
  pending S-1) carry a `PLACEHOLDER` comment wherever they are defined.
- No credential value ever reaches stdout, stderr, the report, a log record or an exception message (FR-004, SC-007).
- Every 📦 type lives in `core/findings/` (data-model.md §1). JSON field names are camelCase aliases of snake_case fields.
- **Tracing (Phase 9, added 2026-09-24).** Langfuse is optional and sits *alongside* the report, never replacing it
  (`Docs/technical_stack.md` §6, FR-11.3). Every open task below keeps three things true: nothing it adds to graph
  state or to a node's input/output carries a secret (the credential and the environment travel only as run
  context — see commit `452735e`); tracing never changes the report, the exit code or what goes to stdout/stderr
  (contracts/cli.md); and with no `LANGFUSE_*` keys set, nothing is traced and nothing touches the network (SC-006).
  A task's **Langfuse:** note says what its change should look like in a trace.
- **Single-commit scope (added 2026-10-09).** SRS v1.4 amended FR-10.3a with a fourth scope, `commit`, selected by
  `--commit REF` (spec FR-005, Story 4 scenario 6; research R-4; contracts/cli.md; plan D-11). It is delivered by
  T110–T111 and by the **Commit scope:** notes on the open tasks of Phases 5 and 6 — the same files and tests as
  `staged` and `range`, so it is not a separate phase. The scope reads git objects only: no task may make it read
  the working tree or the index.
- **Pull-request scope (Phase 10, added 2026-10-09).** SRS v1.5 and ADR-0011 added a `pull-request` scope
  (`--pr URL`) and a nameable head for `range` (`--head REF`). Phase 10 built both, and with them the `range`
  half of User Stories 3 and 4. A **Phase 10:** note on an open task says what Phase 10 already delivered, so
  that task finishes the rest rather than rebuilding it. Two rules bind every later task: nothing from a pull
  request is executed or read as configuration (FR-10.3d), and nothing outside `core/changeset/` may depend on
  how a pull request was fetched — that reader is interim (GitHub MCP server later).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: an installable, empty package with the structural contracts and CI already in force.

- [X] T001 Create `pyproject.toml`: project `agentic-review` version `0.1.0`, `requires-python = ">=3.12"`, hatchling build backend with `src/agentic_review` as the package, console script `agentic-review = "agentic_review.cli.app:main"`, runtime deps `pydantic`, `pyyaml`, `typer`, `rich`, `langchain-core`, `langchain-openai`, `langgraph`; dev dependency group `pytest`, `import-linter`, `jsonschema`; `[tool.pytest.ini_options]` with `testpaths = ["tests"]` (research R-1, R-2)
- [X] T002 Add `[tool.importlinter]` to `pyproject.toml` with `root_package = "agentic_review"` and contracts 1, 2, 3 (forbidden, `allow_indirect_imports = true`) and 6 (layers `agentic_review.cli` > `agentic_review.core.pipeline` > `agentic_review.core.agent` > `agentic_review.core.assembly | agentic_review.core.output` > `agentic_review.core.changeset` > `agentic_review.core.findings | agentic_review.core.config`) exactly as research R-20 states
- [X] T003 [P] Create `.gitignore` with Python patterns (`__pycache__/`, `*.pyc`, `.venv/`, `venv/`, `dist/`, `build/`, `*.egg-info/`, `.pytest_cache/`, `.import_linter_cache/`) and universal patterns (`.DS_Store`, `Thumbs.db`, `*.tmp`, `*.swp`, `.env*`)
- [X] T004 [P] Create the package skeleton with an `__init__.py` in every package of plan.md "Project Structure": `src/agentic_review/{__init__,__main__}.py`, `cli/`, `core/`, `core/{pipeline,changeset,assembly,findings,agent,output,config}/`; `__init__.py` exposes `__version__` via `importlib.metadata.version("agentic-review")`; `__main__.py` calls `cli.app.main`
- [X] T005 [P] Create empty test packages `tests/__init__.py`, `tests/support/__init__.py`, `tests/structural/`, `tests/unit/{changeset,config,findings,assembly,agent,output,cli}/`, `tests/integration/` (each with `__init__.py`)
- [X] T006 Run `uv sync` to create `uv.lock`; confirm `uv run lint-imports` reports the four contracts KEPT on the empty skeleton; record the resolved exact versions (pydantic, pyyaml, typer, rich, langchain-core, langchain-openai, langgraph, openai, pytest, import-linter, jsonschema) in `Docs/technical_stack.md` §7, stating that they were pinned by feature 001's first install (stack §7 rule)
- [X] T007 [P] Create `.github/workflows/ci.yml`: on push and pull_request, matrix `ubuntu-latest` + `windows-latest` × Python `3.12` + `3.13`, `astral-sh/setup-uv`, `uv sync`, `uv run lint-imports`, `uv run pytest`; no secrets referenced (research R-20, SC-006)

**Checkpoint**: `uv sync` succeeds, `uv run lint-imports` passes, CI definition exists.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: the test harness, every published type, configuration, and the change-set producer. Every user story depends on these.

**⚠️ CRITICAL**: no user-story work begins until this phase is complete.

### Test harness and structural checks

- [X] T008 Create `tests/conftest.py`: an autouse fixture that patches `socket.socket.connect` (and `connect_ex`) to raise, so any network use fails the test; an autouse fixture that removes `AGENTIC_REVIEW_API_KEY` and `AGENTIC_REVIEW_DEBUG` from the environment and points `APPDATA`, `XDG_CONFIG_HOME` and `HOME` at a per-test temp directory; a `CANARY_KEY` constant (a distinctive value such as `ar-canary-9f3b2c7d51e84a06`) and a `canary_env` fixture that sets it (research R-19, SC-006, SC-007)
- [X] T009 [P] Create `tests/support/repo_builder.py`: a `RepoBuilder(tmp_path)` helper that runs the git CLI by argv (`shell=False`) to `init` (setting local `user.name`, `user.email`, `core.autocrlf=false`), `write(path, text)`, `write_bytes(path, data)`, `stage(*paths)`, `commit(msg)`, `rename(old, new)`, `delete(path)`, `branch(name)`, `checkout(name)`; returns the repo root (research R-19)
- [X] T010 [P] Create `tests/support/scripted_chat_model.py`: `ScriptedChatModel`, a subclass of `langchain_core.language_models.fake_chat_models.GenericFakeChatModel` that replays a scripted list of `AIMessage`s or exceptions (an `openai.APIError` instance is raised when reached), overrides `bind_tools` to record the tools and kwargs and return itself, and counts invocations in `call_count`; helper constructors `finding_call(**fields)` and `ai_reply(tool_calls=..., invalid_tool_calls=..., usage=...)` (research R-19)
- [X] T011 [P] Create `tests/structural/test_import_contracts.py`: runs `lint-imports` (via `subprocess` argv from the active interpreter's scripts dir, or the `importlinter` API) and asserts every contract is KEPT, so a plain `pytest` fails on a violation (FR-030, research R-20)
- [X] T012 [P] Create `tests/structural/test_git_confinement.py`: walks `src/agentic_review/**/*.py` with `ast`, and fails if any module outside `src/agentic_review/core/changeset/` calls a `subprocess` function whose first argv element is the literal `"git"` (FR-030, research R-3). It scans `src/` only; `tests/support/repo_builder.py` is test tooling and legitimately runs git

### `core/findings/` — every published type, schemas, validation (CF-5)

- [X] T013 [P] Write `tests/unit/findings/test_model.py`: `FindingDraft` accepts a valid draft for each of the four evidence arms; rejects a missing `evidence`, an unknown field (`extra="forbid"`), `startLine < 1`, `endLine < startLine`, whitespace-only `rationale`, an unknown `severity` or `category`, `unverified` with an empty `reason`; serialises with camelCase aliases (data-model §3, FR-014, AC-15)
- [X] T014 [P] Write `tests/unit/findings/test_schema.py`: `inline_refs` leaves no `$ref`/`$defs`/`title` keys; `tool_schema()` equals `inline_refs(FindingDraft.model_json_schema(by_alias=True))` and requires the seven fields of contracts/emit-finding.md; `report_schema()` is draft 2020-12, its `$id` contains `1.0`, its `description` says consumers must ignore unknown fields, `degradations` is required, `context` and `evidence.checks` have `maxItems: 0`, `requestedDepth`/`achievedDepth` allow null, and `DegradationCode` lists all ten codes of `Docs/design/02-domain-model.md` §3.5 (research R-11, R-22)
- [X] T015 [P] Write `tests/unit/findings/test_validation.py`: one test per row of the "Rejection reasons" table in contracts/emit-finding.md asserting the **exact** reason string; a shape failure names its dotted field path; several failures are joined with `; `; a valid call against a `RunMaterial` returns `Accepted` with the parsed draft (FR-013, FR-015, gap D-1)
- [X] T016 [P] Write `tests/unit/findings/test_fingerprint.py`: 12 lowercase hex characters; equals `sha256("fp1\0" + file + "\0" + category + "\0" + (ruleId or ""))[:12]`; unchanged when lines, severity or rationale change; changes with file or category (research R-23)
- [X] T017 Implement `src/agentic_review/core/findings/model.py`: `Severity`, `Category` literals; the four evidence models (`CheckEvidence`, `ContextEvidence`, `DiffEvidence`, `UnverifiedEvidence`) as a `kind`-discriminated union `EvidenceRef`; `FindingDraft` (flat wire shape, `extra="forbid"`, camelCase aliases, `endLine ≥ startLine` validator, trimmed non-empty rationale); `Finding` = draft + `id`, `schemaVersion`, `turnIndex`, `fingerprint`; `ToolObservation` (`status: ok|error|denied`, `reason` required unless ok, `content`) (data-model §3)
- [X] T018 Implement `src/agentic_review/core/findings/report.py`: `ScopeKind`, `ResolvedScope`, `ExcludedPath`, `FileSummary` (with `reviewed`, `notReviewedReason: deleted|binary|not-typescript-or-javascript`), `ChangeSummary`, `EvidenceRecord` (`status: not-attempted`, `checks` max 0 items), `DegradationCode` (all ten codes of 02 §3.5), `Degradation` (`source` CF-1…CF-9, `code`, `detail`), `CompletionStatus` (seven values), `Verdict` (five values), `Sampling`, `RunMetadata` (every field of data-model §6, `stageDurationsMs` holding only stages that ran, `emitPath: "tool-call"`), `ReviewReport` (`context` max 0 items, `degradations` required) (data-model §2, §6)
- [X] T019 [P] Implement `src/agentic_review/core/findings/port.py`: `ReviewedFile(line_count, hunk_count)`, `RunMaterial` (reviewed files mapping; empty `check_ids`, `context_ranges`, `rule_ids`), `ReviewContext` (`instructions`, `material_statement`, `diff_section`, `estimated_tokens`, `material`), `ReviewOutcome` (all fields of data-model §5), and the `ReviewPort` protocol with `review(context) -> ReviewOutcome` (contracts/internal-seams.md §4)
- [X] T020 [P] Implement `src/agentic_review/core/findings/fingerprint.py`: `fingerprint(draft) -> str` per research R-23
- [X] T021 Implement `src/agentic_review/core/findings/schema.py`: `SCHEMA_VERSION = "1.0"` (hand-set, never derived from the package version); `inline_refs(schema)` that resolves `$ref` against `$defs`, drops `$defs` and `title`; `tool_schema()`; `report_schema()` generated from `ReviewReport` with `$schema` 2020-12, versioned `$id`, the unknown-fields description, and the null-depth description (research R-11, R-22)
- [X] T022 Implement `src/agentic_review/core/findings/validation.py`: `Accepted(draft)`, `Rejected(reason)`, `validate_call(name, args, material)` — unknown tool name, then shape via `FindingDraft.model_validate` rendered as `dotted.path: message` joined by `; `, then reference checks in the order of data-model §3 with the fixed reason strings of contracts/emit-finding.md; `invalid_json_rejection()` for `arguments: not valid JSON` (research R-14)
- [X] T023 Create `tests/support/report_assertions.py`: `assert_valid_report(report_or_json)` validating with `jsonschema` (Draft 2020-12) against `report_schema()`; `assert_invariants(report)` for invariants 1–7 of data-model §6; `assert_no_canary(*texts)` scanning for `CANARY_KEY`; `assert_stage_durations(report, expected_stages)` checking keys present and values ≥ 0, never bounded (SC-002, SC-007, SC-008)

### `core/config/` — settings, credential, redaction (CF-9)

- [X] T024 [P] Write `tests/unit/config/test_settings.py`: defaults match data-model §7 (placeholders included); `schemaVersion` must be 1; every section rejects unknown keys; `agent.toolCallCeiling ≥ 1`; `agent.temperature` in [0, 2]; `agent.baseUrl` must be http(s); `checks.*.command` non-empty; there is no field that could hold a credential (FR-002, FR-003, FR-004)
- [X] T025 [P] Write `tests/unit/config/test_loader.py`: absent file → defaults; a file setting one `agent` field keeps the other `agent` defaults (per-field merge); an unknown field, a duplicate key and an invalid value each raise `ConfigError` naming the file and dotted field path; a YAML syntax error names line and column; `apiKey` anywhere is an unknown field; `ignored_settings()` lists only the `context.*`/`checks.*` paths present in the file, plus `agent.investigationTools` only when `true` (FR-002, FR-003, research R-8)
- [X] T026 [P] Write `tests/unit/config/test_credentials.py`: environment variable wins; the user-level file (`%APPDATA%\agentic-review\credentials.yml` on Windows, `$XDG_CONFIG_HOME` then `~/.config` elsewhere) is read when the variable is absent; a user-level path inside the repository root is refused; neither present → `CredentialMissing` whose message names `AGENTIC_REVIEW_API_KEY` and the user-level path; `repr()`/`str()` of the credential never contain the value (FR-004, research R-9)
- [X] T027 [P] Write `tests/unit/config/test_redact.py`: `redact(text, secret)` replaces every occurrence; handles `None`/empty secret; leaves text without the secret unchanged
- [X] T028 [P] Implement `src/agentic_review/core/config/settings.py`: Pydantic `Settings` with `ContextSettings`, `CheckSettings`/`ChecksSettings`, `AgentSettings`, `BudgetSettings`, all `extra="forbid"` with camelCase aliases and the defaults of data-model §7, each placeholder labelled `PLACEHOLDER` with its TBD
- [X] T029 [P] Implement `src/agentic_review/core/config/redact.py`: `redact(text, secret) -> str`
- [X] T030 Implement `src/agentic_review/core/config/loader.py`: a `yaml.SafeLoader` subclass rejecting duplicate keys; `load_settings(path: Path | None, explicit: bool) -> LoadedSettings(settings, ignored_settings)`; `ConfigError(message)` formatted as contracts/cli.md's example (`Error in <file>` / `  <dotted.path>: <message>` / `Nothing was reviewed. Fix the field above and re-run.`); an explicit path that does not exist is a `ConfigError` (research R-8)
- [X] T031 Implement `src/agentic_review/core/config/credentials.py`: `Credential` (masked `repr`/`str`, `.reveal()`, `source`, `location`), `user_credential_path(env)`, `find_credential(env, repo_root) -> Credential | CredentialMissing` (contracts/config.md "The credential")

### `core/changeset/` — the change set, working-tree scope, exclusions (CF-1)

- [X] T032 [P] Write `tests/unit/changeset/test_diff_parser.py` on literal git output: `--name-status -z -M` parsing (A, M, D, R<score> with previous path); `--numstat -z -M` binary detection (`-\t-`); patch split on `diff --git` headers and `@@` hunk headers; `Hunk.text` kept verbatim including CRLF; `changed_line_ranges` from `+` lines in new-file coordinates; language from extension per research R-7 (FR-007, FR-009)
- [X] T033 [P] Write `tests/unit/changeset/test_exclusion.py`: glob semantics (`**` zero or more segments, `*`/`?` within one segment, pattern without `/` matches at any depth); every default pattern of contracts/config.md excludes a sample path with the right `default:<name>` rule; a configured pattern yields `config:<pattern>`; a path matching both records the default rule; adding a configured pattern leaves 100% of the defaults in force; a renamed file is judged by its new path (FR-008, SC-009, research R-6)
- [X] T034 [P] Write `tests/unit/changeset/test_resolve_working_tree.py` using `RepoBuilder`: modified tracked file; untracked non-ignored file → `added` with one synthesised hunk; ignored file absent; deleted file with no hunks; renamed file with `previous_path`; binary file (NUL byte) with no hunks; `README.md` listed with language `other` and no hunks; running from a subdirectory gives repo-relative POSIX paths; unborn `HEAD` works; `reviewable_files` excludes deleted/binary/other; `locate_repository` returns `None` outside a repo; `ref_exists`; `head_is_unborn` (FR-005, FR-007, FR-009, research R-4, R-5)
- [X] T035 [P] Write `tests/unit/changeset/test_summary.py`: `summarise` produces a `ChangeSummary` with no diff text, correct `reviewed`/`notReviewedReason`, hunk and line counts; `measure_new_files` returns line counts of the reviewed version for reviewable files only (data-model §2, research R-5)
- [X] T036 [P] Implement `src/agentic_review/core/changeset/model.py`: frozen dataclasses `Hunk`, `ChangedFile`, `ChangeSet` (with derived `reviewable_files`), `ScopeRequest(kind, base)`, and `language_for(path)`; `ChangeSet` imports `ResolvedScope`/`ExcludedPath` from `core/findings/report.py` (data-model §2). `ChangedFile` also carries `added_lines`/`removed_lines` from `--numstat`: `ChangeSummary` reports them, including for binary and other-language files that have no hunks, and data-model §2 does not list a source for them
- [X] T037 [P] Implement `src/agentic_review/core/changeset/_git.py`: `run_git(repo_root, *args) -> str` using `subprocess.run(["git", "-c", "core.quotepath=off", *args], shell=False, capture_output=True)`, UTF-8 decode with `errors="replace"`, raising `GitError(args, stderr)` on non-zero exit; `run_git_bytes` for raw output; the only module that executes git (research R-3, R-5)
- [X] T038 [P] Implement `src/agentic_review/core/changeset/exclusion.py`: `DEFAULT_EXCLUSIONS` (rule name → patterns, contracts/config.md), `glob_to_regex(pattern)`, `classify(path, configured) -> str | None` returning the rule name, defaults checked first (research R-6)
- [X] T039 Implement `src/agentic_review/core/changeset/diff_parser.py`: `parse_name_status(z_output)`, `parse_numstat(z_output)`, `split_patch(patch) -> dict[path, list[Hunk]]`, `changed_line_ranges(hunks)`, `synthesise_added_file(text) -> Hunk` (depends on T036)
- [X] T040 Implement `src/agentic_review/core/changeset/resolve.py`: `locate_repository(cwd)`, `ref_exists(repo_root, ref)`, `head_is_unborn(repo_root)`, and `resolve(repo_root, scope, exclude, *, was_defaulted)` for the **working-tree** scope (`git diff HEAD`, or the empty tree when `HEAD` is unborn, plus `git ls-files --others --exclude-standard`), applying exclusions at resolution, building `ResolvedScope` with its one-line description; `staged` and `range` raise `NotImplementedError` until US4 (research R-4, R-5; depends on T037–T039)
- [X] T041 Implement `src/agentic_review/core/changeset/summary.py`: `summarise(change_set) -> ChangeSummary` and `measure_new_files(change_set) -> Mapping[str, int]` reading the working-tree file for the working-tree scope (research R-5)

**Checkpoint**: `uv run pytest tests/structural tests/unit` and `uv run lint-imports` pass. Commit: `feat(core): add findings model, config, and change-set resolution`.

---

## Phase 3: User Story 1 — Review my uncommitted changes (Priority: P1) 🎯 MVP

**Goal**: `agentic-review review` with no options reviews the uncommitted working-tree change in one model pass and prints findings, counts and a verdict with the matching exit code.

**Independent Test**: fixture repo with one modified `.ts` file, stand-in model emitting two valid findings, run with no options → both findings in the terminal, scope stated as the default, exit code matches the verdict.

### Tests for User Story 1 ⚠️ write first

- [X] T042 [P] [US1] Write `tests/unit/assembly/test_prompt.py`: `assemble` puts every reviewable file's hunks into `diff_section` verbatim under `path (change type[, renamed from X])` and `[hunk i]` headers; `material_statement` is "No checks were run. No related context was gathered."; non-reviewable files are absent; `RunMaterial` carries line and hunk counts for reviewed files and empty check/context/rule sets; `estimated_tokens == ceil(len(prompt) / 3)` (FR-012, research R-15)
- [X] T043 [P] [US1] Write `tests/unit/agent/test_binding.py`: with `ScriptedChatModel`, exactly one tool named `emit_finding` is bound, its parameters equal `tool_schema()`, and the bound kwargs contain no `tool_choice` (FR-011, FR-018, contracts/emit-finding.md "Binding rules")
- [X] T044 [P] [US1] Write `tests/unit/agent/test_graph_happy_path.py`: a reply with two valid calls → two `Finding`s with ids `f-1`, `f-2`, `turnIndex 0`, fingerprints, `completion_status == emitted`, `toolCallsTotal == toolCallsEmission == 2`, `repairTurns == 0`; each call got a `ToolMessage` whose JSON is `{"status": "ok", "reason": null, "content": "accepted as f-n"}`; a reply whose prose contains finding-like JSON but no tool call yields 0 findings, completion `no-tool-call` and a `no-tool-call` degradation (source `CF-6`), so an MVP run with zero findings is never presented as clean; `tokens_in`/`tokens_out` copied from `usage_metadata`, `None` when absent (FR-013, FR-015, FR-021)
- [X] T045 [P] [US1] Write `tests/unit/output/test_verdict.py`: every row of research R-17's table maps to its verdict (FR-023)
- [X] T046 [P] [US1] Write `tests/unit/output/test_render.py`: from one `ReviewReport`, the terminal text (Rich console recording, no colour) contains in order the scope line with `(default)`, reviewed and not-reviewed files with reasons, excluded paths with rules, "No checks were run in this build.", "No related context was gathered in this build.", each finding as `path:start-end` with severity, category, rationale and evidence, counts `blocking / important / nit`, each degradation, and the verdict line; `no-judgement` prints "No review was performed"; `to_json` output parses back to an equal report (FR-024, FR-027, contracts/cli.md "Terminal summary")
- [X] T047 [P] [US1] Write `tests/unit/cli/test_exit_codes.py`: `findings`/`no-findings`/`nothing-to-review` → 0, `blocking` → 1, `no-judgement` → 2 (FR-023)
- [X] T048 [US1] Write `tests/integration/test_story1_review_uncommitted.py` covering US1 acceptance scenarios 1–5 through both `run_review` (with an injected `ScriptedChatModel`-backed port and `canary_env`) and the Typer app via `typer.testing.CliRunner`: scope stated and defaulted; an `important` + `nit` pair shows every field and counts 0/1/1 with exit 0; one `blocking` finding → verdict `blocking`, exit 1; "no checks were run" and "no related context was gathered" always present; terminal findings equal JSON findings field for field. Every report passes `assert_valid_report`, `assert_invariants`, `assert_no_canary` and `assert_stage_durations(preflight, changeSet, assembly, review, output)` (SC-002, SC-007, SC-008)

### Implementation for User Story 1

- [X] T049 [P] [US1] Implement `src/agentic_review/core/assembly/budget.py`: `estimate_tokens(text) -> int` = `ceil(len(text) / 3)`, documented as an estimate, not a tokenizer count (research R-15)
- [X] T050 [US1] Implement `src/agentic_review/core/assembly/prompt.py`: `INSTRUCTIONS` (role, severity and category vocabularies, evidence rules, "findings only via emit_finding; prose is discarded; reply without a tool call when done"), `MATERIAL_STATEMENT`, and `assemble(change_set, line_counts, budget) -> ReviewContext` building the diff section and `RunMaterial` (data-model §4, contracts/internal-seams.md §3)
- [X] T051 [P] [US1] Implement `src/agentic_review/core/agent/accounting.py`: a `CallAccounting` object holding `tool_calls_total`, `tool_calls_emission`, `tool_calls_investigation` (always 0), `repair_turns`, accepted findings with sequential `f-n` ids, and token totals summed across turns (research R-13)
- [X] T052 [US1] Implement `src/agentic_review/core/agent/graph.py`: a LangGraph `StateGraph` with nodes `call_model` (sends system instructions + a user message of `material_statement` and `diff_section`) and `process_calls` (validates each tool call in order with `validate_call`, counts it, builds a `Finding` via `fingerprint` and `SCHEMA_VERSION`, appends one `ToolMessage` with the `ToolObservation` JSON per call; `invalid_tool_calls` are rejected as `arguments: not valid JSON`), edge `process_calls → END`; at `END`, completion is `emitted` when any call was made and `no-tool-call` (with its CF-6 degradation) when the first reply made none; no checkpointer, fresh state per review (research R-12, R-14, R-16)
- [X] T053 [US1] Implement `src/agentic_review/core/agent/build.py`: `build_review_port(settings: AgentSettings, credential: Credential, *, chat_model=None) -> ReviewPort`; builds `ChatOpenAI(base_url, model, api_key=credential.reveal(), temperature, timeout=requestTimeoutSeconds, max_retries=2  # PLACEHOLDER)` only when `chat_model` is None; binds `[{"type": "function", "function": {"name": "emit_finding", "description": ..., "parameters": tool_schema()}}]` with no `tool_choice`; `provider` = base URL host; returns an object whose `review(context)` runs the graph and returns `ReviewOutcome` (research R-10, R-11)
- [X] T054 [US1] Write `scripts/s1_tool_calling_probe.py` (not part of pytest): builds a fixed fixture diff with one planted defect in a temp repo, uses the real `assemble` and `build_review_port` with a real key from `AGENTIC_REVIEW_API_KEY`, runs `--runs N` (default 50) per `--model` at temperature 0, and writes `specs/001-walking-skeleton/s1-results.md` with per-run calls made, valid, schema-rejected, reference-rejected, invalid JSON, no call, repair fixed, tokens and latency; sets no pass mark (research R-21, quickstart C1)
- [X] T055 [P] [US1] Implement `src/agentic_review/core/output/verdict.py`: `compute_verdict(completion, findings) -> Verdict` per research R-17
- [X] T056 [P] [US1] Implement `src/agentic_review/core/output/json_out.py`: `to_json(report) -> str` (by alias, UTF-8, `\n` newline at end)
- [X] T057 [US1] Implement `src/agentic_review/core/output/build.py`: `build_report(*, change_summary, outcome | None, completion, degradations, settings, started_at, stage_durations, budget_hit, tool_version) -> ReviewReport` filling `RunMetadata` (null depths, `investigationToolsEnabled: false`, configured model fields and zero counters when no review ran), `context: []`, `evidence: {status: not-attempted, checks: []}`, and the verdict from `compute_verdict` (data-model §6, contracts/review-report.md)
- [X] T058 [US1] Implement `src/agentic_review/core/output/terminal.py`: `render_terminal(report, console)` producing the nine content items of contracts/cli.md "Terminal summary" in order, excluded paths collapsed to a count beyond 10, plain text when the console is not a terminal; the only Rich import under `core/`
- [X] T059 [P] [US1] Implement `src/agentic_review/core/pipeline/timing.py`: `StageTimer(clock)` with a `stage(name)` context manager recording integer milliseconds per stage that ran (FR-029)
- [X] T060 [US1] Implement `src/agentic_review/core/pipeline/preflight.py`: `preflight(request, env) -> PreflightFailure | PreflightOk(repo_root, settings, ignored_settings, credential)` performing checks 1 (inside a git repo), 2 (config valid) and 4 (credential) of contracts/cli.md in that order, every message redacted (FR-001 partial; US3 completes it)
- [X] T061 [US1] Implement `src/agentic_review/core/pipeline/run.py`: `ReviewRequest`, `Reviewed`, and `run_review(request, *, env, clock, now, review_port=None)` running preflight → change set (`resolve`, `summarise`, `measure_new_files`) → assembly → review (building the port through `core/agent/build.py` when none is injected) → output, timing every stage, redacting every degradation detail (contracts/internal-seams.md §1)
- [X] T062 [P] [US1] Implement `src/agentic_review/cli/exit_codes.py`: the verdict → integer table and `EXIT_PREFLIGHT = 3`
- [X] T063 [US1] Implement `src/agentic_review/cli/app.py`: Typer app with a `review` command (no options yet) that builds `ReviewRequest` from `Path.cwd()`, calls `run_review` with `os.environ`, prints a `PreflightFailure` message to stderr and exits 3, otherwise renders the terminal summary to stdout via a Rich `Console` and exits with the mapped code; `main()` entry point (contracts/cli.md, contracts/internal-seams.md §7)
- [X] T064 [US1] Run `uv run lint-imports` and `uv run pytest`; fix until green; mark US1 complete

**Checkpoint**: User Story 1 works end to end offline. Commit: `feat(review): review uncommitted changes in one model pass`. **MVP stop point.**

---

## Phase 4: User Story 2 — "No findings" never pretends to be a clean review (Priority: P2)

**Goal**: every failure after preflight still yields a report whose completion status, degradations and exit code tell it apart from a review with accepted findings.

**Independent Test**: the same fixture, a stand-in model scripted for each failure → each run produces a distinguishable report.

### Tests for User Story 2 ⚠️ write first

- [X] T065 [P] [US2] Write `tests/unit/agents/test_repair_turn.py`: one rejected call → a second model call whose messages are system, user, assistant reply, one `ToolMessage` per call, then the fixed repair user message of contracts/emit-finding.md; the repaired finding has `turnIndex 1`, `repairTurns == 1`, no degradation; a second rejection or a repair reply with no call → `invalid-model-output` (completion `invalid-model-output` if nothing accepted, else `emitted` with the degradation); repair is taken at most once; mixed valid/invalid calls accept the valid ones immediately (FR-016, research R-14). The code already has the repair loop but caps it at `MAX_REPAIR_TURNS = 5` (`agents/review_reporting_agent.py`), against this task and its own comment: the test pins it to one. **Langfuse:** the repair turn appears as a second `generation` under the review reporting agent, whose input ends with the repair message
- [X] T066 [P] [US2] Write `tests/unit/agents/test_ceiling.py`: with ceiling 2 and a reply of 4 calls, calls 3–4 get `denied` observations with the reason of contracts/emit-finding.md, findings 1–2 are kept, completion `ceiling-reached`, a `tool-budget-exhausted` degradation records 2 dropped calls; the repair turn consumes no slot but calls inside it do; no repair turn once the ceiling is reached (FR-017, research R-13). **Langfuse:** the denied calls are visible in the `validate_calls` node's output (their `denied` observations), so a trace shows what the ceiling cut
- [X] T067 [P] [US2] Write `tests/unit/agent/test_provider_errors.py`: `openai.APIConnectionError`, `APITimeoutError`, a 4xx `APIStatusError`, a 429, `httpx.HTTPError`, and `finish_reason == "content_filter"` each yield completion `provider-error` with a `provider-error` degradation (source `CF-6`) whose detail contains no canary key even when the exception message does; a provider error in the repair turn after accepted findings → `emitted` + `provider-error` degradation; `review()` never raises for these (FR-020, research R-10, R-17). **Langfuse:** a failed model call is a `generation` at level `ERROR` whose status message is the redacted detail, never the provider's own message; the canary check extends to tracer payloads (T107's helper)
- [X] T068 [P] [US2] Write `tests/unit/agents/test_no_tool_call.py`: a first reply with no tool call → `no-tool-call` (kept from US1); a **repair** reply with no tool call is `RepairFailed` → `invalid-model-output`, never `no-tool-call`; a first reply of only rejected calls is not `no-tool-call` (FR-018, gap D-5, data-model §5)
- [X] T069 [P] [US2] Write `tests/unit/assembly/test_budget.py`: an estimate above `budget.maxTokens` returns `BudgetExhausted(estimated_tokens, limit)` and never a truncated `ReviewContext`; an estimate at the limit is accepted (FR-019). **Langfuse:** the estimate and the limit belong in the `assemble_context` node's output, so an over-budget run is explainable from the trace alone
- [X] T070 [US2] Write `tests/integration/test_story2_failure_modes.py` covering US2 acceptance scenarios 1–7 through `run_review` and the CLI: provider failure → exit 2 and "No review was performed"; repair success → normal report, empty degradations; repair failure with nothing accepted → `invalid-model-output`, exit 2 (AC-13); no tool call → `no-tool-call`, exit 0, and both outputs carry the D-5 wording; ceiling reached → findings kept, `ceiling-reached`; diff over the limit → `budget-exhausted`, stage keys include `assembly` but not `review`, the stand-in called 0 times, exit 2; accepted findings with no damage → `degradations == []`. Also asserts that the eight outcomes of contracts/review-report.md differ pairwise in (exit, completionStatus, degradation codes) (SC-003). Every report passes the `report_assertions` helpers. **Langfuse:** each scenario also runs under the capturing tracer of T107 and asserts no secret in any payload, and that the trace for a run with no model call (budget exhausted) holds no `generation`

### Implementation for User Story 2

- [X] T071 [P] [US2] Implement `src/agentic_review/agents/provider_errors.py`: `to_degradation(exc, secret) -> Degradation` for `openai.APIError` subclasses and `httpx.HTTPError`, plus `content_filter_degradation()`; details redacted (research R-9, R-10). **Langfuse:** the same redacted detail is what the failed `generation` carries — one mapping, used for the report and the trace
- [X] T072 [US2] Extend `src/agentic_review/core/review/accounting.py` with the ceiling: `admit_call()` returning whether the call may be processed, a dropped-call count, and the `denied` observation reason (research R-13)
- [X] T073 [US2] Extend `src/agentic_review/agents/review_reporting_agent.py`: the conditional edge `decide_repair → call_model` (`process_calls` was split into `validate_calls → record_coverage → decide_repair`) taken only when `rejected > 0 and repair_turns == 0 and ceiling not reached`, the repair user message, `turnIndex 1` for repair-turn findings; provider exceptions and `content_filter` caught in `call_model`; completion status and degradations derived at `END` per the state machine of data-model §5 and research R-17 (no-tool-call, ceiling-reached, invalid-model-output, provider-error). **Langfuse:** keep node names stable — they are the observation names every saved trace filter and dashboard keys on
- [X] T074 [US2] Extend `src/agentic_review/core/assembly/budget.py` and `prompt.py`: `BudgetExhausted(estimated_tokens, limit)`, and `assemble` returns it when the estimate over the whole prompt exceeds `budget.maxTokens` (TBD-3 placeholder), never building a partial diff (FR-019)
- [X] T075 [US2] Extend `src/agentic_review/agents/pipeline_agent.py`: on `BudgetExhausted`, record a `budget-exhausted` degradation (source `CF-4`, redacted detail with estimate and limit), set `budgetHit: true`, skip the review stage, go to output (FR-019, FR-022). Skipping is a conditional edge `assemble_context → build_report`, so the graph (and the trace) shows the review node was not run rather than run as a no-op
- [X] T076 [US2] Extend `src/agentic_review/core/output/terminal.py`: for completion `no-tool-call`, print "No findings. The model made no tool call, so this build cannot tell a change with nothing to report from a model that did not use the finding tool." (research R-16)
- [X] T077 [US2] Add `--ceiling N` (integer ≥ 1) to `review` in `src/agentic_review/cli/app.py`, overriding `agent.toolCallCeiling` (contracts/cli.md). `ReviewRequest.ceiling` and the override in the `preflight` node already exist; this adds the flag. **Langfuse:** the effective ceiling is trace metadata (T106), so runs can be filtered by it
- [X] T078 [US2] Run `uv run lint-imports` and `uv run pytest`; fix until green

**Checkpoint**: Stories 1 and 2 both pass. Commit: `feat(review): report every failure mode as a degradation`.

---

## Phase 5: User Story 3 — Fail fast, before spending anything (Priority: P3)

**Goal**: every preflight problem stops the run with a message naming it, exit 3, and zero model calls.

**Independent Test**: no repository, one invalid config field, no credential → each exits 3 with a specific message; the stand-in model is called zero times.

### Tests for User Story 3 ⚠️ write first

- [ ] T110 [P] [US3] Extend `tests/unit/findings/test_schema.py`: `report_schema()` lists exactly the five scope kinds `working-tree`, `staged`, `range`, `commit`, `pull-request` (the test exists since Phase 10 and lists four: add `commit`); and extend `tests/unit/config/test_settings.py`: `scope: commit` in the config file is rejected naming `scope`, because a commit is named per run and never by the file (FR-10.3a as amended in SRS v1.4, data-model §2 and §7)
- [ ] T079 [P] [US3] Write `tests/unit/pipeline/test_preflight.py` (create `tests/unit/pipeline/__init__.py`): checks run in the order of contracts/cli.md and stop at the first failure; `range` without `--base` names `--base`; `--base` with a non-range scope is rejected; an unknown base names the ref; `range` with unborn `HEAD` is refused; an explicit `--config` path that does not exist fails; every message says nothing was reviewed. `preflight()` now takes `CredentialSources`, not the environment (commit `452735e`). **Commit scope:** `--scope commit` without `--commit` names `--commit`; `--commit` with any other `--scope`, or with `--base`, is rejected naming `--commit`; `--commit` alone is coherent and selects the scope; an unknown commit names the ref, in a repository with no commits too. **Phase 10:** `tests/unit/pipeline/test_preflight.py` exists (T115) and already covers the `range` and `--pr` cases; add check order across all five, the explicit `--config` path that does not exist, and the commit cases
- [ ] T080 [US3] Write `tests/integration/test_story3_preflight.py` covering US3 acceptance scenarios 1–5 through the CLI: not a repo (message names the directory), invalid field and unknown field (message names the dotted path), missing credential (names `AGENTIC_REVIEW_API_KEY` and the user-level path), unknown range base (names the ref); each exits 3, stdout is empty even with `--json`, the stand-in model `call_count == 0`, and `resolve` was not called (SC-004). **Langfuse:** a preflight failure still yields one short trace — the `preflight` node, then `END` — whose output is the redacted failure message. **Commit scope:** scenario 4 also covers `--commit nope` — stderr names `nope`, exit 3, `resolve` not called. **Phase 10:** the range and pull-request failures are already covered through the CLI by `tests/integration/test_pull_request_scope.py`

### Implementation for User Story 3

- [ ] T111 [US3] Add the `commit` scope to the types the later tasks build on: `ScopeKind` in `src/agentic_review/core/findings/report.py` gains `commit` (`ScopeSetting` in `core/config/settings.py` does **not**); `ScopeRequest` in `core/changeset/model.py` and `ReviewRequest` in `agents/pipeline_agent.py` each gain `commit: str | None = None`. `SCHEMA_VERSION` stays `1.0` — the value is added before feature 001 first publishes the schema. `resolve` keeps raising `NotImplementedError` for the scope until T086. T079–T082 depend on this task
- [ ] T081 [US3] Complete `src/agentic_review/core/pipeline/preflight.py`: add check 3 (scope arguments coherent) and check 5 (base exists via `ref_exists`, `HEAD` not unborn for `range`) in contract order; every message states what is wrong, where it was looked for, and that nothing was reviewed (FR-001). **Commit scope:** check 3 gains `commit` ⇔ `--commit` and the `--commit`/`--base` conflict; check 5 gains "the commit named by `--commit` exists" via `ref_exists`, naming the ref. **Phase 10:** checks 3 and 5 exist for `range` and `--pr` (T122); only the `commit` half remains
- [ ] T082 [US3] Add `--config PATH` and `--base REF` options to `review` in `src/agentic_review/cli/app.py`, passing them into `ReviewRequest`. **Commit scope:** add `--commit REF` as well, passed into `ReviewRequest.commit`. **Phase 10:** `--config`, `--base` and `--head` exist (T124); only `--commit` remains
- [ ] T083 [US3] Run `uv run lint-imports` and `uv run pytest`; fix until green

**Checkpoint**: Stories 1–3 pass. Commit: `feat(preflight): stop before any model call on a named problem`.

---

## Phase 6: User Story 4 — Choose what gets reviewed (Priority: P4)

**Goal**: staged, range and single-commit scopes, default and configured exclusions, and an honest "nothing to review".

**Independent Test**: fixture with staged and unstaged edits, a two-commit branch and a changed `dist/` file → each scope, including one of the branch's commits on its own, reviews exactly the expected files, and `dist/` appears only as excluded.

### Tests for User Story 4 ⚠️ write first

- [ ] T084 [P] [US4] Write `tests/unit/changeset/test_resolve_scopes.py`: `staged` sees only index changes (`git diff --cached`, empty tree when unborn); `range` uses the merge-base (`base...HEAD`) and ignores commits merged into `base` after the branch point; `ResolvedScope` records `baseRef` as given, `headRef == "HEAD"`, and abbreviated commit IDs in the description; `measure_new_files` reads the index blob for `staged` and the `HEAD` blob for `range` (FR-005, FR-006, research R-4, R-5). **Commit scope:** `commit` compares the named commit with its first parent (`git diff REF^1 REF`) and sees none of the commits after it, no staged or unstaged edit and no untracked file; a root commit is compared with the empty tree, every file `added`; a merge commit is compared with its first parent (add a `merge(name)` helper to `tests/support/repo_builder.py`); a rename inside the commit keeps `previous_path`; `ResolvedScope` records `kind == "commit"`, `headRef` as given (an ID, a branch name, `HEAD~1`), `baseRef` null, `wasDefaulted` false, and a description carrying the abbreviated IDs of the commit and its parent and saying when it is a root or a merge commit; `measure_new_files` reads the commit's blob, so a later edit to the same file in the working tree does not change the count. **Phase 10:** the `range` cases are in `tests/unit/changeset/test_resolve_range.py` (T113); write `staged` and `commit` here
- [ ] T085 [US4] Write `tests/integration/test_story4_scopes_and_exclusions.py` covering US4 acceptance scenarios 1–5: staged scope stated as chosen (`wasDefaulted: false`), also when named by the config file; range reviews base→head and records both; a `dist/` file is excluded with `default:build-output` and never in the prompt the stand-in received; a configured pattern adds to the defaults; all changes excluded/deleted/binary/non-TS → `nothing-to-review`, reasons listed, stand-in called 0 times, exit 0, and a JSON report still written (FR-008, FR-010, SC-009). **Commit scope:** scenario 6 — with a later commit on top and uncommitted edits to the same file, `--commit <first commit>` puts only that commit's hunks in the prompt the stand-in received; the scope is stated as that commit and as chosen; `--commit` wins over a `scope:` named by the config file; a commit touching only excluded or non-TS files → `nothing-to-review`. **Phase 10:** scenario 2 (range) and scenarios 7–8 are covered by `tests/integration/test_pull_request_scope.py` (T116)

### Implementation for User Story 4

- [ ] T086 [US4] Extend `src/agentic_review/core/changeset/resolve.py` with the `staged` and `range` scopes per research R-4, and `src/agentic_review/core/changeset/summary.py` so `measure_new_files` reads the reviewed version for each scope (`git show :path`, `git show HEAD:path`). **Commit scope:** `resolve` handles `commit` (first parent, or the empty tree when `REF^1` does not exist; no `ls-files --others`), reusing the tracked-comparison path the other scopes use; `measure_new_files` reads `git show REF:path`. No read of the working tree or the index on this path. **Phase 10:** `range` is built on `diff_branches`, and `_collect` is the shared diff-to-files path (T119); add `staged` and `commit` on it
- [ ] T087 [US4] Extend `src/agentic_review/agents/pipeline_agent.py` (was `core/pipeline/run.py`; moved by ADR-0009/ADR-0010): scope precedence flag → config → default with `was_defaulted` true only when neither named it, and configured `exclude` passed to `resolve` — both **already present** in the `resolve_change_set` node, so verify rather than rebuild; when `reviewable_files` is empty, skip assembly and review and build a `nothing-to-review` report, as a conditional edge `resolve_change_set → build_report` so the graph stays acyclic and the skip is visible (FR-006, FR-010). **Langfuse:** a nothing-to-review trace has no `generation`, and the resolved scope kind is a trace tag (T106). **Commit scope:** `request.commit` set → scope kind `commit` ahead of the config's `scope`, `was_defaulted` false, and `ScopeRequest.commit` passed to `resolve`. **Phase 10:** `ScopeRequest.head` is passed, and a pull request opened by preflight bypasses `resolve` (T123); the nothing-to-review edge must cover that path too
- [ ] T088 [US4] Add `--scope working-tree|staged|range|commit` to `review` in `src/agentic_review/cli/app.py` (`--commit` itself arrives with T082; `commit` is accepted here so that `--scope commit --commit REF` is valid). **Phase 10:** `--scope` exists and offers `working-tree` and `range`; add `staged` and `commit` to `OFFERED_SCOPES`
- [ ] T089 [US4] Run `uv run lint-imports` and `uv run pytest`; fix until green

**Checkpoint**: Stories 1–4 pass. Commit: `feat(changeset): add staged, range and commit scopes and nothing-to-review`.

---

## Phase 7: User Story 5 — Use the result from a script (Priority: P5)

**Goal**: a JSON report on stdout or in a file, a `schema` command, `--version`, and complete run metadata.

**Independent Test**: request JSON to stdout and to a file for a findings run and each Story 2 failure → every report validates against `agentic-review schema`, and stdout holds only the JSON document.

### Tests for User Story 5 ⚠️ write first

- [ ] T090 [P] [US5] Write `tests/unit/cli/test_argv_normalisation.py`: a bare `--json` at the end of argv, or followed by a token starting with `-`, becomes `--json -`; `--json out.json` is unchanged; `-` means stdout (research R-18)
- [ ] T091 [US5] Write `tests/integration/test_story5_machine_output.py` covering US5 acceptance scenarios 1–5: `review --json` → stdout parses as exactly one JSON document, summary on stderr; `review --json out.json` → file written (UTF-8, `\n`), summary on stdout; `schema` exits 0 from a non-repo directory with no credential and prints a schema that `jsonschema` accepts as a valid Draft 2020-12 schema; every report from Stories 1, 2 and 4 scenarios validates against the printed schema; the report carries model, provider, sampling, ceiling, `investigationToolsEnabled: false`, the four counters, completion status, schema and tool versions, `startedAt`, `durationMs` and per-stage durations; `--version` prints `agentic-review 0.1.0 (report schema 1.0)` (FR-025, FR-026, FR-028, SC-002)

### Implementation for User Story 5

- [ ] T092 [US5] Implement in `src/agentic_review/cli/app.py`: `normalise_argv(argv)`; `--json [PATH]` choosing streams per contracts/cli.md "Streams" (Rich summary to stderr when JSON goes to stdout); writing the report file; the `schema` command printing `report_schema()` as JSON; the `--version` callback (research R-18, FR-025, FR-028). **Langfuse:** the report gains no trace id or URL — that would change the published schema, which needs a spec change first. `schema` and `--version` never initialise tracing
- [ ] T093 [US5] Run `uv run lint-imports` and `uv run pytest`; fix until green

**Checkpoint**: all five stories pass. Commit: `feat(cli): add JSON report output, schema command and version`.

---

## Phase 8: Polish & Cross-Cutting Concerns

- [ ] T094 [P] Write `tests/integration/test_edge_cases.py` covering every spec "Edge Cases" bullet: renamed file reviewed under its new path with previous path recorded; deleted, binary and `README.md`/`package.json` listed and not reviewed; running from a subdirectory; findings for an unreviewed file, an out-of-range line, check or context evidence, or a `ruleId` rejected with the fixed reasons; mixed valid/invalid calls in one reply; partial acceptance with a failed repair → `emitted` + degradation; prose with no call discarded; `--json` on preflight failure leaves stdout empty; `context`/`checks` sections accepted, no effect, one stderr notice (FR-031). **Langfuse:** every case runs under T107's capturing tracer with the no-secret assertion
- [ ] T095 Print the ignored-settings notice once to stderr in `src/agentic_review/cli/app.py` from `Reviewed.ignored_settings`, listing the dotted paths set for unbuilt capabilities (FR-003)
- [ ] T096 Handle unexpected internal errors after preflight in `src/agentic_review/cli/app.py`: one redacted stderr line, the report path if one was written, exit 2, traceback only when `AGENTIC_REVIEW_DEBUG=1` (research R-24), with a test in `tests/unit/cli/test_internal_error.py`. Restore the `AGENTIC_REVIEW_DEBUG` lines that commit `06b8342` removed from `.env.example`. **Langfuse:** the trace is still flushed, with the root observation at level `ERROR` and the same redacted one-line message
- [ ] T097 Run the full offline suite with no `AGENTIC_REVIEW_API_KEY` and no `LANGFUSE_*` keys set: `uv run lint-imports` and `uv run pytest` green (SC-006)
- [ ] T098 Walk quickstart.md group B (B1–B6) by hand in a scratch repository and record any deviation. **Langfuse:** repeat B1 with the `LANGFUSE_*` keys set and confirm one trace per run appears. **Commit scope:** B5 now includes `review --commit nope`; also run `review --commit HEAD` and confirm the scope line names that commit
- [ ] T099 [P] Update `specs/README.md`: feature 001 status → implemented (S-1 and SC-001 pending a real key)
- [ ] T100 **Maintainer, needs a real key:** run `uv run python scripts/s1_tool_calling_probe.py --runs 50 --model meta/llama-3.3-70b-instruct`, read `specs/001-walking-skeleton/s1-results.md`, decide the default model and whether FR-5.6b is pulled forward, and record the one-line summary in `Docs/technical_stack.md` §7 (quickstart C1, research R-21). The existing `s1-results.md` covers only `qwen2.5-coder:7b` (0 tool calls in 50 runs); the planned default has not been probed. **Langfuse:** with keys set, tag the probe's traces `s1` and the model name so failed runs can be read call by call
- [ ] T101 **Maintainer, needs a real key:** run quickstart C2 against a public TypeScript repository (SC-001). **Langfuse:** keep the trace link with the result

---

## Phase 9: Langfuse tracing (added 2026-09-24)

**Purpose**: an optional trace of every review in Langfuse — one trace per run, one observation per pipeline node, the
model call as a `generation` with model name and token usage — for debugging and, later, evaluation.

**Authority**: this phase is **outside spec 001's requirements**; no `FR-0NN` asks for it. It is admitted by
`Docs/technical_stack.md` §6 (a hosted tracing service *alongside* our own record, never the only one; FR-11.3) and
bounded by §3.9 (the credential is never in the trace). T102 records the library choice where the stack document
requires it. It can land any time after US1; landing it **before US2** gives the Langfuse notes in Phases 4–8
something to check against.

**Independent Test**: with the `LANGFUSE_*` keys unset, the suite runs offline and unchanged; with an in-memory span
exporter in place of the network, a stand-in review produces one trace whose nodes, generation, names and metadata
match T106, and no payload carries a secret.

### Tests for Phase 9 ⚠️ write first

- [ ] T104 [P] Write `tests/unit/agents/test_tracing.py`: tracing is off (no client built, no handler, no socket opened) when `LANGFUSE_PUBLIC_KEY` or `LANGFUSE_SECRET_KEY` is absent; on when both are set; the mask replaces the provider credential wherever it appears in an observation's input, output or metadata; an exporter or handler that raises never fails the review and never changes its report (FR-11.2)
- [ ] T107 Extend `tests/integration/test_trace_carries_no_credential.py` into a shared helper (`tests/support/tracer_capture.py`) that later integration tests reuse, and add a run through the **real** Langfuse handler with `Langfuse(span_exporter=InMemorySpanExporter())`: the exported spans hold neither the provider credential nor `LANGFUSE_SECRET_KEY`, and the trace has the shape of T106 (trace name, one span per node that ran, the review reporting agent typed `agent`, the model call typed `generation` with token usage)

### Implementation for Phase 9

- [ ] T102 [P] Record Langfuse in `Docs/technical_stack.md`: §5 dependency inventory (role: optional hosted tracing; swap cost low — confined to `agents/`), §7 pinned version (`langfuse` 4.15.5, installed by commit `06b8342`), and a line in §6 saying it is the hosted service used alongside FR-11.3's own record, which it never replaces
- [ ] T103 [P] Add import contract 7 to `pyproject.toml` — `cli` and `core` may not import `langfuse`; only `agents/` may — and update the contract count wherever it is stated (`CLAUDE.md`, `Docs/technical_stack.md` §4)
- [ ] T105 Read the tracing settings the way the credential is read (commit `452735e`): `core/config/` gains a function that keeps only `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` (masked, as `Credential` is), `LANGFUSE_BASE_URL` and `LANGFUSE_TRACING_ENVIRONMENT` from the environment, and returns `None` when either key is missing. It travels to the pipeline as run context (`PipelineDeps`), never as state
- [ ] T106 Implement `src/agentic_review/agents/tracing.py` and wire it into `run_review`: build the Langfuse client from T105's settings (release = `agentic_review.__version__`, a mask that redacts the provider credential); attach the LangChain `CallbackHandler` to the pipeline invocation; trace name `review-change-set` with tags `cli` and the scope kind, metadata model, provider host, ceiling and completion status; compile the review reporting agent's graph under a distinct name so it is a separate, `agent`-typed node rather than a second anonymous `LangGraph`; set the trace's input to the review request and its output to the verdict and finding counts, not the raw state; `flush()` in a `finally` so a short-lived CLI run never loses its trace. Follow `.claude/skills/langfuse` and fetch the current Langfuse docs before writing it
- [ ] T108 [P] Document tracing in `Docs/operation_guidelines.md`: how to switch it on (the three `LANGFUSE_*` variables, already in `.env.example`), and plainly that with tracing on, the diff under review and the model's replies are sent to the Langfuse project — a data-egress decision for whoever sets the keys
- [ ] T109 **Maintainer, needs real keys:** run one review with tracing on, fetch the trace (`npx langfuse-cli`), audit it against the fetched https://langfuse.com/docs/observability/best-practices, fix the gaps, and record the audited trace link and what changed

**Checkpoint**: suite green with and without the in-memory exporter; `uv run lint-imports` passes with contract 7. Commit: `feat(agents): trace reviews to Langfuse when configured`.

---

## Phase 10: Pull-request scope and a nameable range head (added 2026-10-09)

**Purpose**: review a public GitHub pull request by URL, and a local branch without checking it out, from two
explicit change-set functions: `diff_branches` (the three-dot diff) and `GitPullRequestSource` (the fetch).

**Authority**: SRS v1.5 (FR-10.3a amended, FR-10.3d new, FR-4.8 extended) and
[ADR-0011](../../Docs/adr/0011-cli-reads-a-public-pull-request.md); spec FR-005, FR-032 and Story 4 scenarios 7–8;
[research R-25](./research.md#r-25--reading-a-pull-request-added-2026-10-09-srs-v15-adr-0011); plan D-13.

**Built out of order, at the maintainer's request**: it depends only on US1, and it delivers the `range` half of
User Stories 3 and 4 early. The **Phase 10:** notes on T079–T088 say what is left for those stories.

**The git-based fetch is interim.** It is to be replaced by a `PullRequestSource` backed by the official GitHub MCP
server. That is not a task here: it needs its own ADR (a GitHub token, an MCP client outside `core/`). Until then,
no task may add to `core/changeset/pull_request.py` a feature the MCP server already provides, and nothing outside
`core/changeset/` may learn how a pull request was fetched.

**Independent Test**: with a local repository served over `file://` standing in for GitHub, `review --pr <URL>`
run from a directory that is not a repository reviews exactly what the pull request changed since it left the
default branch, honours no configuration from it, and leaves no temporary directory behind — and a
`PullRequestSource` that never touches git yields the same kind of report.

### Tests for Phase 10 ⚠️ write first

- [X] T112 [P] Extend `tests/support/repo_builder.py` with `config`, `update_ref`, `delete_branch`, `rev_parse`; create `tests/support/pull_request_remote.py` — a repository whose pull request exists only under `refs/pull/7/head`, with `uploadpack.allowFilter` set, a commit on `main` after the branch point, a `dist/` change and a hostile `.agentic-review.yml` inside the pull request; expose it as a session-scoped `pull_request_remote` fixture in `tests/conftest.py` (research R-25)
- [X] T113 [P] Write `tests/unit/changeset/test_resolve_range.py`: three-dot semantics (what the base did after the branch point is absent); a head that is not checked out; `head` defaulting to `HEAD`; uncommitted and untracked files not part of a range; renames; exclusions; `ResolvedScope` fields and description; line counts from the head blob, not the working tree; `diff_branches` on its own; unrelated histories have no merge base (FR-10.3a, research R-4)
- [X] T114 [P] Write `tests/unit/changeset/test_pull_request.py`: the URL table (accepted and rejected, including an argument-injection attempt); the clone argv carries `--filter=blob:none --no-checkout` and no credential helper; git cannot prompt; the clone has only `.git` and is missing blobs; the change set, scope and line counts of the fixture pull request; a named base; `close` removes the clone, read-only pack files included; unknown pull request, unknown base and unreachable repository each raise `PullRequestError` naming the problem and leave nothing behind (FR-10.3d, research R-25)
- [X] T115 [P] Write `tests/unit/pipeline/test_preflight.py` (create `tests/unit/pipeline/__init__.py`) for what Phase 10 adds: `range` ⇔ `--base`, `--head` only with `range`, unknown base and head named, no common history, unborn head, an option-shaped ref refused; `--pr` needs no repository, passes `--base` to the source, rejects `--scope` and `--head`, names a malformed URL before anything is fetched; a missing credential never costs a fetch; a `PullRequestError` becomes a redacted preflight failure; configuration is taken from `--config` only. **T079 completes this file** for User Story 3
- [X] T116 Write `tests/integration/test_pull_request_scope.py` through `run_review` and the CLI: Story 4 scenarios 7 and 8; a finding past the end of the head version is rejected; configuration inside the pull request, and in the working directory, is not honoured while `--config` is; an unknown pull request exits 3 with the stand-in called 0 times; the clone is gone after success, after a preflight failure and after a later stage raises; **a source that never touches git produces the same kind of report**; every report passes the `report_assertions` helpers. Extend `tests/unit/findings/test_schema.py` (the scope kinds) and `tests/unit/config/test_credentials.py` (no local repository)

### Implementation for Phase 10

- [X] T117 Record the decision before the code: `Docs/adr/0011-cli-reads-a-public-pull-request.md` and its row in `Docs/adr/README.md`; SRS v1.5 (FR-10.3a, FR-10.3d, FR-4.8, §1.2, §7, Appendix B); `Docs/design/02-domain-model.md` §3.1 and `04-contracts.md` §6; this feature's spec, contracts, data model, research R-4 and R-25, plan D-13; `CLAUDE.md`
- [X] T118 [P] Extend `src/agentic_review/core/changeset/_git.py`: optional `env` and `timeout` on `run_git`/`run_git_bytes`; a timeout is raised as `GitError`. Still the only module that runs git
- [X] T119 Extend `src/agentic_review/core/changeset/resolve.py`: move the shared diff-to-files body into `_collect`; add `BranchDiff`, `diff_branches(repo_root, base, head, exclude)` and `have_merge_base`; `resolve` handles `range` through it. `ScopeRequest` gains `head` (`core/changeset/model.py`); `measure_new_files` reads the head blob for `range` and `pull-request` (`core/changeset/summary.py`). `staged` keeps raising until T086
- [X] T120 Create `src/agentic_review/core/changeset/pull_request.py`: `PullRequestRef`, `parse_pull_request_url`, `PullRequestError`, the `PullRequestSource` and `OpenedPullRequest` protocols, `clone_arguments`, `discard_workspace`, and `GitPullRequestSource` per research R-25; the fetch timeout labelled `PLACEHOLDER`; the module docstring states that it is interim and what replaces it
- [X] T121 [P] `ScopeKind` in `src/agentic_review/core/findings/report.py` gains `pull-request` (`ScopeSetting` does not: it is never a config value); `find_credential` in `core/config/credentials.py` accepts no repository root
- [X] T122 Extend `src/agentic_review/core/pipeline/preflight.py`: keyword arguments `scope`, `base`, `head`, `pr`, `pull_requests`; check 1 accepts a pull request URL in place of a repository; check 2 never reads a pull request's or the working directory's file for `--pr`; check 3 for `range` and `--pr`; check 5 for range refs and `source.open`. `PreflightOk.repo_root` may be None and it gains `pull_request`
- [X] T123 Extend `src/agentic_review/agents/pipeline_agent.py`: `ReviewRequest.head` and `.pr`; `PipelineDeps.pull_requests` (default `GitPullRequestSource`) and the matching `run_review` keyword; `_resolve_change_set` uses the opened pull request when there is one; `run_review` closes it in a `finally`. The graph is unchanged. **Langfuse:** the opened pull request is pipeline state and so is traced — it holds a path and ref names, never a secret
- [X] T124 Extend `src/agentic_review/cli/app.py`: `--scope` (only built values are offered: `working-tree`, `range`; anything else exits 3), `--base`, `--head`, `--pr`, `--config`
- [X] T125 Add section "5 · Review a branch range and a pull request" to `notebooks/run_review_quickstart.ipynb`: settings (`RANGE_BASE`, `RANGE_HEAD`, `PR_URL`, `PR_BASE`, all `None` so "Run All" skips them), a range run, a pull-request run that confirms no temporary clone is left, and a preflight failure on purpose. Saved without outputs
- [X] T126 [P] Document the new flags in `Docs/operation_guidelines.md`, plainly including that `--pr` contacts github.com and that the pull request's diff is sent to the model provider
- [ ] T127 **Maintainer, needs a real key and network:** run `uv run --env-file .env agentic-review review --pr <URL of a public TypeScript pull request>` from outside any repository; confirm the scope line names the pull request and its base, and that no `agentic-review-pr-*` directory is left in the temp folder. Then run the notebook's section 5

**Checkpoint**: `uv run python -m pytest` and the import contracts green. Commit: `feat(changeset): review a public pull request and a named branch range`.

---

## Dependencies & Execution Order

### Phase dependencies

```mermaid
flowchart LR
    P1["Phase 1<br/>Setup"] --> P2["Phase 2<br/>Foundational"]
    P2 --> US1["Phase 3<br/>US1 · MVP"]
    US1 --> US2["Phase 4<br/>US2"]
    US1 --> US3["Phase 5<br/>US3"]
    US1 --> US4["Phase 6<br/>US4"]
    US1 --> US5["Phase 7<br/>US5"]
    US2 & US3 & US4 & US5 --> P8["Phase 8<br/>Polish"]
    US1 -.->|"T054 script exists"| S1["T100 S-1 run<br/>(maintainer)"]
    US1 --> P9["Phase 9<br/>Langfuse"]
    US1 --> P10["Phase 10 ✅<br/>PR scope · range head"]
    P10 -.->|"range half already built"| US3
    P10 -.->|"range half already built"| US4
    P9 -.->|"recommended before"| US2

    style US1 fill:#fff4e0
    style S1 fill:#f2f2f2
    style P9 fill:#eef4ff
    style P10 fill:#e8f7e8
```

- **Setup → Foundational → US1** is strictly sequential.
- **US2–US5 each depend only on US1**, since US1 creates the pipeline and CLI they extend. They touch shared files
  (`agents/pipeline_agent.py`, `cli/app.py`), so run them one at a time, in priority order.
- **Phase 9 (Langfuse)** depends only on US1. Doing it before US2 lets every later phase check its **Langfuse:**
  note as it lands. Order within it: T104, T107 (tests) → T102, T103, T105 → T106 → T108 → T109.
- **T111 (the `commit` scope's types) comes first in US3**: T079–T082 and every **Commit scope:** note build on it.
- **Phase 10 (pull-request scope)** depended only on US1 and is done, apart from the maintainer's live run (T127).
  It built `--scope`, `--base`, `--head`, `--config` and `range` resolution, so US3 and US4 are smaller than
  their task text reads: follow the **Phase 10:** notes.
- **US5's integration test** reuses scenarios from US2 and US4, so it should land after them (it is P5 anyway).
- **T100 (S-1)** needs only T053–T054. It blocks SC-001 and the default model choice, not any other task.

### Within each phase

- Tests are written first and fail. Then models, then services, then the pipeline and CLI wiring.
- In Phase 2: T017 → T018 → {T019, T020} → T021 → T022 → T023. T036–T038 → T039 → T040 → T041.

### Parallel opportunities

- Phase 1: T003, T004, T005, T007 after T001–T002.
- Phase 2: T009–T012 together; T013–T016 together; T024–T027 together; T032–T035 together; T028/T029 and T036–T038 together.
- US1: T042–T047 together; T049, T051, T055, T056, T059, T062 together.
- US2: T065–T069 together.

## Parallel Example: User Story 1

```text
Task: "Write tests/unit/assembly/test_prompt.py"
Task: "Write tests/unit/agent/test_binding.py"
Task: "Write tests/unit/agent/test_graph_happy_path.py"
Task: "Write tests/unit/output/test_verdict.py"
Task: "Write tests/unit/output/test_render.py"
Task: "Write tests/unit/cli/test_exit_codes.py"
```

---

## Implementation Strategy

### MVP first (User Story 1 only)

1. Phase 1: Setup. Commit `build: scaffold agentic-review package and CI`.
2. Phase 2: Foundational. Commit.
3. Phase 3: User Story 1. Commit.
4. **Stop and validate**: `uv run pytest`, `uv run lint-imports`, and a manual `agentic-review review` in a scratch repository.

### Incremental delivery

Langfuse (Phase 9) → US2 (honest failures) → US3 (preflight) → US4 (scopes) → US5 (machine output) → Polish. Each phase ends green and is committed on its own.

---

## Requirement coverage

Every FR and SC in spec.md maps to at least one task.

| Requirement | Tasks |
|---|---|
| FR-001 | T060, T079–T081, T111, T115, T122 |
| FR-002 | T024, T025, T028, T030, T080 |
| FR-003 | T025, T030, T094, T095 |
| FR-004 | T008, T026, T029, T031, every integration test via `assert_no_canary` |
| FR-005, FR-006 | T034, T040, T048, T082, T084–T088, T110, T111, T113, T116, T119, T123, T124 |
| FR-032 | T112, T114–T117, T120, T122, T123 |
| FR-007 | T032, T034, T036, T039, T040 |
| FR-008 | T033, T038, T040, T085, T087 |
| FR-009 | T032, T034, T035, T041, T094 |
| FR-010 | T085, T087 |
| FR-011, FR-012 | T042, T043, T050, T052, T053 |
| FR-013, FR-014, FR-015 | T013, T015, T017, T022, T044, T052, T094 |
| FR-016 | T065, T073 |
| FR-017 | T066, T072, T073, T077 |
| FR-018 | T043, T068, T073, T076 |
| FR-019 | T069, T074, T075 |
| FR-020 | T067, T071, T073 |
| FR-021 | T044, T051 |
| FR-022 | T070, T075 |
| FR-023 | T045, T047, T055, T062 |
| FR-024, FR-027 | T046, T048, T058 |
| FR-025, FR-028 | T090–T092 |
| FR-026 | T018, T057, T091 |
| FR-029 | T023, T059, T061 |
| FR-030 | T002, T011, T012 |
| FR-031 | T048, T070, T080, T085, T091, T094 |
| SC-001 | T101 (maintainer) |
| SC-002 | T023, T048, T091 |
| SC-003 | T070 |
| SC-004 | T080 |
| SC-005 | T015, T023 (invariants 6–7) |
| SC-006 | T007, T008, T097 |
| SC-007 | T008, T023, every integration test |
| SC-008 | T023, T048 |
| SC-009 | T033, T085 |
| *(no spec 001 requirement)* `Docs/technical_stack.md` §6, §3.9 · FR-11.3 "alongside, never the only record" | T102–T109 (Phase 9, Langfuse) |

## Phase 11: The HTML report (added 2026-10-18)

**Purpose**: a third rendering of the same `ReviewReport` — one self-contained HTML document — produced either
during a review (`review --html PATH`) or from a report written earlier (`render REPORT --html PATH`), from one
renderer in `core/output/`.

**Authority**: SRS **FR-10.4d (Should, new in v1)**, with FR-10.4a's "derived from the finding model and not
produced independently" and FR-5.10's clean-versus-never-looked distinction; `Docs/technical_stack.md` §2, §3.1,
§3.7, §4 (contract 8) and §5; `Docs/design/01-logical-architecture.md` §4; `contracts/cli.md` §`render`.
No ADR: a templating library is a technology selection, which `CLAUDE.md` places in `technical_stack.md`, and no
load-bearing constraint is reversed.

**It is a Should.** v1 is complete without it. No acceptance criterion depends on it, Appendix B's "Verified by"
column for CF-7 is unchanged, and AC-7 and AC-16 keep saying "in both outputs" — they are Must-level and must not
come to depend on a Should.

**T092 remains unchecked.** This phase implements only `--json PATH`, the named-file half of FR-025, because
`render` needs a producer. Still T092's: `normalise_argv`, the optional-value `--json [PATH]` form, `--json` and
`--json -` to **stdout** with the "Streams" switch that moves the summary to stderr, the `schema` command, and the
`--version` callback — along with T090 and T091 in full. **User Story 5 is not complete and its checkpoint is not
reached.**

**The HTML gains no Langfuse trace id or URL**, for the reason T092 already records: the report carries none, and
adding one would change the published schema, which needs a spec change first.

**A boundary for later, needing its own ADR**: if the HTML ever gains client-side script, or is published anywhere
(a gh-pages artifact, an email attachment sent by the tool), that is a distribution and data-egress decision of the
ADR-0006/ADR-0007 kind, and FR-10.4d's no-script clause has to be reversed in a new record first.

**Independent Test**: `review --json r.json --html a.html` on a repository with planted defects, then
`render r.json --html b.html` from a directory that is not a repository and with no credential in the environment;
`a.html` and `b.html` are byte-identical, open in a browser with no network request, and a `<script>` planted in a
reviewed source file appears as text in a rationale rather than executing.

### Documentation first for Phase 11

- [X] T128 SRS v1: **FR-10.4d** and its rationale in §4.7; the CF-7 charter row; the §1.2 in-scope line; Appendix B (`FR-10.4a–c` to `FR-10.4a–d`, "Verified by" deliberately unchanged). No AC-17, and no §7 row — HTML was absent from v1, never excluded
- [X] T129 [P] `Docs/technical_stack.md`: the §2 stack row; §3.1 package data and the `importlib.resources` precedent for `_vendor/resolver.js`; §3.7; the §4 contract table (**Six** to **Seven**, row 8, and why there is no 7 — reserved for Langfuse by T103); the §5 inventory row; the §7 pin after T134
- [X] T130 [P] `Docs/design/01-logical-architecture.md` §4: `R3` in the fan-out diagram, `cli/` gains "write a file", two decision rows. `Docs/design/04-contracts.md` §6: the `render` command line and the `--html PATH` row
- [X] T131 [P] `CLAUDE.md`: contract count 5 to 6 in both places; `review` **and `render`** implemented; Jinja2 in the stack bullet
- [X] T132 [P] `contracts/cli.md`: the `--html PATH` row; the `--json` row narrowed to the named-file form this build offers; the Streams rows and the output-path preflight rule; the `## render` section with its exit-code ruling
- [X] T133 [P] This phase header

### Dependency and contract for Phase 11

- [X] T134 `uv add jinja2` (floor `>=3.1`, where `jinja2.Markup` was removed and the escaping API settled); record the resolved `jinja2` and `markupsafe` versions in `Docs/technical_stack.md` §7. It may already be in `uv.lock` transitively through `jupyter` and `nbconvert`, so the lock may not move — say so in the commit message; it must still be a **direct** dependency
- [X] T135 Add import contract **8** ("only core.output may import Jinja2", forbidding `jinja2` and `markupsafe` everywhere else, `cli` included) to `pyproject.toml` and update the `[tool.importlinter]` header comment; `uv run lint-imports` green

### Tests for Phase 11 write first

- [X] T136 [P] Create `tests/support/report_factory.py` holding the report `tests/unit/output/test_render.py::_report` builds inline; `_report` becomes a one-line delegation. It is what lets the template be iterated with **zero provider calls**, and the markdown wrapper reuses it
- [X] T138 Write `tests/unit/output/test_load.py` and `tests/unit/output/test_html.py`: a self-contained document; required sections in order; anchors by `finding.id` and **never** the fingerprint, which collides for two same-category findings in one file; model-authored prose and a hostile file path escaped; a `no-tool-call` run never shown as clean; one sentence per verdict; degradations; absent stage durations omitted rather than printed as `None`; every exclusion listed past the terminal's cut-off; the run-metadata allow-list; byte-identical twice; `StrictUndefined`. For `load`: round-trip from `to_json`, identical HTML from a loaded report, an unknown schema version naming both versions, malformed JSON, a named missing field, an unknown field refused, and a message that never repeats a rejected value
- [X] T142 [P] Write `tests/structural/test_template_escaping.py` (modelled on `test_git_confinement.py`): no `|safe`, autoescape block, `Markup`, script tag, absolute URL or `@import` in the template; no `model_dump`, `.items()` or `environ`; `autoescape is True` and `undefined is StrictUndefined`; the template resolves through `importlib.resources`; no `__file__` anywhere under `core/output/`
- [X] T143 [P] Write `tests/unit/cli/test_render_command.py` and `tests/unit/cli/test_output_files.py`: `render` writes and exits 0, needs no repository, config or credential, **does not map a verdict onto its exit code**, and exits 3 naming a missing report, malformed JSON, an unknown schema version or an unwritable output; `_reject_json_to_stdout` catches a bare `--json`; `--json -` exits 3 and not Click's 2; `--html` into a missing directory exits 3 with the stand-in called 0 times
- [X] T145 Write `tests/integration/test_html_report.py`: the HTML's findings match the JSON report (FR-027 extended to the third surface); **a saved report renders to the same HTML as the run did**; no planted credential in the text or the bytes; a `no-tool-call` run not shown as clean; a provider error says no review was performed; both files UTF-8 with newline endings; a preflight failure writes neither file

### Implementation for Phase 11

- [X] T137 Create `src/agentic_review/core/output/view.py` — the shared wording and derivations (`NO_TOOL_CALL_LINE`, the five verdict sentences, the not-reviewed reasons, severity counts, line spans, evidence lines, stage rows, and `run_rows` as an explicit **allow-list** so a field added to `RunMetadata` later cannot reach the HTML by accident); refactor `terminal.py` to import them and delete its local copies. The suite stays green with no test changes
- [X] T139 Create `src/agentic_review/core/output/load.py`: `load_report(text) -> ReviewReport` and `ReportNotLoadable`. Text in, model out — the filesystem belongs to `cli/`. The schema version is checked **before** validation, because `WireModel` forbids extra fields and a later report would otherwise fail with an unreadable list of unexpected keys; validation errors carry dotted field paths and never the rejected values
- [X] T140 Create `src/agentic_review/core/output/templates/report.html.j2` and `core/output/html.py`: `render_html(report, *, title=None) -> str`, the only module importing Jinja2. `autoescape=True` literally, `StrictUndefined`, the template read through `importlib.resources` and never `Path(__file__)`. It writes no file and reads no clock, environment, cwd or other file — the document's timestamp is `run.started_at`, which is what makes the two entry points byte-identical
- [X] T141 [P] `scripts/render_html_demo.py`: build a report from `report_factory`, or load a JSON path, and write HTML. **Zero provider calls.** Move it earlier if template work starts before T140 is green
- [X] T144 Extend `src/agentic_review/cli/app.py`: `--json PATH` and `--html PATH`, both validated through `_could_not_start` **before** the review runs so a mistyped path never costs a provider call; a `_write` helper that forces newline endings; the `render` command; `_reject_json_to_stdout` in `main()` — deliberately **not** named `normalise_argv`, which is T092's and does a different job

### Verification for Phase 11

- [X] T146 `uv run lint-imports` and `uv run pytest` green; update the test count in `CLAUDE.md`
- [X] T147 [P] `uv build`, then confirm `agentic_review/core/output/templates/report.html.j2` is in the wheel. **Confirmed 2026-10-18: hatchling ships it from `packages = ["src/agentic_review"]` with no `force-include`, and it is the wheel's only non-Python file**
- [ ] T148 **Maintainer, needs a real key and network:** `scripts/make_review_demo.py`, then `review --json r.json --html r.html`, then `render r.json --html r2.html`; diff the two HTML files and open both in a browser
- [X] T149 [P] `Docs/operation_guidelines.md`: how to produce and read an HTML report, that it is self-contained and safe to send on, and that the JSON remains authoritative

## Notes

- `[P]` tasks touch different files and depend on no unfinished task.
- Mark each task `[X]` as it completes. T100 and T101 stay open until the maintainer runs them with a real key.
- A library that behaves differently from research.md is reported, not worked around silently (Principle I).
