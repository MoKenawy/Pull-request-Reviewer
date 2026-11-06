# Research — Feature 003, Rule Library

**Date**: 2026-11-06 · **Feature**: [spec.md](./spec.md) · **Plan**: [plan.md](./plan.md)

Decisions taken before design, each with its rationale and the alternatives rejected. Where a decision was already made elsewhere, this file records it and points at the authority rather than re-deciding it.

---

## R-1 — Rule files are YAML package data under `core/patterns/rules/`

**Decision**: each rule is a YAML document, shipped as package data inside the wheel, read through `importlib.resources`, parsed with `yaml.safe_load`, and validated by the Pydantic models in [data-model.md](./data-model.md).

**Rationale**: three things have to be true at once. The rules must be in the wheel, because the static-prompt decision puts them in *every* review ([`02-domain-model.md`](../../Docs/design/02-domain-model.md) §3.8). They must go through the **same** loader and the same error style as a project's own rules (FR-024…FR-027), or one path names the offending field and the other does not. And `wrong`/`correct` hold multi-line TypeScript, which a YAML block scalar carries far better than a Python string literal. **No new dependency is implied**: `pyyaml` is already a direct dependency and already the configuration parser, and `importlib.resources` is stdlib with an established precedent in this repository — [`technical_stack.md`](../../Docs/technical_stack.md) §3.1 requires package data to be read that way and never by path arithmetic from `__file__`, which breaks in a zipped distribution. So [`technical_stack.md`](../../Docs/technical_stack.md) needs no amendment, which matters because design may not choose a technology.

**Alternatives rejected**:
- *A Python module of frozen dataclasses* — no loader, no package data, but then the shipped library and a configured one take two code paths with two error styles, and FR-1.2d's "name the offending field" would exist for one of them.
- *`tests/corpus/rules/`*, which [`06-verification.md`](../../Docs/design/06-verification.md) §2 showed until 2026-11-06 — impossible once the rules ship in the system prompt of every review. That line was corrected; had it stood, the harness feature would have measured a copy of the library rather than the library.

**If a format had implied a new dependency**, design could not have picked it: the plan would have raised it for the stack document, which would need a stack-table row, a dependency-inventory row with its swap cost, an exact version pin at the first commit that installs it, and a layout line if it brought package data.

---

## R-2 — Our code appends the rules block; the managed prompt never holds the rules

**Decision**: `core/assembly/` builds the system message as the instructions text followed by the rendered rules block. The instructions may come from the managed prompt store or from the built-in fallback; the rules block is always ours.

**Rationale**: the decisive argument is a failure mode. `load_instructions` catches **every** exception and falls back to the built-in text with a `problem` recorded. If the rules lived in the managed prompt, a timeout would produce a review with **no rules at all** — FR-6.1 silently unmet, which Principle V and FR-11.2 both forbid. Two further reasons: attribution is validated against the *loaded* library, so rules edited in the store and not in the repository would be shown to the model and then rejected as unknown; and FR-6.3a's "v1 shall ship five rules" stops being true if the rules live in a hosted store. Keeping them separate also keeps the prefix stable, since instructions and rules change on different cadences.

**Consequence, and it is operational rather than code**: the managed prompt currently holds a copy of the built-in instructions, which say the model is given "the complete diff … and nothing else". After this feature that sentence is false and nothing tells the model to cite a rule. **Republishing the managed prompt is a task in this feature**, not an afterthought — otherwise every run with the store configured shows rules the instructions never mention.

**Alternative rejected**: *rules inside the managed prompt*, for the iteration speed. The failure mode above makes it unsafe, and the operational cost is the same either way.

---

## R-3 — CF-1 evaluates the globs; `core/patterns/` carries them as data

**Decision**: the glob dialect stays in `core/changeset/exclusion.py`, which already owns it. `core/patterns/` exposes its scopes as **plain builtin tuples of strings** and evaluates nothing. The pipeline hands those tuples to change-set resolution.

**Rationale**: `patterns` and `changeset` are **both Layer-1 capabilities** ([`01-logical-architecture.md`](../../Docs/design/01-logical-architecture.md) §3), and capabilities never import each other — "never up, never sideways". §3's own remedy for two capabilities that must combine is that combining them is the pipeline's job, and passing glob lists is exactly that. The alternative, re-implementing the translator inside `core/patterns/`, would give the tool two glob dialects that drift apart silently; one dialect is the whole point of reusing FR-3.5's.

**Correction recorded**: [`02-domain-model.md`](../../Docs/design/02-domain-model.md) §3.8 previously said `core/changeset/` was "a layer above" `core/patterns/` and so *may* import it. It is not, and it may not. The sentence was corrected on 2026-11-06; its conclusion — plain glob lists — was right for the wrong reason.

---

## R-4 — Rule scope is applied after reviewability, not before

**Decision**: order the filters as FR-3.5's configured exclusions → the existing reviewable-language test → rule scope, and apply rule scope **only to files that are already reviewable**.

**Rationale**: a design gap neither §3.8 nor the spec's first draft closed. Non-TS/JS files are already outside review, and they already carry a reason saying so. If rule scope ran first and indiscriminately, a changed `README.md` would be reported as "no rule applies" instead of "not a reviewed language" — two mechanisms producing different explanations for the same file, with the less honest one winning. Ordering costs nothing against FR-3.5's rationale, because a non-reviewable file is never parsed or budgeted anyway.

**Alternatives rejected**: *rule scope first* (above); *rule scope replacing the language test* — the language boundary is spec 001's FR-009 and is not CF-8's to absorb.

---

## R-5 — The new reason is `rules:no-scope-match`, and it bumps the schema a minor version

**Decision**: the third exclusion reason takes the existing `<source>:<detail>` shape. The published report's reason pattern is widened to admit the `rules:` source, and `SCHEMA_VERSION` goes from `1.0` to `1.1` in the same change.

**Rationale**: the report constrains an excluded path's reason to `default:<name>` or `config:<pattern>`, and that pattern is doing real work — the terminal prints the reason and a consumer can split it. A bare third value would make the pattern a list of exceptions rather than a rule, and would leave no room for a fourth source. Admitting a value is an added enum value, which [`02-domain-model.md`](../../Docs/design/02-domain-model.md) §4 classifies as a **minor** bump, with old consumers unaffected provided they ignore unknowns — a rule that document already states. This is the project's first schema bump, so it is worth doing by the book: the version is hand-set, never derived from the package version.

**Alternative rejected**: the bare `no-rule-scope` the design document first used. It reads marginally better in a terminal and would have needed no design edit; the convention argument won, and §3.8 was corrected to match.

---

## R-6 — Configured rules are added, never substituted

**Decision**: one configuration key names a file of additional rules. Its rules join the shipped ones. An identifier that collides with a shipped rule's is an error. Overriding or narrowing a shipped rule is out of scope for v1.

**Rationale**: FR-6.1 is a **Must** and calls the library *configurable*, so leaving the surface out would strand a Must with no feature scheduled to finish it. Additive-only follows the precedent already set for configured exclusions, where the list merges rather than replaces, for the stated reason that replacement semantics let one added pattern silently switch off a default nobody meant to disable. Collision-as-error keeps an identifier meaning exactly one rule, which FR-6.2a's attribution depends on.

**Alternatives rejected**: *full override with a precedence order* — more capable, and it makes "which rule won?" a question the output has to answer; deferred to v2 with the rest of breadth. *No configuration surface at all* — leaves FR-6.1 half-delivered.

---

## R-7 — The library loads at preflight; the `load_patterns` node renders and publishes

**Decision**: preflight loads and validates the library and puts it on the run's state. The existing `load_patterns` node stops being a pass-through and becomes a thin adapter that renders the rules block and publishes the set of rule identifiers. The graph's nodes and edges do not move.

**Rationale**: forced by R-4 and by FR-6.1a's "when the change set is resolved". The `load_patterns` node sits *after* change-set resolution, so the library cannot both load there and be available to CF-1. Preflight is also the only stage that may halt a run, which is what a malformed rules file needs — FR-027's exit 3 with no provider call, the same shape a malformed configuration already has. The node keeps its place because [`02-domain-model.md`](../../Docs/design/02-domain-model.md) §3.8 says so, and because moving a node would reopen the declared-graph decision.

**Open consideration, carried not closed**: graph state is serialised by every attached tracer, so putting the whole library on the run state ships five rules' worth of examples into each trace at every node transition. It carries no secret, and at five rules it is bounded. If it proves heavy, the fallback is a cached loader with only the identifiers and the scopes on the state. Start with the library on the state, for traceability.

---

## R-8 — The budget counts the rules block and gains one constant; per-section allocation stays with 004

**Decision**: route the rules block through the existing whole-prompt estimate, and add a function that returns the fixed section's size. Build no per-section allocation and no eviction.

**Rationale**: FR-2.5a's per-section budgeting belongs to feature 004, which spec 001 defers to it explicitly. What 003 owes is that the section *exists* as a constant — which is what [`05-cross-cutting.md`](../../Docs/design/05-cross-cutting.md) §1.1 now claims — and that rules cannot beat the budget by being uncounted.

**Watch item**: a static prefix raises every prompt's floor, so a change set that fit before may now exhaust the budget. No requirement is violated — the run reports it and reviews nothing, which FR-2.5b requires — but the degradation's detail should name the fixed section's share so the cause is legible. **No test may assert the library is under some token count**: the budget's limit is an acknowledged placeholder, and Principle VI forbids justifying a decision with one.

---

## R-9 — The five shipped rules, and how they are scoped

**Decision**: five rules drawn from the categories the instructions already ask the model to look for, scoped narrowly but **covering TS/JS between them**, with at least one applying to test files.

**Rationale**: the maintainer chose narrow scopes so that the drop behaviour is live from day one rather than latent. Two guardrails follow, and the second is sharper than it looks. Narrow means narrow *within* TS/JS, never narrower — the union must cover the ordinary source file, or the tool reviews less than its user expects. And **at least one rule must apply to test files**: if every rule excluded them as production-code rules, a test-only change would be dropped entirely, while the instructions explicitly ask for findings about behaviour changed without a test or an existing test weakened. That is a shipped-data decision with a user-visible failure mode, so FR-016 makes it a requirement and Story 2 makes it a scenario.

**Alternative rejected**: *all five on the permissive default*, which makes the drop path unreachable in practice and ships a behaviour nothing exercises.

---

## R-10 — Four existing import contracts are extended; no new contract is added

**Decision**: contract 6's layer list gains `core.patterns` **beside** `core.changeset`, and `core.patterns` is added to the enumerated source lists of the three forbidden-dependency contracts covering the terminal renderer, the git layer and the template engine.

**Rationale**: Principle VII requires a contract whose packages exist to be enabled in the feature that creates them. Putting `patterns` in the same layer as `changeset` is what makes `changeset → patterns` a contract violation, which is precisely the enforcement R-3 needs — siblings in one layer are independent in import-linter, so the plain-glob-list seam is checked rather than merely intended. It also forbids `config → patterns` for free, since config sits lower and upward imports are already banned. The framework-freedom contract already covers the new package through its wildcard, so it needs no edit, and no new numbered contract is warranted: contract 6 already expresses the one new structural rule.

---

## R-11 — This feature closes feature 001's task T087

**Decision**: build the `nothing-to-review` path here, and mark T087 closed in 001's task list.

**Rationale**: FR-015 requires an empty review scope to complete without reading as clean, and the outcome it needs does not exist yet — T087 is open. The alternatives were to block this feature on separate work in 001, or to drop the scenario and leave FR-6.1a's last clause unverified, which is the clause the SRS amendment was taken for. Building it here is the only option that delivers the requirement. It is the single place this feature touches pipeline routing, and the conditional edge must keep the graph acyclic, as T087 itself specifies.

---

## R-12 — AC-4 is verified offline, and claimed

**Decision**: AC-4 is delivered by this feature, verified with a scripted stand-in model.

**Rationale**: the criterion is that a finding originating from a rule names that rule. Two halves are entirely ours and both testable without a provider: the identifier survives from the tool call to both outputs, and an identifier the model was never shown is rejected rather than published. Together with "every loaded rule is in the prompt", that closes the loop — every acceptable identifier names a rule the model demonstrably saw. How *often* a real model chooses to cite a rule is a measurement, and measurement is feature 007; the SRS itself says prompt quality has no evidence behind it until the corpus exists.

**Alternative available if wanted**: a probe outside the test suite, in the shape of the existing tool-calling probe, running one real review and recording whether a rule was cited. It would cost one free-tier request per run and leave the offline guarantee intact.
