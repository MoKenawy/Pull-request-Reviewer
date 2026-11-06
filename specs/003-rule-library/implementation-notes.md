# Implementation notes — feature 003, Rule Library

**Date**: 2026-11-06 · **Covers**: T001 – T049 (Phases 1–5) · **Tasks**: [tasks.md](./tasks.md)

Where the implementation diverged from [tasks.md](./tasks.md), and why. Constitution Principle I says a task that
needs a decision the documents do not make **stops and reports it** rather than settling it in code; this file is
that report. Everything here is a divergence of *means*, not of requirement: no FR or SC was added, relaxed or
reinterpreted, and every one of them is still delivered by the task it was mapped to.

Phases 6–8 (T050–T063) are not built. See [§4](#4--what-phases-68-still-owe).

---

## 1 · Divergences from tasks.md

### T025 / T019 — the system message is not built in `prompt.py`

tasks.md puts `system_message(instructions, rules_block)` in `core/assembly/prompt.py` and has the rules block
"land in the system message". `prompt.py` does not build the system message: `agents/review_reporting_agent.py`
does, at the `SystemMessage(content=...)` that starts a review run.

**Done:** the helper is in `prompt.py` as the task says, *and* `review_reporting_agent.py` now calls it. Without
the second half the helper would be dead code and T019's "in the system message, not the user message" would be
untestable end to end. `agents/review_reporting_agent.py` is therefore a file T025 edits that tasks.md does not
name. `tests/integration/test_story1_rule_attribution.py` pins the seam, so a future change that stops joining
the two there fails a test rather than silently dropping every rule from the prompt.

### T025 / T028 — `assemble` takes the rendered block and the identifiers, not the library

tasks.md says both "`assemble` taking the library" (T025) and that the `load_patterns` node should "render the
block, publish the identifiers, write both onto the run state, and **pass them to** `_assemble_context`" (T028).
Those two cannot both hold without rendering the library twice per run.

**Done:** T028's reading. `_load_patterns` renders and publishes onto `PipelineRun`; `assemble` takes
`rules_block: str = ""` and `rule_ids: frozenset[str] = frozenset()`. Three reasons: the block is rendered once;
the node has real work, which is what stops it being the pass-through R-7 wants it to stop being; and
`core/assembly/` needs no import of `core/patterns/` at all, so the capability's data crosses the boundary as
plain builtins — the same seam research R-3 requires of CF-1's glob tuples, for the same reason.

`PipelineRun` gained two fields (`rules_block`, `rule_ids`), which T028 does not mention but needs: nodes
communicate through state.

### T026 — `fixed_section_tokens` lives in `prompt.py`, not `budget.py`

tasks.md puts it in `core/assembly/budget.py`. It cannot go there: `prompt.py` imports `budget.py`, so a function
in `budget.py` that needs `system_message` would require either an import cycle or a second copy of the join —
and the join is precisely the thing that must not be duplicated, since SC-004 is about its exact bytes.

**Done:** both `system_message` and `fixed_section_tokens` are in `prompt.py`; `budget.py` keeps the limit logic
and gains `BudgetExhausted.fixed_section_tokens`. T020's test went to `tests/unit/assembly/test_budget.py`, which
is where `budget.py`'s tests already live (tasks.md said `test_prompt.py`). `test_prompt.py:98-101` also had to
change: it called `prompt_text` positionally, and that function's first parameter is now the composed system
message rather than the instructions alone.

### T027 — `core/findings/port.py` needed no edit

`RunMaterial.rule_ids` already existed. What was missing was the *population*, which happens in `assemble`.
`port.py` changed only to add `ReviewContext.rules_block`, placed **last** among the fields: inserting it after
`instructions`, as data-model §3 reads, would have put a defaulted field before four undefaulted ones.

### T031 — the fixed section's share is carried on `BudgetExhausted`

The degradation is built in `_build_report`, where `run.context` is `None` because assembly failed. So the number
has to travel on the value assembly returned. `BudgetExhausted` gained `fixed_section_tokens: int = 0`; the
existing equality assertion in `test_budget.py` was updated to construct it.

Note it is non-zero even with no library loaded — the instructions alone are the fixed section — which is more
informative than the task implies and needed no extra code.

### T034 — written as a structural test, in `tests/structural/`

tasks.md asks for a unit test proving `load_library()` works "against the **installed** distribution, so a wheel
that forgot the package data fails here rather than in a user's install". It cannot do that. The project is
installed **editable** (`_editable_impl_agentic_review.pth` points at `src/`) and CI runs `uv sync`, so
`importlib.resources` resolves to the source tree in both places; a test written that way would pass against a
wheel containing no `*.yml` at all.

**Done:** `tests/structural/test_rules_package_data.py`, in the shape of `test_template_escaping.py` — the rules
are reached *through* `importlib.resources` and never by path arithmetic from `__file__`, which is the mechanism
that actually prevents the failure (the second works in a source tree and breaks in a zipped wheel). **Still
owed, by nobody:** catching a wheel that genuinely forgot its data needs `uv build` plus inspection of the
artifact. No task in this feature does that, and it is worth one in 006's hardening.

No `pyproject.toml` build change was needed: hatchling ships every file under `packages = ["src/agentic_review"]`,
which is also why the HTML template already works.

### T035 — pulled forward from Phase 4 into Phase 2, and the shipped scopes were narrowed twice

Phase 2's own checkpoint ("the library loads") and its test `test_the_shipped_library_loads_with_no_configured_file`
both need shipped rules, so the five were authored in Phase 2 rather than Phase 4.

The first version scoped two rules to `**/*.ts` / `**/*.js`. That is **research R-9's rejected alternative** in
disguise: with any rule matching every TypeScript file, no reviewable file is ever dropped and the whole of
FR-6.1a is unreachable in practice. The shipped scopes are now rooted at `src/`, `lib/`, `app/`, `api/`,
`server/`, `routes/`, `packages/`, `tests/` and `test/`, so `scripts/`, `tools/`, `examples/` and the repository
root are covered by nothing. `tests/unit/patterns/test_shipped_rules.py` pins both halves: the union covers an
ordinary source file and a test file, and it does not cover everything.

### T044 — the reason constant lives in `core/findings/report.py`

tasks.md puts `rules:no-scope-match` in `core/changeset/exclusion.py`. Both `core/changeset/` (which produces it)
and `core/output/` (which renders the count) need the one spelling, and `core/output/` reaching into a sibling
capability for it would contradict `01-logical-architecture.md`'s revision note that every type in the published
report schema is defined in `core/findings/`. Import contract 6 would have allowed it; the design note would not.

**Done:** `RULES_NO_SCOPE_MATCH` is defined in `core/findings/report.py`, beside the `ExcludedPath.rule` pattern
it has to satisfy. `exclusion.py` owns `RuleScope` and `in_any_rule_scope` and reuses the existing
`glob_to_regex`, as the task requires; it adds no second translator.

### T045 — the gate is `ChangedFile.is_reviewable`, applied after the file is built

tasks.md says apply the filter "after the configured exclusions and after the reviewable-language test", which
reads as one ordered chain in `_collect`. There is no reviewable-language *filter*: a non-TS file stays in
`ChangeSet.files` and is reported through `notReviewedReason` — a different array from `excluded`.

**Done:** `_apply_rule_scope` runs after the `ChangedFile` objects are constructed and tests
`changed.is_reviewable and not in_any_rule_scope(...)`. Research R-4's ordering is honoured exactly: a changed
`README.md` keeps *not a reviewed language*, a configured exclusion keeps *its* pattern, and only a file that
would otherwise have been reviewed can get `rules:no-scope-match`.

`rule_scopes` also had to thread through `_resolve_working_tree` and `_resolve_range`, which T045 does not name.

### T046 — feature 001's T087 is **not** ticked

tasks.md says to tick it. T087 also requires the **commit scope** (`ScopeRequest.commit`, `ReviewRequest.commit`,
`ScopeKind` gaining `"commit"` — none exist) and a **Langfuse** clause depending on 001's open T106. Ticking it
would record unbuilt work as done, which is the failure T046's own note warns against, in the other direction.

**Done:** a dated note under T087 in `specs/001-walking-skeleton/tasks.md` saying which clause 003 closed, which
remain, and which tasks they belong to. The box stays unticked.

Two edits T046 needed and does not name: `_build_report` asserted `run.budget_exhausted is not None` on its
no-outcome branch, which the new route trips, so it now distinguishes three cases (an outcome, budget exhaustion,
nothing reviewable). And the `nothing-to-review` branch sets **no degradation** — nothing failed.

### T047 — the schema bump breaks 1.0 reports, and that is accepted

`core/output/load.py` refuses any `schemaVersion` but the current one, so after `1.0 → 1.1` a report written by
an earlier build no longer loads with `agentic-review render`. No artifact in this feature mentions it.

**Decided by the maintainer: bump and accept the break.** Nothing is published yet, and adding minor-version
tolerance to the loader would be behaviour no requirement asks for. It is recorded here, in `SCHEMA_VERSION`'s
docstring, and in the commit message rather than left silent.

tasks.md's "update every test asserting `1.0`" would also have produced two tautologies:
`tests/unit/output/test_load.py` and `tests/unit/cli/test_render_command.py` used `"1.1"` as the deliberately
**unknown** version, and `test_load.py:43` contains no `"1.0"` at all. Those fixtures now use `"2.0"`, and the
shared fixtures in `tests/support/report_factory.py` derive from `SCHEMA_VERSION` so the next bump needs no edit
there.

### The `load_patterns` stage is not timed — design gap 003/D-10

Timing the node looked free, and is not. `StageDurations` is a fixed set of five stages and the published report
model is `extra="ignore"`, so a `patterns` duration would be recorded and then **silently dropped** — which
SRS §8 rule 2 ("every stage records its own duration") and Principle V both refuse. Adding the field is a
published-schema change no requirement in this feature asks for, and the same question is owed by feature 002's
checks stage and feature 004's parse stage.

**Done:** the node is untimed, with the reasoning in its docstring, and the question is raised as **003/D-10**
rather than settled here.

### Design gap 003/D-9 — a relative `patterns.rules` with `--pr`

`contracts/rules-file.md` §1 makes the path repo-root-relative, but a `--pr` review has no repository root
(`PreflightOk.repo_root` is `None`) and its configuration comes only from `--config` or the defaults.

**Done, as the loud option:** an absolute path works everywhere; a relative path with `--pr` is a preflight
failure naming the key and saying there is no repository root to resolve it against. Resolving against the
current directory was rejected because that is exactly what FR-10.3d refuses for the configuration file itself.
Raised as **003/D-9** for the design documents; the choice is covered by
`tests/unit/pipeline/test_preflight.py`.

### T014 / T056 — the configured path reaches preflight in Phase 2

T056 is listed in Phase 7, but T015 requires "a malformed configured rules file is a preflight failure" and
"no key configured loads the shipped library alone", which cannot be tested without it. `load_library`'s `extra`
parameter and the settings-to-preflight wiring are therefore both built. Phase 7's remaining work is T053/T054's
tests and T055's shipped-collision check — most of which `load_library` already does.

### T001 — the package's public surface

`core/patterns/__init__.py` re-exports the public names, as T001 asks and as the quickstart's
`from agentic_review.core.patterns import load_library` requires. Note this **deviates from house style**: every
other `__init__.py` under `core/` is empty and consumers import from the submodule. The quickstart is the
contract here, so the re-export stays; it is worth knowing it is the only one.

### Additions the analyze pass found missing from tasks.md

Three requirements were mapped to tasks that did not fully cover them. Each gained an assertion:

| | |
|---|---|
| **SC-004** | T011 only tested `rules_block`'s own determinism. `test_the_fixed_section_is_byte_identical_across_two_different_change_sets` in `tests/unit/assembly/test_prompt.py` tests what SC-004 actually says — the instructions-and-rules portion, across two runs over different change sets |
| **FR-028** | T036 is implementation-only, the one requirement in the feature with no test task. `test_the_results_library_states_its_source_and_rule_count_for_the_trace` asserts both facts on the preflight result |
| **FR-021** | T049's count needed a plural/singular case and a "no count when nothing was dropped" case, both in `tests/unit/output/test_render.py` |

---

## 2 · Things tasks.md describes that needed no code

- **T052** — `core/findings/validation.py:116-118` was already correct, and its comment already described the
  post-003 world. The branch became reachable the moment T027 populated `material.rule_ids`. (Phase 6.)
- **T050 / T022** — `tests/unit/findings/test_validation.py` already covered the discard and the rejection almost
  verbatim, including the exact message. Only T022's "the identifiers come from a *real loaded library*" was new,
  and that was added.
- **No renderer work for attribution.** `terminal.py`, `html.py` and `report.html.j2` already printed a finding's
  rule. T049's count is the only output change this feature needed.
- **T059** — neither `Docs/design/01-logical-architecture.md` §2.2 nor `Docs/technical_stack.md` §4 has a
  built/not-built marker to flip. §2.2's fourth column is "1:1?" and already reads `✅`; the stack doc's tree is
  the *target* layout, and lists `context/`, `execution/` and `_vendor/`, none of which exist. The real edit there
  is adding `rules/` to the tree with a package-data note, mirroring the `templates/` line. (Phase 8.)

---

## 3 · Stale references noticed in passing, owned by nobody

- `Docs/design/schemas-and-contracts.md:1063` and `STRUCTURE_REVIEW.md:98` still attribute the regression harness
  and the `regression` command to "feature 003". The 2026-11-06 split moved both to **007**. No task covers
  either file.
- `spec.md`'s design-gap **D-5** says `Docs/design/02-domain-model.md` §3.8's literal "needs correcting" from
  `no-rule-scope`. It was already corrected, with a dated settled-by note. The spec's remark is stale.

---

## 4 · What Phases 6–8 still owe

T050–T063. Of those, **T057** — republishing the Langfuse-managed system prompt so its instructions match
T030's text — is the one with a consequence rather than a tidy-up: until it is done, every run with
`LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY` in the environment shows the model five rules that the stored
instructions never mention and never ask it to cite. It needs the maintainer's Langfuse credentials and cannot
run offline, so it is not in this change.

The code is safe either way: research R-2's whole point is that the rules block is appended by our code, so a
stale stored prompt degrades the wording and can never drop the library.
