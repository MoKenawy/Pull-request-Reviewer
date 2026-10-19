# Calculation Basis — Agentic Code Review Pitch Deck

**Status: non-normative.** A business-side working document, not a specification. It defines nothing to build.

**Date:** 2026-10-10. It matches the deck as specified in [`0063-pitch-deck.md`](./0063-pitch-deck.md) on that date, and uses the slide numbers of the ten-slide order: title, problem, solution, market, business model, traction, competition, team, financials, the ask. Updated 2026-10-14 for slide 2's new figures (section 7).

This file shows how every number on the slides was reached: the inputs, where each input comes from, the arithmetic, and what is assumed. It is the place to look when someone asks "where does that figure come from?". The reasoning behind the choices is in [`0052-unit-economics-and-financials.md`](../0050-financial-planning/0052-unit-economics-and-financials.md); this file is only the working.

**Four kinds of number.** Each figure below is marked as one of these.

| Mark | Meaning |
|---|---|
| **Quoted** | Copied from a source. No arithmetic of ours |
| **Measured** | Counted by us: a run of the tool, the git history, or the GitHub data |
| **Calculated** | Arithmetic on quoted or measured inputs |
| **Assumed** | A choice of ours that no source or measurement supports yet |

Figures are computed on unrounded values and rounded for display, so a hand check on the rounded numbers can differ in the last digit.

---

## 1. The cost of serving a seat: $1.14 to $5.81 a month

This figure is on slides 5 and 9. It is built in five steps.

### Step 1. Model cost of one review: $0.0418

Cost = (input tokens × input price + billed output tokens × output price) ÷ 1,000,000.

| Input | Value | Kind | Source |
|---|---|---|---|
| Input tokens | 3,739 | Measured | Two runs of a 160-line pull request, trpc/trpc#7616, on Gemini 3.8 Flash, 2026-10-10 ([`review-volume-report.md`](../0050-financial-planning/0051-cost-structure/review-volume-report.md) §1.3) |
| Billed output tokens | 15,534 in run 1; 5,287 in run 2 | Measured | Same. "Billed output" is the provider's total minus the input, so it includes the model's thinking tokens |
| Input price | $0.75 per 1M tokens | Quoted | [Google's pricing page](https://ai.google.dev/gemini-api/docs/pricing), paid tier, through 2026-12-31 |
| Output price | $3.75 per 1M tokens | Quoted | Same; "including thinking tokens" |

| Run | Arithmetic | Result |
|---|---|---|
| 1 | (3,739 × 0.75 + 15,534 × 3.75) ÷ 1,000,000 = (2,804.25 + 58,252.50) ÷ 1,000,000 | $0.0611 |
| 2 | (3,739 × 0.75 + 5,287 × 3.75) ÷ 1,000,000 = (2,804.25 + 19,826.25) ÷ 1,000,000 | $0.0226 |
| Average | ($0.0611 + $0.0226) ÷ 2 | **$0.0418** |

### Step 2. Downloading the repository: $0.0038 to $0.0357 a review

Cost = repository size in GB × the NAT gateway's price per GB.

| Input | Value | Kind | Source |
|---|---|---|---|
| Smallest repository | 73 MB = 0.073 GB | Measured | The five repositories of the measurement ladder ([`review-volume-report.md`](../0050-financial-planning/0051-cost-structure/review-volume-report.md) §4) |
| Largest repository | 686 MB = 0.686 GB | Measured | Same |
| NAT gateway data price | $0.052 per GB | Quoted | [`pr-variable-pricing-model.md`](../0050-financial-planning/0051-cost-structure/pr-variable-pricing-model.md) §6, Frankfurt list price |
| Every review downloads the whole repository through the gateway | — | **Assumed** | Ours. The tool downloads less than the full size, and a service could keep a copy, so this is an upper bound |

| | Arithmetic | Result |
|---|---|---|
| Low | 0.073 × $0.052 | $0.0038 |
| High | 0.686 × $0.052 | $0.0357 |

### Step 3. Cost of one review: $0.0456 to $0.0775

| | Arithmetic | Result |
|---|---|---|
| Low | $0.0418 + $0.0038 | **$0.0456** |
| High | $0.0418 + $0.0357 | **$0.0775** |

The slides say "five to eight cents" for this range.

### Step 4. Reviews per seat per month: 25 to 75

| Input | Value | Kind | Source |
|---|---|---|---|
| Pull requests opened by core developers | 6,570 | Measured | Ten public TypeScript repositories, September 2026 ([`review-volume-report.md`](../0050-financial-planning/0051-cost-structure/review-volume-report.md) §2.2) |
| Core developers | 263 | Measured | Same. A core developer opened at least four pull requests in the month |
| Reviews per pull request if every push is reviewed | 3 | Measured, used as a stand-in | The top of the range of median commits per pull request in the same data. A commit is not always a push |
| A seat is a developer whose pull requests are reviewed | — | **Assumed** | Ours, following how rivals count a seat |

| | Arithmetic | Result |
|---|---|---|
| Average pull requests per developer per month | 6,570 ÷ 263 | 24.98, used as **25** |
| Reviews if each pull request is reviewed once | 25 × 1 | **25** |
| Reviews if every push is reviewed | 25 × 3 | **75** |

The average is used and not the median (13), because a cost is a total and a total follows the average.

### Step 5. Cost of a seat

| | Arithmetic | Result |
|---|---|---|
| Low: reviewed once, small repository | 25 × $0.0456 | **$1.14** |
| High: every push, large repository | 75 × $0.0775 | **$5.81** |

**What is not in it:** the always-on infrastructure (section 4), database and storage use, pull requests larger than 160 lines, and anyone's time.

---

## 2. The price: $22 a seat a month

On slides 4, 5, 7 and 9.

| Input | Value | Kind | Source |
|---|---|---|---|
| CodeRabbit, entry price | $24 per developer per month, billed annually | Quoted | [`tool-reference.md`](../../tool-reference.md) |
| Graphite, entry price | $20 per user per month, billed annually | Quoted | Same; [Graphite's pricing page](https://graphite.com/pricing), read 2026-10-10 |
| The price must stay under CodeRabbit's $24 | — | Decision | Founder, 2026-10-10 |
| Greptile's $30 is an anomaly and is not averaged | — | Decision | Founder, 2026-10-10 |
| Graphite is the second price in the average | — | **Assumed** | Ours. It is the only other seat price in our references that keeps the average under $24. Cubic's $40 is left out for the same reason as Greptile's |

| Arithmetic | Result |
|---|---|
| ($24 + $20) ÷ 2 | **$22** |

---

## 3. What a seat leaves: $16 to $21, or 74% to 95%

On slide 9.

| | Arithmetic | Result |
|---|---|---|
| Least: the price less the highest cost | $22 − $5.81 | $16.19, shown as **$16** |
| Most: the price less the lowest cost | $22 − $1.14 | $20.86, shown as **$21** |
| Least, as a share of the price | $16.19 ÷ $22 | **74%** |
| Most, as a share of the price | $20.86 ÷ $22 | **95%** |

This is a contribution margin: before the always-on infrastructure and before anyone's time.

---

## 4. Always-on infrastructure: $96.36 a month

On slide 9. Each line is an hourly price × 730 hours, the cost sheet's accounting month.

| Resource | Hourly price | Kind | Arithmetic | A month |
|---|---|---|---|---|
| One load balancer | $0.027 | Quoted: [`pr-variable-pricing-model.md`](../0050-financial-planning/0051-cost-structure/pr-variable-pricing-model.md) §4 | 730 × $0.027 | $19.71 |
| One NAT gateway | $0.052 | Quoted: same file §6 | 730 × $0.052 | $37.96 |
| One public IPv4 address | $0.005 | Quoted: same file §5 | 730 × $0.005 | $3.65 |
| One t3.medium server | $0.048 | Quoted price, from third-party price lists ([DoiT](https://www.doit.com/compute/spot/eu-central-1/t3.medium), [aws-pricing.com](https://aws-pricing.com/t3.medium.html)); the choice of instance is **Assumed** | 730 × $0.048 | $35.04 |
| **Total** | | | $19.71 + $37.96 + $3.65 + $35.04 | **$96.36** |

**Assumed, all ours:** that the service runs on this layout, with one of each resource; that these hours are a fixed cost and not passed to the customer; that one server holds every review. The cost sheet marks its own prices "verify with AWS Pricing Calculator before committing cash".

---

## 5. Break-even: 5 to 6 seats

On slide 9. Seats = always-on cost ÷ what a seat leaves, rounded up.

| | Arithmetic | Result |
|---|---|---|
| Best case | $96.36 ÷ $20.86 = 4.62 | **5 seats** |
| Worst case | $96.36 ÷ $16.19 = 5.95 | **6 seats** |

It covers infrastructure only. No one's pay is in it.

---

## 6. The market figures

On slide 4. The inputs and their sources are in [`004-market-study.md`](../004-market-study.md).

### TAM: $10.5B to $13.1B a year

| Input | Value | Kind | Source |
|---|---|---|---|
| Professional developers worldwide | 36.5M | Quoted | SlashData, early 2025 |
| Rivals' entry prices | $24 and $30 per developer per month | Quoted | CodeRabbit and Greptile pricing pages |

| | Arithmetic | Result |
|---|---|---|
| Yearly spend per developer | $24 × 12; $30 × 12 | $288; $360 |
| TAM, low | 36.5M × $288 | $10.512B, shown as **$10.5B** |
| TAM, high | 36.5M × $360 | $13.14B, shown as **$13.1B** |

### SAM: $2.0B to $4.0B a year

| Input | Value | Kind | Source |
|---|---|---|---|
| Developers who use JavaScript or TypeScript | 68.8% | Quoted | Stack Overflow 2025 |
| Developers in pull-request teams | 55% | Quoted, as a proxy | JetBrains 2025: developers who regularly use CI/CD tools |
| Developers who use AI tools | 50.6% daily; 80.8% at all | Quoted | Stack Overflow 2025 |
| The three shares are independent | — | **Assumed** | The market study's own caveat |

| | Arithmetic | Result |
|---|---|---|
| Developers, low | 36.5M × 68.8% × 55% × 50.6% | 6.99M, shown as 7.0M |
| Developers, high | 36.5M × 68.8% × 55% × 80.8% | 11.16M, shown as 11.2M |
| SAM, low | 6.99M × $288 | $2.01B, shown as **$2.0B** |
| SAM, high | 11.16M × $360 | $4.02B, shown as **$4.0B** |

### Reviewers in the SAM: 5.3M to 8.5M

| Input | Value | Kind | Source |
|---|---|---|---|
| Developers who review code as part of their work | 76.4% (68.8% + 7.6%) | Quoted | Stack Overflow 2019, 70,390 responses |

| | Arithmetic | Result |
|---|---|---|
| Low | 6.99M × 76.4% | 5.34M, shown as **5.3M** |
| High | 11.16M × 76.4% | 8.53M, shown as **8.5M** |

### The market at our own price: $9.6B

| | Arithmetic | Result |
|---|---|---|
| Yearly spend per developer | $22 × 12 | $264 |
| TAM at $22 | 36.5M × $264 | $9.636B, shown as **$9.6B** |
| SAM at $22, low | 6.99M × $264 | $1.845B, shown as $1.8B (speaker notes) |
| SAM at $22, high | 11.16M × $264 | $2.946B, shown as $2.9B (speaker notes) |

### SOM, year 1: $3,960 a year

Counted bottom-up from the pilot alone, by the founder's decision of 2026-10-10. The slide adds: "Later years wait for the pilot's result."

| Input | Value | Kind | Source |
|---|---|---|---|
| Pilot teams | 6 | Decision | The founder's figure of 2026-10-10, and the number in the ask on slides 1 and 10 |
| Seats per team | 5 | **Assumed** | The team size these documents use as an illustration; not measured |
| Share of pilot seats that pay | 50% | **Assumed** | The founder's figure of 2026-10-10. Nothing measures it; the pilot will |
| Price | $264 a seat a year | Calculated | Section 2: $22 × 12 |

| | Arithmetic | Result |
|---|---|---|
| Seats in the pilot | 6 × 5 | 30 |
| Paying seats | 30 × 50% | 15 |
| SOM, year 1 | 15 × $264 | **$3,960** a year |

### In the speaker notes: about 0.4%, and 460 repositories

| Figure | Kind | Arithmetic or source |
|---|---|---|
| The category leader's seats | Calculated | $40M of yearly revenue (Sacra's estimate for CodeRabbit) ÷ $288 a seat a year ≈ 139,000 seats |
| About 0.4% of professional developers | Calculated | 139,000 ÷ 36.5M = 0.38% |
| 460 repositories | Quoted | Sun et al., arXiv 2508.18771: public repositories using the most-adopted open-source review Action, January 2025 |

---

## 7. The other numbers on the slides

| Slide | Figure | Kind | How it was reached |
|---|---|---|---|
| 1 Title | About five times as long (notes) | Calculated | The same figure as slide 2, below |
| 1 Title | Three people did more than 85% of the reviewing, in half of ten projects (notes) | Measured | [`review-volume-report.md`](../0050-financial-planning/0051-cost-structure/review-volume-report.md) §2.5: in five of the ten public TypeScript repositories, three people did more than 85%. Nothing calculated |
| 2 Problem | +441.5% review duration; +31.3% merged without review | Quoted | Faros AI, 22,000 developers, through O'Reilly ([`004-market-study.md`](../004-market-study.md)): teams with high AI adoption. On the slide since 2026-10-14, in place of LinearB's 30-day merge rates (84.5% and 32.7%) |
| 2 Problem | About 5× as long to review | Calculated | 1 + 441.5% = 1 + 4.415 = 5.415, rounded down to "about 5×". The 31.3% is shown as "31%", and said as "nearly a third more" |
| 3 Solution | 1 command, 1 model pass (notes) | Quoted | The CLI contract and SRS v1 §2.1 |
| 3 Solution | 16 files; 10 reviewed; 6 listed, not reviewed | Measured | The run's own output, 2026-10-09. 10 + 6 = 16 |
| 3 Solution | 1 finding; 9 of 10 reviewed files with no finding call | Measured | Same output. 10 − 1 = 9 |
| 3 Solution | 125.4 s; "about two minutes" in the notes | Measured; Calculated | Same output. 125.4 ÷ 60 = 2.09 minutes, clone included |
| 3 Solution | 169 lines added, 38 removed | Quoted | The pull request's page on GitHub |
| 6 Traction | 2026-09-17; 2026-10-09 | Measured | Commit dates in the git history |
| 6 Traction | 93 of 127 tasks (notes) | Measured; Calculated | Ticked and open boxes in `specs/001-walking-skeleton/tasks.md`: 93 + 34 = 127 |
| 5 Business model | $24; $20 | Quoted | Section 2 |
| 5 Business model | "Doubles in 2027" | Quoted | Google's pricing page: $1.50 and $7.50 per 1M tokens from 2027-01-01, twice the 2026 prices |
| 7 Competition | 3 of 4 rivals filter findings out | Calculated: a count | CodeRabbit, Qodo and Claude Code Review say so on their own pages; Greptile's pages do not say ([`competitive-landscape.md`](../competitive-landscape.md)) |
| 7 Competition | $24; $30; $15–25 a review | Quoted | Rivals' own pricing pages and documentation |
| 8 Team | 6 people: 4 junior software engineers, 1 senior Oracle developer, 1 sales manager | Quoted | Founder, 2026-10-10 |

---

## 8. The same figures from 2027

Google's listed prices for the model double on 2027-01-01. The slides show 2026 figures and say so; these are the 2027 ones.

| Figure | Arithmetic | Result |
|---|---|---|
| Model cost of one review | The same tokens at $1.50 and $7.50, or $0.0418 × 2 | $0.0837 |
| Cost of one review | $0.0837 + $0.0038; $0.0837 + $0.0357 | $0.0875 to $0.1194 |
| Cost of a seat | 25 × $0.0875; 75 × $0.1194 | $2.19 to $8.95 |
| What a seat leaves | $22 − $8.95; $22 − $2.19 | $13.05 to $19.81 |
| As a share of the price | ÷ $22 | 59% to 90% |
| Break-even seats | $96.36 ÷ $19.81 = 4.86; ÷ $13.05 = 7.38 | 5 to 8 |

---

## 9. Every assumption in one place

| # | Assumption | Affects | What would replace it |
|---|---|---|---|
| 1 | Two runs of one 160-line pull request stand for every review | Cost of a review, a seat, the margin, break-even | The three larger sizes of the measurement ladder, and more runs per size. The two runs differ by 2.7 times |
| 2 | Every review downloads the whole repository through the NAT gateway | Cost of a review | A measurement on a hosted service |
| 3 | A seat is a developer whose pull requests are reviewed | Reviews per seat | The founder's definition of a seat |
| 4 | Public open-source repositories stand for company teams | Reviews per seat | The pilot |
| 5 | Three reviews per pull request when every push is reviewed | The high end of every cost | A count of pushes, which the data does not hold |
| 6 | Graphite is the second price in the average | The price | The founder's choice of rivals, or of a price |
| 7 | One load balancer, one NAT gateway, one address, one t3.medium server | Always-on cost, break-even | A design for the hosted service |
| 8 | Always-on hours are a fixed cost covered by the margin | Break-even | The founder's confirmation |
| 9 | The three market shares are independent | SAM | A cross-tabulation of the survey's raw data |
| 10 | Everyone's time costs nothing | Every result | A staffing plan |

---

## 10. The review allowance: 150 reviews a seat a month

Not on a slide; it is in the speaker notes of slide 9. Decided by the founder on 2026-10-10, on our recommendation: each seat includes 150 reviews a month, pooled across the team.

Cost of a seat that uses its whole allowance = 150 × the cost of one review (section 1, step 3; section 8 for 2027).

| | Arithmetic | Result |
|---|---|---|
| Through 2026, low | 150 × $0.0456 | $6.85 |
| Through 2026, high | 150 × $0.0775 | $11.63 |
| From 2027, low | 150 × $0.0875 | $13.12 |
| From 2027, high | 150 × $0.1194 | **$17.90** |
| What the worst such seat leaves | $22 − $17.90 | $4.10 |
| A team of five, pooled | 5 × 150 | 750 reviews a month |

- **Why 150:** it is the round number that keeps the costliest seat under the $22 price at 2027 costs, and it is two to six times the average seat's 25 to 75 reviews. The choice is ours; no customer has been asked.
- **Without an allowance** a seat would cost more than $22 after 184 to 482 reviews in a month (Calculated: $22 ÷ the cost of one review, across both price periods).

---

## 11. The theoretical forecast: 313 and 986 seats per $1M invested

On slide 9. We have no traction, so this forecast borrows the category leader's capital efficiency. It is a benchmark, not a plan: we have raised nothing.

| Input | Value | Kind | Source |
|---|---|---|---|
| CodeRabbit, raised by the end of 2024 | Just under $20M | Quoted | Its Series A announcement of August 2024, as reported by [Maginative](https://www.maginative.com/article/coderabbit-secures-16m-in-series-a-funding-expands-ai-powered-code-review-capabilities/) |
| CodeRabbit, raised by the end of 2025 | $88M | Quoted | Its Series B announcement of September 2025 (Business Wire), in [`004-market-study.md`](../004-market-study.md) |
| CodeRabbit's yearly revenue, end of 2025 | $25M | Quoted, an estimate | [Sacra](https://sacra.com/c/coderabbit/) |
| CodeRabbit's revenue growth over 2025 | 1,288.9% | Quoted, an estimate with no stated basis | Same |
| CodeRabbit's entry price | $24 a month, $288 a year | Quoted | [`tool-reference.md`](../../tool-reference.md) |
| Our price | $22 a month, $264 a year | Calculated | Section 2 |
| We would convert money into seats as well as CodeRabbit did | — | **Assumed** | Ours. Our build does less than its product |
| $1M is invested in us | — | **Assumed** | Ours. We have raised nothing and ask for no money |

| Step | Arithmetic | Result |
|---|---|---|
| CodeRabbit's revenue, end of 2024 | $25M ÷ (1 + 12.889) | $1.8M |
| Its seats, end of 2024 | $1.8M ÷ $288 | 6,250 |
| Its seats, end of 2025 | $25M ÷ $288 | 86,806 |
| Seats per $1M raised, year 2 | 6,250 ÷ 20 | 312.5, shown as **313** |
| Seats per $1M raised, year 3 | 86,806 ÷ 88 | 986.4, shown as **986** |
| Our revenue per $1M invested, year 2 | 312.5 × $264 | **$82,500** a year |
| Our revenue per $1M invested, year 3 | 986.4 × $264 | $260,417, shown as **$260,400** a year |

Year 1 is shown as "build and pilot, no revenue": CodeRabbit's first-year revenue is not published, and our hosted service does not exist yet.

---

## 12. The ask: 6 teams, 8 weeks, 1,000 reviews, 20%

On slides 1 and 10. Set by the founder on 2026-10-10.

| Figure | Kind | How it was reached |
|---|---|---|
| 6 teams | Decision | The same six pilot teams the SOM assumes (section 6) |
| 8 weeks, from 1 January 2027 | Decision | The start date is the founder's. Eight weeks from Friday 1 January ends on Friday 26 February 2027 |
| 28 February 2027 | Decision | The end of the month in which the pilot ends |
| 1,000 reviews | Calculated target | Below the volume worked out in the table that follows |
| 20% of findings acted on | Quoted benchmark, used as a target | Earlier work cited by Chowdhury et al. (MSR 2026) reports that developers act on 0.9% to 19.2% of AI review comments. 20% is just above the top of that range |

| Step | Arithmetic | Result |
|---|---|---|
| Developers in the pilot | 6 teams × 5 | 30 |
| Pull requests a month | 30 × 25 (section 1, step 4) | 750 |
| Months in eight weeks | 8 ÷ 4.35 weeks a month | 1.84 |
| Pull requests in the pilot | 750 × 1.84 | about 1,380 |
| Model cost of the pilot, reviewed once | 1,380 × $0.0875 to $0.1194, the 2027 cost of a review (section 8) | $121 to $165 |
| Model cost if every push is reviewed | Three times that | $362 to $494 |

**Assumed:** five developers a team; the average of 25 pull requests a month, measured in public repositories; one review per pull request. The 2027 prices apply because the pilot starts on the day the model's listed prices double.

**A condition on the 20%.** In five measured runs on the working model the tool reported no finding. A milestone counted in findings needs the tool to report them, so this should be checked before the pilot starts.
