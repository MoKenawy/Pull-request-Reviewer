# Unit Economics and Financials — Agentic Code Review

**Status: non-normative.** A business-side working document, not a specification. It defines nothing to build.

**Date:** 2026-10-10 · **Tasks:** 4 (pricing unit) and 6 (financials) of the pitch rework list.

This file sets a price for the hosted review service and sets our estimated costs beside it. Every figure is calculated from an input named in section 1. Nothing here is a forecast of customers: no one has used the service, and the hosted service itself is not designed.

**The pricing rule was settled in three steps on one day; only the last stands.**

1. Per review, at cost plus a margin. It gave five to eight cents a review and about a dollar a developer a month.
2. A monthly price per seat, from the average of rivals' prices, with our cost structure estimated beside it. With CodeRabbit and Greptile averaged, that was $27.
3. **The same rule with two limits from the founder: the price must stay under CodeRabbit's $24, and Greptile's $30 is treated as an anomaly and left out.** That gives $22.

Section 9 records the two replaced versions. The per-review figures remain as the cost side of this file.

Confidence labels follow [`004-market-study.md`](../004-market-study.md): **A** primary data, **B** reputable secondary, **C** our calculation. **Assumed** marks a choice of ours that no source or measurement supports yet.

---

## Summary

- **The price is $22 per developer per month,** the average of CodeRabbit's $24 and Graphite's $20. It is under CodeRabbit's price, as the founder requires, and Greptile's $30 is left out as an anomaly (C).
- **A seat is estimated to cost us $1.14 to $5.81 a month to serve** through 2026: the model's tokens and the download of the repository, for 25 to 75 reviews, 25 being the average number of pull requests a developer opens in a month. From 2027-01-01, when the model's price doubles, $2.19 to $8.95 (C, with assumptions).
- **That leaves $16 to $21 a seat through 2026, a contribution margin of 74% to 95%,** and 59% to 90% from 2027.
- **The always-on infrastructure is estimated at $96.36 a month,** with one small server in it (Assumed). Five to six seats cover it through 2026, and five to eight from 2027.
- **The price is not much of a difference.** We are $2 under CodeRabbit, and our build does less than theirs today.
- **Each seat includes 150 reviews a month, pooled across the team** (decided 2026-10-10). A seat that uses all of them costs an estimated $6.85 to $11.63 to serve through 2026 and $13.12 to $17.90 from 2027, still under $22. Without the allowance a seat would cost more than it pays after 184 to 251 reviews in a month at 2027 prices.
- **The cost estimate is low in three known ways:** larger pull requests are unmeasured, nothing has been run on a hosted service, and nobody's time is priced.
- **The three-year forecast is theoretical** (section 6). We have no traction, so it applies the category leader's capital efficiency to each $1M invested: about 313 seats and $82,500 a year by year 2, and 986 seats and $260,400 a year by year 3. We have raised nothing.

---

## 1. Decisions and inputs

| Input | Value | Source | Tier |
|---|---|---|---|
| Pricing unit | One seat for one month | Founder, 2026-10-10 | Decision |
| Pricing rule | The average of rivals' prices, with our cost structure estimated beside it | Same | Decision |
| Limits on the price | Under CodeRabbit's $24. Greptile's $30 is an anomaly and is not averaged | Founder, 2026-10-10, the last of the three steps | Decision |
| Review allowance | 150 reviews a month, pooled across the team | Founder, 2026-10-10, on our recommendation | Decision |
| CodeRabbit, entry price | $24 per developer per month, billed annually (Essentials) | [`tool-reference.md`](../../tool-reference.md) | A |
| Graphite, entry price | $20 per user per month, billed annually (Starter), with "Limited AI reviews" | [`tool-reference.md`](../../tool-reference.md); [Graphite's pricing page](https://graphite.com/pricing), read 2026-10-10 | A |
| Greptile, entry price | $30 per seat per month (Pro). Left out of the average | [`tool-reference.md`](../../tool-reference.md); [Greptile's pricing page](https://www.greptile.com/pricing), read 2026-10-10 | A |
| Cubic, entry price | $40 per developer per month (Team). Left out of the average | [Cubic's pricing page](https://www.cubic.dev/pricing), read 2026-10-10 | A |
| Model | Gemini 3.8 Flash, as the working assumption | Founder, 2026-10-10 | Decision |
| Model price | $0.75 input and $3.75 output per 1M tokens through 2026-12-31; $1.50 and $7.50 from 2027-01-01 | [Google's pricing page](https://ai.google.dev/gemini-api/docs/pricing), read 2026-10-10 | A |
| Model cost of a median-size review | $0.0418 through 2026; $0.0837 from 2027 | [`review-volume-report.md`](./0051-cost-structure/review-volume-report.md) §3.4: two measured runs, $0.0226 and $0.0611 | C, from A |
| Reviews per seat per month | 25 if each pull request is reviewed once; up to 75 if every push is reviewed | Same file §2.2: the average number of pull requests opened per core developer, ten public TypeScript repositories (6,570 ÷ 263 = 24.98), and up to three pushes each | C, from A |
| Repository size | 73 MB to 686 MB | Same file §4: the five repositories of the measurement ladder | A |
| Cloud unit prices | Load balancer $0.027 an hour, NAT gateway $0.052 an hour and $0.052 per GB, public IPv4 address $0.005 an hour | [`pr-variable-pricing-model.md`](./0051-cost-structure/pr-variable-pricing-model.md), list prices for Frankfurt | B: the sheet says to "verify with AWS Pricing Calculator before committing cash" |
| Server | One t3.medium (2 vCPUs, 4 GiB) at $0.048 an hour in Frankfurt | The instance type is **Assumed**: the cost sheet leaves it "TBD". The price is from third-party price lists ([DoiT](https://www.doit.com/compute/spot/eu-central-1/t3.medium), [aws-pricing.com](https://aws-pricing.com/t3.medium.html)), read 2026-10-10 | B |

**What a seat is.** A developer whose pull requests are reviewed in the month. This is how rivals count: Greptile's pricing page says "A seat is any developer who received a review from Greptile during the billing period." It is Assumed for us; the founder's decision names a seat and does not define one.

---

## 2. The price: the average of rivals' prices, under CodeRabbit's

| Which rivals | Their entry prices | Average | Under $24? |
|---|---|---|---|
| **CodeRabbit and Graphite** | $24, $20 | **$22.00** | **Yes** |
| Those two and Cubic | $24, $20, $40 | $28.00 | No |
| CodeRabbit and Greptile, the earlier version | $24, $30 | $27.00 | No |

**$22 is used throughout this file and the deck.**

What to know about it:

- **Which rivals are averaged is my choice, made to fit the founder's two limits.** With Greptile out, the rivals with a seat price in our references are CodeRabbit, Graphite and Cubic. Cubic's $40 is higher than the price ruled an anomaly, so it is left out for the same reason, and any average with it in is over $24.
- **Graphite is a weak comparison.** It is a workflow tool whose $20 plan includes only "Limited AI reviews", and the competitive landscape treats it as a complement, not a rival. Without it there is nothing to average: the price would simply be a figure under $24 that the founder picks.
- **Both prices are billed annually.** A price billed month by month would normally be higher.
- **Qodo and Claude Code Review are in no average.** Qodo is credit-based with no seat price in our references, and Claude Code Review bills per review, $15 to $25 on average.
- **Cost does not decide the price.** Section 3 puts our cost at a dollar or three a seat, far below any of these figures.

---

## 3. Our estimated cost per seat

**Per review.** Two parts are estimated; the rest is unmeasured.

| Part | Through 2026-12-31 | From 2027-01-01 | How |
|---|---|---|---|
| Model tokens, median-size review | $0.0418 | $0.0837 | Measured: two runs of a 160-line pull request |
| Downloading the repository through the NAT gateway | $0.0038 to $0.0357 | The same | Calculated: 73 MB and 686 MB × $0.052 per GB. An upper bound for each repository: the tool downloads less than the full size, and a service could keep a copy between reviews |
| Database, storage, logging | Not estimated | | Unmeasured. Small at the cost sheet's unit prices; nothing has been run on a hosted service |
| **Per review** | **$0.0456 to $0.0775** | **$0.0875 to $0.1194** | |

**Per seat per month** = cost per review × the average number of reviews in the month.

The average is used, not the median, because a cost is a total and a total follows the average. The median developer opens 13 pull requests a month; the average is 25, pulled up by a few people who open 100 to 200. Until 2026-10-10 this file used 13 and understated the cost of a seat by about half.

| | 25 reviews, small repository | 75 reviews, large repository |
|---|---|---|
| Through 2026-12-31 | $1.14 | $5.81 |
| From 2027-01-01 | $2.19 | $8.95 |

- **The model is most of it.** Tokens alone come to $1.05 to $3.14 a seat through 2026, and $2.09 to $6.28 from 2027.
- **The estimate is for a typical review.** 160 changed lines is close to the median of 155. A quarter of pull requests are over 581 lines, and none that large has been measured on this model.
- **The two measured runs differ by 2.7 times,** $0.0226 against $0.0611, for the same pull request. Almost all of the cost is the model's thinking, and its length varies from run to run.

---

## 4. What a seat leaves

Contribution = $22 − the cost of serving the seat. It is a **contribution margin**: before the always-on infrastructure in section 5 and before anyone's time.

| | Cost of a seat | Contribution | Share of the price |
|---|---|---|---|
| Through 2026-12-31 | $1.14 to $5.81 | $16.19 to $20.86 | 74% to 95% |
| From 2027-01-01 | $2.19 to $8.95 | $13.05 to $19.81 | 59% to 90% |

**The risk in a flat price: a heavy seat.** A seat costs more than $22 to serve once it passes a number of reviews in the month (Calculated: $22 ÷ cost per review).

| | Reviews in a month before a seat loses money |
|---|---|
| Through 2026-12-31 | 284 to 482 |
| From 2027-01-01 | 184 to 251 |

In the ten-repository sample a few developers open 100 to 200 pull requests a month. Reviewed on every push, at up to three pushes each, that is 300 to 600 reviews. Greptile limits this with 50 credits a seat and $1 for each one more.

**The allowance, decided on 2026-10-10: 150 reviews a month, pooled across the team.** A team of five has 750 between them.

| | A seat that uses its full 150 reviews costs | And leaves |
|---|---|---|
| Through 2026-12-31 | $6.85 to $11.63 | $10.37 to $15.15 |
| From 2027-01-01 | $13.12 to $17.90 | $4.10 to $8.88 |

The average seat uses 25 to 75 reviews, so the allowance is two to six times ordinary use. It keeps the worst seat above cost; it was chosen by us for that reason and has not been tested on a customer. `[MISSING: what happens when a team passes its allowance]`

---

## 5. Always-on cost and break-even

**How the two cost sheets are read together.** The cost sheet prices every resource by use and says not to write a resource down as a fixed monthly cost. The pricing template has a fixed cost `F` and a break-even point. Both hold if the resources are split in two:

- **Used per review** (tokens, the repository download): counted in the cost of a seat, section 3.
- **Running whether or not anyone reviews** (the hours of the load balancer, the NAT gateway and the server; a public address): this is `F`. The cost sheet itself calls a NAT gateway "capacity cost + usage cost".

This split is my reading, to be confirmed.

**`F`, estimated (Calculated, 730 hours a month):**

| Resource | A month | Basis |
|---|---|---|
| One load balancer | $19.71 | Cost sheet |
| One NAT gateway | $37.96 | Cost sheet |
| One public IPv4 address | $3.65 | Cost sheet |
| One t3.medium server | $35.04 | Assumed instance; 730 × $0.048 |
| **`F`** | **$96.36** | |

Not in it: the server's disk, logging, capacity units on the load balancer, and anything a second availability zone would double. One server is assumed to serve every review: a review takes 76 to 153 seconds and spends most of it waiting for the model, so one machine can hold many at once. How many is unmeasured.

**Break-even** = `F` ÷ contribution per seat, rounded up. It is the pricing template's formula, "Break-even Customers = F / [P - (C × R)]", with the customer being a seat.

| | Seats to cover `F` |
|---|---|
| Through 2026-12-31 | 5 to 6 |
| From 2027-01-01 | 5 to 8 |

**One team, or two small ones, covers the always-on cost.** That is a statement about infrastructure only. It says nothing about paying the six people who build the product.

---

## 6. Years 1 to 3: a theoretical forecast

**Why theoretical.** A forecast is normally built on traction, and we have none: no user outside the team, no pilot, no letter of intent. On 2026-10-10 the founder asked for a theoretical forecast based on what rivals' investments have bought, mainly CodeRabbit's. CodeRabbit is the only rival for which both funding and revenue estimates exist; Greptile's funding is reported inconsistently, and Qodo's revenue is not reported at all.

**What CodeRabbit raised, and what it was earning at the time.**

| Year since founding | Raised by then | Yearly revenue then | Source | Tier |
|---|---|---|---|---|
| 1, end of 2023 | A seed round, amount not published | Not published | [Sacra](https://sacra.com/c/coderabbit/): "founded in early 2023" | — |
| 2, end of 2024 | Just under $20M, after a $16M Series A in August 2024 | About $1.8M (Calculated below) | Round: CodeRabbit's announcement, reported by [Maginative](https://www.maginative.com/article/coderabbit-secures-16m-in-series-a-funding-expands-ai-powered-code-review-capabilities/). Revenue: derived from Sacra | B |
| 3, end of 2025 | $88M, after a $60M Series B in September 2025 | $25M | Round: Business Wire, in [`004-market-study.md`](../004-market-study.md). Revenue: Sacra's estimate | A for the round; B for the revenue |
| Later, July to August 2026 | $231M, after a $143M Series C in August 2026 | $50M in July 2026 | Same; the total is Calculated: $88M + $143M | A; B |

- **Revenue at the end of 2024 (Calculated).** Sacra gives $25M at the end of 2025 and growth of 1,288.9% over 2025. $25M ÷ (1 + 12.889) = $1.8M. Sacra does not state the basis of that growth rate, so this is the weakest figure here. It is consistent with the market study's "roughly 8x in the year to April 2026".
- **CodeRabbit has never published its revenue.** Every dollar figure for it is Sacra's estimate.

**Capital efficiency: paying seats per $1M raised.** Seats are revenue ÷ $288, CodeRabbit's entry price for a year, the same method the market study uses.

| | Revenue per $1 raised | Seats | Seats per $1M raised |
|---|---|---|---|
| End of year 2 | $1.8M ÷ $20M = $0.09 | $1.8M ÷ $288 = 6,250 | 6,250 ÷ 20 = **313** |
| End of year 3 | $25M ÷ $88M = $0.28 | $25M ÷ $288 = 86,806 | 86,806 ÷ 88 = **986** |

**The forecast: the same efficiency, at our price, for each $1M invested.** Our price is $22 a month, $264 a year.

| | Year 1 | Year 2 | Year 3 |
|---|---|---|---|
| Seats per $1M invested | Build and pilot | 313 | 986 |
| Revenue a year, at $264 a seat | None | $82,500 | $260,400 |
| Cost of serving those seats, at 2027 prices | — | $8,200 to $33,600 | $25,900 to $106,000 |
| What is left before people and before the investment itself | — | $48,900 to $74,300 | $154,400 to $234,500 |

- **The serving cost** is seats × 12 × $2.19 to $8.95, the cost of a seat from 2027 (section 3). The always-on infrastructure of $1,156 a year is not subtracted; at this scale it would be more than one server.
- **The investment is not earned back in three years.** By year 3 each $1M invested brings in about $260,000 a year. CodeRabbit itself had raised $88M to reach $25M a year.
- **If we matched CodeRabbit's whole path and its funding,** year 3 would be 86,806 seats and $22.9M a year at our price (Calculated: 86,806 × $264). That is a ceiling for a funded leader, not a target for us.

**What this forecast assumes, all of it unproven.**

1. **We would turn money into paying seats as well as the category leader did.** Our build does less than its product, and it had a two-year head start.
2. **We would have money to invest.** We have raised nothing, and the pitch asks for pilot teams, not funding. `[MISSING: the investment to assume for us]`
3. **A seat is worth CodeRabbit's entry price.** Its revenue includes higher tiers and add-ons, so dividing by the entry price overstates its seats.
4. **Year 2 rests on one growth figure** that its source gives without a basis.

**The formula, for when the pilot supplies our own numbers.**

```text
revenue               = N × P × 12
cost of serving       = N × S × 12
contribution          = N × (P − S) × 12
result before people  = contribution − F × 12
```

| Variable | Meaning | Value |
|---|---|---|
| `N` | Seats on the hosted service | `[MISSING: from the pilot. No one uses the service today]` |
| `P` | Price per seat per month | $22 |
| `S` | Cost of serving a seat for a month | $1.14 to $5.81 through 2026; $2.19 to $8.95 from 2027 |
| `F` | Always-on infrastructure per month | $96.36, estimated |

As a unit, not a forecast: 100 seats for a year are $26,400 of revenue, $1,369 to $6,976 of serving cost and $1,156 of always-on cost at 2026 prices, which leaves $18,267 to $23,874 before people. At 2027 prices the serving cost is $2,624 to $10,742 and what is left is $14,501 to $22,619.

---

## 7. The market at this price

The market study sizes the market at rivals' entry prices, $24 to $30 a month, and that range still includes Greptile's price. At $22 our own price is below it, so the same people are worth a little less to us.

| Layer | At the market study's proxy, $24 to $30 a month | At our price, $22 a month |
|---|---|---|
| Yearly spend per developer | $288 to $360 | $264 |
| TAM, 36.5M developers | $10.5B to $13.1B | $9.6B |
| SAM, 7.0M to 11.2M developers | $2.0B to $4.0B | $1.8B to $2.9B |

- The SAM is computed on the unrounded 6.99M and 11.16M developers.
- **The proxy was not changed.** It is a decision of 2026-10-08 about what rivals charge, and Greptile does charge $30. Whether the market study should also drop Greptile from its range is the founder's call; if it did, the proxy would be CodeRabbit's $24 alone, a TAM of $10.5B.
- **Revenue SOM (decided 2026-10-10): the pilot alone.** 6 pilot teams × 5 seats = 30 seats; half of them paying is 15 seats, $3,960 a year. Later years wait for the pilot's result ([`004-market-study.md`](../004-market-study.md)). At the estimated cost of a seat, those 15 seats leave $2,914 to $3,755 a year, which covers the always-on infrastructure of $1,156.

---

## 8. Assumptions

1. **The price is the average of CodeRabbit's and Graphite's entry prices,** both billed annually, and is not adjusted for what each product does.
2. **A seat is a developer whose pull requests are reviewed,** opening 25 a month, the average in ten public repositories. Public open-source repositories stand for company teams.
3. **The model is Gemini 3.8 Flash on the paid tier, at list price.** The free tier allows 20 requests a day for this model and marks content as used to improve the provider's products, so a paid service cannot run on it.
4. **A review is one model call with the build's current prompt,** which is what the measured runs were. Running the project's tests, gathering related code or adding repair turns would raise the cost; running customers' tests would add sandboxed compute that is not estimated here at all.
5. **A median-size pull request stands for every pull request.** It understates.
6. **The service runs on AWS in Frankfurt on one small server,** the cost sheet's layout with an instance we chose. The service is not designed, so this is an estimate of a layout, not of a system.
7. **No salary, support, payment fee or tax is in any figure.** Prices are list prices in US dollars.

---

## 9. What is still missing, and what was replaced

- `[MISSING: what happens past the review allowance]`, and whether the price is billed monthly or annually.
- `[MISSING: cost of a review above 160 changed lines on Gemini 3.8 Flash]`. Three sizes of the measurement ladder were refused by the free tier's daily limit.
- `[MISSING: the infrastructure one review uses, and how many reviews one server holds at once]`.
- `[MISSING: seats on the hosted service, and whether any team would pay]`. The canvas records "no evidence anyone would pay".
- `[MISSING: what the hosted service gives a customer that the free tool does not]`. At $22 a seat the free tool on the customer's own key gives the same review for the cost of the tokens, $1.05 to $3.14 a month by our estimate.
- `[MISSING: who pays]`: the reviewer, the team or its lead.

**The two versions replaced the same day.**

- **Per review, cost plus a markup.** Markups of 25%, 50% and 100% side by side: $0.0523, $0.0628 and $0.0837 a review through 2026, $0.68 to $1.09 for a developer's 13 reviews, a TAM of $298M to $477M, and 1,466 to 5,862 reviews a month to cover an always-on cost of $61.32 without a server.
- **$27 a seat,** the average of CodeRabbit's $24 and Greptile's $30: a contribution of $23.98 to $26.41, and 4 to 5 seats to cover the always-on cost, both worked out on 13 reviews a month.

Neither set of figures is used anywhere now.

**Two earlier conflicts, as they stand now.**

- **Which model the cost is based on.** The cost sheet prices Qwen3.8 27B and the comparison sheet recommends gpt-oss. Since 2026-10-10 the working model is Gemini 3.8 Flash, which neither sheet covers.
- **Fixed or variable infrastructure.** Read together in section 5, pending confirmation.

---

## 10. Every calculation

| What | Formula and inputs | Result |
|---|---|---|
| Price per seat | ($24 + $20) ÷ 2 | $22.00 |
| Average with Cubic | ($24 + $20 + $40) ÷ 3 | $28.00 |
| Model cost of a review, through 2026 | Mean of (3,739 × 0.75 + 15,534 × 3.75) ÷ 1M and (3,739 × 0.75 + 5,287 × 3.75) ÷ 1M | $0.041844, shown as $0.0418 |
| Model cost of a review, from 2027 | The same tokens at $1.50 and $7.50 | $0.0837 |
| Repository download | 0.073 GB × $0.052; 0.686 GB × $0.052 | $0.0038; $0.0357 |
| Cost per review | $0.0418 + $0.0038; $0.0418 + $0.0357 | $0.0456; $0.0775 |
| Cost per review, from 2027 | $0.0837 + $0.0038; $0.0837 + $0.0357 | $0.0875; $0.1194 |
| Average pull requests per developer | 6,570 pull requests ÷ 263 core developers | 24.98, shown as 25 |
| Cost of a seat, through 2026 | 25 × $0.0456; 75 × $0.0775 | $1.14; $5.81 |
| Cost of a seat, from 2027 | 25 × $0.0875; 75 × $0.1194 | $2.19; $8.95 |
| Contribution | $22 − cost of a seat | $16.19 to $20.86; from 2027, $13.05 to $19.81 |
| Share of the price | Contribution ÷ $22 | 74% to 95%; from 2027, 59% to 90% |
| Reviews before a seat loses money | $22 ÷ cost per review | 284 to 482; from 2027, 184 to 251 |
| Server | 730 × $0.048 | $35.04 |
| `F` | 19.71 + 37.96 + 3.65 + 35.04 | $96.36 |
| Break-even seats | $96.36 ÷ contribution, rounded up | 5 to 6; from 2027, 5 to 8 |
| A seat at its full allowance | 150 × cost per review | $6.85 to $11.63; from 2027, $13.12 to $17.90 |
| What that seat leaves | $22 − the line above | $10.37 to $15.15; from 2027, $4.10 to $8.88 |
| 100 seats, revenue | 100 × $22 × 12 | $26,400 |
| 100 seats, cost of serving | 100 × 12 × cost of a seat | $1,369 to $6,976; from 2027, $2,624 to $10,742 |
| Always-on, one year | $96.36 × 12 | $1,156.32 |
| CodeRabbit's revenue, end of 2024 | $25M ÷ 13.889 | $1.8M |
| CodeRabbit's seats | $1.8M ÷ $288; $25M ÷ $288 | 6,250; 86,806 |
| Seats per $1M raised | 6,250 ÷ 20; 86,806 ÷ 88 | 312.5, shown as 313; 986.4, shown as 986 |
| Our revenue per $1M invested | 312.5 × $264; 986.4 × $264 | $82,500; $260,417, shown as $260,400 |
| Serving cost for those seats, 2027 prices | Seats × 12 × $2.19; × $8.95 | $8,200 to $33,600; $25,900 to $106,000 |
| The leader's path at our price | 86,806 × $264 | $22.9M |
| TAM at $22 | 36.5M × $22 × 12 | $9.636B, shown as $9.6B |
| SAM at $22 | 6.99M and 11.16M × $264 | $1.85B; $2.95B, shown as $1.8B to $2.9B |

Figures are computed on unrounded values and rounded for display, so a hand check on the rounded figures can differ in the last digit.
