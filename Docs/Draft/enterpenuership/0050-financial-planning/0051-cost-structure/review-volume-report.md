# Review Volume and Cost per Review — Measurement Report

**Status: non-normative.** A business-side working document, not a specification. It defines nothing to build.

**Date:** 2026-10-09, updated 2026-10-10 · **Task:** 5 of the pitch rework list, "measure average review volume".

Pricing the hosted review service needs two numbers: what one review costs, and how many reviews a customer runs in a month. This report records the runs made so far, the data collected, the runs proposed to finish the measurement, and the decisions still open.

**The product is still experimental, so this report does not pick a model or a price.** Both are inputs to the cost. The report measures tokens, lists prices as scenarios, and keeps cost per review as a formula (section 3).

**Updated 2026-10-10: a working model.** The founder set Gemini 3.8 Flash as the model to assume and gave the go-ahead to run the ladder on it. The formula stays, and Gemini's prices are one more scenario in it, now the base case. The ladder was started and stopped by the provider's free-tier limit of 20 requests a day: two of its five sizes are measured (sections 1.3 and 3.4).

Confidence labels follow [`004-market-study.md`](../../004-market-study.md): **A** is primary data (the GitHub API, OpenRouter's own price list, a run's own report), **C** is our calculation from A inputs.

---

## Summary

- **Usage is measured, as a proxy.** Across ten public TypeScript repositories, a core developer opens about 11 to 13 pull requests a month. For a team of five that is 55 to 65 reviews a month if each pull request is reviewed once, and up to about three times that if every push is re-reviewed (C, from A).
- **Reviewing rests on fewer people than writing does** (added 2026-10-10, section 2.5). In the same repositories, 182 core reviewers did 97.7% of the reviewing, a median of 21.5 pull requests each a month, against 13 opened per core developer (C, from A).
- **Cost per review is a formula, not a number:** tokens × price. The tokens depend on the pull request and the model; the price depends on the model and the provider. Neither model nor price is fixed here.
- **Tokens have been measured twice,** both with gpt-oss-120b: a small demo change (4,634 input, 2,660 output) and one real pull request, microsoft/playwright#43199 (12,441 input, 4,888 output).
- **Prices spread widely, which is why they stay variables.** For the real pull request, the six price scenarios collected so far range from $0.0007 to $0.036 a review, about 54 times apart. Two sources disagree on the price of the same model, and one model's price varies about 20 times between providers (A).
- **Output tokens carry most of the cost:** 66% to 99% of it, in both runs and every scenario. Output is the part that changes most from model to model, so it is the main thing the runs have to measure.
- **The tool's default budget would refuse a share of real pull requests.** It fits about 575 changed lines. Between 4% and 37% of pull requests per repository are larger, 25% across the whole sample (C, an upper bound).
- **Provisional reading, from one real pull request:** in every scenario that review costs under four cents, and a developer's month of reviews comes to between about one cent and about $1.30, against rivals' $24 to $30 per seat. If more runs confirm this, the price will be set by the markup and the fixed costs, not by the model cost.
- **On Gemini 3.8 Flash, a median-size review costs about four cents** (added 2026-10-10, sections 1.3 and 3.4). Five runs completed: three of a 50-line pull request, at $0.0184 on average, and two of a 160-line one, at $0.0418, with the two runs $0.0226 and $0.0611 apart. From 2027-01-01 the provider's prices double, and so do these.
- **Thinking tokens are 99% of the billed output, and the tool does not count them.** The tool recorded 264 output tokens over the five runs; the provider billed 33,936. Any cost worked out from the tool's own count is about 129 times too low on this model.
- **The ladder is not finished.** The key is on the provider's free tier, which allows 20 requests a day for this model. The three larger sizes, which cover the larger half of real pull requests, are not measured on Gemini.
- **No run on Gemini reported a finding.** In all five, the model replied without calling the finding tool, and the build cannot tell "nothing to report" from "did not use the tool".
- **Next:** the three unmeasured sizes (section 4), on a paid key or after the daily limit resets, and the decisions in section 5.

---

## 1. The runs made so far

### 1.1 The demo run

The first run is saved in [`run_review_quickstart.ipynb`](../../../../../notebooks/run_review_quickstart.ipynb) and predates this task: it reviewed the demo repository, not a real pull request.

| | |
|---|---|
| When | 2026-09-26, 16:35 UTC |
| What was reviewed | Uncommitted changes in the demo repository `review-demo`: 7 files changed, 4 reviewed (20 changed lines), 3 listed but not reviewed, 1 excluded |
| Model and provider | `openai/gpt-oss-120b` on Groq, temperature 0 |
| Duration | 7.9 seconds, 7.5 of them in the model step |
| Tokens | 4,634 input and 2,660 output, summed over two model calls (one repair turn) |
| Findings | 1 blocking, 0 important, 1 nit, from 2 `emit_finding` calls |
| Checks and context | None. The build states "No checks were run in this build." and "No related context was gathered in this build." |
| Degradation reported | CF-6 `incomplete-file-coverage`: no finding call named `src/search.ts` or `src/users.ts` |
| Verdict | blocking |

**Against the planted defects.** The demo repository plants six defects ([`make_review_demo.py`](../../../../../scripts/make_review_demo.py)). The run caught two.

| Planted defect | File | Caught? |
|---|---|---|
| A computed value never used | `src/format.js` | Yes, as a nit |
| Every error swallowed; the caller gets `undefined` | `src/retry.ts` | Yes, as blocking |
| SQL injection through string concatenation | `src/search.ts` | No |
| A rejected promise escapes the `try` (missing `await`) | `src/users.ts` | No |
| Loop reads one element past the end | `src/users.ts` | No |
| Empty-array guard removed, so the average is NaN | `src/users.ts` | No |

The four misses are all in the two files the degradation names, so the run reported its own gap.

What this run costs under each price scenario is in section 3.

### 1.2 Pull-request runs

On 2026-10-09 the build gained a pull-request scope, and microsoft/playwright#43199 (section 2.1) was reviewed from the notebook three times. The notebook's saved outputs come from different executions, so each row says where its figures come from.

| Run | Model as set | Outcome | Tokens | Time | Where it is recorded |
|---|---|---|---|---|---|
| A | `openai/gpt-oss-120b` on Groq | Completed: 1 finding call, 1 repair turn | 12,441 input, 4,888 output | 63.8 s: 11.9 s reading the pull request, 50.5 s in the model step | The notebook's saved run metadata, started 15:10 UTC |
| B | `qwen/qwen3.8-27b` on Groq | One finding, then the provider refused the next request: HTTP 413, 7,126 input tokens requested against a limit of 7,000 a minute | Not recorded | 14.6 s | The notebook's saved output |
| C | Not recorded in the output | Completed: 1 finding, a nit, and a reported gap: no finding call named 9 of the 10 reviewed files | Not recorded | 125.4 s, including the clone | Output supplied by the founder; shown on the deck's MVP slide |

What these runs add (A):

- **The first real token counts:** 12,441 input and 4,888 output for a 188-line change, with gpt-oss-120b.
- **Input per model call is about 6,200 to 7,100 tokens** for this pull request: run A used 12,441 over two calls, and run B's refused request was 7,126. The tool's own estimate was 7,200, so it is close.
- **A provider's rate limit is a third variable beside model and price.** Groq serves `qwen/qwen3.8-27b`, but its on-demand tier allows 7,000 input tokens a minute for it, less than one request for this pull request.
- **Still unknown:** which model produced run C, and the token counts of runs B and C.

### 1.3 The ladder on Gemini 3.8 Flash

Run on 2026-10-10 with the script in Appendix B, `gemini-3.8-flash` through the provider's OpenAI-compatible address, temperature 0, budget 80,000, the built-in system prompt. Every run that completed took one model call and no repair turn.

| Run | Pull request | Changed lines reviewed | Files reviewed / listed | Input | Output the tool recorded | Thinking | Output billed | Seconds | Findings | Outcome |
|---|---|---|---|---|---|---|---|---|---|---|
| small 1 | trpc/trpc#7614 | 50 | 2 / 2 | 2,685 | 50 | 4,523 | 4,573 | 117.4 | 0 | No finding call |
| small 2 | trpc/trpc#7614 | 50 | 2 / 2 | 2,685 | 45 | 5,798 | 5,843 | 75.8 | 0 | No finding call |
| small 3 | trpc/trpc#7614 | 50 | 2 / 2 | — | — | — | — | 203.9 | — | Provider error, during a network outage |
| small 3, repeated | trpc/trpc#7614 | 50 | 2 / 2 | 2,685 | 50 | 2,649 | 2,699 | 101.9 | 0 | No finding call |
| median 1 | trpc/trpc#7616 | 160 | 3 / 3 | 3,739 | 67 | 15,467 | 15,534 | 153.0 | 0 | No finding call |
| median 2 | trpc/trpc#7616 | 160 | 3 / 3 | 3,739 | 52 | 5,235 | 5,287 | 96.4 | 0 | No finding call |
| median 3 | trpc/trpc#7616 | 160 | 3 / 3 | — | — | — | — | 251.6 | — | Refused: daily limit (HTTP 429) |
| Playwright 1 to 3 | microsoft/playwright#43199 | 188 | 10 / 16 | — | — | — | — | 78 to 80 | — | Refused: daily limit |
| budget edge 1 and 2 | n8n-io/n8n#39795 | 574 | 15 / 15 | — | — | — | — | 100 to 106 | — | Refused: daily limit |
| budget edge 3, large 1 to 3 | n8n-io/n8n#39795, excalidraw/excalidraw#12142 | 574, 1,690 | | | | | | | | Not started |

"Output billed" is the provider's total minus the input (Calculated), and "thinking" is that minus the output the tool recorded. A first trial run of the small pull request, made before the script kept the provider's total, recorded 2,685 input and 49 output tokens in 67.7 seconds; it is not in the table.

What these runs show (A for the counts, C for what is worked out from them):

- **Thinking tokens are almost all of the billed output:** 98.9% for the small pull request and 99.4% for the median one. The provider's price list says output is charged "including thinking tokens".
- **The tool's own output count leaves them out.** The provider's OpenAI-compatible reply puts thinking tokens only in its total, and the build adds up the input and output fields ([`accounting.py`](../../../../../src/agentic_review/core/review/accounting.py)). Over the five runs it recorded 264 output tokens where 33,936 were billed, about 129 times fewer. On this provider the tool's report cannot be used to work out cost. That is an engineering matter, reported here and not changed.
- **Output varies a great deal between identical runs.** The same 160-line pull request, at temperature 0, was billed 15,534 output tokens once and 5,287 the next time. The small one ranged from 2,699 to 5,843. Three runs per size is too few to pin an average down.
- **Input is small and steady:** 2,685 tokens for 50 changed lines and 3,739 for 160, the same in every run. That is about 9.6 tokens for each further changed line (Calculated: (3,739 − 2,685) ÷ (160 − 50)), far below the tool's own estimate of 33, which overestimates on purpose. Two sizes do not make a trend.
- **No run reported a finding.** In all five the model answered without calling `emit_finding`, and the build reported the gap itself: "this build cannot tell a change with nothing to report from a model that did not use the finding tool." What the model said instead is not kept in the report. The two tRPC pull requests may have nothing worth reporting; these runs cannot show it either way.
- **A review took 76 to 153 seconds,** the clone included, in one model call.
- **The free tier stops at 20 requests a day.** The provider's refusal reads: "Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 20, model: gemini-3.8-flash". This session got seven answers from the model before the refusals began, so the rest of the day's 20 were used some other way: by earlier use of the same key, or by requests that failed. Which is not known. A team of five opening 55 to 65 pull requests a month would fit in that limit only if no day had more than 20 model calls.
- **Still unknown on this model:** the cost of the three larger sizes, and whether it reports findings on a change that has defects.

Since section 2.1 was written, microsoft/playwright#43199 was closed without being merged, on 2026-10-09 at 18:09 UTC. The tool still reads it. The other four pull requests were open at their recorded heads on 2026-10-10.

---

## 2. Data collected

### 2.1 The pull request chosen for the first real run

| | |
|---|---|
| Pull request | [microsoft/playwright#43199](https://github.com/microsoft/playwright/pull/43199), "fix(core): make playwright-core bundlable into a single file" |
| State on 2026-10-09 | Open, not a draft, 1 commit, opened 2026-10-07, head `af4a20e`, targets `main` |
| Size | +169 −38 lines in 16 files |
| What the tool will review | 10 TypeScript/JavaScript files, 188 changed lines |
| Listed but not reviewed | 6 files, 19 changed lines: four `DEPS.list` files, one workflow file, one shell script |
| Diff size | 21,472 characters in all; 18,635 in the reviewed files |
| Against the budget | About 7,200 estimated tokens with the instructions, inside the 20,000 default (C) |

"Estimated tokens" is the tool's own estimate, characters divided by three ([`budget.py`](../../../../../src/agentic_review/core/assembly/budget.py)).

How the build will read it: the pull-request scope added on 2026-10-09 ([ADR-0011](../../../../adr/0011-cli-reads-a-public-pull-request.md)) clones the repository without checking it out and compares the pull request's head with the default branch. No checks run and no settings are read from the pull request.

### 2.2 Pull-request volume in ten public TypeScript repositories

Every pull request opened in September 2026 in ten repositories was read from the GitHub API on 2026-10-09: 8,849 pull requests, 7,670 of them opened by human accounts (A). July and August add the opened counts only. Appendix A has the query and the definitions.

A **core developer** is a non-bot account that opened at least four pull requests in the month, about one a week.

| Repository | Opened Jul / Aug / Sep | Bot share (Sep) | Human authors | Core developers | Share of human PRs from core | PRs per core developer, median (mean) | Commits per PR, median (mean) |
|---|---|---|---|---|---|---|---|
| angular/angular | 354 / 370 / 504 | 0% | 65 | 23 | 87% | 11 (19.0) | 1 (1.1) |
| excalidraw/excalidraw | 137 / 162 / 142 | 0% | 95 | 4 | 29% | 4.5 (10.2) | 1 (17.6) |
| microsoft/playwright | 377 / 261 / 316 | 13% | 58 | 10 | 79% | 10 (21.8) | 1 (1.6) |
| microsoft/vscode | 2,093 / 2,418 / 2,593 | 12% | 270 | 59 | 89% | 20 (34.4) | 2 (5.0) |
| n8n-io/n8n | 1,691 / 1,724 / 2,200 | 22% | 167 | 83 | 94% | 14 (19.3) | 3 (8.5) |
| nestjs/nest | 143 / 211 / 270 | 47% | 39 | 8 | 67% | 10.5 (12.0) | 1 (1.7) |
| supabase/supabase | 825 / 911 / 945 | 6% | 203 | 41 | 76% | 11 (16.4) | 2 (4.1) |
| trpc/trpc | 23 / 94 / 51 | 8% | 24 | 1 | 45% | 21 (21.0) | 1 (2.3) |
| twentyhq/twenty | 1,106 / 1,292 / 1,633 | 9% | 104 | 29 | 93% | 16 (47.3) | 3 (8.5) |
| vitest-dev/vitest | 131 / 196 / 195 | 7% | 95 | 5 | 42% | 7 (15.2) | 1 (3.9) |

**Pull requests per developer** (C).

- The median across the ten repositories is **11 a month**, from 4.5 to 21.
- Pooled over all 263 core developers the median is **13 a month**. A quarter open 6 or fewer and a quarter open 31 or more.
- The pooled mean is 25, pulled up by a few people who open 100 to 200 a month. This report uses the median.

**From pull requests to reviews** (C).

Reviews per developer per month = pull requests per developer per month × reviews per pull request.

| Trigger assumed | Reviews per pull request | Per developer per month | Team of five per month |
|---|---|---|---|
| Once, when the pull request is opened | 1 | 11 to 13 | 55 to 65 |
| On every push | 1 to 3, from the median commits per pull request | 11 to 39 | 55 to 195 |

The team of five is an illustration; it is the team size [`dummy-pricing-example.md`](../dummy-pricing-example.md) assumes. That example's 120 reviews a month falls inside this range.

**Bots.** Bot accounts opened 1,179 of the 8,849 pull requests, 13%. Most are dependency and release automation. AI coding agents appear as bot accounts in three repositories: `copilot-swe-agent` opened 86 pull requests in VS Code and 1 in Playwright, and `claude` opened 28 in Supabase.

**Limits of this proxy.**

- These are open-source projects, most of them backed by a company. They stand in for company teams until the pilot measures real ones.
- The per-pull-request details cover September only.
- Commit count is a rough stand-in for pushes. Squash and force-push workflows hide pushes (Angular's mean is 1.1), and one push can carry several commits.
- AI-written pull requests opened from a person's own account cannot be told apart from hand-written ones.

### 2.3 Pull-request size and the tool's budget

"Changed lines" is additions plus deletions, for human-authored pull requests opened in September.

| Repository | Median | P75 | P90 | Share over about 575 changed lines |
|---|---|---|---|---|
| angular/angular | 53 | 187 | 644 | 10% |
| excalidraw/excalidraw | 183 | 817 | 1,798 | 30% |
| microsoft/playwright | 48 | 107 | 318 | 6% |
| microsoft/vscode | 151 | 470 | 1,314 | 22% |
| n8n-io/n8n | 286 | 885 | 1,889 | 35% |
| nestjs/nest | 96 | 201 | 597 | 11% |
| supabase/supabase | 81 | 298 | 838 | 15% |
| trpc/trpc | 124 | 964 | 3,726 | 30% |
| twentyhq/twenty | 291 | 1,092 | 2,814 | 37% |
| vitest-dev/vitest | 42 | 97 | 205 | 4% |

- **Pooled over all 7,670 pull requests:** median 155 changed lines, P75 581, P90 1,625, P95 2,923. The mean is 3,267, dominated by a few enormous pull requests, so it is not used.
- **The Playwright pull request**, at 207 changed lines, sits a little above the pooled median. Within Playwright it is larger than 86% of September's pull requests.
- **The default budget fits about 575 changed lines** (C). The estimate comes from one pull request: its reviewed files carry 99 characters of diff per changed line, which is 33 estimated tokens a line, plus about 1,000 for the instructions, against the 20,000 default in [`settings.py`](../../../../../src/agentic_review/core/config/settings.py).
- **So a share of real pull requests would be refused as the build stands:** 4% to 37% by repository, 18% at the median repository, 25% of the pooled sample. This is an upper bound, because it counts every changed line as TypeScript or JavaScript, and lock files, snapshots and generated files are not reviewed.

That default is a stated placeholder (SRS §8, TBD-3). This figure is a first input for setting it.

**Update, 2026-10-10.** In the working tree the default is now 200,000, a change that is staged and not yet committed. By the same estimate that fits about 6,030 changed lines (Calculated: (200,000 − 1,000) ÷ 33), and 145 of the 7,670 pull requests are larger: 1.9% of the pooled sample, from 0% to 6% by repository. The "25% refused" finding above describes the 20,000 default.

### 2.4 Model prices collected

These are scenarios, not a choice. Prices are per 1M tokens.

| Model | Source | Input | Output | Cache read |
|---|---|---|---|---|
| gpt-oss-20b | [`model-comparison.md`](./model-comparison.md), dated 2026-10-01 | $0.018 | $0.09 | not given |
| gpt-oss-120b | [`model-comparison.md`](./model-comparison.md) | $0.03 | $0.17 | not given |
| Qwen3.8 27B | The cost sheet, [`pr-variable-pricing-model.md`](./pr-variable-pricing-model.md) | $0.0248 | $4.35 | $0.0198 |
| Qwen3.8 27B | OpenRouter's default listing, read 2026-10-09 (A) | $0.425 | $2.55 | $0.085 |
| Qwen3.8 27B | OpenRouter, range across its 19 providers (A, Appendix C) | $0.045 to $0.99 | $1.40 to $5.25 | $0.0198 to $0.99 |
| Gemini 3.8 Flash, paid tier, through 2026-12-31 | Supplied by the founder on 2026-10-10 and re-read on [Google's pricing page](https://ai.google.dev/gemini-api/docs/pricing) the same day (A) | $0.75 | $3.75, "including thinking tokens" | $0.075 |
| Gemini 3.8 Flash, paid tier, from 2027-01-01 | Same | $1.50 | $7.50 | $0.15 |
| Gemini 3.8 Flash, free tier | Same | Free | Free | Free |

Three things in this table are the reason prices are treated as variables:

- **Two sources disagree on the same model.** No OpenRouter provider lists the cost sheet's input or output price for Qwen3.8 27B today; only its cache-read price matches one provider.
- **One model has many prices.** Qwen3.8 27B's input price varies about 20 times between providers. OpenRouter routes each request to one of them, so the price paid changes from request to request unless a provider is pinned.
- **The model itself is open.** The comparison sheet recommends gpt-oss for text-only work, the cost sheet prices Qwen, and the build's default is a placeholder model on NVIDIA NIM's free tier.

The gpt-oss prices and the cost sheet's 5.5% OpenRouter fee were taken as written and not re-checked.

**Gemini 3.8 Flash is the working model since 2026-10-10.** Two things about its price list matter here. Every paid price doubles on 2027-01-01. And the free tier is not a basis for a paid service: it is limited to 20 requests a day for this model (section 1.3), and the same page marks free-tier content as used to improve the provider's products.

### 2.5 Who reviews: reviewers per repository and their load

Added on 2026-10-10, after the reviewer was set as the project's one audience ([`000-problem-and-audience.md`](../../000-problem-and-audience.md)). The reviews on the same 7,670 human pull requests were read from the GitHub API (A). Appendix A has the query and the definitions.

A **reviewer** is a non-bot account that reviewed at least one pull request it did not open. A **core reviewer** reviewed at least four different pull requests in the month, the same threshold as a core developer.

| Repository | Human PRs | With a human review | Merged with none | Reviewers | Core reviewers | Core developers | PRs reviewed per core reviewer, median | Share of reviewing done by the top 3 |
|---|---|---|---|---|---|---|---|---|
| angular/angular | 504 | 75% | 9% | 28 | 10 | 23 | 14.5 | 75% |
| excalidraw/excalidraw | 142 | 6% | 79% | 2 | 2 | 4 | 4.5 | 100% |
| microsoft/playwright | 276 | 78% | 1% | 6 | 4 | 10 | 55.5 | 87% |
| microsoft/vscode | 2,288 | 75% | 0% | 62 | 45 | 59 | 27 | 33% |
| n8n-io/n8n | 1,714 | 76% | 2% | 99 | 75 | 83 | 16 | 13% |
| nestjs/nest | 144 | 30% | 71% | 5 | 2 | 8 | 22 | 96% |
| supabase/supabase | 892 | 71% | 1% | 69 | 29 | 41 | 16 | 33% |
| trpc/trpc | 47 | 6% | 91% | 1 | 0 | 1 | none | 100% |
| twentyhq/twenty | 1,482 | 67% | 13% | 16 | 11 | 29 | 66 | 67% |
| vitest-dev/vitest | 181 | 50% | 21% | 6 | 4 | 5 | 26 | 91% |

"Merged with none" is the share of merged human pull requests with no recorded human review. In the small projects it is mostly maintainers merging their own work.

**Pooled over the ten repositories** (C).

- **Most pull requests get a human review, from few people.** 5,384 of 7,670 (70.2%) had at least one; 363 of 5,394 merged ones (6.7%) had none.
- **182 core reviewers did 97.7% of the reviewing,** 6,897 of 7,058 reviewer-and-pull-request pairs. There are 263 core developers, so 0.69 core reviewers for each; the median repository has 0.47.
- **A core reviewer reviews more than a core developer writes:** a median of 21.5 pull requests a month, against 13 opened. A quarter review 42 or more.
- **The work is concentrated.** The top fifth of all 294 reviewers did 73% of it, and the top tenth 55%. In five of the ten repositories, three people did more than 85%.
- **Reviewers and authors are mostly the same people.** 182 of the 263 core developers (69.2%) reviewed someone else's pull request that month, 157 (59.7%) at least four. 227 of the 294 reviewers (77.2%) also opened one.
- **Reviewers already receive automated comments.** A bot account reviewed 5,711 of the 7,670 human pull requests (74.5%), and more than half of them in five of the ten repositories. Bot accounts here include security scanners and CI bots as well as AI reviewers, so this is an upper bound on AI review. Which tools they are is left to the differentiator check (task 2).
- **A first human review usually arrives the same day:** median 2.7 hours, three quarters within 24 hours, a tenth after 94 hours or more.

**Limits.** The limits in section 2.2 apply. Two more: a review left as plain conversation comments is not counted, and review of pull requests opened late in September may not have happened yet when the data was read on 2026-10-09.

---

## 3. The cost model: model and price as variables

### 3.1 The formula

```text
cost per review                    = (T_in × P_in + T_out × P_out) × (1 + f)
model cost per developer per month = R × cost per review
```

| Variable | Meaning | Depends on | Known so far |
|---|---|---|---|
| `T_in` | Input tokens per review | The size of the pull request, the instructions, and how many model calls the review takes. Roughly the same for every model | Two runs, each over two calls: 4,634 for 20 changed lines, and 12,441 for 188. The tool's own estimate is about 1,000 plus 33 per changed line, per call, and it overestimates on purpose |
| `T_out` | Output tokens per review, including any reasoning tokens | **The model**, and how many findings it reports | gpt-oss-120b, two runs: 2,660 and 4,888. Gemini 3.8 Flash, five runs: 2,699 to 15,534 billed, of which 45 to 67 were visible output. The tool's own count leaves thinking tokens out on Gemini, so `T_out` there is the provider's total minus `T_in` |
| `P_in`, `P_out` | Price per input and output token | The model and the provider. A provider's rate limits decide whether a request is served at all | Six scenarios in section 2.4 |
| `f` | Platform fee | The route to the model | 0 when calling a provider directly; 5.5% for OpenRouter in the cost sheet |
| `R` | Reviews per developer per month | The team and the trigger | 11 to 13 if each pull request is reviewed once; up to 39 on every push (section 2.2) |

The build does not report cached tokens separately, so a cache-read term is left out for now.

### 3.2 The demo run under each price scenario

The token counts are the demo run's: 4,634 input and 2,660 output, from gpt-oss-120b on a 20-line change. Applying another model's price to them is an illustration, because another model would produce a different output count. Costs are before the platform fee. `R` is shown at 12, the middle of the once-per-pull-request range, and at 36, three times that.

| Scenario | `P_in` / `P_out` per 1M | Cost per review | Per developer per month, `R` = 12 | `R` = 36 |
|---|---|---|---|---|
| gpt-oss-20b | $0.018 / $0.09 | $0.0003 | $0.004 | $0.012 |
| gpt-oss-120b, the model that produced these tokens | $0.03 / $0.17 | $0.0006 | $0.007 | $0.021 |
| Qwen3.8 27B, cost sheet | $0.0248 / $4.35 | $0.0117 | $0.14 | $0.42 |
| Qwen3.8 27B, OpenRouter default listing | $0.425 / $2.55 | $0.0088 | $0.11 | $0.32 |
| Qwen3.8 27B, cheapest provider for this run | $0.14 / $1.40 | $0.0044 | $0.05 | $0.16 |
| Qwen3.8 27B, dearest provider | $0.80 / $5.25 | $0.0177 | $0.21 | $0.64 |

What the table shows already (C):

- **The spread is about 55 times** between the cheapest and the dearest scenario, for the same tokens.
- **Output tokens carry 74% to 99% of the cost** in every scenario. `T_out` is also the variable that depends most on the model, so it is what the runs most need to measure.
- **Every scenario is small against a seat price.** Rivals charge $24 to $30 per developer per month; the largest figure here is $0.64. Real pull requests are larger than this demo change, so the measured figures will be higher, but the gap is wide.

### 3.3 The real pull-request run under each price scenario

The same scenarios applied to run A: 12,441 input and 4,888 output tokens, from gpt-oss-120b on microsoft/playwright#43199, a 188-line change. The same caution holds: another model would produce a different output count.

| Scenario | `P_in` / `P_out` per 1M | Cost per review | Per developer per month, `R` = 12 | `R` = 36 |
|---|---|---|---|---|
| gpt-oss-20b | $0.018 / $0.09 | $0.0007 | $0.008 | $0.024 |
| gpt-oss-120b, the model that produced these tokens | $0.03 / $0.17 | $0.0012 | $0.014 | $0.043 |
| Qwen3.8 27B, cost sheet | $0.0248 / $4.35 | $0.0216 | $0.26 | $0.78 |
| Qwen3.8 27B, OpenRouter default listing | $0.425 / $2.55 | $0.0178 | $0.21 | $0.64 |
| Qwen3.8 27B, cheapest provider for this run | $0.14 / $1.40 | $0.0086 | $0.10 | $0.31 |
| Qwen3.8 27B, dearest provider | $0.80 / $5.25 | $0.0356 | $0.43 | $1.28 |

- **The spread is the same:** about 54 times between the cheapest and the dearest scenario.
- **Output tokens carry 66% to 99% of the cost** here, a little less than in the demo run, because a real change has a longer prompt.
- **The gap to a seat price holds on real code:** the largest figure is $1.28 a developer a month, against rivals' $24 to $30.

This is one pull request of roughly median size, run once with one model. The ladder in section 4 is what turns it into an average.

### 3.4 Cost per review on Gemini 3.8 Flash

Section 1.3's token counts at the paid-tier prices, with `f` = 0 because the provider is called directly (C).

| Size | Runs | Input | Output billed, mean (range) | Cost per review through 2026-12-31, mean (range) | Cost per review from 2027-01-01, mean |
|---|---|---|---|---|---|
| Small, 50 changed lines | 3 | 2,685 | 4,372 (2,699 to 5,843) | $0.0184 ($0.0121 to $0.0239) | $0.0368 |
| Median, 160 changed lines | 2 | 3,739 | 10,410 (5,287 to 15,534) | $0.0418 ($0.0226 to $0.0611) | $0.0837 |

One row worked through: median run 1 is (3,739 × $0.75 + 15,534 × $3.75) ÷ 1,000,000 = $0.0028 + $0.0583 = $0.0611.

- **The base case for the financials is $0.0418 a review,** the mean of the two median-size runs. 160 changed lines is close to the pooled median of 155 (section 2.3), and 50.6% of the 7,670 sampled pull requests are that size or smaller. It is a typical review, not an average one.
- **The real average is higher, by an unmeasured amount.** A quarter of pull requests are over 581 changed lines, and none that large has been run on this model.
- **Output is 92% of the cost** across the five runs (Calculated: 33,936 × $3.75 against 15,533 × $0.75 for the input).
- **Per developer per month:** $0.54 at 13 reviews and $1.63 at 39, model cost only, through 2026; $1.09 and $3.26 from 2027 (Calculated: 13 and 39 × the base case).
- **For comparison, the gpt-oss-120b run of the Playwright pull request** (12,441 input and 4,888 output) would cost $0.0277 at Gemini's 2026 prices. It is not a Gemini measurement: Gemini's output count for that pull request is unknown.

The prices, the margins and the break-even built on this are in [`0052-unit-economics-and-financials.md`](../0052-unit-economics-and-financials.md).

---

## 4. Proposed runs

**State on 2026-10-10:** the small and median steps are measured on Gemini 3.8 Flash (section 1.3). The Playwright, budget-edge and large steps are not: the provider's free tier refused them. They need a key on the paid tier, at an estimated cost under $1 for all nine runs, or one more day for each 20 requests.

One pull request cannot give an average, so the proposal is a ladder of five open pull requests of different sizes. Each is almost entirely TypeScript or JavaScript, and all were open on 2026-10-09.

| Step | Pull request | Changed lines | Files | Head | Repository size |
|---|---|---|---|---|---|
| Small | [trpc/trpc#7614](https://github.com/trpc/trpc/pull/7614) | 50 | 2 | `43379bf` | 73 MB |
| Median | [trpc/trpc#7616](https://github.com/trpc/trpc/pull/7616) | 160 | 3 | `4bf746b` | 73 MB |
| Your choice, already run (section 1.2) | [microsoft/playwright#43199](https://github.com/microsoft/playwright/pull/43199) | 207 (188 reviewed) | 16 | `af4a20e` | 245 MB |
| Budget edge | [n8n-io/n8n#39795](https://github.com/n8n-io/n8n/pull/39795) | 574 | 15 | `5fc5db8` | 686 MB |
| Large, about P90 | [excalidraw/excalidraw#12142](https://github.com/excalidraw/excalidraw/pull/12142) | 1,690 | 8 | `88acf0d` | 107 MB |

**How they would be run.**

- **The model and the provider are parameters of each run.** The script in Appendix B takes them on the command line, and each result records which model and provider produced it, so results from different models sit side by side.
- **More than one model is worth running.** The ladder on a second model costs cents and shows how `T_out` moves with the model, which is the largest unknown in the formula.
- **A run only works if the provider serves the model and its limits allow the request.** Run B shows the second half: Groq serves `qwen/qwen3.8-27b`, but its on-demand limit of 7,000 input tokens a minute refused a request for the Playwright pull request.
- **Three runs per pull request per model**, 15 per model, because output tokens vary between runs.
- **Budget raised to 80,000** for these runs, so the two largest are measured, not refused. The large one comes to about 57,000 estimated tokens.
- **Recorded per run:** model, provider, input and output tokens, duration, repair turns, findings by severity, degradations, and the full JSON report.
- **Head commits are noted above** because an open pull request can change before it is run.

**Estimated cost: under $1 per model, even at the dearest prices collected** (C). The 15 runs come to about 280,000 estimated input tokens, $0.28 at the dearest input price. Output is unknown; assuming up to 8,000 tokens a run, it adds $0.63 at the dearest output price. At gpt-oss-120b's prices the same runs cost about 3 cents.

**What the results become.** Input tokens against changed lines give the fixed part and the per-line part of `T_in`. Output tokens per run give `T_out` for each model. With the size distribution in section 2.3, that gives average tokens per review; section 3's formula then turns any model's price into a cost per review and a cost per developer per month.

---

## 5. Open decisions

**State on 2026-10-10.** Decisions 1 to 3 below were answered: go ahead, on Gemini 3.8 Flash, with the full ladder. Decision 4 is carried as both cases in the financials. Two new ones replace them:

- **How to finish the ladder:** enable billing on the key, or run the remaining nine reviews over later days inside the free limit.
- **Whether the tool should record thinking tokens.** Until it does, its own report understates cost on this provider. That is a change to the build, for the engineering side.

The original list, as written on 2026-10-09:

1. **Go-ahead to run the ladder.** The runs call a paid or rate-limited provider with your key. The Playwright pull request has now been run from the notebook; the other four steps have not.
2. **Which models to measure first.** This is not a choice of model for the product, only of what to measure now. Recommended: start with whatever the keys you have can reach, and add models as keys appear. So far gpt-oss-120b on Groq completes the Playwright pull request, and `qwen/qwen3.8-27b` on Groq's on-demand tier does not.
3. **The five-step ladder, or the Playwright pull request alone.** Recommended: the ladder, since an average needs more than one size.
4. **Which trigger to assume when turning pull requests into reviews:** once per pull request, or on every push. The two differ by up to three times. Recommended: carry both, once per pull request as the base case, until the pricing unit is settled (task 4).

**No longer a decision:** which model the service uses and what it costs. On 2026-10-09 both were left as variables while the product is experimental. On 2026-10-10 Gemini 3.8 Flash became the working assumption; the model and its price remain parameters of the formula.

**Carried forward, not decisions for this task:**

- The 20,000-token default budget refuses up to a quarter of real pull requests. That belongs to the engineering side (TBD-3).
- The cost sheet writes Qwen's prices into its equation as fixed numbers. When the financials are built (task 6), they become the parameters `P_in` and `P_out`.

---

## Appendix A — How the volume data was collected

- **Source:** GitHub's GraphQL search API, called through the `gh` command-line tool on 2026-10-09. Read-only.
- **Sample:** ten repositories whose main language on GitHub is TypeScript, active in the period, of different sizes, most with a company-employed core team.
- **Period:** every pull request created from 2026-09-01 to 2026-09-30, with its author, account type, additions, deletions, changed files, commit count and state. For July and August, only the count of pull requests opened, from the REST search API.
- **Query**, one per repository and date range. A range with more than 1,000 results was split in half, because the search API returns 1,000 at most.

```graphql
query($q: String!, $after: String, $n: Int!) {
  search(query: $q, type: ISSUE, first: $n, after: $after) {
    issueCount
    pageInfo { hasNextPage endCursor }
    nodes { ... on PullRequest {
      number createdAt merged isDraft state additions deletions changedFiles
      commits { totalCount }
      author { login __typename }
    } }
  }
}
```

with `$q` set to, for example, `repo:microsoft/playwright is:pr created:2026-09-01..2026-09-30`.

- **Definitions.** A *human* pull request has an author whose account type is not `Bot`; a pull request with a deleted author counts as a bot. A *core developer* opened at least four human pull requests in September. *Changed lines* is additions plus deletions. *Commits per pull request* is the count at the time of reading.
- **The raw data is not in the repository.** It is 8,849 records in a temporary working folder, and the query above reproduces it in about 15 minutes.
- **Reviews (section 2.5)** were read on 2026-10-09 for the same pull requests, by number, in batches of 40: for each, up to 60 reviews with the reviewer's account, account type, review state and time. A *human review* is a review in any state except pending, by a non-bot account other than the pull request's author. Twenty-eight pull requests had more than 60 reviews and are counted on their first 60. This second read takes about 20 minutes.

---

## Appendix B — The measurement script and settings

Neither file is in the repository. Both were run on 2026-10-10 for section 1.3, with two additions to the script below: it records the provider's total token count for each model call, through a LangChain callback, and it removes the `LANGFUSE_*` variables from the environment so that every run uses the built-in system prompt. The script calls the same `run_review` the command line calls, then reads the token counts from the report the pipeline already builds. It depends on the `pr` field added to `ReviewRequest` on 2026-10-09.

**Settings.** Model-neutral on purpose: the model and the provider are passed to each run.

```yaml
schemaVersion: 1
agent:
  requestTimeoutSeconds: 180   # a guess: a reasoning model on a real pull request can pass the 60-second default
budget:
  maxTokens: 80000             # for the measurement only, so the largest pull requests are measured, not refused
```

**One run**, from the project root:

```text
uv run --env-file .env python measure_review.py --pr <pull request URL> --config measure.yml --out <folder>
    --model <model id> --base-url <provider address> --key-env <variable holding that provider's key>
```

`--key-env` lets `.env` hold one key per provider. The tool itself reads only `AGENTIC_REVIEW_API_KEY`, so the script copies the named variable into it for that run. It never prints or stores the key.

**Script**

```python
"""Run one review of a public pull request and record what it used: tokens, time, findings.

    uv run --env-file .env python measure_review.py --pr https://github.com/OWNER/REPO/pull/N --config measure.yml \
        --out DIR --model MODEL_ID --base-url PROVIDER_ADDRESS [--key-env NAME_OF_KEY_VARIABLE]

The model and the provider are parameters of a run, not fixed choices: each result records which model produced it,
so results from different models can sit side by side. The provider key is read from the environment, as the tool
itself does; this script never prints or stores it.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from agentic_review.agents.pipeline_agent import ReviewRequest, Reviewed, run_review
from agentic_review.agents.review_port import build_review_port
from agentic_review.core.output.json_out import to_json

sys.stdout.reconfigure(encoding="utf-8")

KEY_VARIABLE = "AGENTIC_REVIEW_API_KEY"  # the only variable the tool reads a credential from

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("--pr", required=True, help="the pull request URL")
parser.add_argument("--config", required=True, type=Path, help="settings file (budget, timeouts)")
parser.add_argument("--out", required=True, type=Path, help="directory for the report and the summary line")
parser.add_argument("--model", help="model id for this run; overrides the settings file")
parser.add_argument("--base-url", help="provider address for this run; overrides the settings file")
parser.add_argument("--key-env", default=KEY_VARIABLE, help=f"variable holding this provider's key (default {KEY_VARIABLE})")
parser.add_argument("--label", default="", help="a note stored with the summary, e.g. the size step")
args = parser.parse_args()

env = dict(os.environ)
if args.key_env != KEY_VARIABLE:
    if not env.get(args.key_env):
        print(f"COULD NOT START:\nThe environment variable {args.key_env} is not set.")
        sys.exit(3)
    env[KEY_VARIABLE] = env[args.key_env]


def with_model(agent_settings, credential):
    overrides = {k: v for k, v in {"model": args.model, "base_url": args.base_url}.items() if v}
    return build_review_port(agent_settings.model_copy(update=overrides), credential)


request = ReviewRequest(cwd=Path.cwd(), pr=args.pr, config_path=args.config)
started = time.perf_counter()
result = run_review(request, env=env, port_factory=with_model if (args.model or args.base_url) else None)
elapsed = time.perf_counter() - started

if not isinstance(result, Reviewed):
    print("COULD NOT START:\n" + result.message)
    sys.exit(3)

report = result.report
run = report.run
files = report.change_summary.files
reviewed = [f for f in files if f.reviewed]
summary = {
    "pr": args.pr,
    "label": args.label,
    "model": run.model,
    "provider": run.provider,
    "verdict": report.verdict,
    "completion": run.completion_status,
    "seconds": round(elapsed, 1),
    "tokens_in": run.tokens_in,
    "tokens_out": run.tokens_out,
    "repair_turns": run.repair_turns,
    "tool_calls": run.tool_calls_total,
    "files_listed": len(files),
    "files_reviewed": len(reviewed),
    "lines_added_reviewed": sum(f.added_lines for f in reviewed),
    "lines_removed_reviewed": sum(f.removed_lines for f in reviewed),
    "findings": len(report.findings),
    "findings_by_severity": {s: sum(1 for f in report.findings if f.severity == s) for s in ("blocking", "important", "nit")},
    "degradations": [f"{d.source} {d.code}" for d in report.degradations],
}

args.out.mkdir(parents=True, exist_ok=True)
stem = args.pr.rstrip("/").split("/")[-3] + "-" + args.pr.rstrip("/").split("/")[-1] + "-" + str(run.model).replace("/", "_")
(args.out / f"{stem}.report.json").write_text(to_json(report), encoding="utf-8")
with (args.out / "runs.jsonl").open("a", encoding="utf-8") as log:
    log.write(json.dumps(summary) + "\n")

print(json.dumps(summary, indent=2))
```

---

## Appendix C — Qwen3.8 27B providers on OpenRouter

Read on 2026-10-09 from OpenRouter's public endpoint list for `qwen/qwen3.8-27b` (A). Prices are per 1M tokens. All 19 support tool calls, which the build requires.

| Provider | Input | Output | Cache read |
|---|---|---|---|
| Wafer | $0.0450 | $2.30 | $0.0198 |
| DekaLLM | $0.0490 | $3.00 | $0.0200 |
| Darkbloom | $0.0500 | $2.20 | $0.0250 |
| Ionstream | $0.0893 | $2.35 | $0.0850 |
| Reka | $0.1400 | $1.40 | $0.0350 |
| Phala | $0.1500 | $1.875 | $0.0375 |
| DeepInfra | $0.1500 | $1.875 | $0.0375 |
| Mancer 2 | $0.2000 | $2.50 | not listed |
| AkashML | $0.2250 | $1.98 | $0.0500 |
| Parasail | $0.2400 | $2.20 | $0.0500 |
| Chutes | $0.2400 | $2.20 | $0.0240 |
| CoreWeave | $0.4000 | $3.00 | $0.1500 |
| Novita | $0.4200 | $3.00 | $0.0850 |
| Alibaba | $0.4250 | $2.55 | $0.0850 |
| Near AI | $0.4400 | $3.30 | $0.0440 |
| Cloudflare | $0.4500 | $3.20 | $0.0500 |
| Venice | $0.4500 | $3.20 | not listed |
| ModelRun | $0.8000 | $5.25 | $0.1500 |
| Cerebras | $0.9900 | $1.49 | $0.9900 |

The default listing ($0.425 / $2.55 / $0.085) is Alibaba's. For the saved run's token mix, Reka is the cheapest and ModelRun the dearest.
