# Problem and Audience — Agentic Code Review

**Status: non-normative.** A business-side working document, not a specification. It defines nothing to build.

**This is the one place where the project's audience, problem and tagline are worded.** Decided by the founder on 2026-10-09. Every other document and slide copies section 1. Where another document differs, this one is right and the other is out of date; section 8 lists who copies it and what still differs. A business wording, for listeners who are not engineers, was added to section 1 on 2026-10-14.

---

## 1. The definition

| | Wording to use |
|---|---|
| **Tagline** | Review that shows its evidence. |
| **Who** | The reviewer: an engineer who reviews a teammate's AI-assisted TypeScript or JavaScript pull request, in a company or funded team. |
| **Pain** | They can no longer tell, from clean code and passing tests, whether a change fits the codebase. |
| **Why now** | AI writes code faster than a team can read it. The code arrives clean and with its tests passing, so rough code and failing tests no longer show a reviewer where to look. |
| **What we do** | Review the change and show the evidence for every finding, or say the finding is unverified. |

**Problem statement.** Reviewers of AI-assisted TypeScript/JavaScript pull requests cannot tell whether a clean-looking, test-passing change actually fits the codebase. The signals they relied on, rough code and failing tests, no longer point at structural defects: code that passes its tests while choosing the wrong backend, breaking an established convention or eroding the architecture. AI review tools have not been shown to restore that signal: in the studies available, most of their comments are not acted on.

**What is outside it.** Functional bugs, which tests still catch. Omissions that depend on knowledge held only in people's heads, which the product does not reach. Rubber-stamping and missing accountability, which are cultural and which no tool fixes.

**Short forms for slides and speech**

| Use | Wording |
|---|---|
| Problem slide headline | Cheap to write. Flawless to look at. Five times as long to check. Since 2026-10-14 (see "For a business audience" below); it replaced "Reviewers can no longer trust clean, test-passing code" |
| Who, in a sentence | reviewers on TypeScript teams. The one-liner and the elevator pitch say only "reviewers" (founder, 2026-10-10): the language narrows who listens and is not needed to catch attention. The audience itself is unchanged |
| Pain, in a sentence | AI-written software that looks right but isn't. Since 2026-10-14, for listeners who are not engineers; it replaced "AI-written code that passes its tests but doesn't fit their codebase", which says the same to an engineer |
| Point of view | A reviewer of AI-assisted pull requests needs to know when a clean, test-passing change still does not fit the codebase, because clean code and passing tests no longer show where the problems are. |
| Question to design against | How might we show a reviewer, with evidence they can check, when a clean, test-passing change does not fit the codebase? |

"Does not fit the codebase" replaces the older "wrong-shaped". Documents say "AI-assisted pull requests"; slides and speech may say "AI-written code".

### For a business audience

Decided by the founder on 2026-10-14. The problem statement above stays the definition, and it is worded for engineers. For juries, funders and other listeners who are not engineers, use these forms instead. They claim nothing that the definition and section 6 do not support.

| Use | Wording |
|---|---|
| Written problem statement | AI has made writing software cheap and checking it slower. Where AI use is high, one industry study found that a review takes about five times as long, and nearly a third more changes skip review altogether. Companies have sped up production without speeding up quality control. |
| Spoken, in the presentation | AI has made writing software cheap. What it produces looks flawless, like a report with perfect spelling and the wrong facts, so the people checking it can no longer tell where the problems are. The strain shows: where AI use is high, checking a change takes about five times as long, and nearly a third more changes go out with no check at all. |
| Problem slide headline | Cheap to write. Flawless to look at. Five times as long to check. |

**What each one rests on.**

- **The numbers** are Faros AI's, from 22,000 developers, read through O'Reilly (section 6). Median review duration rose 441.5%, which is about five times as long (Calculated: 1 + 4.415 = 5.4). Pull requests merged without review rose 31.3%, said as "nearly a third more". They are vendor data and show a correlation, so say "where AI use is high", never "because of AI". They measure how long a review takes from start to finish, not hours of effort.
- **The written statement carries the "why now" and its measured strain, not the headline pain.** The headline pain, that a clean change can still be wrong, is in the spoken form ("looks flawless … can no longer tell where the problems are") and in the slide's "Flawless to look at". It is still anecdote (section 6).
- **The proofreader comparison and the numbers are two different claims.** The numbers show that review got slower and was skipped more often, not that the mistakes are hidden. The spoken form keeps them in separate sentences for that reason.

**Terms, if they come up.**

| Term | Plain meaning |
|---|---|
| Pull request | A proposed change to the software, submitted for a colleague to approve before it goes in |
| Code review, reviewer | The approval step, and the engineer doing it |
| Tests | Automatic checks that software runs on itself to confirm it works |
| "Does not fit the codebase" | It works, but breaks the company's own rules or design for its software |
| AI-assisted | Written partly or wholly by an AI tool |

### The two supporting pains

They are real for the same reviewer, and the product must answer them, but neither is the headline.

1. **Routine checks, repeated on every pull request.** The reviewer re-runs the same mechanical checks each time: "the repetition, not the difficulty". **This is where "automating usual tasks" sits.** The product does the routine first pass so the reviewer's attention goes to judgement. It is second, not first, because rivals already offer it, so it is a need we must meet and not a reason to choose us.
2. **An AI second opinion they cannot rely on.** Developers act on few AI review comments, and nothing tells the reviewer which ones deserve attention. When the same kind of model wrote the code, the second opinion may also share its blind spots. The tagline answers this one directly: a finding that carries its evidence can be checked quickly, and one that has none says so.

### How we will know it is solved

A measured catch rate on curated defects of this kind, at a false-positive rate low enough that reviewers read the output. Neither exists yet: the regression set is not built, and the tolerable false-positive rate is not set, because two sources disagree on it.

---

## 2. What was decided on 2026-10-09

| Decision | Answer | What it replaces |
|---|---|---|
| The audience | One: the reviewer (Segment 2 of [`001`](./001-chat_result_needs_vs_pains_analysis.md)) | "Primary: organization reviewer; secondary: open-source maintainer" |
| Other segments | Possible later expansions, not secondary audiences (section 4) | A secondary audience |
| From the tech lead's segment | One pain only: architecture that erodes silently while the tests pass. It is the defect class inside the headline pain | — |
| What is served today | A review of uncommitted changes before they are pushed, and a review of a public pull request (section 3) | "v1 serves the author, the reviewer is served from v3" as the whole story |
| The tagline | "Review that shows its evidence" | Two lines carrying one message. "Green no longer means right" is no longer a tagline or a slide headline |
| Market sizing | The obtainable market is counted in reviewers; the larger layers stay in developer seats ([`004-market-study.md`](./004-market-study.md)) | Every layer counted in developers |

**Two readings of mine, to confirm or overrule.**

- **The headline pain is the lost signal, and automating routine checks is the first supporting pain.** The founder's notes fixed the audience and the tagline and asked for the architecture pain to be included; they did not rank the two pains in so many words. The tagline is about evidence, and [`001`](./001-chat_result_needs_vs_pains_analysis.md) ranks the signal pain first, so it leads here. Swapping them means swapping the "Pain" row with supporting pain 1, and the problem slide's headline.
- **The reviewer works "in a company or funded team".** That is the wording of [`002`](./002-chat_result_problem_definition.md), kept. It puts the open-source volunteer maintainer among the later segments.

---

## 3. What is served today, and what is not

| What the build does | Whose seat | State |
|---|---|---|
| Reviews uncommitted changes before they are pushed (also a branch range) | The author's. The reviewer benefits one step later, if fewer defects reach review; that effect is not measured | Built: one model pass, no checks run, no related context |
| Reviews a public pull request named by its address | The reviewer's | Built on 2026-10-09 ([ADR-0011](../../adr/0011-cli-reads-a-public-pull-request.md)). It reads only: nothing is posted on the pull request, private repositories are out of reach, and no checks run |

**Not served yet:** findings posted on the pull request and private repositories (the GitHub Action, v3); running the project's tests and type-check (specified, not built); a measured catch rate (not built); the project's own rules (specified, not built).

**To say whenever the build is shown.** The specification still records two gaps, and this document does not close them. R-5: v1 was specified for the author, and reading a pull request is the first thing it does for the reviewer, not the last. R-1: the project's thesis is unproven at the context depth v1 reaches. Both are in [`agentic-code-review-srs-v1.md`](../../agentic-code-review-srs-v1.md) §9.

---

## 4. Segments left for later

From the five segments in [`001`](./001-chat_result_needs_vs_pains_analysis.md). None is a secondary audience.

| Segment | Why not now | What already touches it |
|---|---|---|
| Pull-request author | Their top need is a fast merge, which pulls against the comprehension work the evidence says helps. Their self-review pain is rated cultural | The pre-push review is run from the author's seat today |
| Tech lead or maintainer in a company | One pain is in scope now (architecture eroding silently). The rest wait: throughput capped by the lead's reading speed, review metrics, fixes that never reach `main` | Probably the person who decides to adopt and to pay; not established |
| Open-source volunteer maintainer | Their two heaviest pains are capacity and accountability, which a tool cannot fix, and rivals already review open-source projects free. Secondary audience until 2026-10-09 | The pull-request review reads public repositories, and the v3 Action's adoption can only be counted in public repositories |
| Security engineer | Deep security tooling is deferred to v2 | Nothing yet |

---

## 5. Re-review of the needs-versus-pains analysis

The same rule as [`001`](./001-chat_result_needs_vs_pains_analysis.md): severity × frequency, then filtered by what a tool can fix and what the market leaves open. Scores are 001's own and are judgement calls, not measurements.

| Reviewer pain | Sev × Freq | Tool-fixable | Crowded or open | Place in the definition |
|---|---|---|---|---|
| Subtle context-wrong code slips past | 5 × 4 = 20 | Partly | Open | **Headline pain** |
| Architecture erosion, convention drift, wrong backend; tests pass anyway (from the tech lead's segment) | 5 × 3 = 15 | Partly | Open | Inside the headline pain: its defect class |
| Repetitive mechanical checking | 4 × 4 = 16 | Partly | Partly crowded | Supporting pain 1 |
| A second pass that is not the writer-AI's twin | 4 × 3 = 12 | Yes | Open | Supporting pain 2 |
| Cannot triage the flood | 4 × 4 = 16 | Partly | Crowded | Not claimed: triage is commonplace among rivals and deferred to v2 |
| Rubber-stamping | 4 × 3 = 12 | No, cultural | — | Not claimed |

**What can catch the headline defect.** 001's own note is "sandboxed execution (FR-4), partially": a test run catches it only sometimes, because by definition the tests pass. The project's own rules and the surrounding code are what catch a change that does not fit; the test run is the evidence a finding points to.

**What has changed since 001 was written.**

- **The verifiability gap is now measured in part.** 001 ranked "no one can independently verify a reviewer" second and called it "an inferred gap, not a pain any Part A source voiced directly". A peer-reviewed study now measures it for AI reviewers (section 6). It is still not a need any reviewer has voiced to us.
- **The headline pain is still anecdote.** Nothing new measures how often clean, test-passing code is wrong for its codebase.
- **The reviewer's load is now measured, for public repositories** (section 6).
- **The AIDev figure stays unused.** The new study draws on the AIDev dataset, which 001 set aside because its paper could not be verified. The dataset is real; the 61.38% figure has still not been checked at its source.

---

## 6. Evidence, and what is still missing

Confidence labels follow [`004-market-study.md`](./004-market-study.md): A primary or peer-reviewed, B reputable secondary, C our calculation.

| Claim | Evidence | Tier |
|---|---|---|
| Clean, test-passing code hides defects that do not fit the codebase | Three sources describe it; one team's first-hand account names the three defect types ([background study](./chat_result_ai_pr_review_background_study.md) A3, A4) | Anecdote. How often it happens is unmeasured |
| Review got slower and thinner where AI use is high | Median review duration up 441.5%, pull requests merged without review up 31.3% (Faros AI, 22,000 developers, through O'Reilly) | B, vendor data; a correlation |
| Routine checking wears reviewers down | "the repetition, not the difficulty": two source types agree (background study A3) | Anecdote |
| AI review comments are mostly not acted on | Human comments addressed about 60% of the time, review agents' comments 0.9% to 19.2% (earlier work cited by Chowdhury et al., MSR 2026) | A, second-hand |
| AI review signal is low and varies by tool | 12 of 13 review agents average under 60% signal, by a keyword-based measure; pull requests reviewed only by agents merged at 45.20%, against 68.37% for human-only review (Chowdhury et al., MSR 2026; 3,109 pull requests with AI-generated code) | A. The authors name the keyword measure as a limit |
| AI review speeds decisions without improving quality | 1.02 million pull requests, 207 projects (Zhong et al., arXiv, July 2026) | A, preprint |
| Review work rests on few people, each carrying more than they write | In ten public TypeScript repositories in September 2026: 182 core reviewers carried 97.7% of the reviewing of 7,670 human pull requests, a median of 21.5 each, against 13 opened per core developer; the top fifth of reviewers did 73% of it ([`review-volume-report.md`](./0050-financial-planning/0051-cost-structure/review-volume-report.md) §2.5) | C, from A. Public repositories stand in for company teams |
| Reviewers there already receive automated comments | In five of those ten repositories, a bot account reviewed more than half of the human pull requests (same source) | C, from A. Bot accounts include scanners and CI bots as well as AI reviewers |

The MSR 2026 figures were re-read at the source on 2026-10-09.

**Still missing**

- `[MISSING: a reviewer's own words]`. No reviewer has been interviewed; every quotation is second-hand.
- `[MISSING: how often the headline defect happens]`. It waits for the regression set and the pilot.
- `[MISSING: who pays]`. The reviewer uses the tool; whether the reviewer, the team or its lead pays follows from the pricing unit, which is undecided.

---

## 7. Every earlier definition, side by side

| # | Document | Who suffers | The pain | The mechanism | Now |
|---|---|---|---|---|---|
| 1 | Requirement catalogue §2.1.1 ([`agentic-code-review-srs.md`](../agentic-code-review-srs.md)) | Human reviewers, as a capacity | "a review bottleneck" | AI-assisted development "sharply increased the volume and size of pull requests"; linters and single-shot reviewers cover fragments | Background. Volume is the upstream cause, not the headline: faster review and triage are crowded |
| 2 | Needs versus pains ([`001`](./001-chat_result_needs_vs_pains_analysis.md)) | Five segments | Top-ranked: the reviewer "can't trust that clean-looking, test-passing code is actually correct" | Sorts each pain into technical or cultural | The source of the ranking; re-reviewed in section 5 |
| 3 | Problem definition ([`002`](./002-chat_result_problem_definition.md) and the [full document](../Agentic_Code_Review_Problem_Definition_v1.md)) | Organization reviewer first, open-source maintainer second | Cannot tell whether "clean-looking, test-passing changes" fit the repository | Speed as the working root cause; the lost signal as the place a tool can act | The closest to section 1. Changed: one audience, shorter statement, the clause about rivals' internals replaced by measured evidence |
| 4 | Entrepreneurship problem statement (on `main` only) | "the engineer who peer-reviews a colleague's" pull request "inside a company" | Three insights: green no longer means right; a second AI opinion may not be independent; the fatigue is repetition | Passing tests and clean code "no longer correlate with structural correctness" | Same audience, and its three insights are section 1's headline and two supporting pains. Its solution, "an open-source GitHub Action", describes v3 |
| 5 | Specification, normative ([`agentic-code-review-srs-v1.md`](../../agentic-code-review-srs-v1.md) §1.1, §2.2, R-5; ADR-0006) | Served: "the developer author". Named persona: the reviewer | "reducing a reviewer's queue", claimed for v3 | — | Unchanged. Only the founder amends it. ADR-0011 adds that reading a pull request "is the first thing v1 does for that reviewer" |
| 6 | Business model canvas ([`003`](./003-business-model-canvas.md)), before 2026-10-09 | Primary peer reviewers, secondary open-source maintainers, "today's actual user: the change author" | "does this clean, test-passing code fit this repo?" | — | Block 1 and risk 2 updated to section 1 |
| 7 | Pitch pack ([`0060-final-pitch/`](./0060-final-pitch/)), before 2026-10-09 | "TypeScript teams" | "AI-written code that passes its tests but doesn't fit their codebase" | "Green no longer means right" as a second tagline | The one-liner names the reviewer; one tagline; the problem headline is the pain |
| 8 | Market study ([`004`](./004-market-study.md)) | Counted: 36.5M professional developers | "Signal quality is the open gap, not speed" | Review became the bottleneck when writing got cheap | Obtainable market narrowed to reviewers |
| 9 | Competitive landscape ([`competitive-landscape.md`](./competitive-landscape.md)) | "contributors and adopters" | "checks whether the code is actually correct" | Rivals verify with a model, ours with a test run | Re-checked on 2026-10-10 and withdrawn as worded: rivals run sandboxed checks too, and our test run is not built. The file's new section names what is left |
| 10 | Founder's note, 2026-10-09 | The reviewer | "Automating usual tasks to help the reviewer" | — | Supporting pain 1 |
| 11 | Background study A1 ([`chat_result_ai_pr_review_background_study.md`](./chat_result_ai_pr_review_background_study.md)) | Author, agent or maintainer: three failure points left unreconciled | — | "Generation got cheap; verification and maintenance did not" | Background. Section 1's "why now" is this mechanism |

---

## 8. Where this wording is used

| Document | State on 2026-10-10 |
|---|---|
| [`../Agentic_Code_Review_Problem_Definition_v1.md`](../Agentic_Code_Review_Problem_Definition_v1.md) | Updated: audience, problem statement, POV-2's evidence. The reasoning sections are unchanged |
| [`001`](./001-chat_result_needs_vs_pains_analysis.md), [`002`](./002-chat_result_problem_definition.md) | Kept as records, with a dated note marking what is out of date |
| [`003-business-model-canvas.md`](./003-business-model-canvas.md) | Fully refreshed on 2026-10-10: all nine blocks, the three risks, the diagram and the evidence table |
| [`004-market-study.md`](./004-market-study.md) | Reviewer view added; the obtainable market narrowed to reviewers; our own price, $22 a seat, noted beside the proxy |
| [`0060-final-pitch/`](./0060-final-pitch/) and the designed deck | Follows section 1 throughout. The one-liner and the elevator pitch say only "reviewers"; the solution and competition slides were reworked after the differentiator re-check. On 2026-10-14 the problem slide, its speaker notes, slide 2 of the Arabic script and the calculation basis took the business wording. The same day the one-liner and the elevator pitch took the new "Pain, in a sentence", and the title slide's speaker notes were rewritten around review time and the reviewing bottleneck |
| Entrepreneurship problem statement | **Not updated.** It exists only on `main`, not on the working branch. When the branches meet, it needs a pointer to this file and its solution paragraph brought up to date |
| [`agentic-code-review-srs-v1.md`](../../agentic-code-review-srs-v1.md) §1.1, §2.2, R-5; ADR-0006; `CLAUDE.md` | **Left as they are on purpose.** They are normative or append-only, and they say v1's primary user is the author. Whether §2.2 should now list the reviewer as a v1 user is the founder's call |
| [`../agentic-code-review-srs-ar.md`](../agentic-code-review-srs-ar.md) and the Arabic problem-definition files named in 002 | Stale; not re-synced |
| [`competitive-landscape.md`](./competitive-landscape.md) | A dated re-check of the differentiator was added on 2026-10-10. The earlier text still says "contributors and adopters" |
| [`feature-inventory.md`](./feature-inventory.md) | Not touched. It names no audience that conflicts |
