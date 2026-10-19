# Agentic Code Review — Problem Definition (v1)

> **Updated 2026-10-09.** The audience, the wording of the problem statement and the tagline are now set in one place, [`enterpenuership/000-problem-and-audience.md`](./enterpenuership/000-problem-and-audience.md), and this document follows it. Three things changed here: the open-source maintainer is no longer a secondary audience but one of four segments left for later; the primary problem statement uses the wording set there; and POV-2 now has measured evidence behind it. The point-of-view statements, the root-cause chain, the questions and the appendix are otherwise unchanged, and remain the reasoning behind that definition.

## Audience

**The one audience: the organization reviewer** — an engineer performing peer review on a colleague's AI-assisted TS/JS pull request inside a company or funded team. They operate under **employee accountability**: a named human is answerable for what merges, and that accountability — not any tool — is the team's ultimate trust mechanism. What this reviewer lacks is not accountability but a reliable *signal*: they can no longer tell, from clean code and passing tests, whether a change actually fits the repo.

**Later, not now: the open-source maintainer/contributor.** Until 2026-10-09 this was the secondary audience. It is now one of four segments held for later, with the pull-request author, the tech lead and the security engineer. Same correctness-signal pain, but with no accountability backstop — no employment stake, no institutional recourse if a review is wrong. This is the audience where independent, evidence-backed review (POV-2) has genuine standalone value rather than being merely an internal measurement tool.

> ⚠️ Honest flags on this ordering:
> - Leading with the org reviewer **reverses the project's earlier locked "OSS-primary" decision.** Treat this document as the record of that pivot; if the pivot wasn't intended, this section is where to catch it.
> - **On 2026-10-09 the secondary audience was dropped, not replaced.** There is one audience, the reviewer; every other segment is a possible later expansion.
> - Because the org reviewer already has employee accountability, **POV-2 (verifiability) is weak for this audience** and strong only for the open-source maintainer. The document reflects this rather than pretending verifiability sells equally to both.
> - The org setting invites scope creep toward governance, RBAC, and audit features. Those remain **out of v1 scope**; the audience is the reviewer *role*, not the org's compliance apparatus.

---

## User Persona

**The organization reviewer** (primary) — peer reviewer on a TS/JS repo inside a company or funded team.

- **Context:** rising volume of AI-assisted PRs arriving clean-looking and test-passing; a named human (them, or the author) is accountable for what merges.
- **What they used to rely on:** rough code and failing tests as cues for where to look — a correlation AI-assisted production has broken.
- **Core frustration:** cannot tell, from clean code and green tests, whether a change fits the repo's established shape and convention — and discovers the mismatch only after merge.
- **Secondary frustrations:** a "second opinion" AI reviewer that silently shares the authoring model's blind spots; fatigue from re-running the same mechanical checks on every diff.
- **Trust mechanism:** employee accountability — so their need is a better *signal*, not proof the tool is trustworthy (that need belongs to the open-source maintainer, a later segment).

---

## Point-of-View Statements

**POV-1(a) — test-passing-wrong-shape**
The peer reviewer of an AI-assisted TS/JS PR needs to know when code that passed its tests still diverges from the repo's established shape or convention, because tests passing no longer means the change fits — but the reviewer has no signal separating "correct and conventional" from "correct-looking and wrong-shaped."

*Evidence caveat: anecdote (N=3, unquantified). High confidence it exists; soft confidence on frequency.*

**POV-2 — no way to verify the reviewer** *(a later segment: the open-source maintainer)*
The open-source maintainer adopting any AI reviewer — with no employee-accountability backstop to fall back on — needs evidence that the reviewer's findings are trustworthy before routing scarce attention through it, because staking review capacity on an unmeasured tool just relocates the bottleneck — but every tool on the market (including this one, today) reports its own quality, and no independent precision/recall signal exists.

*Audience scope: this POV is load-bearing for the open-source maintainer, who since 2026-10-09 is a later segment, and weak for the organization reviewer, who already trusts review outcomes through employee accountability. It is retained here mainly as a **measurement instrument** (see Commit-First Decision), not as a user need of the audience.*

*Assumption flag: analyst inference (B4 [INFERENCE]), voiced by no Part A source. A meta-need, one step removed from the evidence.*

*Update, 2026-10-09: no longer inference alone. A peer-reviewed study (Chowdhury et al., MSR 2026, 3,109 pull requests; cited in [`enterpenuership/004-market-study.md`](./enterpenuership/004-market-study.md)) found that 12 of 13 review agents average under 60% signal by a keyword-based measure, and it cites earlier work in which human review comments were addressed about 60% of the time against 0.9% to 19.2% for agents' comments. That measures the gap. It is still not a need that a reviewer has voiced to us, and the first half of it reaches the organization reviewer too: an AI review cannot be taken on trust.*

**POV-3 — shared blind spots**
The reviewer on a team whose writer-AI and reviewer-AI share a model lineage needs the second pass to fail *differently* from the first, because two instances of the same model omit the same things — but a review agent's independence is invisible: you can't tell from the output whether it shares the author's blind spots.

*Frequency caveat: conditional — only bites teams already running a lineage-sharing AI reviewer. Growing, not universal.*

**POV-4 — repetitive mechanical checking**
The reviewer facing high AI-generated PR volume needs to stop re-running the same mechanical checks on every diff, because the fatigue is the *repetition*, not the difficulty — but offloading it to a bot only helps if the bot's noise doesn't cost more attention than it saves (an unresolved A5 conflict the corpus can't settle).

**POV-5 — secrets/vulns reaching the human unfiltered**
The security engineer on a team shipping AI-assisted PRs needs machine-gate-able issues (leaked secrets, known-vulnerable deps) stopped before they consume human review attention, because these are cleanly technical and tooling-addressable — but the deep tooling that would catch them (TruffleHog, OWASP, supply-chain) is v2-deferred, so v1 cannot fully deliver this.

*Scope caveat: real and solvable, but unfundable at full depth in v1. Held as a v2 anchor; only `npm audit` (FR-4.3) is v1-available.*

---

## Root Cause & Leverage Point

**Root cause (rate mismatch).** AI has accelerated code *production* beyond the rate at which that code can be comprehended, reviewed, and safely merged. The downstream failures form a single chain:

1. **AI accelerates development** — code is produced far faster than by hand.
2. **Delivery expectations rise to match** — teams and projects absorb AI's speed as the new baseline; developers are expected to ship at the accelerated rate.
3. **Developers lean harder on AI, and trust it more,** to keep pace with the raised expectation.
4. **Comprehension is sacrificed for speed** — developers ship faster than they can fully understand what they shipped.
5. **Issues get bypassed** — checks a slower process performed implicitly are skipped because they cost time the developer no longer has.
6. **More PRs, each denser with latent issues, enter the queue.**
7. **Reviewers are flooded** — with both PR volume and higher defect density per PR — while still expected to clear the queue at the pre-AI pace.

The accelerating factor (AI) is not accountable for the issues it introduces; accountability still rests entirely on humans whose comprehension the same acceleration has hollowed out.

**Why a tool cannot fix the root.** The rate mismatch is sustained by *expectation and incentive* — an organizational choice to treat AI's output speed as the delivery baseline. That lever is cultural (A7), not technical. A review tool cannot slow production, restore developer comprehension, or supply the accountability AI lacks.

**Where a tool *can* act — the leverage point (axis: signal decoupling).** What the rate mismatch destroys, and what a tool *can* rebuild, is the correlation between the signals reviewers trusted and actual correctness. In a slower, hand-written process, rough code and failing tests reliably flagged problems. AI-accelerated production breaks that link: code now arrives clean-looking and test-passing while still being *structurally wrong* for the repo. This project does not fix the root — **it restores one specific, machine-checkable signal the root destroyed.**

Three points make that restoration differentiated rather than table stakes:

- **Execution-backed review (FR-4).** The tool runs the project's tests and type-checks in a sandbox and attaches that evidence to each finding — reaching test-passing-wrong-shape defects that text-only reviewers structurally cannot. Nearly absent from the market (only Greptile TREX beta gestures at it).
- **Fresh-context independence (FR-5.1).** The review pass runs isolated from any code-writing agent, so it fails *differently* rather than inheriting the author-AI's blind spots. No commercial product claims independence from the authoring model.
- **Reproducible verifiability (FR-6.2b).** A versioned regression set makes the reviewer's own catch rate measurable and inspectable — the instrument the entire market currently lacks, where quality is vendor self-report.

**Honest boundary.** Speed and volume (steps 1–2, 6–7) are where the pain is loudest, but the fast-review / triage response to them is already commoditized and is *not* this project's bet. The project's leverage is on *depth* — signal restoration — not on making review faster. Naming it this way prevents the over-claim the loud-but-crowded speed axis invites.

---

## Primary Problem Statement

Reviewers of AI-assisted TypeScript/JavaScript pull requests cannot tell whether a clean-looking, test-passing change actually fits the codebase. The signals they relied on, rough code and failing tests, no longer point at *structural* defects: code that passes its tests while choosing the wrong backend, breaking an established convention, or eroding the architecture. AI review tools have not been shown to restore that signal: in the studies available, most of their comments are not acted on.

This is distinct from functional bugs (which tests still catch) and from invisible-team-memory omissions (which the product does not address).

*Wording as set on 2026-10-09 in [`enterpenuership/000-problem-and-audience.md`](./enterpenuership/000-problem-and-audience.md). The earlier wording began "Teams reviewing" and ended with a clause about how rival tools work inside ("infer from text without executing the code or exposing evidence that their judgments are reliable"). That clause is replaced by what has been measured, and what rivals do with tests and checks is being re-checked separately (task 2 in [`0064-progress-report.md`](./enterpenuership/0060-final-pitch/0064-progress-report.md)).*

The project is **solved (v1)** when, on a public TS/JS repo using only free tiers, the system runs the project's tests and type-checks in a sandbox, attaches that execution evidence to each finding, and demonstrates against a versioned regression set (FR-6.2b) a measurable, reproducible catch rate on curated test-passing-but-wrong-shape defects — at a false-positive rate low enough that reviewers don't skim past the output.

Explicitly out of this statement: invisible-team-memory omissions, rubber-stamping behavior, the ban-wing OSS maintainer, and the deep security tooling of POV-5.

> **Evidence flag on the named defect types.** "Wrong backend, broken convention, architecture erosion" trace to a single N=1 first-hand taxonomy (Ullah, Segment 3). The specificity is a legitimate scope boundary, not three independently validated categories — do not treat it as measured breadth.

---

## How Might We Questions

**From POV-1(a)**
- HMW surface, to a reviewer, that code passed its tests *and still* diverges from the repo's established shape or convention?
- HMW give a reviewer confidence about correctness that doesn't collapse when the code looks clean?
- HMW use what a repo already encodes (existing patterns, imports, call sites) as the yardstick for "right shape"?
- HMW make execution evidence (what ran, what passed) legible enough that a reviewer trusts a finding without re-deriving it?

**From POV-2**
- HMW let an adopter judge whether this reviewer is any good *before* trusting it with their attention?
- HMW make review quality reproducible across versions, so a change to the agent can be shown to help or hurt?
- HMW expose which checks fired (and which didn't) so a finding's basis is inspectable?

**From POV-3**
- HMW make a review's independence from the authoring model *demonstrable* rather than merely asserted?
- HMW measure whether a fresh-context pass actually catches things a same-lineage pass misses?
- HMW keep the review pass from silently inheriting the author-AI's assumptions?

**From POV-4**
- HMW reduce the mechanical checking a reviewer repeats per diff without raising the noise they have to wade through?
- HMW measure whether the tool's output saves more reviewer attention than it consumes?
- HMW let a team tune the signal/noise tradeoff to their own tolerance (given the corpus can't say who's right)?

**From POV-5**
- HMW stop known-mechanical issues (secrets, vulnerable deps) from reaching human attention using only what's already free in v1 (e.g. `npm audit`)?
- HMW signal clearly which security classes v1 *does* and *does not* cover, so the tool doesn't imply protection it lacks?
- HMW structure v1 so the v2 security tooling drops in without rearchitecting (mapping into the FR-0 finding model)?

---

## POVs Resting on Unvalidated Assumptions

| POV | Assumption | Tier | Risk if wrong |
|---|---|---|---|
| POV-1(a) | "Clean code hides wrong-shape" happens often enough to matter | Anecdote, N=3, unquantified | Build for a rare event |
| POV-2 | OSS adopters actually *want* verifiability (org adopters have accountability instead) | Analyst inference, voiced by nobody | Build an instrument no *user* asked for — justified only as internal measurement |
| POV-3 | Enough teams run lineage-sharing reviewers | Conditional, growing | Addressable market smaller than it looks |

All three of the most differentiated bets sit on the weakest evidence tier. That is the central strategic tension.

---

## Commit-First Decision

Commit to **POV-2's HMW — build the versioned regression set (FR-6.2b) — first.**

Note the reason is **measurement, not trust.** For the primary (org) audience, adopters already trust review outcomes through employee accountability, so "build it so adopters can trust us" does not apply to them. What *does* apply — regardless of audience — is that the regression set is the instrument that converts every internal claim from inference into measurement. POV-1(a)'s frequency becomes a number; POV-3's "fresh context catches more" becomes a testable matched-arm experiment; the problem statement's success signal becomes defined. The other pillars cannot be *shown* to work until they can be measured, and building execution-backed review first would give you a differentiated feature you can't prove is any good — the exact position B4 says the whole market is stuck in. (For the secondary OSS audience, the same instrument doubles as external evidence — but its justification does not depend on that.)

*Residual risk: the regression set is only as credible as the defects curated into it, drawn from the same anecdotal corpus. It doesn't escape the evidence problem — it makes it inspectable, which is still strictly better than hiding it inside a model's self-assessment.*

---

## Appendix: Full Problem-Axis Analysis

> *This document commits to speed-as-root as its working frame (see Root Cause & Leverage Point). This appendix retains the fuller analysis that frame was selected from, for traceability. Note the deliberate disagreement: the analysis below classifies speed as a **mechanism** and accountability as the **root**. Both are kept intentionally — the working frame is a scoping choice, not a claim that the analysis below is wrong.*

Each axis below is a *different* candidate root, not a restatement of the same one. Two axes are treated as distinct only if a solution could move one without moving the other.

### The axes

**1. Speed / rate mismatch**
Production outran review throughput. *Solution shape:* make review faster. *Status:* commoditized (B3); a mechanism, not a root.

**2. Accountability gap**
The entity producing the code (AI) can't answer for it, and the human nominally responsible no longer fully comprehends it. *Solution shape:* none tooling-based — A7 marks it cultural; OSS policies keep it deliberately human. *Status:* arguably the true root, but **not tool-addressable.**

**3. Signal decoupling** *(the axis the thesis rests on)*
The cues reviewers trusted — rough code, failing tests — no longer correlate with correctness. Clean + green now coexists with wrong-shape. *Solution shape:* restore machine-checkable signals (execution, convention/shape checking). *Status:* the differentiator; underserved (B4).

**4. Comprehension erosion**
Developers ship code they didn't fully understand (author abdication). *Solution shape:* push comprehension work back to the author. *Status:* cultural (A7, [Ullah]); the corpus's #1 prescription and the thing authors are least incentivized to do.

**5. Verifiability gap**
No one can independently tell whether *any* reviewer (human or AI) is actually any good — the entire quality axis is vendor self-report. *Solution shape:* reproducible regression set / external evidence. *Status:* the commit-first instrument; but an *analyst inference*, voiced by no user.

**6. Independence gap (shared blind spots)**
Writer-AI and reviewer-AI share a lineage, so the second pass omits what the first omitted. *Solution shape:* fresh-context isolation. *Status:* real gap (B4), conditional frequency.

**7. Trust-attribution gap** *(distinct from #5)*
*Who* backs the review outcome differs by segment: org has employee accountability; OSS has nothing. *Solution shape:* differs by audience — evidence for OSS, irrelevant for org. *Status:* the axis that made the audience definition keep slipping.

**8. Noise / false-positive tolerance**
Whether a reviewer's output helps depends on FP discipline nobody in the corpus is shown to achieve; and the *right* FP target differs by segment ([Ullah] vs [Stenberg], unresolved A5). *Solution shape:* tunable signal/noise. *Status:* a live conflict, not a solved parameter.

### How they relate — root, mechanism, or symptom

| Axis | Root / Mechanism / Symptom | Tool-addressable? |
|---|---|---|
| 2. Accountability gap | **Root** | No (cultural) |
| 4. Comprehension erosion | Root-adjacent (the human side of #2) | No (cultural) |
| 1. Speed | **Mechanism** (how #2 manifests) | Partly (commoditized) |
| 3. Signal decoupling | **Mechanism → leverage point** | **Yes** |
| 6. Independence gap | Symptom of same-model reuse | Yes |
| 5. Verifiability gap | Meta-axis (about the reviewer, not the code) | Yes (instrument) |
| 7. Trust-attribution | Segmentation axis (reframes audience) | Only via #5, OSS-only |
| 8. Noise tolerance | Constraint / parameter | Yes, but no "correct" setting |

### The structural point

Axes **2 and 4 are the roots but unfixable by a tool.** Axis **1** is the mechanism everyone *notices* first (which is why it's tempting) but it's commoditized. The project lives entirely on **axis 3** — signal decoupling — with **5** as its instrument and **6** as an adjacent bet. Everything buildable is downstream of a root the project explicitly cannot touch.

The honest shape: **the project is not solving the root cause. It is restoring one machine-checkable signal that the root cause destroyed.** Naming it this way guards against over-claiming — which, given that the chosen audience (OSS) has the *widest* accountability gap and the *least* ability to close it, is the exact over-claim the project is most at risk of making.

*Note, 2026-10-09: this appendix was written while the audience was still the open-source maintainer, and that last sentence is kept as written. The audience is now the organization reviewer (see the top of this document).*
