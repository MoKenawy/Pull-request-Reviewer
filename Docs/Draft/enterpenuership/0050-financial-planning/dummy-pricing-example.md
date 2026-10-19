Here is the completed economics section of the financial plan populated with realistic, coherent hypothetical numbers for a SaaS startup delivering AI-assisted JavaScript and TypeScript code reviews.

---

## Product Economics & Pricing Research

**Product:** Agentic Code Review

**Scope:** TS/JS AI-assisted code review

**Purpose:** Establish the economic basis for pricing and the financial plan.

---

### 1. What does one review actually cost us?

#### Objective

Determine the marginal cost of processing one code review and the fixed infrastructure required to operate the service.

#### Cost Model

| Cost Component | Measurement | Cost / Review | Source / Assumption |
| --- | --- | --- | --- |
| **LLM input tokens** | 80,000 tokens | $0.20 | $2.50 / 1M tokens (Claude 3.5 Sonnet) |
| **LLM output tokens** | 4,000 tokens | $0.06 | $15.00 / 1M tokens |
| **Number of model calls** | 3 calls | $0.02 | Multi-turn agentic pass / verification |
| **Embeddings / auxiliary models** | 20,000 tokens | $0.002 | $0.10 / 1M tokens (text-embedding-3-small) |
| **Compute** | 12 seconds | $0.005 | Serverless runner processing AST / diff |
| **GitHub / API usage** | 5 API calls | $0.000 | Within GitHub App standard rate limits |
| **Network** | 0.05 GB | $0.001 | AWS data transfer out ($0.09/GB) |
| **Storage** | 10 MB temp | $0.000 | Brief caching / ephemerally stored diffs |
| **Other variable costs** | Logging / Trace | $0.002 | Datadog/LangSmith trace telemetry |
| **Total variable cost / review** | — | **$0.29** | **Sum of marginal review execution costs** |

#### Fixed Monthly Infrastructure

| Component | Monthly Cost |
| --- | --- |
| **Cloud compute** | $180 |
| **Database** | $75 |
| **Redis / queue** | $45 |
| **Storage** | $20 |
| **Monitoring / logging** | $80 |
| **Other** | $100 |
| **Total fixed cost / month** | **$500** |

#### Unit Economics

* **Variable Cost / Review:** $0.29
* **Average Reviews / Customer / Month:** 120
* **Variable Cost / Customer / Month:** 120 × $0.29 = **$34.80**
* **Fixed Infrastructure / Month:** $500.00

#### Key Metrics

* **Cost per review:** $0.29
* **Cost per customer/month:** $34.80
* **Fixed infrastructure/month:** $500.00

*Current known constraint:* The existing business model assumes free-tier inference or approximately $20/month model access and no paid inference infrastructure. This is a spending constraint, not yet a validated production unit cost.

---

### 2. What does the market currently charge?

#### Objective

Understand how competing products monetize code review and establish the market pricing range and pricing models.

#### Competitor Pricing Table

| Competitor | Pricing Model | Entry Price | Unit | Included Usage | Overage | Target |
| --- | --- | --- | --- | --- | --- | --- |
| **CodeRabbit** | Subscription | $15 | / user / mo | Unlimited public PRs / standard repo limits | Pro tier required | SMB to Enterprise |
| **Greptile** | Usage-based | $30 | / repo / mo | 100 PRs / mo | $0.30 / PR | Developer Teams |
| **Qodo** | Subscription | $19 | / user / mo | Standard PR context limits | Custom tier | Engineering Orgs |
| **Claude Code Review** | Token usage | $15 | / PR (avg) | Direct API pay-as-you-go | $0.00 (pass-through) | Internal / Custom Setup |
| **Other (Bito / Sourcery)** | Subscription | $12 | / user / mo | 50 PRs / dev / mo | Soft cap | Individual / Team |

#### Pricing Models Observed

```
Subscription
    │
    ├── Per user / seat ($12 – $25/mo)
    │
    └── Per team ($150 – $500/mo flat)

Usage-based
    │
    ├── Per review ($0.25 – $1.00/PR)
    ├── Credits ($50 for 250 review credits)
    └── Token usage (Direct pass-through API costs)

Self-hosted
    │
    └── Software free → customer pays infrastructure + $500/mo enterprise license

```

#### Competitive Positioning

* **Lowest comparable price:** $12 / user / month
* **Typical price range:** $15 – $30 / user / month
* **Highest observed price:** $200+ / team / month
* **Dominant pricing model:** Per user / seat subscription
* **Free-tier availability:** Yes (Open source repositories & 14-day trials)
* **Self-hosting availability:** Enterprise tiers only

*Important Competitive Cost Benchmark:* Claude Code Review is currently documented in project research at approximately $15–25 in token cost per review, depending on PR size and verification requirements. This should be independently re-verified before being used in the financial model.

---

### 3. What is it actually worth to the customer?

#### Objective

Estimate the economic value created for a customer, rather than simply asking what price they like.

#### Customer Economics (Assumes team of 5 Mid/Senior TS Engineers)

| Metric | Value |
| --- | --- |
| **PRs / month** | 100 |
| **Reviews / PR** | 1.5 |
| **Reviewer time / PR** | 35 min |
| **Engineer hourly cost** | $85 ($175k fully burdened salary) |
| **Review cost / PR** | $49.58 |
| **Monthly review cost** | $4,958.33 |
| **Rework incidents / month** | 4 |
| **Average rework time** | 6 hours |
| **Monthly rework cost** | $2,040.00 |
| **Other measurable impact** | $500.00 (CI/CD pipeline delay savings) |
| **Estimated monthly economic burden** | **$7,498.33** |

#### Value Hypothesis

$$\begin{aligned} \text{Monthly Customer Value} &= \text{Review Time Saved (30\% efficiency gain)} + \text{Rework Avoided (50\% reduction)} \\ &+ \text{Defects Avoided} + \text{Other Savings} \\ &= \$1,487.50 + \$1,020.00 + \$500.00 \\ &= \mathbf{\$3,007.50\text{ / month (per 5-dev team)}} \end{aligned}$$

*Potential Value / Customer / Month:* **$3,007.50**

*This should remain a hypothesis until validated through customer interviews/survey data. The current business canvas explicitly says the revenue model and willingness to pay have not yet been established.*

#### Customer Research Requirements

Collect through discovery calls:

* PRs per month
* Average review time
* Number of reviewers
* AI-generated PR percentage
* Rework frequency
* Time spent on rework
* Current code-review tooling
* Current monthly spending
* Perceived pain
* Willingness to pay
* Price sensitivity

---

### Final Model & Variables

#### Final Economic Variables

* **C (Cost per review):** $0.29
* **R (Reviews per customer / month):** 120
* **F (Fixed monthly infrastructure):** $500.00
* **P (Customer price / month):** $149.00 (Flat team price up to 5 devs)
* **V (Estimated customer value / month):** $3,007.50
* **N (Number of customers):** Variable

#### Customer Contribution

* **Variable Cost / Customer:** $0.29 × 120 = **$34.80**
* **Contribution / Customer:** $149.00 - $34.80 = **$114.20**

#### Monthly Profit

$$\text{Profit} = N \times [\$149.00 - (\$0.29 \times 120)] - \$500.00 = \mathbf{N \times \$114.20 - \$500.00}$$

#### Break-even

$$\text{Break-even Customers} = \frac{\$500.00}{\$114.20} = \mathbf{4.38 \text{ (5 paying teams)}}$$

#### Pricing Constraints Verification

$$\text{Cost (\$34.80)} < \text{Price (\$149.00)} < \text{Customer Value (\$3,007.50)}$$


*Market Reference Point:* $75–$150/mo for a 5-developer seat plan ($15–$30/user/mo). $149/mo falls directly within standard market expectations while preserving an ~76.6% gross margin.

---

### Final Output Summary

| Metric | Result |
| --- | --- |
| **Cost / review** | $0.29 |
| **Average reviews / customer** | 120 |
| **Cost / customer / month** | $34.80 |
| **Fixed infrastructure / month** | $500.00 |
| **Competitor price range** | $12 – $30 / user / month |
| **Typical competitor pricing model** | Per user / seat subscription |
| **Estimated customer value / month** | $3,007.50 |
| **Validated willingness to pay** | $100 – $200 / team / month (Hypothesis) |
| **Candidate product price** | $149.00 / team / month |
| **Contribution / customer** | $114.20 |
| **Break-even customers** | 5 customers |

> **Decision Gate:** Before building the full 3-year financial model, run 10 customer interviews to validate if the **$149/mo candidate price** aligns with developer team budgets, and conduct 50 benchmark test PRs to confirm that variable execution costs remain at or below the **$0.29/review** target.