# Competitive Landscape

This document positions **Agentic Code Review** against existing tools in and around the automated code-review space. It is written for contributors and adopters deciding whether this project fits their needs, and for maintainers keeping the project honest about where it does and does not compete.

For plain, non-comparative descriptions of each tool, see [`tool-reference.md`](./tool-reference.md).

> Snapshot as of September 2026. Pricing and features change quickly; re-verify before relying on specifics.
>
> **Re-checked 2026-10-10.** How each rival checks a finding was re-read on its own pages, and the verification claims below did not hold as written. Read [Differentiator re-check](#differentiator-re-check-2026-10-10) before the sections on differentiators and the positioning summary.

## How to read this

The tools people mention in the same breath as this project are not actually competing on one axis. They fall into three groups:

1. **Full-context AI reviewers** — the direct conceptual competitors (Greptile, CodeRabbit, Qodo).
2. **Managed multi-agent reviewers** — architecturally different, but the best design reference (Claude Code — Code Review).
3. **Different categories entirely** — a process linter (Danger/DangerJS) and a workflow tool (Graphite) that attack the same underlying problem from other angles.

Our scope is deliberately narrow: an **open-source GitHub Action with a local CLI over the same core** ([ADR-0006](../adr/0006-local-cli-core-action-as-adapter.md)), **TypeScript/JavaScript only**, a **single free/low-cost model provider** behind a thin interface, **fix suggestions as comments only** (auto-remediation deferred to v2), and a **canonical, versioned finding model** as the single source of truth for output.

Note that the CLI is not a differentiator — Greptile, CodeRabbit and Claude Code all ship one. It is **table stakes we now meet**, adopted primarily because developing a review agent through a four-minute CI loop is untenable. The differentiators below are unchanged by it.

**Sequencing caveat (2026-09-08).** GitHub integration is now deferred to **v3** ([SRS §2.3.3](./agentic-code-review-srs.md)), so v1 and v2 ship the CLI alone. Read the positioning below as describing the product at v3. Until then the project competes only where every tool in this document also offers a local mode — which is the weakest ground of the three differentiators, since the execution-backed claim thins on a machine where the developer can already run their own tests. This is a deliberate engineering sequence, not a repositioning; it does mean the competitive claim is not testable against real adopters until v3.

**Business-model caveat (2026-10-03).** The project is now **open core** ([canvas §5](./003-business-model-canvas.md)): the command-line tool and its engine stay open source and free, and revenue is planned from a **hosted review service** priced at variable cost plus a markup. Wherever this document says "free", "zero cost" or "no per-seat cost", it describes the open-source tool, which an adopter runs on their own machine or runner. The hosted service is paid and it is not designed yet, so nothing below positions it against anything. Its price was decided on 2026-10-10: $22 per seat per month, under CodeRabbit's $24, with Greptile's $30 treated as an anomaly.

---

## Tier 1 — Full-context AI reviewers (direct competitors)

### Greptile
The closest match to our architectural thesis — reviews grounded in whole-repository context rather than diff-local feedback. Its credit-metered economics (one standard review = one credit) are a useful confirmation that **per-review inference cost is the binding constraint** in this category, which is exactly what our blast-radius triage and single-free-provider decisions are built around. Its free tier for OSS projects competes directly with our "free for public repos" goal — an adopter can already get context-aware reviews at no cost from a hosted tool.

### CodeRabbit
The market-share leader, and it has already shipped, as paid features, several things that sit on our roadmap or in our design: blast-radius triage, a deterministic "codegraph" (a more ambitious cousin of our tree-sitter dependency analysis), and continuous "Learnings" (adjacent to our pattern library). Realistically, our v1 feature set is close to CodeRabbit's entry tier minus the polish and the six-million-repo moat. **We do not try to out-feature CodeRabbit.** Our edge is openness, zero cost, and auditability — not breadth.

### Qodo (formerly Codium)
The most important one for contributors to study, because its PR-review engine (**PR-Agent / Qodo Merge**) has an open-source lineage and is the closest existing thing to what we are building. Its self-learning "rules system" is a more mature take on our pattern library, and its governance/audit-trail framing validates our decision to make the finding model a versioned, serializable source of truth.

---

## Tier 2 — Managed multi-agent reviewer (best design reference)

### Claude Code — Code Review
Architecturally different (a fleet of frontier-model agents on managed infrastructure) but the single most instructive design precedent for this project. Several of its choices mirror ours and are worth citing as prior art:

- **Non-blocking by design.** Its check run always completes with a neutral conclusion. This is exactly our FR-8.3.
- **A verification step.** It checks candidate findings against actual code behavior before posting them. Our execution-backed findings (FR-4) are our version of this — but we verify **deterministically**, by running the real test suite, where they verify **agentically**. That determinism is a genuine, nameable differentiator.
- **A machine-readable output contract.** A parseable comment in the check-run details yields per-severity counts. Our JSON artifact (FR-8.2) is a more principled, schema-versioned version of the same idea.
- **The cost reality.** Each review averages **$15–25** in token cost, scaling with PR size and how many findings need verification.

That cost figure is the most important number in this analysis. It quantifies what our free-tier budget is up against and is the empirical justification for triage-by-blast-radius (don't spend $25 reviewing a docs typo) and context capping. Our bet is that deterministic execution + a cheap model + aggressive triage captures most of the value at a small fraction of the cost. That is defensible — but the gap between "frontier model with verification" and "free NIM-tier model" is also the honest risk to our review **quality**, and we hold that tension consciously rather than assume the architecture erases it.

---

## Tier 3 — Different categories

### Danger / DangerJS
Not a competitor — a complement and a positioning foil. Danger is deterministic and rule-based; it checks that you followed the process (CHANGELOG present, ticket linked, labels set), not whether the code is correct. The cleanest one-line framing of this project to a skeptical audience:

> **Danger checks that you followed the process; Agentic Code Review checks whether the code is actually correct.**

Two practical implications: we should aim to **compose with** DangerJS rather than replace it (many TS/JS repos already run it), and its Dangerfile is a proven ergonomic model for user-authored, in-repo rules — worth borrowing for our pattern library and config UX.

### Graphite (stacked diffs)
A workflow alternative that attacks the **same root problem we state** — the AI-driven surge in PR volume and size — from the **input side** (make PRs smaller) rather than the **review side** (review them better). Complementary, not competing. The strategic signal worth internalizing: Graphite's acquisition by Cursor is the industry betting that **code writing and code review converge into one vendor's loop**. Our fresh-context, decoupled review agent (Objective 3) is a deliberate bet **against** that direction, to avoid the self-confirmation bias of a model reviewing its own output.

---

## Where this project stands

### What the landscape confirms we got right
- **Non-blocking output** — Claude Code does the same, for the same reason.
- **Blast-radius triage** — CodeRabbit monetizes exactly this; it is a real axis of value.
- **A canonical, versioned finding model** — Qodo's governance framing and Claude Code's machine-readable output both point the same way; ours is more rigorous than either.
- **Cost as an architectural driver** — Claude Code's $15–25/review and Greptile's credit metering prove the constraint is real, not theoretical.

### Genuine differentiators (lead with these, not features)

*Superseded in part on 2026-10-10: differentiator 2 is withdrawn as worded, and 1 and 3 are narrowed. See the re-check below.*

1. **Open-source, self-hostable GitHub Action with no per-seat cost.** The Tier 1 tools have OSS-free *programs*, but the engine is a hosted black box. Ours is inspectable and forkable end to end. That is the tool an adopter runs themselves; the hosted service is the paid tier (see the business-model caveat above).
2. **Deterministic, execution-backed verification.** Competitors verify agentically (expensive, non-reproducible). We verify by running the actual test suite (cheap, auditable, reproducible). This is our strongest technical story.
3. **Fresh-context decoupling as a stated anti-bias principle** — a deliberate stance against the writer/reviewer convergence the Cursor–Graphite deal represents.

### Honest limitations (kept here on purpose)
- **Feature breadth.** Our v1 is roughly CodeRabbit's entry tier against a product with a massive install base. We will not win on breadth, and shouldn't try.
- **Quality gap.** A free NIM-tier model without agentic verification is very likely noisier than a frontier-model-with-verification reviewer. The NFR pass should set an explicit **accuracy / false-positive** target, not only latency and cost targets. The pattern-library regression set (FR-6.2b) is currently the main guard against shipping a noisy reviewer — and noise is what kills adoption of tools in this category.
- **The test-suite assumption.** "Execution-backed" only adds value on repositories with a runnable test suite. On the median public TS/JS repo that may not hold, which erodes differentiator #2 for part of the target audience. Worth measuring the size of that gap before making execution the headline feature.
- **The paid tier (added 2026-10-03).** Under open core the hosted service has to be worth paying for next to our own free tool, and next to rivals' free hosted tiers: Greptile's Starter plan, and the free open-source plans of CodeRabbit and Qodo. What it adds is not stated yet.

---

## Differentiator re-check (2026-10-10)

**This section supersedes the verification claims above and in the positioning summary.** It was written for the final pitch (task 2 of the rework list), after the reviewer became the one audience and the tagline became "Review that shows its evidence". Each rival's own pages were read on 2026-10-10. Everything quoted from a vendor is that vendor's claim; none of it was tested.

### What each rival says it does

| Tool | How a finding is checked | What the reader is shown | Source |
|---|---|---|---|
| CodeRabbit | "CodeRabbit also runs verification scripts on the review comments provided by the LLMs", and "These verification scripts are generated in the sandbox". Linters and scanners "run automatically in secure sandboxed environments". "any low value feedback is automatically filtered out and not passed on to the user" | "You can see the code definitions that were used in the review comment." Tool output is attached under a "Review details" comment | [Vendor blog, 2025-07-17](https://www.coderabbit.ai/blog/context-engineering-ai-code-reviews); [tools documentation](https://docs.coderabbit.ai/tools) |
| Greptile | TREX, in public beta since 2026-06-15: "Greptile doesn't just review your PR, it writes and runs targeted tests in a sandbox", which "runs against the services, dependencies, and framework your repo already uses, not a generic mock environment." | It "attaches logs, screenshots, traces, scripts, or videos when something fails." Review summaries carry a "Confidence score and a short verdict at the top" | [Changelog](https://www.greptile.com/changelog), entries of 2026-06-15 and 2026-09-16 |
| Qodo | "a judge agent merges their findings, removes duplicates, and filters out anything low-confidence". Nothing on the page says it runs tests or executes code | "every finding states what needs attention, why it matters, and how to fix it, ranked by severity" | [Code review documentation](https://docs.qodo.ai/code-review) |
| Claude Code Review | "a verification step checks candidates against actual code behavior to filter out false positives" | "Findings include a collapsed **Why this was flagged** section that you can expand to read why Claude flagged the issue and how it verified the problem." | [Documentation](https://code.claude.com/docs/en/code-review) |

Not found on any of these pages: a statement that the tool runs the repository's own existing test suite, or that it reports which files it did not cover.

### What this does to our three differentiators

| Claim made above | Built today? | Does a rival already do it? | Verdict |
|---|---|---|---|
| "Competitors verify agentically… We verify by running the actual test suite" (differentiator 2; "Verification" row of the summary) | No. Today's build runs no checks | Greptile writes and runs tests in a sandbox, and CodeRabbit runs verification scripts and linters in one. Neither is "a model only" | **Withdrawn as worded.** What is left is narrower: the project's own existing tests and type-check, run once by our code and never by the model (FR-4.6, FR-4.7). It is specified, not built, and it must be said that way |
| "Review that shows its evidence" (the tagline; FR-5.2c) | Yes. Every finding carries a typed evidence reference, checked at the call boundary. Today the evidence is the part of the change the finding rests on | Claude Code Review shows "how it verified the problem"; Greptile attaches logs and traces; CodeRabbit shows the definitions it used | **True, but shared.** Showing evidence is not ours alone |
| "Open-source… inspectable and forkable end to end" (differentiator 1) | The code is public. The repository has no LICENSE file yet, so it is not yet open source in the legal sense | Qodo's original engine, PR-Agent, is MIT-licensed and "a community-maintained legacy project of Qodo": "Qodo has donated PR-Agent to the open-source community." ([repository](https://github.com/qodo-ai/pr-agent)). CodeRabbit, Greptile and Claude Code Review are closed | **Holds against three of four**, once a licence is added |
| Fresh-context reviewer, separate from the code-writing agent (differentiator 3) | Yes, by construction: the tool only reviews | Claude Code Review also uses fresh agents | **Weak.** A design stance, not a reason to choose us |

### What is ours, stated as narrowly as the evidence allows

1. **Nothing is dropped silently.** A finding the tool cannot back with evidence is kept and marked "unverified", with a reason (FR-5.2c). Three of the four rivals describe the opposite design: unconfirmed or low-confidence findings are filtered out before the reader sees them (the CodeRabbit, Qodo and Claude Code Review quotations above). This is built. Whether a reviewer prefers a labelled finding to a filtered one is untested, and a rival would call the filtering a feature.
2. **The review reports its own gaps.** It says which files got no finding, that no checks ran and that no related context was gathered (FR-11.2; the degradations on the MVP slide). No rival page read here describes this. An absence on four pages is weak evidence; it is not proof that they do not do it.
3. **Price: a small difference, not a reason to choose us.** The hosted service is priced at $22 per seat per month, $2 under CodeRabbit (decided 2026-10-10; see [`0052-unit-economics-and-financials.md`](./0050-financial-planning/0052-unit-economics-and-financials.md)). It is the average of CodeRabbit's $24 and Graphite's $20; the founder ruled that it stay under CodeRabbit's price and that Greptile's $30 is an anomaly.
4. **An engine that can be read and forked**, once the licence is in place.

**Where rivals are ahead today, said plainly.** They verify more than our build does: ours makes one model pass and runs nothing. A reviewer choosing on verification alone would not choose today's build.

### Prices, side by side

| Tool | Unit | Price | A review costs |
|---|---|---|---|
| CodeRabbit | Per developer per month | $24, billed annually (Essentials) | Not priced per review in the plan; "pay-as-you-go reviews" are listed as an add-on, with no price in our tool reference |
| Greptile | Per seat per month, with credits | $30 per seat with 50 credits; "Extra credits cost $1 each"; a standard review is 1 credit and a TREX review 3 | Standard: $0.60 inside the plan (Calculated: $30 ÷ 50), $1.00 beyond it. With tests run: $1.80 and $3.00 (Calculated: × 3) |
| Claude Code Review | Per review, by token usage | "Each review averages $15-25 in cost" | $15–25 |
| Agentic Code Review | Per seat per month | $22, the average of CodeRabbit's $24 and Graphite's $20 | About $0.88 at 25 reviews a month (Calculated: $22 ÷ 25). Our estimated cost of a review is $0.0456 to $0.0775 |

Sources: [`tool-reference.md`](../tool-reference.md) for CodeRabbit and for Greptile's credits per review; [Greptile's pricing page](https://www.greptile.com/pricing) and the Claude Code Review documentation, both read 2026-10-10. The four tools do different amounts of work for the price: Claude Code Review runs many agents for about 20 minutes, and ours makes one model pass.

### Who is already reviewing pull requests, in our own sample

From the ten public TypeScript repositories measured in [`review-volume-report.md`](./0050-financial-planning/0051-cost-structure/review-volume-report.md) §2.5: 5,711 of the 7,670 human pull requests opened in September 2026 were reviewed by a bot account. Counted by account (Calculated from the same data):

| Reviewer account | Pull requests reviewed | Share of the 7,670 | Where |
|---|---|---|---|
| A reviewer bundled with the code host, left unnamed in these documents by an earlier decision | 2,481 | 32.3% | Mostly one repository |
| `cubic-dev-ai` (Cubic) | 2,064 | 26.9% | n8n (1,676 of 1,714) and Twenty (388) |
| `greptile-apps` (Greptile) | 901 | 11.7% | Twenty (901 of 1,482) |
| `coderabbitai` (CodeRabbit) | 521 | 6.8% | Supabase (490 of 892) and tRPC (31 of 47) |

- **Cubic is a rival this document does not cover.** It reviewed more of the sample than Greptile and CodeRabbit together. Its pricing page lists $40, $99 and $200 per developer per month ([cubic.dev/pricing](https://www.cubic.dev/pricing), read 2026-10-10) and does not say how it checks a finding. `[MISSING: a profile of Cubic]`
- **Neither Qodo nor Claude Code Review appears** as a reviewing account in the sample.
- **The sample is ten repositories.** One repository can carry a whole tool's count, as the "Where" column shows, so these shares describe the sample and not the market.

### What follows for the pitch

- The competition slide no longer says "Rivals verify with a model; ours runs the tests". It names the differences above, says where rivals are ahead, and says that the price, $2 under CodeRabbit, is not the reason to choose us.
- The tagline and the one-liner stay true. They describe what the product does, not what only it does. The clause that is ours alone is the second half of the definition: "or say the finding is unverified".
- The limits listed under "Honest limitations" stand, and the test-suite assumption now applies to a narrower claim.

---

## Positioning summary

*The "Verification" row is superseded by the re-check above: rivals do not verify with a model alone, and our test run is specified, not built.*

| | Agentic Code Review (this project) | Tier 1 hosted reviewers | Claude Code Review | Danger/DangerJS | Graphite |
|---|---|---|---|---|---|
| Category | Open-source AI reviewer | Hosted AI reviewer | Managed multi-agent reviewer | CI process linter | Stacked-diffs workflow |
| Cost model | Open-source tool: free, on a single low-cost provider. Hosted service: $22 per seat per month, under CodeRabbit's $24 (planned) | Per-seat subscription | Per-review token usage | Free (MIT) | Per-seat subscription |
| Verification | Deterministic (real test run) | Agentic / model-based | Agentic behavior check | None (rule-based) | Agentic (add-on) |
| Openness | Fully open, forkable | Closed engine | Closed | Fully open | Closed |
| Bias stance | Decoupled fresh-context agent | Varies | Fresh agents | N/A | Converging with writer (Cursor) |
| Scope | TS/JS, GitHub Action + local CLI | Multi-language, hosted | Multi-language, managed | Any lang, CI glue | GitHub-native workflow |

*See [`tool-reference.md`](./tool-reference.md) for detailed, non-comparative descriptions and sourced pricing.*
