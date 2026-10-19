# Chat Result — Needs-vs-Pains Analysis (Agentic Code Review v1)

> **Re-reviewed 2026-10-09.** The analysis below is kept as written. What was decided from it, and the evidence that has arrived since, are in the last section, "Re-review, 2026-10-09", and in [`000-problem-and-audience.md`](./000-problem-and-audience.md).

## Summary of the discussion

The task was to digest the Prompt 1 background study (Part A problem space, Part B solution landscape) into a needs-vs-pains analysis across five conflicting user segments, working strictly from Part A evidence and inheriting its weaknesses.

An initial blocker was raised: the first two project documents (Project Definition, Functional Requirements) are **not** a background study and contain none of the evidence infrastructure (surveys, sample sizes, citations) the task's rules depend on. Rather than fabricate an evidence base, the analysis was paused until the actual background study was supplied. Once provided, the analysis proceeded strictly from it.

The governing constraint throughout: **Part A has no independent, controlled measurement of the problem.** Two datasets (LinearB, AIDev) are both second-hand through one blog; AIDev rests on an unverifiable future-dated arXiv ID. Everything else is anecdote (N≈1) or unanimous-but-unmeasured expert framing. Severity/frequency scores are judgment calls anchored to evidence tier, not measurements — a pain grounded in N=1 anecdote cannot earn a confident high-frequency score however vivid.

---

## Segment 1 — PR Author

| Need (outcome) | Pain Point (from Part A) | Evidence + source/N | Agent-fixable? | Sev | Freq |
|---|---|---|---|---|---|
| My PR merges without a long back-and-forth | Review is now the bottleneck; merge rates fell (84.5%→32.7% cohort) | LinearB, 8.1M PRs, second-hand cohort comparison — not causal, not a time trend | Partial — agent can pre-catch mechanical issues so human round-trips shrink | 3 | 3 |
| I catch my own defects before a human sees them | Author never comprehended their own diff (author abdication) | [AIBuilderClub] framing; [Ullah] "run review pre-open" — A7 labels this cultural, not tooling | No — cultural (accountability norm) | 4 | 3 |
| I don't get buried in bot noise on my PR | AI reviewers manufacture concerns; trains skimming | [Ullah] N=1, first-hand; [Stenberg] disagrees (FPs cheap) — unresolved conflict A5 | Partial — depends on FP discipline the corpus can't confirm anyone achieves | 3 | 3 |

The author's top need (fast merge) conflicts with what the corpus says would actually help (author does *more* comprehension work upfront). Evidence pushes work toward the author; the author's incentive pushes it away.

---

## Segment 2 — Human Reviewer

| Need (outcome) | Pain Point (from Part A) | Evidence + source/N | Agent-fixable? | Sev | Freq |
|---|---|---|---|---|---|
| I spend attention only on changes that carry risk | Dumped-on reviewer; can't triage the flood | [AIBuilderClub] locates pain at reviewer; LinearB pickup ~200→1,050 min (second-hand, cohort) | Partial — blast-radius triage (FR-3) helps, but already commoditized (B3) | 4 | 4 |
| I stop rubber-stamping and actually catch things | "Gave up and started hitting approve" | [AIBuilderClub] relaying Reddit, N≈1 per account, upvotes ≠ N | No — cultural (behavior/incentive) | 4 | 3 |
| Subtle context-wrong code doesn't slip past me | "Clean-looking" code hides omissions (missing auth check) | 3-source qualitative through-line ([Nguyen], [Ullah], [Stenberg]) — strongest through-line, entirely anecdotal | Partial — execution + context (FR-2/FR-4) surface some; invisible-team-memory class it cannot | 5 | 4 |
| I'm not doing repetitive mechanical checking every time | Loss of per-author calibration; recheck everything; fatigue is "the repetition, not the difficulty" | [AIBuilderClub] (Reddit N≈1) + [Ullah] (second, non-Reddit seat) — corroborated across two source types | Partial — machine gates offload mechanical catches (A7 technical) | 4 | 4 |
| A second pass that isn't the writer-AI's twin | Shared blind spots between writer-AI and reviewer-AI | [Ullah] + [AIBuilderClub] — load-bearing rationale for FR-5.1 | Y (technical) — fresh-context isolation | 4 | 3 |

---

## Segment 3 — Tech Lead / Maintainer (corporate)

| Need (outcome) | Pain Point (from Part A) | Evidence + source/N | Agent-fixable? | Sev | Freq |
|---|---|---|---|---|---|
| Team throughput isn't capped by my personal reading speed | Lead is single point of context — "velocity capped by my reading speed" | [Ullah] N=1 team, first-hand | Partial — offloading first-pass helps; context in the lead's head is the hard part | 4 | 3 |
| Nothing merges that erodes architecture silently | Architecture erosion, convention drift, wrong-backend — tests pass anyway | [Ullah] N=1 taxonomy (concrete, first-hand) | Partial — execution (FR-4) catches test-passing-wrong-shape sometimes; drift needs pattern library (FR-6) | 5 | 3 |
| I can run review metrics off PR history and trust them | Review record is thin (61.38% agent PRs no recorded review) | AIDev, 33,596 PRs — arXiv ID unverifiable; "thin record" ≠ "no oversight," authors' own caveat | Partial — dual/structured output (FR-8) improves record-keeping | 3 | 3 |
| Fixes actually reach main | "A fix isn't worth anything until merged; nobody reviews the 10k-line PR" | [MorganStanley] via [AIBuilderClub], single report | Partial — size gates help; the 10k-line PR is also a workflow-culture problem | 4 | 3 |

---

## Segment 4 — OSS Volunteer Maintainer

| Need (outcome) | Pain Point (from Part A) | Evidence + source/N | Agent-fixable? | Sev | Freq |
|---|---|---|---|---|---|
| My finite attention isn't consumed by low-value PRs | "Automated tooling scales; maintainer attention doesn't" | [OpenTofu policy] + [Stenberg] — corroborated, 2 sources; but a capacity reality | No — cultural/staffing (A7) | 5 | 4 |
| I don't waste time on incoherent AI submissions | "Patches authors cannot explain; fixes for problems that don't exist" | [OpenTofu], single project | Partial — agent can flag incoherence/no-op diffs, can't enforce the explain-every-line norm | 4 | 3 |
| I'm not exposed to license/provenance risk from AI PRs | Training-data license-provenance exposure (BUSL Terraform fork) | [OpenTofu], single project — reason they ban outright | No — no tool in the catalog addresses this (B4 open gap) | 4 | 2 |
| OSS discussion isn't degraded by AI wall-of-text | Collaboration norm degraded | [Stenberg], unique to one source | No — cultural, collaboration norm | 3 | 2 |
| A human stays accountable for what merges | Abdication of responsibility to machines | [Stenberg] + all three policies | No — deliberately kept human (A7) | 4 | 3 |

This segment's two highest-severity pains (attention-doesn't-scale, human accountability) are exactly the ones A7 labels not tooling-addressable. An agent aimed here will overpromise. The OSS position is a spectrum (hard ban ↔ conditional ↔ tool-assisted); a comments-only agent is unwelcome to the ban wing regardless of quality.

---

## Segment 5 — Security Engineer

| Need (outcome) | Pain Point (from Part A) | Evidence + source/N | Agent-fixable? | Sev | Freq |
|---|---|---|---|---|---|
| Secrets/vulns/dep issues never reach human review unfiltered | Machine-gate-able issues hitting human attention | [AIBuilderClub] — A7 explicitly labels this technical/tooling-addressable | Y (technical) — machine gates (osv-scanner, gitleaks, semgrep) | 4 | 3 |
| Missing authz/security omissions in clean-looking code get caught | Agent mistake "looks like senior work wrapped around a missing authorization check" | [Nguyen] via [AIBuilderClub], anecdote, single vivid case | Partial — pattern library + execution surface some; semantic authz reasoning unreliable | 5 | 2 |

Thinly represented in Part A — essentially one Nguyen anecdote plus the general machine-gate point; not inflated here. Deep security tooling (TruffleHog, OWASP, supply-chain) is v2-deferred in project scope, so v1 barely serves this segment.

---

## Where segments' needs CONFLICT

1. **Author wants fast merge ↔ Reviewer/Lead want thoroughness.** The corpus's own prescription (author comprehension work pre-open) resolves this against the author's incentive. A tool that speeds merges without adding author work optimizes for the wrong party per the evidence.
2. **Everyone hates noise, but prices it differently.** Reviewer/Author/Lead treat false positives as signal-destroying ([Ullah]); Stenberg treats them as cheap and worth it. Unresolved A5 conflict — do not average. FP-tuning target depends on which segment you serve; the corpus can't say who's right.
3. **Lead wants velocity ↔ OSS maintainer wants gatekeeping.** Corporate lead measures success as *merged*; OSS maintainer as *kept out*. Same tool, opposite success metrics.
4. **"Move work left to the author" ↔ Author resists it.** The one thing Part A most agrees on is the one thing the author is least incentivized to do — and it's cultural, so the tool can't force it.

---

## Solvable-by-agent vs organizational (from A7)

**Technical (a PR-review agent can plausibly move):**
- Independent second pass / shared blind spots → fresh-context (FR-5.1)
- Diff too large to review in one pass → size gates
- Agent can't see rules/context → repo memory + pattern library (FR-6)
- Secrets/vuln/dep issues off the human → machine gates
- Test-passing-wrong-shape → sandboxed execution (FR-4), partially

**Organizational (agent cannot fix):**
- Rubber-stamping / "give up and approve"
- Author not comprehending own diff
- Maintainer attention not scaling (capacity/staffing)
- Human accountability for merges (deliberately human)
- AI wall-of-text collaboration degradation

---

## Cross-check against Part B — real gap or crowded space?

| Solvable pain | Already addressed by existing tools? | Real gap? |
|---|---|---|
| Whole-repo context | Yes — commoditized; all four AI pre-reviewers claim it (B1) | Crowded. FR-2 is table stakes |
| Blast-radius triage | Yes — shipped commercially (CodeRabbit, Qodo) B3 | Crowded |
| Fresh-context independence | No — the products *are* the risk; none claims independence (B4) | Real gap |
| Execution-backed review | Nearly no — only Greptile TREX beta gestures at it (B4) | Real gap — genuinely differentiated |
| Independent quality evaluation / reproducible regression set | No — zero third-party precision/recall data; entire quality axis is vendor self-report (B4) | Real gap — clearest opportunity, maps to FR-6.2b |
| Machine gates for secrets/vulns | Partly — published OSS pattern (B1 cat. 5) | Semi-crowded; v2-deferred in scope |
| License/provenance auditing | No tool addresses it (B4) | Real gap — but not agent-fixable, out of scope |

---

## The 3–5 highest-leverage pains

Ranking = (severity × frequency) filtered by solvable and underserved, then defended. High-scoring pains that are crowded or cultural are deliberately demoted — leverage ≠ pain size.

**1. Reviewer can't trust that clean-looking, test-passing code is actually correct (context-wrong / silent drift).**
Sev 5, Freq 4. Strongest qualitative through-line (3 sources, A3/A4). Partially solvable via execution (FR-4) + pattern library (FR-6). Underserved — execution-backed review nearly absent from Part B. Best leverage: the pain the market can't currently reach, and FR-4 is built for it.
⚠️ Inherited weakness: entirely anecdotal and unmeasured. High confidence in existence, low in frequency — the Freq 4 is soft.

**2. No one can independently verify a reviewer (AI or otherwise) is any good.**
Sev 4, Freq 5. Solvable and maximally underserved — B4 calls it the market's biggest blind spot; no commercial tool offers a transparent regression set. Maps to FR-6.2b. Highest-leverage on the underserved axis specifically.
⚠️ An inferred gap ([INFERENCE] in B4), not a pain any Part A source voiced directly — one analytical step removed from evidence.

**3. Shared blind spots between writer-AI and reviewer-AI.**
Sev 4, Freq 3. Solvable (fresh-context, FR-5.1) and a real gap (B4). Corroborated by 2 sources. Strong because solvable + underserved + architecture already targets it.
⚠️ Frequency capped: only bites teams running an AI reviewer sharing a model lineage — conditional, growing, not universal.

**4. Reviewer/lead attention wasted on mechanical, repetitive checking.**
Sev 4, Freq 4. Corroborated across two different source types (Reddit N≈1 and Ullah's independent report) — relatively least-weak evidence in A3. Solvable via machine gates + triage. Partly crowded (triage commoditized, B3), so ranks below the differentiated three.

**5. Secrets/vulns/dep issues reaching the human unfiltered.**
Sev 4, Freq 3. Cleanly technical (A7), clearly solvable. Demoted hard — semi-crowded (published OSS pattern) and deep tooling is v2-deferred, so v1 can't capture this leverage yet.

**Deliberately excluded despite high sev×freq:** maintainer-attention-doesn't-scale (Sev 5, Freq 4) and rubber-stamping (Sev 4) — both cultural (A7). Building for them is the trap: easy to claim, impossible to deliver.

---

## Single-source / unreplicated flags on the ranking

- #1 rests entirely on anecdote (no quantification anywhere in the corpus).
- #2 is an analyst inference, not a voiced user pain.
- #4's underlying merge/pickup numbers trace to one second-hand vendor cohort comparison (LinearB), non-causal.
- The AIDev 61.38% that would support #3-adjacent record-keeping claims rests on an unverifiable future-dated arXiv ID — do not lean on it.

**Honest summary:** the architecture's two most differentiated bets (execution-backed review, reproducible regression set) target the two most underserved gaps — but both rest on the corpus's weakest evidence tier (anecdote and inference), because the strongly-evidenced pains are either commoditized or cultural. Not a reason to abandon them; a reason to build the regression set (FR-6.2b) first, since it's the instrument that would convert leverage claims from inference into measurement.

---

## Re-review, 2026-10-09

**Decided from this analysis** (founder, 2026-10-09). The wording is in [`000-problem-and-audience.md`](./000-problem-and-audience.md).

- **Segment 2, the human reviewer, is the project's one audience.**
- **One pain comes with it from Segment 3:** "Nothing merges that erodes architecture silently". It is the same defect class as the reviewer's top pain, clean-looking and test-passing but wrong for the codebase. The lead's other three needs stay with Segment 3.
- **Segments 1, 3, 4 and 5 are possible later expansions,** not secondary audiences.
- **Among the reviewer's pains,** context-wrong code is the headline, repetitive mechanical checking and the writer-AI's twin are the two supporting pains, and triage and rubber-stamping are not claimed. The table is in section 5 of that file.

**What is out of date above**

- **Ranking #2, "No one can independently verify a reviewer", is no longer only an inference.** A peer-reviewed study (Chowdhury et al., MSR 2026, 3,109 pull requests) found 12 of 13 review agents averaging under 60% signal by a keyword-based measure, and cites earlier work in which human review comments were addressed about 60% of the time against 0.9% to 19.2% for agents' comments. The flag that no source voiced it still holds: no reviewer has said it to us.
- **Ranking #1 is unchanged:** still anecdote, and still unmeasured in frequency.
- **The AIDev caveat stands.** That study draws on the AIDev dataset, so the dataset is real. The 61.38% figure has still not been checked at its source and stays unused.
- **The reviewer's load has since been measured for public repositories:** in ten TypeScript repositories in September 2026, 182 core reviewers did 97.7% of the reviewing, a median of 21.5 pull requests each, against 13 opened per core developer ([`review-volume-report.md`](./0050-financial-planning/0051-cost-structure/review-volume-report.md) §2.5). It measures how much reviewing a reviewer carries, not any single pain.

