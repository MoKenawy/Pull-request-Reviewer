Below is a concise working template you can use as the **economics section of the financial plan**. I’ve kept it aligned with the current project scope and explicitly separated **measured facts, assumptions, and hypotheses**.

# Product Economics & Pricing Research

**Product:** Agentic Code Review  
**Scope:** TS/JS AI-assisted code review  
**Purpose:** Establish the economic basis for pricing and the financial plan.

---

## 1. What does **one review actually cost us?**

### Objective

Determine the **marginal cost of processing one code review** and the fixed infrastructure required to operate the service.

### Cost Model

| Cost Component | Measurement | Cost / Review | Source / Assumption |
|---|---:|---:|---|
| LLM input pricing | Variable | $0.0248 per 1M tokens| found in model-comparison.md |
| LLM output pricing | Variable | $4.35 per 1M tokens| found in model-comparison.m |
| Number of model calls | scales in/out with LLM input/output | $___ | ___ |
| Embeddings / auxiliary models | ___ | $___ | ___ |
| Compute | ___ seconds/minutes | $___ | ___ |
| GitHub/API usage | ___ | $___ | ___ |
| Network | negligble | $___ | ___ |
| Storage | negligble(PR stored on users github) | $___ | ___ |
| Other variable costs | ___ | $___ | ___ |
| **Total variable cost / review** | | **$___** | |

### Fixed Monthly Infrastructure

| Component | Monthly Cost |
|---|---:|
| Cloud compute | $___ |
| Database | $___ |
| Redis / queue | $___ |
| Storage | $___ |
| Monitoring / logging | $___ |
| Other | $___ |
| **Total fixed cost / month** | **$___** |

### Unit Economics

```text
Variable Cost / Review = $____

Average Reviews / Customer / Month = ____

Variable Cost / Customer / Month
= Reviews × Cost / Review
= $____

Fixed Infrastructure / Month
= $____
```

### Key Metrics

```text
Cost per review:              $____
Cost per customer/month:      $____
Fixed infrastructure/month:   $____
```

**Current known constraint (revised 2026-10-03):** the limit of free-tier inference or approximately $20/month for model access applies to building the open-source tool. Under the open-core model ([canvas §5](../003-business-model-canvas.md)) the hosted review service is the paid product: its inference and infrastructure are usage costs, itemised in [`pr-variable-pricing-model.md`](./0051-cost-structure/pr-variable-pricing-model.md) and passed on at cost plus a markup. Neither is yet a validated production unit cost.

---

# 2. What does the market currently charge?

### Objective

Understand how competing products monetize code review and establish the **market pricing range and pricing models**.

### Competitor Pricing Table
| Competitor | Pricing Model | Entry Price | Unit | Included Usage | Overage | Target |
| --- | --- | --- | --- | --- | --- | --- |
| **CodeRabbit** | Hybrid (Seat-based + Metered Overage) | $24 | /dev/mo (billed annually) | Unlimited standard PR reviews per active PR contributor | $0.25 / reviewed file (or $0.40 / min for Agent tasks) | Mid-market & Enterprise dev teams seeking predictable PR pricing |
| **Greptile** | Credit-based Hybrid (Seat + Usage) | $30 | /seat/mo | 50 credits / seat / mo | $1.00 / extra credit (Base review = 1 credit, Plus = 3, Apex = 10) | Fast-moving engineering teams prioritizing deep context reviews |
| **Qodo** | Hybrid (Base Platform Fee + Metered Usage) | $30 | /team/mo | Up to 30 seats base inclusion; credits billed usage-wise | $0.012 / credit pooled across the team | Early-stage startups to mid-market teams looking for a shared base fee |
| **Claude Code Review** | Usage-based Add-on + Platform Seat | $20 | /seat/mo base (Team) + token usage | Platform seats include general Claude access; PR reviews are billed on usage | Metred per token (~$15–$25 average cost per reviewed PR) | Existing Anthropic Team & Enterprise customers running complex PR audits |
| **DeepSource** | Hybrid (Seat-based + Lines of Code Metering) | $24 | /dev/mo | Unlimited static analysis; base AI review quota | $8 per 100K lines of code analyzed for AI features | Organizations focusing on security, SAST compliance, and deep code quality |
### Pricing Models Observed

```text
Subscription
    │
    ├── Per user / seat
    │
    └── Per team

Usage-based
    │
    ├── Per review
    ├── Credits
    └── Token usage

Self-hosted
    │
    └── Software free → customer pays infrastructure
```

The current competitive analysis already identifies subscription, credit-based, and usage-based approaches in this market. :chatgpt-content-reference{index="1"}

### Competitive Positioning

Record:

- Lowest comparable price: **$___**
- Typical price range: **$___ – $___**
- Highest observed price: **$___**
- Dominant pricing model: **___**
- Free-tier availability: **___**
- Self-hosting availability: **___**

### Important Competitive Cost Benchmark

Claude Code Review is currently documented in the project research at approximately **$15–25 in token cost per review**, depending on PR size and verification requirements. This should be independently re-verified before being used in the financial model. :chatgpt-content-reference{index="2"}

---

# 3. What is it actually worth to the customer?

### Objective

Estimate the **economic value created for a customer**, rather than simply asking what price they like.

### Customer Economics

| Metric | Value |
|---|---:|
| PRs / month | ___ |
| Reviews / PR | ___ |
| Reviewer time / PR | ___ min |
| Engineer hourly cost | $___ |
| Review cost / PR | $___ |
| Monthly review cost | $___ |
| Rework incidents / month | ___ |
| Average rework time | ___ hours |
| Monthly rework cost | $___ |
| Other measurable impact | $___ |
| **Estimated monthly economic burden** | **$___** |

### Value Hypothesis

```text
Monthly Customer Value
=
Review Time Saved
+
Rework Avoided
+
Defects / Issues Avoided
+
Other Measurable Savings
```

Then:

```text
Potential Value / Customer / Month = $____
```

This should remain a **hypothesis** until validated through customer interviews/survey data. The business canvas now states the revenue model (open core, decided 2026-10-03), and still records no evidence that anyone would pay.

### Customer Research

Collect:

- PRs per month
- Average review time
- Number of reviewers
- AI-generated PR percentage
- Rework frequency
- Time spent on rework
- Current code-review tooling
- Current monthly spending
- Perceived pain
- Willingness to pay
- Price sensitivity

---

# Final Model

The three studies converge into one pricing model:

```text
                 CUSTOMER VALUE
                      │
                      │ Value ceiling
                      ▼
              ┌───────────────┐
              │ Target Price  │
              └───────────────┘
                      ▲
                      │
          ┌───────────┴───────────┐
          │                       │
          │                       │
   MARKET PRICE              OUR COST
          │                       │
          ▼                       ▼
 Competitor range          Cost / Review
 Competitor model          Cost / Customer
```

## Final Economic Variables

```text
C = Cost per review
R = Reviews per customer / month
F = Fixed monthly infrastructure
P = Customer price / month
V = Estimated customer value / month
N = Number of customers
```

### Customer Contribution

```text
Variable Cost / Customer
= C × R

Contribution / Customer
= P - (C × R)
```

### Monthly Profit

```text
Profit
=
N × [P - (C × R)]
- F
```

### Break-even

```text
Break-even Customers
=
F / [P - (C × R)]
```

### Pricing Constraints

A candidate price should satisfy:

```text
                    P
                    │
          ┌─────────┼─────────┐
          │         │         │
          ▼         ▼         ▼
      P > Cost    P < Value   P ≈ Market
```

More formally:

```text
Cost < Price < Customer Value
```

while the **market price** provides a reference point rather than a hard constraint.

---

## Final Output of the Research

At the end, we should be able to fill this one-page summary:

| Metric | Result |
|---|---:|
| **Cost / review** | **$___** |
| **Average reviews / customer** | **___** |
| **Cost / customer / month** | **$___** |
| **Fixed infrastructure / month** | **$___** |
| **Competitor price range** | **$___ – $___** |
| **Typical competitor pricing model** | **___** |
| **Estimated customer value / month** | **$___** |
| **Validated willingness to pay** | **$___** |
| **Candidate product price** | **$___** |
| **Contribution / customer** | **$___** |
| **Break-even customers** | **___** |

**Decision gate:** don't build the financial plan from the candidate price alone. First establish which numbers are **measured**, which are **competitor facts**, and which remain **hypotheses**. That distinction is particularly important here because the current project has a strong technical thesis but still has unvalidated revenue and customer-value assumptions. :chatgpt-content-reference{index="4"}