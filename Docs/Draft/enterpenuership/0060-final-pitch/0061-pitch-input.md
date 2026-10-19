# Pitch Input Sheet — Agentic Code Review

**Status: non-normative.** A business-side working document, not a specification. It defines nothing to build.

**Source discipline.** Every value below is copied from a file in this repository or was decided by the founder on 2026-10-03, and says which. Nothing was researched or estimated until 2026-10-10. On that date three kinds of outside or measured input were added, each named where it is used: rivals' own pages, read for the differentiator re-check; Google's price list for Gemini 3.8 Flash; and five measured review runs. A field with no source is written `[MISSING: what is needed]`. Where two files disagree, both are quoted under `[CONFLICT]` and neither is chosen.

This sheet is the INPUT section of the deck prompt in the *Pitch Implementation Guidelines* (2026-10-03), in that prompt's field order. [`0062-one-liner-and-elevator-pitch.md`](./0062-one-liner-and-elevator-pitch.md) and [`0063-pitch-deck.md`](./0063-pitch-deck.md) were written from it and from nothing else, with one exception since 2026-10-10: the 1968 conference report quoted in the elevator pitch's hook, an outside source cited in the first of those files.

---

## Step 0: audience, ask and format

| Decision | Answer | Where it comes from | Passes the guide's test? |
|---|---|---|---|
| Audience | Juries and funders: the DEPI final-pitch jury | Founder, 2026-10-03 | Yes: one audience |
| Ask | TypeScript teams run the tool on their real changes in a pilot | Founder, 2026-10-03 | **Not yet.** It names an action, but not how many teams, for how long, or from when |
| Business | Open core: a free open-source command-line tool, plus a paid hosted review service priced per seat per month, at the average of rivals' prices and under CodeRabbit's | Founder, 2026-10-03; the seat price and its limits, 2026-10-10 | Recorded in the canvas §5 and the competitive landscape. The paid service itself is not designed (see Business model) |
| Format | Presented live | Assumed, not confirmed | Confirm |
| Time slot | 10 minutes | Assumed: the guide's default when no slot is given | Confirm |
| Language | English | Founder, 2026-10-03 | Yes |

---

## INPUT

### [Pitch setup]

- **Venture name:** Agentic Code Review. Source: [`pr-agent-pricing-template.md`](../0050-financial-planning/pr-agent-pricing-template.md) ("Product: Agentic Code Review"). The canvas title says "Agentic Code Reviewer", and the installed command is `agentic-review`.
- **One-liner:** We help reviewers catch AI-written software that looks right but isn't, by showing the evidence for every finding. Since 2026-10-14 it says "software that looks right but isn't" in place of "code that passes its tests but doesn't fit their codebase", for listeners who are not engineers (founder). Source: written in [`0062-one-liner-and-elevator-pitch.md`](./0062-one-liner-and-elevator-pitch.md); it names the reviewer since 2026-10-09, and since 2026-10-10 its last part is the tagline's claim, not "the project's own rules and test results", which today's build does not use. It no longer names TypeScript (founder, 2026-10-10).
- **Tagline:** Review that shows its evidence. Source: founder, 2026-10-09; [`000-problem-and-audience.md`](../000-problem-and-audience.md) §1.
- **Audience:** juries and funders.
- **Format:** presented live (assumed).
- **Time slot in minutes:** 10 (assumed).
- **Language:** English.

### [Problem]

- **Who has the problem:** the reviewer, "an engineer who reviews a teammate's AI-assisted TypeScript or JavaScript pull request, in a company or funded team". Set as the one audience on 2026-10-09. Source: [`000-problem-and-audience.md`](../000-problem-and-audience.md) §1. The pull-request author, the tech lead, the open-source maintainer and the security engineer are possible later segments (§4).
  - **The pain:** "They can no longer tell, from clean code and passing tests, whether a change fits the codebase." Two supporting pains: routine checks repeated on every pull request, and an AI second opinion they cannot rely on (same file, §1).
  - **For a business audience** (founder, 2026-10-14; same file, §1, "For a business audience"). Written: "AI has made writing software cheap and checking it slower. Where AI use is high, one industry study found that a review takes about five times as long, and nearly a third more changes skip review altogether. Companies have sped up production without speeding up quality control." The problem slide's headline: "Cheap to write. Flawless to look at. Five times as long to check." A spoken form for the presentation is in the same place.
  - `[CONFLICT]` Narrowed on 2026-10-09, not closed. What is served today: "A review of uncommitted changes before they are pushed, and a review of a public pull request" (same file, §2). [`agentic-code-review-srs-v1.md`](../../../agentic-code-review-srs-v1.md) §2.2 still says "v1's primary user is the **author**, not the reviewer", and §1.1 that v1 "is an **engineering milestone, not the product**: the product claim — reducing a reviewer's queue on pull requests — is made in v3, when the same core reaches GitHub."
- **The problem in the customer's own words:**
  - `[MISSING: a quote from a reviewer the team interviewed itself]`. `Docs/Draft/problem-statrment-entrepreneurship` (on `main` only) §1 says the insights "come from a background study (secondary sources and a small first-hand anecdote, N=3), not from our own interviews."
  - Second-hand quotes that exist, all from [`chat_result_ai_pr_review_background_study.md`](../chat_result_ai_pr_review_background_study.md) A3 and A5 unless noted:
    - "looks like senior work wrapped around a missing authorization check": Nguyen, relayed by AIBuilderClub; a single case ([`001-chat_result_needs_vs_pains_analysis.md`](../001-chat_result_needs_vs_pains_analysis.md), Segment 5).
    - "gave up and just started hitting approve": a Reddit account relayed by AIBuilderClub, N≈1.
    - "the repetition, not the difficulty": Ullah, from the reviewer's seat.
    - "two AIs are not two independent reviewers": Ullah.
  - The team's own summary, not a customer's words: "Green no longer means right." (`Docs/Draft/problem-statrment-entrepreneurship` (on `main` only) §1). Since 2026-10-09 it is no longer a tagline or a slide headline, and since 2026-10-10 it no longer opens the elevator pitch.
- **Evidence (number, story or quote) + source:**
  - **Story.** "Correct-looking but context-wrong (legacy v1 auth; tests passed because both backends resolved)." Source: Ullah 2026, one team, first-hand; background study A4. The same account gives two more cases: "Silent convention drift (`"completed"` string vs `Status.Completed` enum)" and "Architecture erosion (controller → repo, skipping app layer; self-written tests pass against wrong shape)."
  - **Numbers.** All from the background study A2.

    | Figure | Value | Source and sample | Caveat stated in the study |
    |---|---|---|---|
    | Manual vs AI-assisted 30-day merge rate | 84.5% vs 32.7% | LinearB 2026: 8.1M PRs, ~4,800 teams, own platform data | Second-hand via AIBuilderClub 2026; cohort comparison, not a trend |
    | Reviewer pickup time | ~200 → ~1,050 min | Same | Same |
    | Diff size at P75 | 157 → 400+ LOC | Same | Same |
    | Feature-branch throughput YoY | +59% (largest ever) | CircleCI 2026: 28M+ runs, 22,000+ orgs | Measures CI runs, not AI authorship |
    | Median main-branch throughput | −7% | Same | Same |
    | Build success rate | 70.8%, 5-yr low | Same | Same |

  - **Evidence tier.** "'Clean-looking' code hides subtle omissions" is "Corroborated by 3 sources" and "entirely anecdotal" (A3). The study's own verdict: "No source is an independent, controlled measurement of the problem", and "No figure demonstrates AI *caused* the effect."
  - **Numbers added 2026-10-10.** Sources and caveats are in [`000-problem-and-audience.md`](../000-problem-and-audience.md) §6.

    | Figure | Value | Source and sample | Caveat |
    |---|---|---|---|
    | Median review duration, and pull requests merged without review, at teams with high AI adoption | +441.5% (about five times as long); +31.3% | Faros AI, 22,000 developers, through O'Reilly ([`004-market-study.md`](../004-market-study.md)). On the problem slide since 2026-10-14 | Vendor data; a correlation, not a cause. The primary report has not been read |
    | Review agents averaging under 60% signal | 12 of 13 | Chowdhury et al., MSR 2026: 3,109 pull requests with AI-generated code | A keyword-based measure, which the authors name as a limit |
    | Merge rate, reviewed only by agents vs only by humans | 45.20% vs 68.37% | Same | A comparison of two groups, not a cause |
    | Review comments addressed, human vs review agents | About 60% vs 0.9% to 19.2% | Earlier work cited by the same paper | Second-hand |
    | Reviewing done by core reviewers | 97.7%, by 182 people | Our measurement: ten public TypeScript repositories, 7,670 human pull requests, September 2026 | Public repositories stand in for company teams |
    | Pull requests a month, reviewed per core reviewer vs opened per core developer | 21.5 vs 13 (medians) | Same | Same |

### [Solution]

- **What the product or service does:**
  - **As specified for v1** ([`agentic-code-review-srs-v1.md`](../../../agentic-code-review-srs-v1.md) §1.2): "A local CLI reviewing a working tree, staged changes, or a branch range in a TS/JS repository"; "Execution of the project's tests and type-check, with a recorded evidence trail"; "A review agent isolated from any code-writing agent, grounded in that evidence and in a pattern library"; "A pattern library and a runnable regression harness reporting a catch rate". Each finding carries an evidence reference or is "explicitly marked **unverified**, with a reason" (FR-5.2c). v1 ships "at least five pattern rules" (FR-6.3a).
  - **As built today.** On branch `001-us2-no-finding-clean-review` (tip `b11d548`, 2026-09-28, not merged to `main`), `agentic-review review` reviews uncommitted changes in one model pass. The contract for that build, [`contracts/cli.md`](../../../../specs/001-walking-skeleton/contracts/cli.md), requires the output to say "No checks were run in this build." and "No related context was gathered in this build.", and states "`regression` arrives in 003." So today's build runs no tests and has no catch rate. This is taken from the commit history and the contract; the build was not re-run for this sheet.
- **How the customer uses it, step by step** (SRS §2.3 and [`contracts/cli.md`](../../../../specs/001-walking-skeleton/contracts/cli.md)):
  1. Install the tool. Distribution is specified as "A PyPI package with a console entry point, installed with `uv tool install` or `pipx`". `[MISSING: whether and when a release is published]`
  2. Supply a model-provider key in `AGENTIC_REVIEW_API_KEY`. The default provider is the NVIDIA NIM free tier.
  3. Run `agentic-review review` inside the repository. The scope is the working tree by default, or `staged`, or a `range` with `--base`.
  4. Read the findings in the terminal, or as JSON with `--json`. The exit code is 1 when at least one finding is blocking.

### [Market]

**Price proxy (decided 2026-10-08).** Until a pilot measures review volume per team and the hosted service's markup is set, yearly spend per customer is **rivals' entry price, not ours**. Every figure below that uses it is marked "proxy". Once those two numbers exist, yearly spend becomes price per review × reviews per team per month × 12, the customer unit changes from developers to teams, and TAM, SAM and SOM are recomputed in that unit. **Update, 2026-10-10:** our own price is now set, at $22 per seat per month, under CodeRabbit's $24 and with Greptile's $30 treated as an anomaly. At $22 the TAM is $9.6B and the SAM $1.8B to $2.9B (Calculated in [`0052-unit-economics-and-financials.md`](../0050-financial-planning/0052-unit-economics-and-financials.md) §7). The proxy range itself, which includes Greptile's price, was not changed.

- **All possible customers (count) + source:** 36.5M professional developers worldwide, early 2025. Source: SlashData, cited in [`004-market-study.md`](../004-market-study.md), confidence A. The study does not use GitHub's "180M+ developers", which counts accounts.
- **Customers you can actually reach (count) + source:** 7.0M–11.2M professional developers (SAM, the market study's calculation, confidence C): 36.5M × 68.8% who use TypeScript or JavaScript (JavaScript's share is the floor; Stack Overflow 2025, A) × 55% in pull-request teams (proxy: regular CI/CD use; JetBrains 2025, B, read from a search excerpt) × 50.6%–80.8% who use AI tools daily or at all (Stack Overflow 2025, A). At the proxy price this is $2.0B–$4.0B a year. GitHub reach is not applied, because the command-line tool works on any git repository.
- **Of whom reviewers, the audience:** 5.3M–8.5M (Calculated: 7.0M–11.2M × 76.4% who review code as part of their work; Stack Overflow 2019, 70,390 responses, confidence A but dated). The dollar figure is not recomputed, because the proxy price is per developer seat.
- **Yearly spend per customer, or price × how often they buy:** $24–30 per developer per month (proxy). Source: the entry tiers of CodeRabbit Essentials ($24, billed annually) and Greptile Pro ($30), from the market study, confidence A. Calculated: $24 × 12 = $288 and $30 × 12 = $360 per developer per year.
- **TAM (Calculated, proxy):** 36.5M × $288–360 = $10.5B–$13.1B per year, the market study's ceiling. It is an upper bound: it assumes every professional developer pays rivals' entry price for standalone review.
- **Reality check:** the category leader, CodeRabbit, reaches about 0.4% of professional developers (the market study's own calculation, confidence C: $40M ARR ÷ $288 per seat per year ≈ 139K seats).
- **Target share of reachable customers in the first years (%) + reason:**
  - Revenue SOM (founder, 2026-10-10): bottom-up from the pilot alone. Year 1: 6 pilot teams × 5 seats = 30 seats; half of them paying is 15 seats, $3,960 a year (Calculated). Six teams is the ask; the 50% paying share is the founder's assumption. Later years: `[MISSING: the measured share of pilot seats that pay, and the teams reachable after the pilot]`.
  - Counted in reviewers, the people the product serves: roughly 50–500 over the same three years, at an assumed 2–4 per active repository (the market study, low confidence). For company teams, whose repositories are private: 6 pilot teams × `[MISSING: reviewers per team, measured in the pilot]`.
  - Adoption target for the v3 GitHub Action: about 100–500 public repositories in three years, roughly a quarter of them active, matching the open-source review Actions in Sun et al. (the market study). It does not measure v1, whose command-line users leave no public trace; v1 adoption is the pilot teams.
  - Cap: the leader's ~139K paid seats are 1.5%–4.9% of the GitHub-reachable SAM, reached with $231M raised.
- The guide's sanity check, "SOM is reachable from current traction": the SOM is now the pilot itself, so it is reachable if the ask is met. Traction is still `[MISSING]`.

### [Business model]

- **Price per unit:**
  - Command-line tool: free. Source: founder, 2026-10-03.
  - Hosted review service: **$22 per seat per month**, the average of CodeRabbit's $24 and Graphite's $20, kept under CodeRabbit's price, with Greptile's $30 left out as an anomaly (founder's rule and limits, 2026-10-10; Calculated in [`0052-unit-economics-and-financials.md`](../0050-financial-planning/0052-unit-economics-and-financials.md) §2). A seat is taken to be a developer whose pull requests are reviewed in the month. Which rivals are averaged is our choice: Graphite is a workflow tool with only limited AI review at that price. Two earlier rules of the same day were replaced: per review at cost plus a markup, and $27 a seat. Each seat includes 150 reviews a month, pooled across the team (founder, 2026-10-10). `[MISSING: monthly or annual billing; what happens past the allowance]`
- **Cost per unit:** an estimated $1.14 to $5.81 per seat per month through 2026-12-31, and $2.19 to $8.95 from 2027-01-01, when the provider's prices double. It is 25 to 75 reviews, the average for a developer's month reviewed once or on every push, each $0.0418 in measured model tokens on Gemini 3.8 Flash plus a repository download of $0.0038 to $0.0357 (Calculated in [`0052-unit-economics-and-financials.md`](../0050-financial-planning/0052-unit-economics-and-financials.md) §3; the runs are in [`review-volume-report.md`](../0050-financial-planning/0051-cost-structure/review-volume-report.md) §1.3 and §3.4). `[MISSING: the cost of reviews above 160 changed lines, and anything measured on a hosted service]`
  - Known unit prices, from the same file §12. It labels them "USD list prices before taxes, discounts" and says to "verify with AWS Pricing Calculator before committing cash".

    | Resource | Billing unit | Unit price |
    |---|---|---|
    | Qwen3.8 27B input, on OpenRouter | 1M tokens | $0.0248 |
    | Qwen3.8 27B output | 1M tokens | $4.35 |
    | Qwen3.8 27B cache read | 1M tokens | $0.0198 |
    | OpenRouter Standard platform fee | inference/platform spend | 5.5% |
    | Network Load Balancer, eu-central-1 | NLB-hour | $0.027 ($19.71/month for one, before capacity units) |
    | NAT Gateway | gateway-hour | $0.052 ($37.96/month for one, before data processing) |
    | NAT Gateway data | GB processed | $0.052 |
    | Public IPv4 | IP-hour | $0.005 ($3.65/month each) |
    | EC2 | instance-hour | TBD |

  - `[CONFLICT]` **Which model the cost is based on.** The cost sheet prices Qwen3.8 27B at "$4.35 / 1M output tokens". [`model-comparison.md`](../0050-financial-planning/0051-cost-structure/model-comparison.md) says to "Deploy `Qwen3.8 27B` exclusively for workloads requiring vision-language processing or document context exceeding 131K tokens", and lists gpt-oss-20b at "$0.018 / $0.09" and gpt-oss-120b at "$0.03 / $0.17". The built code defaults to the NVIDIA NIM free tier with a placeholder model. Left open on purpose on 2026-10-09: the model and its price are treated as variables while the product is experimental, and cost per review is a formula with price scenarios in [`review-volume-report.md`](../0050-financial-planning/0051-cost-structure/review-volume-report.md). **Settled as a working assumption on 2026-10-10:** the founder named Gemini 3.8 Flash, which neither sheet covers, at $0.75 input and $3.75 output per 1M tokens through 2026-12-31 and $1.50 and $7.50 after. The model and its price remain parameters of the formula.
  - `[CONFLICT]` **Fixed or variable infrastructure.** The pricing template defines "F = Fixed monthly infrastructure" and "Break-even Customers = F / [P - (C × R)]". The cost sheet treats every resource as usage ("we should not write 'Elastic IP = $3.65/month' as a fixed cost") and passes the whole cost through. **Read together on 2026-10-10, pending the founder's confirmation:** what a review uses counts in the cost of a seat, and what runs all the time is the fixed cost the margin must cover, an estimated $96.36 a month with one assumed small server ([`0052-unit-economics-and-financials.md`](../0050-financial-planning/0052-unit-economics-and-financials.md) §5).
- **Margin per unit + type (gross or contribution):** $16.19 to $20.86 per seat per month through 2026, which is 74% to 95% of the price; 59% to 90% from 2027. A contribution margin: the price less the estimated cost of serving the seat, before always-on infrastructure and anyone's time ([`0052-unit-economics-and-financials.md`](../0050-financial-planning/0052-unit-economics-and-financials.md) §4).
- **Revenue streams:** the hosted review service. Source: [`003-business-model-canvas.md`](../003-business-model-canvas.md) §5, "Open core, decided 2026-10-03".
  - `[MISSING: what the hosted service gives a customer that the free tool does not]`. The founder took this note off the business-model slide on 2026-10-10; it stays open here. The canvas §2 says this "is not stated", and [`competitive-landscape.md`](../competitive-landscape.md) notes that rivals already offer free hosted tiers.
  - `[CONFLICT]` **The paid product is not designed, and the engineering record rules it out.** The requirement catalogue [`agentic-code-review-srs.md`](../../agentic-code-review-srs.md) §2.2 calls a hosted GitHub App "out of scope entirely". ADR-0005: "The product is deliberately **not** a hosted service." SRS §2.1: "It operates no server, holds no remote state". [`feature-inventory.md`](../feature-inventory.md) §2 rates a hosted app "Very High" complexity. The catalogue carries a note of the decision; no requirement, version or ADR exists for the service.

### [Traction]

- **Sales, users, pilots or signed letters of intent, each with a date:** `[MISSING]`. The canvas records none: "no evidence anyone would pay", and today's user is "the change author reviewing their own work, plus the contributors building the system."
- **Build progress. This is not traction; label it as progress wherever it is shown.** Source: git history of this repository.
  - 2026-09-17: commit "feat(review): review uncommitted changes in one model pass", on the branch named above.
  - 2026-09-26: "build: scaffold the agentic-review package, lockfile and CI" merged to `main` (pull request #11).
  - 2026-10-09: commit "feat(changeset): review a public pull request and a named branch range".
  - 2026-10-10: feature 001 has 93 tasks ticked and 34 open in `specs/001-walking-skeleton/tasks.md` on that branch. Calculated: 93 + 34 = 127 tasks. On 2026-09-28 it was 78 and 31.
  - The v1 specification lists 16 acceptance criteria, AC-1 to AC-16 (SRS §6).
  - Not built yet: test execution and the regression harness, so there is no measured catch rate.
  - Measured on 2026-10-10: five review runs on Gemini 3.8 Flash, of two small tRPC pull requests. Each took one model call and 76 to 153 seconds, and none reported a finding.

### [Competition]

- **Alternatives customers use today, and why customers would choose you over each.** Prices are a September 2026 snapshot from [`tool-reference.md`](../../tool-reference.md); the reasons are quoted from [`competitive-landscape.md`](../competitive-landscape.md).

  | Alternative | What it is | Entry price | Why choose us, as the landscape states it |
  |---|---|---|---|
  | CodeRabbit | Hosted AI reviewer; "The market-share leader" | $24/developer/month (Essentials, billed annually) | "Our edge is openness, zero cost, and auditability — not breadth." |
  | Greptile | Hosted AI reviewer; "The closest match to our architectural thesis" | Free for one active developer; $30 per seat per month (Pro) | Its "engine is a hosted black box. Ours is inspectable and forkable end to end." |
  | Qodo | Review and governance platform with an open-source lineage (PR-Agent) | "Uses a credit-based system; specific tiers are on the pricing page (not enumerated here)" | `[MISSING: a reason specific to Qodo; the landscape gives none]` |
  | Claude Code Review | Managed multi-agent reviewer | "Each review averages **$15–25**" | "we verify **deterministically**, by running the real test suite, where they verify **agentically**" |
  | Danger / DangerJS | CI process linter, rule-based, no model | Free (MIT) | A complement: "Danger checks that you followed the process; Agentic Code Review checks whether the code is actually correct." |
  | Graphite | Stacked-diffs workflow with an AI reviewer | $20/user/month (Starter) | A complement: it attacks the problem "from the **input side** (make PRs smaller)" |
  | Manual peer review, no tool | The status quo | none | Implied by the problem definition; the landscape does not analyse it |

  - `[CONFLICT]` **Qodo's price.** [`pr-agent-pricing-template.md`](../0050-financial-planning/pr-agent-pricing-template.md) gives an entry price of "$30" per "/team/mo" and an overage of "$0.012 / credit pooled across the team", with no source; the tool reference gives no figure.
  - "zero cost" in the CodeRabbit row describes the open-source tool only; the landscape's business-model caveat of 2026-10-03 says so.
  - **Re-checked 2026-10-10.** The reasons in the table are the landscape's wording of September. Its re-check withdrew the Claude Code Review row's reason: rivals do not verify with a model alone, and our test run is specified, not built. What the re-check leaves as ours: nothing is dropped silently, the review reports its own gaps, and the engine can be read. Price is a small difference, not a reason to choose us: $22 a seat is $2 under CodeRabbit ([`competitive-landscape.md`](../competitive-landscape.md), "Differentiator re-check").
  - `[MISSING: a profile of Cubic]`. Its account reviewed 2,064 of the 7,670 human pull requests in our ten-repository sample, more than CodeRabbit (521) and Greptile (901) together; it lists $40, $99 and $200 per developer per month.
- **Limits the landscape states about us** (keep them ready for questions):
  - "Our v1 is roughly CodeRabbit's entry tier against a product with a massive install base."
  - "A free NIM-tier model without agentic verification is very likely noisier than a frontier-model-with-verification reviewer."
  - "'Execution-backed' only adds value on repositories with a runnable test suite."
  - Until v3 "the project competes only where every tool in this document also offers a local mode".
  - On the paid tier: "What it adds is not stated yet."

### [Team]

- **The team.** Supplied by the founder on 2026-10-10, with each person's level added later the same day.

  | Name | Level |
  |---|---|
  | Mohammed Gamal Kenawy | Team leader; junior software engineer |
  | Yahia Ahmed Hamed | Junior software engineer |
  | Mahmoud Ayman Mahmoud | Junior software engineer |
  | Abderhman Ehab | Junior software engineer |
  | Mohamed Ali Mahmoud | Senior Oracle developer |
  | Ahmed Shahin | Sales manager |

  - The founder's words: "We're all entry level, junior software engineers, except for the last 2 members." An earlier note the same day said all six work as developers.
  - The guide asks for relevant skills and experience, not titles. What is recorded here is each person's level.
  - The guide asks for 2–4 people on the slide; the team is six, and all six are shown.
  - Names are written as supplied. `[MISSING: confirm the spelling "Abderhman"; the address supplied with it spells the name differently]`
  - The git history has one author, Mohammed Kenawy.
  - The members' email addresses were supplied and are kept out of the repository, except the contact address below.

### [Financials]

- **Revenue and costs for years 1, 2 and 3:** theoretical, by the founder's decision of 2026-10-10, because there is no traction to forecast from. It applies CodeRabbit's capital efficiency to each $1M invested: no revenue in year 1, about 313 seats and $82,500 a year by year 2, and 986 seats and $260,400 a year by year 3, against a serving cost of $8,200 to $33,600 and $25,900 to $106,000 ([`0052-unit-economics-and-financials.md`](../0050-financial-planning/0052-unit-economics-and-financials.md) §6). `[MISSING: seats on the hosted service, and the investment to assume for us]`
- **Break-even point:** 5 to 6 seats cover an estimated $96.36 a month of always-on infrastructure. It is the pricing template's formula, "Break-even Customers = F / [P - (C × R)]", with a seat as the customer, and it covers infrastructure only, not people ([`0052-unit-economics-and-financials.md`](../0050-financial-planning/0052-unit-economics-and-financials.md) §5).
- **Key assumptions behind the forecast:** a price equal to the average of two rivals' entry prices; a seat that opens 25 pull requests a month, the average; Gemini 3.8 Flash at list price; one model call per review; a median-size pull request standing for all; one assumed small server on AWS; no salaries ([`0052-unit-economics-and-financials.md`](../0050-financial-planning/0052-unit-economics-and-financials.md) §8). The earlier money figure remains a spending limit, not a forecast: "Model-provider access on a free tier, or a single plan of about $20/month" (canvas §6).

### [Ask and use of funds]

- **The ask (exact amount or exact action):** 6 teams run the tool on their real changes for 8 weeks, starting 1 January 2027 (founder, 2026-10-10). Since 2026-10-10 the pitch does not name TypeScript; the tool still reviews only TypeScript and JavaScript, so a team that comes forward must have such code.
- **Split by category (% or amount):** not applicable. No funds are requested.
- **Milestone the ask reaches + target date:** 1,000 pull requests reviewed, with reviewers acting on at least 20% of the findings, by 28 February 2027 (founder, 2026-10-10, on our suggestion). The volume is set below what six teams of five are expected to open, about 1,380 pull requests in eight weeks; the 20% is just above the 19.2% that research reports as the top of the range for AI review comments.
- **What a pilot can measure.** These are the blanks in [`pr-agent-pricing-template.md`](../0050-financial-planning/pr-agent-pricing-template.md) §1 and §3: cost per review; PRs per month; average review time; number of reviewers; AI-generated PR percentage; rework frequency; time spent on rework; current code-review tooling; current monthly spending; perceived pain; willingness to pay; price sensitivity.
- **Readiness.** How a pilot team installs the build is not part of the pitch (founder, 2026-10-10). The working build is on an unmerged branch, and the repository has no LICENSE file although FR-9.1 requires the system to "ship with README, LICENSE, and CLI usage documentation".

### [Close]

- **Contact details to show on screen:** mohammedgamal2002@gmail.com (the team leader, supplied by the founder on 2026-10-10) and the repository, `github.com/MoKenawy/Pull-request-Reviewer`.

### [ASSETS]

| File | What it shows | Usable as is? |
|---|---|---|
| [`agentic-code-review-srs-v1.md`](../../../agentic-code-review-srs-v1.md) §2.1 | Pipeline flowchart, eight steps (mermaid) | Yes, once rendered to an image |
| [`agentic-code-review-srs-v1.md`](../../../agentic-code-review-srs-v1.md) §1.1 | The two commands, `review` and `regression` (mermaid) | Yes, once rendered |
| [`competitive-landscape.md`](../competitive-landscape.md) | Positioning summary table, six rows by five tools | Too dense for a slide; cut it to two rows |
| [`003-business-model-canvas.md`](../003-business-model-canvas.md) | Canvas at a glance (mermaid) | Background only |
| [`pr-review-agent-Component-design.drawio`](../../../pr-review-agent-Component-design.drawio) | Component design diagram | Needs exporting to an image |
| [`render_agent_graphs.ipynb`](../../../../notebooks/render_agent_graphs.ipynb) | Renders the agent graphs | Technical; background only |
| [`assets/logo-a-evidence.svg`](./assets/logo-a-evidence.svg), [`logo-b-brackets.svg`](./assets/logo-b-brackets.svg), [`logo-c-lens.svg`](./assets/logo-c-lens.svg) | Three prototype logos, made on 2026-10-10 in the deck's colours | Prototypes. A is on the deck's first and last slides; none is a final logo |
| `[MISSING: screenshot of a real agentic-review review run]` | The product shown, which the guide asks for on the solution slide | |
| `[MISSING: team photos]` | Optional | |

---

## Kept out on purpose

| What | Why |
|---|---|
| Every figure in [`dummy-pricing-example.md`](../0050-financial-planning/dummy-pricing-example.md) ($0.29 per review, $149.00 per team, $3,007.50 of value, 5 break-even customers, its competitor prices) | Its first line says it is "populated with realistic, coherent hypothetical numbers" |
| AIDev: "61.38%" of agent PRs with no recorded review | The study marks it "**arXiv ID unverified / future-dated**" |
| A latency threshold of "roughly 10–30 seconds" | SRS §2.4 withdrew it: "an estimate that nobody measured" |
| Graphite's "less than 3% of AI comments rated unhelpful" | A vendor claim with "no methodology/N" |
| Ullah's "−35% burden month one" and "90–95%" caught before opening | "unbaselined N=1" |
| The two charts in `0051-cost-structure/` (`1690307118-4.webp`, `1690307126-5.webp`) | Graphite's own charts of 2022 pull-request sizes; third-party, and not about AI-written code |
| `Pull-request-decisions-explained-zhang et al.pdf` | Not read: the file is password-protected |
