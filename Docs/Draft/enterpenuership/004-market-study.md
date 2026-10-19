# Agentic Code Review — Market Study

Oct 8, 2026 · @Mohammed

## Gartner outlook

Gartner's forecasts point one way: almost every enterprise engineer will use AI coding tools by 2028, and checking the output is moving to automated platforms. Costs and defect risk rise along the way.

| By | Gartner prediction | What it means for AI code review | Source | Confidence |
| --- | --- | --- | --- | --- |
| 2027 | Over 65% of engineering teams using agentic coding will treat IDEs as optional, moving control, governance and validation to automated platforms | Review moves out of the editor and into automated pipelines, where a GitHub Action runs | [Gartner press release, 20 May 2026](https://www.gartner.com/en/newsroom/press-releases/2026-05-20-gartner-says-the-market-for-enterprise-ai-coding-agents-is-entering-a-new-phase-of-expansion-and-competitive-realignment) | A |
| 2028 | 90% of enterprise software engineers will use AI code assistants, up from under 14% in early 2024 | The volume of AI-written code that needs review keeps growing | Gartner Magic Quadrant for AI Code Assistants (Sep 2025), as quoted by [GitHub](https://github.blog/ai-and-ml/github-copilot/gartner-positions-github-as-a-leader-in-the-2025-magic-quadrant-for-ai-code-assistants-for-the-second-year-in-a-row/) | B, quoted by a vendor rated in the report |
| 2028 | AI coding costs will exceed the average developer's salary, driven by token use and consumption-based pricing | Buyers will favour tools with predictable costs and cheap-model options | [Gartner press release, 24 Jun 2026](https://www.gartner.com/en/newsroom/press-releases/2026-06-24-gartner-predicts-ai-coding-costs-will-surpass-average-developer-salary-by-2028-as-token-consumption-surges) | A |


Gartner publishes no size for the AI code review market; these forecasts give direction, not dollars. Its cost advice is to send simple, high-frequency tasks to smaller models and set token limits, which supports a review tool built on one low-cost model with a capped number of comments.

## Executive summary

No trustworthy published figure exists for the size of the AI code review market. The defensible picture is a large theoretical ceiling and very low paid adoption today.

| Layer | Figure | Basis | Confidence |
| --- | --- | --- | --- |
| Theoretical ceiling (TAM) | $10.5B–$13.1B per year | 36.5M professional developers × $24–30 per seat per month | C — our calculation |
| Category leader revenue | \~$40M ARR (Apr 2026) | Sacra estimate for CodeRabbit | B — investor research |
| Leader growth | >5x revenue year over year (Aug 2026) | CodeRabbit Series C announcement | A — self-reported |
| Leader's paid reach | \~0.4% of professional developers | $40M ÷ $288 per seat per year ≈ 139K seats | C — our calculation |
| Pure-play category ARR | \~$100M–250M (mid-2026) | Leader revenue plus smaller rivals | C — our estimate, low confidence |

- **Capital is concentrating.** CodeRabbit reached a $1.5B valuation (Aug 2026), Qodo raised a $70M Series B (Mar 2026), and Cursor acquired Graphite (Dec 2025).
- **Bundling is the main threat to standalone tools.** GitHub Copilot includes pull request review in its $10-per-month Pro plan.
- **The audience is the reviewer (2026-10-10).** The layers below count developer seats, which is what rivals charge for. About three quarters of developers review code, and the obtainable market is counted in reviewers.
- **Signal quality is the open gap, not speed.** Peer-reviewed evidence shows pull requests reviewed only by AI merge less often than those reviewed only by humans (45.2% vs 68.4%), and most AI review comments are noise.

## Source policy

Every figure in this study comes from a source in one of five trusted classes, and each carries a confidence label.

| Label | Meaning | Examples used |
| --- | --- | --- |
| A | Primary or peer-reviewed: official disclosures, pricing pages, datasets, papers | CodeRabbit releases, GitHub, SlashData, MSR 2026, arXiv |
| B | Reputable secondary: established press, named investor research | TechCrunch, Fortune, Globes, SiliconANGLE, Sacra, O'Reilly |
| C | Our own calculation from A/B inputs, with assumptions stated | Bottom-up TAM, penetration, category ARR |

Company figures are marked **self-reported** even when the source is primary. Vendor-funded research is used only as context and is labelled as vendor-funded.

**Excluded sources**

| Source | Reason excluded |
| --- | --- |
| Market Intelo, The Business Research Company, Virtue Market Research, Intel Market Research | Report mills; no published methodology. Intel Market Research's page states two different sizes and growth rates for the same market |
| Research & Markets, Meticulous, Value Market Research, Data Bridge ("AI code tools") | Scope covers all AI coding tools; code review is not sized separately |
| 360iResearch | Seen only quoted second-hand by an unreliable blog |
| Mordor Intelligence (Agentic AI Development Platform) | Reputable firm, wrong market: agent orchestration platforms, 71.68% of revenue from financial services; code review is not in scope |
| Ideaplan, ai2.work, DEV / aicodereview.cc, Zylos, BytePlus, iLink | Blogs with no traceable data; sources of the unverified "$420M" and "$400–600M" category figures |
| arr.club, ToolJunction, EveryDev, StartupHub, FastAIJobs, VCBacked | Aggregators with conflicting, unsourced funding and revenue figures (e.g. Greptile funding listed from $3.9M to $45.5M) |
| Morph, Pengu Press | Unattributed comparison and summary content |
| Vendor benchmark claims (Martian leaderboard as cited by vendors) | CodeRabbit and Qodo each claim first place; Qodo coverage cites two different F1 scores (50.3% and 64.3%) |

## Market definition

This study sizes the **narrow segment**: tools whose main job is AI review of pull requests. Published estimates disagree mostly because each one mixes these three segments differently.

| Segment | What it includes | Example players | Treatment here |
| --- | --- | --- | --- |
| Narrow: AI PR review | Standalone AI agents that review pull requests | CodeRabbit, Qodo, Greptile, Graphite | Sized |
| Bundled | AI review included inside a broader coding assistant | GitHub Copilot, Cursor (owns Graphite) | Competitive pressure; revenue not separable |
| Adjacent | Code quality and security scanning tools adding AI | Static analysis and SAST vendors | Not sized |

Agentic AI development platforms (agent orchestration for enterprises) are a different market. They are excluded even though the name looks similar.

## Market sizing

The theoretical ceiling is **$10.5B–$13.1B per year**, but the category leader reaches only about **0.4%** of professional developers. Both figures are our calculations (C) from the inputs below.

**Inputs**

| Input | Value | Source | Confidence |
| --- | --- | --- | --- |
| Professional developers worldwide | 36.5M (early 2025) | [SlashData](https://www.slashdata.co/post/global-developer-population-trends-2025-how-many-developers-are-there) | A |
| CodeRabbit Essentials / Team / Advanced | $24 / $48 / $72 per developer per month, billed annually | [CodeRabbit pricing](https://www.coderabbit.ai/pricing) | A |
| Greptile Pro | $30 per seat per month; free for qualifying OSS projects | [Greptile pricing](https://www.greptile.com/pricing) | A |
| GitHub Copilot Pro (PR review included) | $10 per month | [GitHub Copilot plans](https://github.com/features/copilot/plans) | A |
| Graphite Starter / Team (AI reviews included; unlimited from Team) | $20 / $40 per user per month, billed annually | [Graphite pricing](https://graphite.com/pricing) | A |
| CodeRabbit ARR | \~$40M (Apr 2026) | [Sacra](https://sacra.com/c/coderabbit/) | B |

GitHub's "180M+ developers" counts accounts, including students and inactive users. It is not used for sizing.

**Calculation**

1. **Ceiling (TAM):** 36.5M × $24–30 × 12 months = $10.5B–$13.1B per year, using the entry-tier price of the two pure-plays.
2. **Leader seats:** $40M ÷ ($24 × 12) ≈ 139K seats ≈ 0.4% of professional developers. At the $48 Team tier, this falls to ≈ 69K seats.
3. **Pure-play category ARR:** CodeRabbit at \~$40M in April 2026, growing more than 5x per year, implies roughly $60M–75M by August 2026. Qodo, Greptile and Graphite are each smaller. This gives a category estimate of **\~$100M–250M**, low confidence.

**Caveats.** The ceiling assumes every professional developer pays for standalone review, which overstates the realistic market. Not all developers work in pull-request teams, and bundled review (Copilot at $10) sets a low price ceiling. It also prices every developer at rivals' per-seat rates, not at this project's price, and counts all professional developers, not the TypeScript/JavaScript teams this project targets, so it is not this project's serviceable market. Treat the TAM as an upper bound and the seat and ARR figures as the reality check.

**Price used as a proxy (2026-10-08).** The project uses this entry-tier range, $24–30 per developer per month, as its stand-in for yearly spend per customer in its pitch and market figures, until a pilot measures review volume per team and the markup on the hosted service is set. Then yearly spend becomes price per review × reviews per team per month × 12, and the market layers are recomputed in teams rather than developers.

**Our own price (2026-10-10).** The founder set the hosted service's price as a monthly price per seat, from the average of rivals' prices, with two limits: it must stay under CodeRabbit's $24, and Greptile's $30 is treated as an anomaly. That gives $22, the average of CodeRabbit's $24 and Graphite's $20. At $22 the TAM is $9.6B and the SAM $1.8B to $2.9B (C; [`0052-unit-economics-and-financials.md`](./0050-financial-planning/0052-unit-economics-and-financials.md) §7). The proxy range above still runs from $24 to $30 and still includes Greptile; whether to narrow it is not decided. The layers are still counted in developers, not yet in teams.

### Serviceable market (SAM)

The project can serve roughly **7.0M–11.2M professional developers**, or 19–31% of the TAM base. That figure comes from three shares applied to the 36.5M professional developers (C).

| Share | Low | High | What is measured | Source | Confidence |
| --- | --- | --- | --- | --- | --- |
| TypeScript/JavaScript developers | 68.8% | 68.8% | Professionals who did extensive work in JavaScript in the past year. The customer uses TypeScript **or** JavaScript, so the share is at least the larger of the two; JavaScript's 68.8% is the floor for both ends (TypeScript alone: 48.8%) | [Stack Overflow 2025](https://survey.stackoverflow.co/2025/technology) | A |
| Pull-request teams | 55% | 55% | Proxy: developers who regularly use CI/CD tools. No survey asks about PR-based review directly | JetBrains Developer Ecosystem 2025, as cited by the [JetBrains TeamCity blog](https://blog.jetbrains.com/teamcity/2026/03/best-ci-tools) (page not readable; figure seen in search excerpt) | B, proxy |
| AI-tool use | 50.6% | 80.8% | Professionals using AI tools daily (low) or at any frequency (high) | [Stack Overflow 2025](https://survey.stackoverflow.co/2025/ai) | A |

**Calculation**

1. **Low:** 36.5M × 68.8% × 55% × 50.6% ≈ 7.0M developers.
2. **High:** 36.5M × 68.8% × 55% × 80.8% ≈ 11.2M developers.
3. **In dollars:** at $24–30 per seat per month, the proxy price (see the note above), this is about $2.0B–$4.0B per year.

**Caveats**

- Multiplying the shares assumes they are independent. The TypeScript figures suggest they are positively correlated: among professionals who use AI, 51.4% use TypeScript, against 48.8% overall. The product therefore probably understates SAM slightly.
- GitHub reach is not applied. v1 is a local command-line tool that works on any git repository, so GitHub does not limit it. The GitHub Action arrives in v3, and GitHub reach (41%–80.5%) is applied to it as a SOM filter below.
- JavaScript use includes front-end scripting, which is not the same as maintaining a TypeScript/JavaScript repository.
- Both surveys are self-selected; the CI/CD survey has only 805 respondents.

**Next step:** Stack Overflow publishes its 2025 raw responses under an open licence. Cross-tabulating language and AI use in that file would give a joint share for two of the three filters, removing the independence assumption.

### The reviewer among those developers

Added on 2026-10-10. The project's one audience is now the reviewer ([`000-problem-and-audience.md`](./000-problem-and-audience.md)). The layers above count developers because that is what rivals charge for: a seat is a developer whose pull requests get reviewed. This section says how many of those developers are reviewers, and the obtainable market below is counted in reviewers.

| Measure | Value | Source | Confidence |
| --- | --- | --- | --- |
| Review code as part of their work | 76.4% (68.8% because they see value in it, 7.6% because they were told to); 23.6% do not | [Stack Overflow 2019](https://survey.stackoverflow.co/2019/), 70,390 responses. The latest edition we found that asks | A, dated |
| Core developers who also reviewed in the month | 69.2% reviewed at least one pull request, 59.7% at least four | Ten public TypeScript repositories, September 2026 ([`review-volume-report.md`](./0050-financial-planning/0051-cost-structure/review-volume-report.md) §2.5) | C, from A |
| Reviewing done by the top fifth of reviewers | 73% | Same | C, from A |

**Calculation**

1. **Reviewers in the SAM:** 7.0M–11.2M × 76.4% ≈ 5.3M–8.5M.
2. **Dollars are not recomputed.** The proxy price is per developer seat, so the SAM stays $2.0B–$4.0B. If the hosted service is priced per reviewer or per review, this layer is recomputed in that unit.

**Caveats**

- The survey predates AI coding tools, and it covers everyone who answered, not only developers in pull-request teams, where the share who review is probably higher.
- Our own sample is public repositories, and its two figures sit a little under the survey's rather than confirming it.
- Head count understates how uneven the work is: a fifth of the reviewers do about three quarters of the reviewing, so the people who feel the problem most are fewer than these totals.

### Obtainable market (SOM)

A realistic three-year adoption target for the **v3 GitHub Action** is **about 100–500 public repositories**, of which roughly a quarter would be actively used. Counted in reviewers, the people the product serves, that is **roughly 50–500** (low confidence; step 3). No open-source AI review Action in the published research has passed 460 repositories (C, based on A).

This target applies to the Action, not to v1. v1 is a local command-line tool and leaves no public trace such as a workflow file, so code search cannot count its users; its adoption is measured by the pilot teams instead.

**Step 1: the market the v3 Action can technically reach**

| Step | Low | High | Basis | Confidence |
| --- | --- | --- | --- | --- |
| SAM (above) | 7.0M | 11.2M developers | Three shares × 36.5M professional developers | C |
| × GitHub reach | 41% | 80.5% | Organisations using GitHub Actions ([JetBrains State of CI/CD 2025](https://blog.jetbrains.com/teamcity/2025/10/the-state-of-cicd/)); professionals using GitHub regularly ([Stack Overflow 2025](https://survey.stackoverflow.co/2025/technology)) | A |
| = GitHub-reachable SAM | 2.9M | 9.0M developers |  | C |
| × review code as part of their work | 76.4% | 76.4% | Stack Overflow 2019 (the section above) | A, dated |
| = GitHub-reachable reviewers | 2.2M | 6.9M reviewers |  | C |

**Step 2: what comparable tools actually achieved**

| Open-source AI review Action | Stars | Public repos configuring it | Repos with ≥50 PRs |
| --- | --- | --- | --- |
| anc95/ChatGPT-CodeReview (most adopted) | 4.1k in Jan 2025; [4.5k in Oct 2026](https://github.com/anc95/ChatGPT-CodeReview) | 460 | 114 |
| coderabbitai/ai-pr-reviewer (CodeRabbit's own open-source Action) | 1.6k | 108 | 27 |
| mattzcarey/code-review-gpt | 1.7k | 37 | 11 |
| All 16 Actions studied | — | 718 | 178 |

Source: [Sun et al., arXiv 2508.18771](https://arxiv.org/abs/2508.18771), repositories found via GitHub code search in January 2025 (A). Qodo's open-source [PR-Agent](https://github.com/qodo-ai/pr-agent) (13.3k stars) was not in the study and publishes no usage count.

**Step 3: SOM scenarios over three years**

| Scenario | Public repos | Active repos (≈25%) | Reviewers, at 2–4 per active repo | Basis |
| --- | --- | --- | --- | --- |
| Base | \~100 | \~25 | \~50–100 | Matches CodeRabbit's own open-source Action (108 repos) |
| Stretch | \~500 | \~125 | \~250–500 | Matches the most-adopted Action in the study (460 repos) |

The 25% active ratio comes from the most-adopted Action: 114 of its 460 repositories had at least 50 PRs.

**Reviewers per active repository (C, low confidence).** The 2–4 comes from the five smaller repositories in our own sample, which have 0 to 4 core reviewers each; the five larger have 10 to 75 and are not typical of a repository adopting an open-source Action. It is an assumption until adopters can be counted.

**What this count leaves out.** The audience is the reviewer in a company team, and most of those work in private repositories that no public count can see. For them the obtainable market starts with the pilot: 6 pilot teams × `[MISSING: reviewers per team, measured in the pilot]`.

**Benchmark against the leader.** CodeRabbit's \~139K paid seats equal about 1.5%–4.9% of the GitHub-reachable SAM. It reached that with $231M raised and a full team, so it is a ceiling for funded players, not a target for this project.

**Revenue SOM (decided 2026-10-10): bottom-up from the pilot alone.** The founder chose to count the obtainable market only from customers the project can name, and to say that later years wait for the pilot. Year 1 is the pilot teams: 6 teams × 5 seats = 30 seats, of which half are assumed to pay, 15 seats, × $264 a year = **$3,960 a year** (C). Six teams is the pilot ask, set on 2026-10-10; the 50% paying share is the founder's assumption, and no pilot has measured it. Five seats a team is the team size these documents use as an illustration, not a measurement. Years 2 and 3 are `[MISSING: the measured share of pilot seats that pay, and the teams reachable after the pilot]`. The 50–500 target above stays as the adoption target for the v3 Action; it is not used as the revenue SOM.

**Caveats**

- Code search only sees public repositories, so private usage is invisible and these counts are a floor.
- Stars are not usage. The most-adopted Action grew only from 4.1k to 4.5k stars in about 21 months, which suggests slow organic growth in this niche.
- The 25% active ratio comes from a single Action.

## Category leader: CodeRabbit

CodeRabbit's revenue grew roughly 8x in the year to April 2026, to an estimated $40M ARR (Sacra estimate, B). In August 2026 the company reported more than 5x revenue growth year over year (self-reported, A), and investors valued it at $1.5B. It is the strongest available proof that buyers pay for AI review.

| Date | Event | Key figures | Source | Confidence |
| --- | --- | --- | --- | --- |
| Aug 2026 | Series C | $143M at $1.5B valuation; revenue >5x YoY; 2M+ reviews per week; 17,000+ customers; 150,000 OSS projects; $10M+ pledged to keep OSS free for 12 months | [CodeRabbit blog](https://www.coderabbit.ai/blog/introducing-agentic-change-management) | A, self-reported |
| Apr 2026 | Revenue estimate | \~$40M ARR, \~700% YoY from \~$5M in Apr 2025 | [Sacra](https://sacra.com/c/coderabbit/) | B |
| Sep 2025 | Series B | $60M led by Scale Venture Partners; $88M total raised; 10x revenue YoY; 8,000+ paying customers; 100,000+ OSS projects | [Business Wire](https://www.businesswire.com/news/home/20250916401011/en/CodeRabbit-Raises-%2460M-Series-B-Following-Unprecedented-Growth-as-Vibe-Coding-Triggers-a-Need-for-New-Code-Quality-Standards) | A, self-reported |
| Sep 2025 | Valuation and multiple | $550M valuation; \~$15M ARR; \~36.7x forward revenue | [Sacra](https://sacra.com/research/coderabbit-vs-github/), [TechCrunch via Yahoo](https://finance.yahoo.com/news/cursor-continues-acquisition-spree-graphite-215122810.html) | B |

**Reading the numbers carefully**

- CodeRabbit has never disclosed ARR. The dollar figures are Sacra estimates; the growth multiples are the company's own.
- The Series B counted "paying customers"; the Series C counts "customers". The 8,000 → 17,000 change is not like-for-like.
- The $1.5B valuation is roughly 20–25x our estimated ARR of $60M–75M at the time (C). It reflects investor conviction, not market size.

## Competitive landscape

Three well-funded pure-plays compete with two platform owners who bundle review into products developers already pay for.

| Player | Type | Latest event | Funding / valuation | Price | Source | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| CodeRabbit | Pure-play | Series C, Aug 2026 | $143M at $1.5B | $24–72 per developer per month | [CodeRabbit](https://www.coderabbit.ai/blog/introducing-agentic-change-management) | A |
| Qodo | Pure-play | Series B, Mar 2026 | $70M led by Qumra Capital; $120M total | Not checked | [Globes](https://en.globes.co.il/en/article-1001538970) | B |
| Greptile | Pure-play | Series A, 2025 | $25M; Benchmark reportedly led at \~$180M valuation | $30 per seat per month; free for qualifying OSS | [TechCrunch](https://techcrunch.com/?p=3029287), [Greptile pricing](https://www.greptile.com/pricing) | B / A |
| Graphite | Acquired by Cursor | Dec 2025 | Last valued at $290M ($52M Series B); price undisclosed, reported well above that | $20–40 per user per month, AI reviews included | [Fortune](https://fortune.com/2025/12/19/cursor-ai-coding-startup-graphite-competition-heats-up/), [TechCrunch via Yahoo](https://finance.yahoo.com/news/cursor-continues-acquisition-spree-graphite-215122810.html) | B |
| GitHub Copilot | Bundled | PR review in all paid plans | Microsoft | $10 (Pro) to $100 (Max) per month | [GitHub](https://github.com/features/copilot/plans) | A |

- **Qodo** reports enterprise customers including Walmart, NVIDIA, Red Hat and Ford, and an 11x larger enterprise footprint in 2025 ([Dealroom](https://dealroom.co/news/127108-qodo-raises-70m-to-govern-the-ai-code-flood-as-enterprises-lose-trust-in/); self-reported).
- **Graphite** continues as a standalone product under Cursor, which also runs its own reviewer, Bugbot ([SiliconANGLE](https://siliconangle.com/2025/12/19/cursor-acquires-ai-code-review-startup-graphite/)).
- **GitHub** lets organisations enable Copilot review on every pull request, including from contributors without a Copilot seat, billed as usage credits. This undercuts per-seat pricing for occasional contributors.

## Demand drivers

AI made writing code cheap but left reviewing it as slow as before, so review is now the bottleneck. Several independent measurements show this.

| Signal | Figure | Source | Confidence |
| --- | --- | --- | --- |
| Pull requests merged on GitHub | 43.2M per month in 2025, +23% YoY | [GitHub Octoverse 2025](https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/) | A |
| Median review duration at high-AI-adoption teams | +441.5% | Faros AI (22,000 developers, 4,000 teams), via [O'Reilly](https://www.oreilly.com/radar/agentic-code-review/) | B, vendor data |
| PRs merged with zero review | +31.3% | Faros AI, via O'Reilly | B, vendor data |
| Code churn / incidents per PR | +861% / +242.7% | Faros AI, via O'Reilly | B, vendor data |
| Raw output vs real productivity gain | \~4x code for \~12% more delivered value | GitClear, via O'Reilly | B |
| Copilot code review volume | 60M+ reviews, 10x in under a year | GitHub, via O'Reilly | B |

Faros AI sells into this market, as the O'Reilly author notes himself. The direction of these figures agrees across unrelated sources, but treat the exact percentages as indicative.

## Academic evidence

No academic paper estimates market size. What the research measures is effectiveness, and it contradicts vendor claims that AI can review most pull requests without humans.

| Study | Status | Data | Key finding |
| --- | --- | --- | --- |
| [Zhong, Noei, Adams, Zou — From Human-Centric to Agentic Code Review](https://arxiv.org/abs/2607.13196) | arXiv preprint, Jul 2026 | 1.02M reviewed PRs, 207 GitHub projects | AI-agent reviews are linked to faster decisions, but not to better review quality |
| [Chowdhury, Banik, Ferdous, Shamim — From Industry Claims to Empirical Reality: An Empirical Study of Code Review Agents in Pull Requests](https://arxiv.org/html/2604.03196v1) | Peer-reviewed, MSR 2026 (ACM) | 3,109 PRs from the AIDev dataset | AI-only reviewed PRs merge at 45.20% vs 68.37% for human-only, with more abandonment (34.88% vs 21.60%); 12 of 13 agents average under 60% signal |
| [Sun, Kuang, Baltes, et al. — Does AI Code Review Lead to Code Changes?](https://arxiv.org/abs/2508.18771) | arXiv preprint, v2 Apr 2026 | 16 AI review GitHub Actions, 22,000+ comments, 178 repositories | Adoption is growing but effectiveness varies widely; concise, manually triggered, hunk-level comments with code snippets lead to more changes |

The MSR 2026 paper also cites prior work finding that developers act on human review comments about 60% of the time, against 0.9%–19.2% for AI comments.

**What this means for the market:** buyers are paying for speed, but the evidence says quality is unproven. A tool that can show high signal on a public benchmark addresses the gap the research identifies.

## Implications for Agentic Code Review

The project should compete on **signal quality and self-hosting**, not on being free. Free open-source review is already available from the market leaders.

**Why "free for OSS" is not a differentiator**

- CodeRabbit has pledged more than $10M over 12 months to keep its review free for open-source projects.
- Greptile is free for qualifying non-commercial OSS projects.
- GitHub Copilot includes pull request review in its $10-per-month plan.

**Positioning that the evidence supports**

- **Runs in the team's own CI.** As a GitHub Action, code goes only to the model provider the team chooses, not to another SaaS vendor.
- **A second, different reviewer.** In one engineer's test of four AI reviewers on 146 PRs, 93.4% of flagged locations were caught by only one tool ([O'Reilly](https://www.oreilly.com/radar/agentic-code-review/), single experiment). Teams that already use one tool can add a cheap, different second one.
- **Measured signal, published openly.** The research gap is noise. A public signal-to-noise benchmark would be a credible differentiator.

**Design inputs for the SRS and NFRs**

1. Keep comments concise, hunk-level and with code snippets; these are the comments developers act on.
2. Support a manually triggered review mode alongside automatic runs.
3. Add a measurable signal-ratio target as a non-functional requirement, and cap comments per PR.
4. Position the tool as augmenting human review, never as approving pull requests alone.

**Risks**

- Bundled review keeps pushing the price people expect towards zero.
- Free-tier model rate limits may cap throughput on busy repositories.
- A noisy first release would repeat the exact failure the research documents.

## Open gaps and next steps

The weakest number in this study is the pure-play category ARR. It rests on one investor estimate for one company.

- [ ] Find revenue estimates for Qodo, Greptile and Graphite (Sacra, The Information, or funding announcements) to tighten the $100M–250M range
- [ ] Check Qodo's pricing page and add it to the competitor table
- [ ] Read the primary Faros AI and GitClear reports instead of relying on O'Reilly's summary
- [ ] Estimate the share of professional developers who work in pull-request teams, to turn the TAM ceiling into a realistic serviceable market
- [ ] Decide which signal-to-noise benchmark the project will publish against
- [ ] Measure reviewers per team in the pilot, to replace the assumed 2–4 per repository and the 2019 survey share

## Sources

**Primary disclosures and official data (A)**

- [CodeRabbit — Introducing Agentic Change Management (Series C), Aug 2026](https://www.coderabbit.ai/blog/introducing-agentic-change-management)
- [Business Wire — CodeRabbit raises $60M Series B, Sep 2025](https://www.businesswire.com/news/home/20250916401011/en/CodeRabbit-Raises-%2460M-Series-B-Following-Unprecedented-Growth-as-Vibe-Coding-Triggers-a-Need-for-New-Code-Quality-Standards)
- [CodeRabbit pricing](https://www.coderabbit.ai/pricing)
- [Greptile pricing](https://www.greptile.com/pricing)
- [Graphite pricing](https://graphite.com/pricing)
- [GitHub Copilot plans and pricing](https://github.com/features/copilot/plans)
- [GitHub Octoverse 2025](https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/)
- [SlashData — Global developer population trends 2025](https://www.slashdata.co/post/global-developer-population-trends-2025-how-many-developers-are-there)
- [Stack Overflow Developer Survey 2019 — code review](https://survey.stackoverflow.co/2019/)

**Research papers (A)**

- [Chowdhury et al. — From Industry Claims to Empirical Reality: An Empirical Study of Code Review Agents in Pull Requests (MSR 2026)](https://arxiv.org/html/2604.03196v1)
- [Sun et al. — Does AI Code Review Lead to Code Changes? A Case Study of GitHub Actions](https://arxiv.org/abs/2508.18771)
- [Zhong et al. — From Human-Centric to Agentic Code Review](https://arxiv.org/abs/2607.13196)

**Press and investor research (B)**

- [Sacra — CodeRabbit](https://sacra.com/c/coderabbit/)
- [Sacra — CodeRabbit vs. GitHub](https://sacra.com/research/coderabbit-vs-github/)
- [TechCrunch via Yahoo Finance — Cursor acquires Graphite](https://finance.yahoo.com/news/cursor-continues-acquisition-spree-graphite-215122810.html)
- [Fortune — Cursor acquires Graphite](https://fortune.com/2025/12/19/cursor-ai-coding-startup-graphite-competition-heats-up/)
- [SiliconANGLE — Cursor acquires Graphite](https://siliconangle.com/2025/12/19/cursor-acquires-ai-code-review-startup-graphite/)
- [TechCrunch — Benchmark in talks to lead Greptile Series A](https://techcrunch.com/?p=3029287)
- [Globes — Qodo raises $70M](https://en.globes.co.il/en/article-1001538970)
- [Dealroom — Qodo raises $70M](https://dealroom.co/news/127108-qodo-raises-70m-to-govern-the-ai-code-flood-as-enterprises-lose-trust-in/)
- [O'Reilly Radar — Agentic Code Review (Addy Osmani), Jun 2026](https://www.oreilly.com/radar/agentic-code-review/)
- [CXO Today — Gartner on enterprise AI coding agents](https://cxotoday.com/software/gartner-signals-major-competitive-shift-in-enterprise-ai-coding-market/)
- [Gartner, Predicts 2026: AI Potential and Risks Emerge in Software Engineering Technologies (vendor reprint)](https://www.armorcode.com/report/gartner-research)

**Gartner (A, unless noted)**

- [Gartner — Market for enterprise AI coding agents enters a new phase, 20 May 2026](https://www.gartner.com/en/newsroom/press-releases/2026-05-20-gartner-says-the-market-for-enterprise-ai-coding-agents-is-entering-a-new-phase-of-expansion-and-competitive-realignment)
- [Gartner — AI coding costs will surpass average developer salary by 2028, 24 Jun 2026](https://www.gartner.com/en/newsroom/press-releases/2026-06-24-gartner-predicts-ai-coding-costs-will-surpass-average-developer-salary-by-2028-as-token-consumption-surges)
- [GitHub — Gartner 2025 Magic Quadrant for AI Code Assistants (quotes the 90% forecast; B)](https://github.blog/ai-and-ml/github-copilot/gartner-positions-github-as-a-leader-in-the-2025-magic-quadrant-for-ai-code-assistants-for-the-second-year-in-a-row/)
