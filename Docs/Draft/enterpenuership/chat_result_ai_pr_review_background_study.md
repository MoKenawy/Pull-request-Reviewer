# Background Study: Automated PR Review in the Age of AI-Generated Code

> **Export of a structured ingest-and-synthesis session.** The goal was a rigorous, deduplicated understanding of both the *problem* (why PR review is broken under AI-generated code) and the *solution landscape*, produced to feed the design of an open-source Agentic Code Review GitHub Action.

---

## Part 1 — Session Summary (how this study was built)

### Method / contract

Resources were ingested one at a time; no synthesis until explicitly requested. Rules held throughout:

- **Deduplicate aggressively** — a shared claim stated once, tagged "corroborated by N sources."
- **Flag conflicts explicitly** — never average competing sources.
- **Label every point** `[SOURCE: name]`, `[INFERENCE]`, or `[VENDOR CLAIM]`. Vendor claims are marketing until independently corroborated.
- **Preserve numbers with source and sample size** — an 8M-PR benchmark ≠ a scoped study ≠ a Reddit thread.
- **Distinguish correlation from causation** — flag every "AI caused X" that is an inference rather than a demonstrated result.
- **Weight Part A (problem) at least as heavily as Part B (solution).**
- **Close with a MISSING EVIDENCE section.**

### Corpus ingested (5 resources)

| Handle | What it is | Posture / key limitation |
|---|---|---|
| `[AIBuilderClub-2026]` | Engineering blog + artifact kit ("How to Review AI-Generated PRs"), July 2026 | Secondary aggregator; sells a plugin/course. Bundles LinearB + AIDev + OSS policy files behind its own argument. |
| `[Ullah-2026]` | Practitioner handbook / first-person case study by a tech lead | N=1 team, self-reported outcomes, no control. Advocacy for repo-resident memory files. |
| `[Stenberg-2026]` | Personal blog post (daniel.haxx.se), curl lead maintainer, June 2026 | Opinion/manifesto, zero quantification. A maintainer *stance*, not a ratified policy. |
| `[ToolingNotes-2026]` | Self-authored neutral catalog of 7 review tools, Sept 2026 | Most facts originate from vendors' own sites → effectively `[VENDOR CLAIM]` passed through a neutral compiler. |

### Sources cited *through* the corpus (second-hand)

- `[LinearB-2026]` — 8.1M PRs, ~4,800 teams, vendor platform data (cohort comparison, not a trend).
- `[AIDev-study]` — arXiv 2605.02273, 33,596 agent-authored PRs. **arXiv ID unverified / future-dated.**
- `[CircleCI-2026]` — 28M+ CI runs, 22,000+ orgs (measures CI runs, not AI authorship).
- OSS policy files: `[OpenTofu]`, `[Sonarr]`, `[stashapp]`; `[MorganStanley/Moderne]` interview; `[Nguyen]` SDLC post; `[HumanLayer]` on instruction degradation; `r/ExperiencedDevs` threads.

### Corpus health assessment (the load-bearing caveat)

The corpus is **structurally lopsided**. Part B rests on a solid tool catalog. **Part A rests on exactly two datasets — LinearB and AIDev — both cited second-hand through one blog, plus un-sampled anecdote.** No source is an independent, controlled measurement of the problem. Every "AI caused X" reading in the corpus is an inference the sources drew, not a result their data established.

---

## Part 2 — Final Synthesis

### PART A — THE PROBLEM SPACE

#### A1. Root causes

- **Generation got cheap; verification and maintenance did not.** *Corroborated by 4 sources* — `[AIBuilderClub-2026]`, `[Ullah-2026]`, `[Stenberg-2026]`, and implicitly the whole tool market `[ToolingNotes-2026]`. The single most-agreed claim — but a *shared framing asserted by every source and measured by none*. Status: unanimous expert intuition, not demonstrated.
- **Batch/diff sizes grew.** `[LinearB-2026]`: AI-assisted PRs hit 400+ LOC at P75 vs 157 unassisted. The one root cause with a number attached.
- **The reviewer loses the mental model of code they didn't write.** *Corroborated by 3 sources, different angles* — `[Ullah-2026]` (failure-causing knowledge lived in a head/Slack thread, not the diff), `[Stenberg-2026]` (inverse: a maintainer deliberately keeps the model), `[AIBuilderClub-2026]` (loss of per-author calibration heuristic). `[INFERENCE]`: same underlying mechanism from three directions.

**[CONFLICT — not averaged] Where is the leverage point?**
- `[AIBuilderClub-2026]`: problem is **author abdication** → fix = force author comprehension.
- `[Ullah-2026]`: problem is **agent context-blindness** → fix = move team memory into files the agent reads.
- `[Stenberg-2026]`: problem is **abdication to machines at all** → fix = humans stay in control.

Left unreconciled. Defensible read: three distinct failure points on one pipeline (author, agent, maintainer); the corpus doesn't establish which dominates.

#### A2. Quantified symptoms

| Symptom | Figure | Source & sample | Provenance health |
|---|---|---|---|
| Manual vs AI-assisted 30-day merge rate | 84.5% vs 32.7% | `[LinearB-2026]`, 8.1M PRs, ~4,800 teams, own platform data | Second-hand via `[AIBuilderClub-2026]`; cohort comparison, **not a trend** |
| Reviewer pickup time | ~200 → ~1,050 min | Same | Same |
| Diff size at P75 | 157 → 400+ LOC | Same | Same |
| Agent PRs with no *recorded* review activity | 61.38% | `[AIDev-study]`, 33,596 agent PRs, popular-repo subset | Second-hand; **arXiv ID unverified** |
| Of reviewed PRs: agent-only / human-only / mixed | 58.77% / 10.14% / 31.09% | Same (Table 1) | Shares are of *reviewed* PRs only |
| Feature-branch throughput YoY | +59% (largest ever) | `[CircleCI-2026]`, 28M+ runs, 22,000+ orgs | Named report; **measures CI runs, not AI authorship** |
| Median main-branch throughput | −7% | Same | Same |
| Build success rate | 70.8%, 5-yr low | Same | Same |

**Three reading rules:**
1. **[CORRELATION ≠ CAUSATION]** No figure demonstrates AI *caused* the effect. "AI accelerated writing, the system absorbed the cost" is `[INFERENCE by Ullah-2026]`, not a CircleCI finding. Temporal coincidence only.
2. **The AIDev 61.38% is not "no review happened."** The paper's authors state absent *records* ≠ absent *oversight*. Defensible claim: the review *record* is thin.
3. **8.1M-PR benchmark ≠ 33,596-PR study ≠ Reddit thread.** Do not blur telemetry-comparison, scoped-measurement, and anecdote.

#### A3. Failure modes of HUMAN review under AI-code load

*Reddit anecdote via `[AIBuilderClub-2026]`, N≈1 per account, upvotes ≠ sample:*
- **Rubber-stamping / review deficit:** "gave up and just started hitting approve."
- **Loss of per-author calibration:** must check everything every time.
- **Decision fatigue / repetition:** `[Ullah-2026]` corroborates from the reviewer seat ("the repetition, not the difficulty").

**Maintainer burnout / attention doesn't scale.** *2 sources* — `[OpenTofu via AIBuilderClub-2026]` ("no way to scale maintainers' attention") + `[Stenberg-2026]`. `[MorganStanley]`: "nobody reviews a 10,000-line PR."

**"Clean-looking" code hides subtle omissions.** *Corroborated by 3 sources* — `[Nguyen]` ("looks like senior work… missing authorization check"), `[Ullah-2026]` (v1/v2 middleware), `[Stenberg-2026]`. Strongest qualitative through-line — **but entirely anecdotal.**

#### A4. Failure modes of AI-GENERATED code that make it hard to review

Taxonomy from `[Ullah-2026]` (concrete, first-hand, N=1) + mechanism from `[Nguyen]`:
- Correct-looking but context-wrong (legacy v1 auth; tests passed because both backends resolved).
- Local duplication instead of reuse (inline fetch vs existing hook; new dropdowns vs design system).
- Silent convention drift (`"completed"` string vs `Status.Completed` enum).
- Architecture erosion (controller → repo, skipping app layer; self-written tests pass against wrong shape).
- **Tests that verify the code does what the code does** — *3 sources* (`[Nguyen]`, `[Ullah-2026]`, `[AIBuilderClub-2026]`): an agent-written suite is not independent evidence.

**[Stenberg-2026, unsourced/hedged]** "AI code may contain more mistakes than human code." No number, self-hedged. **Do not treat as a defect-rate fact.** `[AIBuilderClub-2026]` deliberately cut thirdhand defect figures for this reason. → MISSING EVIDENCE.

**Hallucinated fixes:** `[OpenTofu]` reports "patches the authors cannot explain and fixes for problems that don't exist." Single project.

#### A5. Failure modes of AI REVIEW tools themselves

- **Shared blind spots between writer-AI and reviewer-AI.** *2 sources* — `[Ullah-2026]` ("two AIs are not two independent reviewers") + `[AIBuilderClub-2026]` (self-confirmation bias). **Load-bearing rationale for fresh-context review (project FR-5.1).**
- **Context-blind feedback:** `[Ullah-2026]` — generic reviewers catch generic problems.
- **Manufactured concerns / notification fatigue:** `[Ullah-2026]` — bots manufacture concerns to look thorough; had to prompt "say nothing blocks when nothing blocks."
- **Detection-without-remediation:** implicit across the landscape; consistent with a comments-only v1.

**[CONFLICT — not averaged] False-positive burden:**
- `[Ullah-2026]` + `[AIBuilderClub-2026]`: FPs are a real cost (cause skim-past, need suppression).
- `[Stenberg-2026]`: FPs are cheap ("easily dismissed"); marginal true catch after humans are exhausted is worth it.
- `[ToolingNotes-2026]`: vendors *claim* engineered-down FP (CodeRabbit verification, Claude behavior-verification, Graphite "<3% unhelpful" — `[VENDOR CLAIM]`, no methodology/N).

Unresolved in this corpus.

#### A6. Who bears the pain

- **OSS volunteer maintainers — a spectrum, not a monolith:** hard ban (`[OpenTofu]`, capacity + BUSL-Terraform license-provenance) ↔ conditional accept (`[Sonarr]`/`[stashapp]`, explain-every-line) ↔ tool-assisted-but-human-owned (`[Stenberg-2026]`, curl's middle position).
- **Corporate teams:** `[MorganStanley]` (a fix is worthless until merged; nobody reviews 10k-line PRs), `[Ullah-2026]` (the lead *is* the bottleneck — velocity capped by reading speed).
- **Author vs reviewer vs lead:** both `[AIBuilderClub-2026]` and `[Ullah-2026]` converge on "move work left to the author."

#### A7. Organizational/cultural vs technical causes

**Technical (tooling-addressable):**
- Agent can't see rules/context not in loaded files → repo memory files.
- Diff too large for one pass → size gates / stacked diffs.
- No independent second pass / shared blind spots → fresh-context review.
- Secrets/vuln/dependency reaching human attention → machine gates.

**Organizational / cultural (NOT tooling-addressable):**
- Rubber-stamping / "give up and approve" (incentive problem).
- Author not comprehending own submission (accountability norm).
- Maintainer attention not scaling (capacity/staffing).
- AI wall-of-text degrading OSS communication (`[Stenberg-2026]`, unique).
- Human accountability for what merges (deliberately kept human).

**[INFERENCE]:** the corpus's strongest prescriptions (explain-every-line, human-is-the-gate, author does comprehension) are **organizational**. An Agentic Code Review tool is a **technical** artifact — it can shrink the reviewer's stack of mechanical catches but cannot manufacture the accountability norm. This bounds what the tool can honestly claim.

---

### PART B — THE SOLUTION LANDSCAPE

#### B1. Categories (deduplicated)

1. **AI pre-reviewers, whole-repo context** — Greptile, CodeRabbit, Qodo, Claude Code Review `[all VENDOR CLAIM]`. **Dedup headline: "reason over full-codebase context, not the diff alone" is the standard pitch, claimed by all four — and it is project FR-2. A differentiator that has already commoditized.**
2. **Repo-level config-as-guardrail (AGENTS.md / CLAUDE.md)** — `[Ullah-2026]` thesis, corroborated as a live standard by `[ToolingNotes-2026]` (Qodo/CodeRabbit "learnings"/"rules") and adoption (>60k projects, Linux Foundation's Agentic AI Foundation). AGENTS.md (open) vs CLAUDE.md (Anthropic); symlink to avoid drift.
3. **Classic deterministic guardrails** — Danger/DangerJS `[verifiable, MIT]`. Process norms only; behavior inspectable, not vendor-asserted.
4. **Workflow alternatives (smaller/stacked diffs)** — Graphite `[VENDOR CLAIM]`. Diff size is both a measured symptom (LinearB P75) and a solution lever.
5. **Machine gates before the human** — `[AIBuilderClub-2026]`: dependency/provenance → secrets+SAST (osv-scanner, gitleaks, semgrep) → fresh-context second-model pass → human on 3 questions. A published pattern over OSS tools.

#### B2. Claims vs reality

- **Whole-repo AI reviewers:** *claim* deep reasoning + low FP; *demonstrated* — nothing independently. All quality claims self-reported `[VENDOR CLAIM]`.
- **Config-as-guardrail:** *does* inject context the agent can't otherwise see (`[Ullah]`, first-hand); *claimed* compounding gains (−35% burden month one, "90–95%" caught pre-open — unbaselined N=1). Failure mode: `[HumanLayer]` instruction-following degrades as file grows (claimed mechanism, no data here).
- **Danger:** does exactly what it says; no claim/behavior gap; can't do semantics.
- **Graphite/stacked diffs:** mechanically keeps diffs small; review-quality benefit is `[INFERENCE]`, not shown.
- **Machine gates:** verifiably move mechanical checks off the human; second-model value hedged by the author's own score-8-gate-passed-then-deleted story.

#### B3. Convergent design principles (build on these)

- **AI reviewer informs, never gates** — *4 sources* (`[AIBuilderClub]`, `[Ullah]`, `[Stenberg]`, `[ToolingNotes]`/Claude "non-blocking by design"). Strongest Part-B consensus. → FR-7.2 / FR-8.
- **Fresh-context / independence** — `[AIBuilderClub]` + `[Ullah]`. → FR-5.1.
- **Dual output (human summary + machine-readable)** — `[AIBuilderClub]` + `[ToolingNotes]`. → FR-8.2.
- **Risk-triage / blast-radius** — `[AIBuilderClub]` + `[ToolingNotes]` (CodeRabbit "blast radius," Qodo risk concentration). → FR-3. **Already a shipped commercial feature, not novel.**

#### B4. Open gaps — what no current solution handles well

- **No independent quality evaluation exists.** Zero third-party precision/recall/FP/catch-rate data for any tool. `[INFERENCE]`: the market's biggest blind spot and the project's clearest opportunity — an *open, reproducible regression set* (FR-6.2b) is something no catalog tool offers transparently.
- **Execution-backed review is rare/absent.** Most tools reason over text/context; only Greptile's beta "TREX" gestures at runtime validation. **Sandboxed test/build/scan execution (FR-4) is genuinely differentiated here.**
- **Shared-blind-spot problem acknowledged but unsolved by products** — none claims independence from the authoring model. Fresh-context isolation addresses a gap vendors don't.
- **Training-data / license provenance auditing** — raised only by `[OpenTofu]` (as a reason to ban), addressed by no tool.
- **Detection-without-remediation** — category stops at comments; auto-fix nascent. v1 comments-only is consistent with the landscape.
- **Organizational failures (A7)** — untouched by any tool, by definition.

---

## MISSING EVIDENCE — what a serious study still needs

1. **Primary, independent AI-vs-human defect-rate data.** Gestured at 3× (`[Stenberg]` hedged, `[OpenTofu]` anecdotal, `[AIBuilderClub]` cut it), never delivered. The single biggest hole.
2. **Verification of the AIDev study.** arXiv 2605.02273 is future-dated and unconfirmed; the 61.38%/58.77% figures anchor much of Part A. Need the paper, methodology, and its non-popular-repo subset (reportedly different shares).
3. **LinearB and CircleCI read directly**, not through a blog — to check whether the causal AI attribution is theirs or the bloggers'.
4. **Any independent benchmark of the seven tools** — precision, recall, FP, catch rate. Graphite's "<3%" needs methodology/N or it's marketing.
5. **A baseline for diff-size → review-quality.** LinearB shows AI PRs are bigger; nothing shows bigger PRs are reviewed *worse* (vs just slower). The Graphite thesis assumes it.
6. **Time-series isolating AI as the variable.** Every causal claim is a cohort comparison or temporal coincidence. A study holding team/repo constant across an AI-adoption boundary would move these from `[INFERENCE]` to evidence.
7. **Non-vendor, non-anecdote problem data.** Part A currently has zero sources that are simultaneously independent, quantified, and not second-hand.
8. **Corpus bias to correct:** heavily OSS-maintainer / small-team weighted; skews toward sources already sold on the "review is the new bottleneck" thesis. No dissenting source; no large-enterprise primary account. Part A unanimity may partly reflect selection, not settled fact.
