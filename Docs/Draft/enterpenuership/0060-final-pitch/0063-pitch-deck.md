# Pitch Deck — Agentic Code Review

**Status: non-normative.** A business-side working document, not a specification. It defines nothing to build.

Step 3 of the *Pitch Implementation Guidelines* (2026-10-03): the deck prompt run on [`0061-pitch-input.md`](./0061-pitch-input.md). This is a slide-by-slide specification to design from, not designed slides. The Gaps report lists what each slide still needs.

**Updated 2026-10-09: one audience, one tagline.** Who has the problem and what the pain is are worded in [`000-problem-and-audience.md`](../000-problem-and-audience.md), and the slides copy it. The tagline is "Review that shows its evidence", on the title slide.

**Updated 2026-10-10: the slide rework.** The slides were reworked after the day's decisions and measurements:

- **The one-liner and the ask** no longer name TypeScript.
- **The differentiator was re-checked** against rivals' own pages and narrowed ([`competitive-landscape.md`](../competitive-landscape.md)).
- **The price is $22 a seat a month,** the average of CodeRabbit's $24 and Graphite's $20, kept under CodeRabbit's price, with Greptile's $30 left out as an anomaly, with our cost estimated beside it ([`0052-unit-economics-and-financials.md`](../0050-financial-planning/0052-unit-economics-and-financials.md)).
- **The team, the contact address and a prototype logo** are in.
- **The founder's clean-up:** four things came off the slides by decision, not because they were supplied: the traction row, roles and per-person lines on the team slide, the note on what the hosted service adds, and the note on how a pilot team installs the build. The review allowance was set at 150 reviews a seat a month, pooled across the team; it is in the financials slide's speaker notes, not on a slide.

**Updated 2026-10-10: the ten-slide format.** The deck now follows the DEPI ten-slide order, by the founder's decision. It had eleven slides in a different order. Every slide number in this file and the files beside it is the new one.

| Now | Slide | Before |
|---|---|---|
| 1 | Title | 1 |
| 2 | Problem | 2 |
| 3 | Solution | 3 and 4, merged: the real run is now the solution slide |
| 4 | Market | 6 |
| 5 | Business model | 7 |
| 6 | Traction | 5, "Results so far" |
| 7 | Competition | 8 |
| 8 | Team | 9 |
| 9 | Financials | 10 |
| 10 | The ask | 11 |

**Updated 2026-10-10: team and forecast.** The founder supplied each member's level, so the team slide has a line per person again. There is no traction to forecast from, so the financials slide now carries a theoretical forecast taken from CodeRabbit's funding and revenue, per $1M invested.

**Updated 2026-10-10: the SOM.** By the founder's decision the obtainable market is counted bottom-up from the pilot alone: 6 pilot teams × 5 seats = 30 seats; half of them paying is 15 seats, $3,960 a year, with a note on the slide that later years wait for the pilot's result.

**Updated 2026-10-10: the script.** The spoken script for the ten slides, in Arabic, is in [`0065-presentation-script-ar.md`](./0065-presentation-script-ar.md).

**Updated 2026-10-10: the ask.** The founder set the ask: 6 teams, for 8 weeks from 1 January 2027, reaching 1,000 pull requests reviewed, with reviewers acting on at least 20% of the findings, by 28 February 2027. It matches the 6 pilot teams the SOM assumes. No bracketed blank is left on any slide.

**Updated 2026-10-14: the problem slide in business words.** By the founder's decision, slide 2 speaks to listeners who are not engineers. Its headline is "Cheap to write. Flawless to look at. Five times as long to check.", and its number is Faros AI's review time and unreviewed merges in place of LinearB's merge rates. The auth-backend story moved to the speaker notes, for when an example is asked for. The wording is in [`000-problem-and-audience.md`](../000-problem-and-audience.md) §1, "For a business audience".

**Updated 2026-10-14: the one-liner and the title slide's notes.** The one-liner on slides 1 and 10 now reads "We help reviewers catch AI-written software that looks right but isn't, by showing the evidence for every finding": 18 words, down from 22. The title slide's speaker notes now open on review time and on how few people carry the reviewing.

In the designed deck the founder shortened slide 8's headline to "Team members", and the theoretical-forecast row is no longer on slide 9, though its footer and speaker notes still refer to it.

## Order

The audience is the DEPI jury, and the order is the guide's ten-slide deck. Each slide answers one question.

| # | Slide | The question it answers | The guide's tip | State |
|---|---|---|---|---|
| 1 | Title | Who are you, in one line? | Name, logo, and your one-sentence pitch | Ready. The logo is a prototype |
| 2 | Problem | What hurts, and for whom? | A real story or number, not adjectives | Ready: two numbers on the slide, one story in the notes |
| 3 | Solution | How do you fix it? | Show the product: a photo beats a paragraph | Ready: one real run on a pull request, with screenshots |
| 4 | Market | How big can this get? | Build it bottom-up from customers you can reach | The SOM follows the tip: it is counted from the pilot teams. The TAM and SAM are top-down, from all developers narrowed by three shares |
| 5 | Business model | How do you make money? | Price, unit cost and margin | Ready: price and estimated cost per seat. The margin is on slide 9 |
| 6 | Traction | Does anyone actually want it? | Sales, users, pilots, signed letters of intent | **Does not answer its question:** there are no users, pilots or letters of intent. The slide shows what is built |
| 7 | Competition | Why will you win? | Name the real alternatives; never say "none" | Ready: four named rivals |
| 8 | Team | Why are you the right people? | Relevant skills and experience, not titles | Each person's level is shown: four junior engineers, a senior Oracle developer, a sales manager. These are levels and titles, not skills |
| 9 | Financials | Where will this be in 3 years? | Simple forecast and your break-even point | Break-even is in. The forecast is theoretical: the leader's capital efficiency applied to each $1M invested. We have no traction and no investment |
| 10 | The ask | What do you need, and for what? | Amount, use of funds, and the milestone | Ready. The ask is pilot teams, not money, so there is no amount or use of funds; the teams, the length, the start and the milestone are stated |

The ask also appears in one line on the title slide, as the guide's rule to state the ask early requires.

---

## Slides

### Slide 1 — Title

- **Headline:** Agentic Code Review: review that shows its evidence
- **Body:**
  - We help reviewers catch AI-written software that looks right but isn't, by showing the evidence for every finding.
  - Ask: 6 teams for an 8-week pilot, from 1 January 2027.
- **Key number:** none
- **Visual:** the prototype logo, `assets/logo-a-evidence.svg`
- **Speaker notes:** AI has made writing software fast, but checking it has not kept up. Where AI use is high, a review takes about five times as long. And the checking rests on very few people: in half of the ten public projects we measured, three people did more than 85% of all the reviewing. They are the bottleneck. We built a reviewer that shows its evidence, so they can check each finding instead of taking it on trust, and we are here to ask for pilot teams, not money.

### Slide 2 — Problem

- **Headline:** Cheap to write. Flawless to look at. Five times as long to check.
- **Body:**
  - Where AI use is high:
  - About 5× as long to review a change.
  - 31% more changes go out with no review.
- **Key number:** median review duration up 441.5%, and pull requests merged without review up 31.3%, at teams with high AI adoption — Source: Faros AI, 22,000 developers, through O'Reilly ([`004-market-study.md`](../004-market-study.md)). Vendor data; a correlation, not a cause. "About 5×" is Calculated: 1 + 4.415 = 5.4.
- **Visual:** two large figures side by side, "≈5×" and "+31%", each with a one-line label.
- **Speaker notes:** AI has made writing software cheap. What it produces looks flawless, like a report with perfect spelling and the wrong facts, so the people checking it can no longer tell where the problems are. The strain shows: where AI use is high, checking a change takes about five times as long, and nearly a third more changes go out with no check at all. These figures come from one vendor's study of 22,000 developers; they show a link, not a cause. If an example is asked for: one tech lead's first-hand account, of an AI-written change that used an old login system while every test passed and nothing in the change looked wrong. Three sources describe this kind of hidden mistake, and none measures how often it happens.

### Slide 3 — Solution

- **Headline:** Every finding shows its evidence
- **Body:**
  - One command reviews a real pull request.
  - Each finding cites evidence, or says "unverified".
  - It reports its gaps. Next: the project's tests.
- **Key number:** 1 finding on a 16-file pull request in 125.4 s, including the clone — Source: the run's own output, made from `notebooks/run_review_quickstart.ipynb` on 2026-10-09 and supplied by the founder. The saved notebook holds an earlier run.
- **Visual:** the product at work: the command; two screenshots of microsoft/playwright#43199 on GitHub; an arrow; and the tool's output redrawn as a card with the file counts, the finding with its severity, category, lines and evidence, the tool's own caveats, and the verdict. The footer names what comes next.
- **Speaker notes:** A developer runs one command and reads the findings. This is a real pull request on Microsoft's Playwright: the command read it from GitHub and reviewed its ten TypeScript and JavaScript files in about two minutes, in one model pass. What you see is built: the finding carries its evidence, and the review says what it did not do, here that no checks ran and that nine of the ten files got no finding call. Evidence from the project's own tests and rules is specified and not built, and nothing is posted on the pull request yet. We have not confirmed the finding with the maintainers, and the pull request has since been closed without merging.

### Slide 4 — Market

- **Headline:** Up to $10.5B–$13.1B a year, at rivals' prices
- **Body:**
  - TAM: 36.5M developers × $288–360 a year.
  - SAM: $2.0B–$4.0B; 5.3M–8.5M reviewers.
  - SOM, year 1: 15 paying seats, $3,960; later years await the pilot.
- **Key number:** $10.5B–$13.1B a year — Source: Calculated: 36.5M professional developers (SlashData, early 2025) × $24–30 per developer per month × 12, from `004-market-study.md`. At our own price, $22, the same count gives $9.6B.
- **Visual:** three bars for TAM, SAM and SOM. The SOM bar is a sliver, with its figure and the note "Later years wait for the pilot's result." A line under the chart gives the TAM at our own price.
- **Speaker notes:** The ceiling assumes every professional developer pays rivals' entry price; narrowed to TypeScript or JavaScript developers in pull-request teams who use AI tools, it is $2.0B–$4.0B, and about three quarters of them review code, who are the people we serve. Our own price, $22 a seat, is set just under the cheaper of those rivals, so for us the same people come to $9.6B and $1.8B to $2.9B. What we can obtain is counted from the bottom up, from the only customers we can name: six pilot teams of five are 30 seats, and we assume half of them go on to pay, which is 15 seats, or $3,960 a year; later years wait for the pilot's result. For scale, the category leader reaches about 0.4% of professional developers, and no open-source review Action has passed 460 repositories.

### Slide 5 — Business model

- **Headline:** Free CLI; hosted reviews at $22 a seat
- **Body:**
  - Command-line tool: open source and free.
  - Hosted service: $22 per developer a month.
  - Our cost per seat, 25–75 reviews: about $1.14–$5.81.
- **Key number:** $22 per seat per month — Source: Calculated: the average of CodeRabbit's $24 and Graphite's $20, their entry prices in `tool-reference.md`; `0052-unit-economics-and-financials.md` §2.
- **Visual:** two cards, free and paid, and a row showing the two rivals' prices, their average, and our estimated cost per seat.
- **Speaker notes:** The command-line tool stays free; the hosted service is priced at $22 per developer a month, the average of two rivals' entry prices and $2 under CodeRabbit's. Serving a seat is estimated to cost us $1.14 to $5.81 a month, which is 25 to 75 reviews at five to eight cents each in model tokens and repository downloads, and that estimate doubles in January 2027 with our provider's prices. The hosted service is not designed yet.

### Slide 6 — Traction

- **Headline:** Built so far: a single-pass command-line review
- **Body:**
  - 2026-09-17: reviews uncommitted changes in one model pass.
  - 2026-10-09: reviews a public pull request by its address.
  - Not built: test runs, catch-rate benchmark.
- **Key number:** 93 of 127 tasks of the first feature done — Source: `specs/001-walking-skeleton/tasks.md` on the working branch, 2026-10-10.
- **Visual:** none
- **Speaker notes:** These are build milestones, not traction: the references record no user outside the team, no pilot and no letter of intent. On 2026-10-10 the first feature had 93 of its 127 tasks ticked, and we have measured review volume in ten public repositories and the cost of a review on two sizes of pull request. We cannot yet show that the tool catches code that does not fit its codebase, because the benchmark that measures a catch rate is not built.

### Slide 7 — Competition

- **Headline:** Where we differ: nothing hidden, every gap reported
- **Body:**
  - Rivals run sandboxed checks, then filter findings out.
  - Ours keeps every finding, labelled "unverified" if unproven.
  - It reports its gaps; $22, just under CodeRabbit.
- **Key number:** 3 of 4 rivals say they filter unconfirmed findings out — Source: CodeRabbit's, Qodo's and Claude Code Review's own pages, read 2026-10-10 and quoted in `competitive-landscape.md`.
- **Visual:** a table of five tools by three columns: how a finding is checked, what happens to an unconfirmed finding, and the entry price. Our row says "one model pass today; the project's own tests next (specified)".
- **Speaker notes:** Rivals verify more than our build does today: one writes and runs tests in a sandbox, another runs verification scripts, and ours makes one model pass. Our difference is narrower and it is built: a finding we cannot back is kept and labelled, where three of four rivals say they filter such findings out, and the review reports its own gaps. Price is a small difference, not the reason to choose us: $22 a seat is $2 under CodeRabbit, for a feature set of about its entry tier, a model that is likely noisier, and no measured catch rate.

### Slide 8 — Team

- **Headline:** Team members
- **Body:**
  - Four junior software engineers, led by Mohammed Gamal Kenawy.
  - Mohamed Ali Mahmoud: senior Oracle developer.
  - Ahmed Shahin: sales manager.
- **Key number:** 6 people: 4 junior software engineers, 1 senior Oracle developer, 1 sales manager — Source: founder, 2026-10-10.
- **Visual:** six cards, each with a name and a level: Mohammed Gamal Kenawy (team leader), Yahia Ahmed Hamed, Mahmoud Ayman Mahmoud and Abderhman Ehab as junior engineers; Mohamed Ali Mahmoud; Ahmed Shahin.
- **Speaker notes:** We are four junior software engineers, a senior Oracle developer and a sales manager, and Mohammed Gamal Kenawy leads the team. If asked: the repository's history shows one author so far.

### Slide 9 — Financials

- **Headline:** At $22 a seat, six seats cover fixed costs
- **Body:**
  - A seat: $22 in, $1.14–$5.81 out.
  - Fixed costs covered by 5–6 seats.
  - Theoretical, per $1M invested: 313 seats, then 986.
- **Key number:** 986 seats and $260,400 a year for each $1M invested, by year 3 — Source: Calculated in `0052-unit-economics-and-financials.md` §6 from CodeRabbit's funding ($88M raised by September 2025) and Sacra's estimate of its revenue ($25M a year at the end of 2025), at our price.
- **Visual:** three figures for one seat (what it pays, what it costs, what it leaves); a band with the always-on cost and the seats that cover it; and a row of three years marked "theoretical forecast".
- **Speaker notes:** A seat brings in $22 a month and is estimated to cost $1.14 to $5.81 to serve, so it leaves $16 to $21, and five to six seats cover the always-on infrastructure. We have no traction, so the forecast is theoretical: it applies the category leader's capital efficiency to each million dollars invested, which at our price is about 313 seats and $82,500 a year by year 2, and 986 seats and $260,400 by year 3. We have raised nothing and are not asking for money, so this is a benchmark, not a plan; if asked about heavy users, a seat includes 150 reviews a month, pooled across the team.

### Slide 10 — The ask

- **Headline:** We ask for pilot teams, not money
- **Body:**
  - We help reviewers catch AI-written software that looks right but isn't, by showing the evidence for every finding.
  - Ask: 6 teams, an 8-week pilot from 1 January 2027, reaching 1,000 reviews and 20% of findings acted on by 28 February 2027.
  - Contact: mohammedgamal2002@gmail.com · github.com/MoKenawy/Pull-request-Reviewer
- **Key number:** 6 teams for 8 weeks — Source: founder, 2026-10-10. Six is the number of pilot teams the SOM on slide 4 assumes.
- **Visual:** none. No funds are requested, so there is no use-of-funds chart; the slide lists what the pilot measures instead. The prototype logo sits in the footer.
- **Speaker notes:** We ask for pilot teams, not money: six teams, running the tool on their real changes for eight weeks from 1 January 2027, and by 28 February 2027 we aim to have reviewed 1,000 pull requests with reviewers acting on at least 20% of the findings. A pilot measures what our plan still leaves blank: pull requests per month, review time, current tools and spending, and willingness to pay, and it gives us our own cost per review from real changes. Repeat the ask in one sentence, then leave this slide on screen during questions.

---

## Gaps report

### 1. Missing information, by slide

| Slide | Missing |
|---|---|
| 1 Title | A final logo |
| 2 Problem | A quote from a reviewer the team interviewed itself. The slide stands without it |
| 3 Solution | Which model produced the run, and its token counts; confirmation of the finding by the maintainers. A repeat on Gemini 3.8 Flash was refused by the provider's daily limit |
| 4 Market | The measured share of pilot seats that pay, which the SOM assumes is half; how many teams can be reached after the pilot |
| 5 Business model | Nothing on the slide. The note on what the hosted service adds was taken off by the founder; the question itself is still open in the financials file and the canvas |
| 6 Traction | Any traction: users, pilots or letters of intent. The row that said so was taken off by the founder, and the speaker notes still say it |
| 7 Competition | A profile of Cubic, which reviewed more of our sample than CodeRabbit and Greptile together; a reason to choose us over Qodo specifically |
| 8 Team | Skills and experience in the guide's sense: the slide gives levels and titles. A spelling to confirm: "Abderhman" |
| 9 Financials | A forecast of our own. The one shown is the leader's capital efficiency applied to a hypothetical $1M; our seats, our investment and our growth are all unknown |
| 10 The ask | Nothing on the slide. Before 1 January 2027: a check that the tool reports findings on the working model, a way for teams to install it, and a LICENSE file |

### 2. Numbers shown without a source

None on the slides: every number carries its source on the "Key number" line or in the table of sources below. Two inputs are assumptions with no source at all: the 10-minute slot and the live format. The market's yearly spend is rivals' entry price. Our own price is an average of two rivals' prices, and which two is our choice. One input is an assumption of ours: the server in the always-on cost.

### 3. Contradictions between inputs

Full quotations and links are in [`0061-pitch-input.md`](./0061-pitch-input.md).

| # | One input says | Another says | Where it stands |
|---|---|---|---|
| 1 | Canvas §5: "Open core, decided 2026-10-03", with revenue from "a hosted review service" | Requirement catalogue §2.2: a hosted GitHub App is "out of scope entirely". ADR-0005: "The product is deliberately **not** a hosted service." SRS §2.1: "It operates no server" | Open. The paid product has a pricing rule and no specification, version or ADR. Expect "why pay if the tool is free?": the canvas says the hosted tier's added value "is not stated" |
| 2 | `000-problem-and-audience.md` §1: the audience is the reviewer, "an engineer who reviews a teammate's AI-assisted TypeScript or JavaScript pull request" | SRS §2.2: "v1's primary user is the **author**, not the reviewer". SRS §1.2 leaves "GitHub integration beyond reading a public pull request" to v3 | Narrowed on 2026-10-09, not closed. What is served today is a review of uncommitted changes and a review of a public pull request by its address (ADR-0011), which slide 3 shows. Its speaker notes say the limit aloud, as SRS §9 (R-5) requires |
| 3 | Landscape, differentiator 2: "We verify by running the actual test suite", where "Competitors verify agentically" | Rivals' own pages, read 2026-10-10: Greptile "writes and runs targeted tests in a sandbox"; CodeRabbit "runs verification scripts on the review comments". Our build runs no checks | **Closed on 2026-10-10 by withdrawing the claim.** The landscape's re-check records it, and slide 7 no longer says "ours runs the tests" |
| 4 | Cost sheet: Qwen3.8 27B at "$4.35 / 1M output tokens" | Model comparison: gpt-oss at "$0.018 / $0.09" and "$0.03 / $0.17". The built tool defaults to the NVIDIA NIM free tier | Settled as a working assumption on 2026-10-10: Gemini 3.8 Flash, which neither sheet covers. The model and its price stay parameters of the cost formula |
| 5 | Pricing template: "F = Fixed monthly infrastructure", with break-even at "F / [P - (C × R)]" | Cost sheet: every resource is usage, and "we should not write 'Elastic IP = $3.65/month' as a fixed cost" | Read together in `0052-unit-economics-and-financials.md` §5: what a review uses counts in the cost of a seat, and what runs all the time is `F`. This reading waits for the founder's confirmation |
| 6 | Tool reference: Qodo "Uses a credit-based system; specific tiers are on the pricing page (not enumerated here)" | Pricing template: Qodo at "$30" per "/team/mo", no source | Open. The slide uses "credit-based" |

**A conflict inside the guide itself.** Slides 1 and 10 must carry the one-liner and the ask line, and together they exceed the 25-word body limit of rule 9: the one-liner is 18 words, which is under the limit by itself but not once the ask line is added. The guide's own laundry one-liner is 22 words, so it would break the limit the same way. Both slides keep the one-liner whole. With the ask filled in they are at 29 and 44 words.

### 4. Every calculation made

| What | Formula and inputs | Result |
|---|---|---|
| Review duration as a multiple | 1 + 441.5% = 1 + 4.415 | 5.415, shown as "about 5×" |
| Tasks in feature 001, on 2026-10-10 | 93 ticked + 34 open | 127 |
| Yearly spend per developer (proxy) | $24 × 12; $30 × 12 | $288; $360 |
| TAM (the market study's figure, re-checked) | 36.5M × $288; 36.5M × $360 | $10.512B; $13.14B, shown as $10.5B–$13.1B |
| SAM, developers (re-checked) | 36.5M × 68.8% × 55% × 50.6%; 36.5M × 68.8% × 55% × 80.8% | 6.99M; 11.16M, shown as 7.0M–11.2M |
| SAM, dollars (re-checked) | 6.99M × $288; 11.16M × $360 | $2.01B; $4.02B, shown as $2.0B–$4.0B |
| Reviewers in the SAM | 6.99M × 76.4%; 11.16M × 76.4% | 5.34M; 8.53M, shown as 5.3M–8.5M |
| Price per seat | ($24 + $20) ÷ 2 | $22 |
| Model cost of a median-size review | Mean of (3,739 × $0.75 + 15,534 × $3.75) ÷ 1M and (3,739 × $0.75 + 5,287 × $3.75) ÷ 1M | $0.0418 |
| Cost per review | $0.0418 + a repository download of $0.0038 to $0.0357 | $0.0456 to $0.0775 |
| Cost of a seat | 25 × $0.0456; 75 × $0.0775 | $1.14; $5.81 |
| Contribution per seat | $22 − $5.81; $22 − $1.14 | $16.19; $20.86, shown as $16 to $21 |
| Always-on infrastructure | $19.71 + $37.96 + $3.65 + $35.04 | $96.36 a month |
| Break-even seats | $96.36 ÷ $20.86; ÷ $16.19, rounded up | 5; 6 |
| CodeRabbit's revenue at the end of 2024 | $25M ÷ (1 + 1,288.9%) | $1.8M |
| CodeRabbit's seats | $1.8M ÷ $288; $25M ÷ $288 | 6,250; 86,806 |
| Seats per $1M raised | 6,250 ÷ 20; 86,806 ÷ 88 | 313; 986 |
| Our revenue per $1M invested | 313 × $264; 986 × $264 | $82,500; $260,400 a year |
| TAM at $22 | 36.5M × $22 × 12 | $9.6B |
| SAM at $22 | 6.99M × $264; 11.16M × $264 | $1.8B; $2.9B |
| SOM, year 1 | 6 teams × 5 seats; 30 × 50%; 15 × $264 | 30 seats; 15 paying seats; $3,960 a year |
| Pull requests in the pilot | 30 developers × 25 a month; × 8 weeks ÷ 4.35 weeks a month | 750 a month; about 1,380 in all |
| Model cost of the pilot, at 2027 prices | 1,380 × $0.0875 to $0.1194; three times that if every push is reviewed | $121 to $165; $362 to $494 |

Every figure on the slides is worked through, with its inputs and assumptions, in [`Calculation_basis.md`](./Calculation_basis.md). The full list for the financials is in `0052-unit-economics-and-financials.md` §10. The speaking-time estimates are in [`0062-one-liner-and-elevator-pitch.md`](./0062-one-liner-and-elevator-pitch.md).

### 5. Use-of-funds check

No. No split was given: the ask is an action, not an amount, so there are no shares to add up.

---

## Sources and caveats for every number

Prepared for questions, as the guide advises.

| Number | Slide | Source | If asked |
|---|---|---|---|
| About five times as long | 1, notes | The same Faros AI figure as slide 2 | As for slide 2 |
| Three people, more than 85% of the reviewing, in half of ten projects | 1, notes | Our measurement: `review-volume-report.md` §2.5, ten public TypeScript repositories, September 2026 (C, from A) | Public repositories stand in for company teams. In those five repositories, three people did more than 85%; across all ten, the top fifth of 294 reviewers did 73% |
| About 5×; +31% | 2 | Faros AI, 22,000 developers, through O'Reilly; `004-market-study.md` (confidence B) | Vendor data, and Faros sells into this market. A correlation at teams with high AI adoption, not a cause. It measures how long a review takes from start to finish, not hours of effort. The primary report has not been read. 5× is 441.5% more, rounded down from 5.4× |
| One team; three sources | 2, notes | Background study A3 and A4 | Anecdote. Nobody has measured how often this happens; the benchmark and the pilot exist to find out |
| 16 files, 10 reviewed; 1 finding; 9 of 10 files; 125.4 s | 3 | The run's own output, 2026-10-09 | One run on one pull request. The finding is the tool's claim and is unconfirmed. The output did not include the model or the token counts |
| 1 command, 1 model pass | 3, notes | `contracts/cli.md`; SRS v1 §2.1 | In version 1 the model is called once per review |
| 36.5M | 4 | SlashData, early 2025, via `004-market-study.md` (confidence A) | Professional developers worldwide. GitHub's 180M+ counts accounts and is not used |
| $10.5B–$13.1B | 4 | Our calculation in the market study (confidence C) | An upper bound at rivals' entry prices, which stand in for ours; not our serviceable market |
| $2.0B–$4.0B | 4 | Market study SAM (confidence C), from Stack Overflow 2025 (A) and JetBrains 2025 (B, proxy) | The pull-request-team share is a proxy read from a search excerpt; the shares are multiplied as if independent |
| 5.3M–8.5M reviewers | 4 | Market study (confidence C): the SAM × 76.4% who review code as part of their work, Stack Overflow 2019 (A, 70,390 responses) | The survey is from 2019, before AI coding tools, and is not limited to pull-request teams |
| $22; $9.6B; $1.8B to $2.9B | 4 | Our calculation, `0052-unit-economics-and-financials.md` §2 and §7 (confidence C) | $22 is the average of CodeRabbit's $24 and Graphite's $20. The larger figures on the slide are at $24 to $30, which still includes Greptile's price |
| 15 paying seats; $3,960 a year | 4 | Calculated: 6 pilot teams × 5 seats × 50% × $264 | Six teams is the ask; the half-paying share is the founder's assumption of 2026-10-10. Five seats a team is an illustration, not a measurement. Nothing measures the paying share yet, and the figure covers year 1 only |
| About 0.4%; 460 repositories | 4, notes | Market study (C; A) | CodeRabbit's reach rests on Sacra's revenue estimate; 460 counts public repositories using the most-adopted open-source review Action, January 2025 |
| $22 | 5, 7, 9 | Calculated: ($24 + $20) ÷ 2, from `tool-reference.md` | The founder's limits: under CodeRabbit's $24, and Greptile's $30 left out as an anomaly. Graphite is a workflow tool whose $20 plan has only limited AI review, so it is a weak comparison. Both prices are billed annually |
| $1.14–$5.81 | 5, 9 | Calculated in `0052-unit-economics-and-financials.md` §3 | An estimate: 25 to 75 reviews a month, each $0.0418 in measured model tokens plus a repository download. 25 is the average number of pull requests a core developer opens a month in ten public repositories; 75 is three reviews for each. Two measured runs, a median-size pull request, nothing run on a hosted service. It doubles in 2027 with the model's price |
| 2026-09-17; 2026-10-09 | 6 | Git history, branch `001-us2-no-finding-clean-review` | The build is on a feature branch that is not merged to `main` |
| 93 of 127 | 6, notes | `specs/001-walking-skeleton/tasks.md` on that branch, 2026-10-10 | The task count covers the first feature only |
| 3 of 4 rivals filter | 7 | Vendors' own pages, quoted in the landscape's re-check | CodeRabbit, Qodo and Claude Code Review say it. Greptile's pages do not say |
| 6 people; their levels | 8 | Founder, 2026-10-10 | The git history shows one author. An earlier note from the founder said all six work as developers |
| $16 to $21; $96.36; 5 to 6 seats | 9 | `0052-unit-economics-and-financials.md` §4 and §5 | The always-on figure is an estimate: one load balancer, one NAT gateway, one address and one assumed small server in Frankfurt, at list price. Break-even covers infrastructure only, not people |
| 6 teams; 8 weeks; 1 January 2027 | 1, 10 | Founder, 2026-10-10 | Eight weeks from 1 January ends on 26 February. The start is the day our model provider's prices double |
| 1,000 reviews by 28 February 2027 | 10 | Calculated: 30 developers × 25 pull requests a month is 750 a month, about 1,380 in eight weeks | A target set below the expected volume. It assumes five developers a team and each pull request reviewed once |
| 20% of findings acted on | 10 | The top of the range that earlier work, cited by Chowdhury et al. (MSR 2026), reports for AI review comments is 19.2% | A target, not a result. In five runs on the working model the tool reported no finding, so this needs checking before the pilot starts |
| 313 and 986 seats; $82,500 and $260,400 | 9 | `0052-unit-economics-and-financials.md` §6: CodeRabbit's funding from its own announcements, its revenue from Sacra's estimates | Theoretical. It assumes we would turn money into paying seats as well as the category leader did, with a product that does less. CodeRabbit has never published its revenue; the 2024 figure is derived from a growth rate Sacra gives without a basis. We have raised nothing |

---

## Pre-delivery checklist

The guide's twelve boxes. Four can be ticked today.

- [ ] Audience, ask and format are written down, and the deck order matches the audience. **Partly:** the audience, the ask and the order are set. The format and the time slot are still assumed.
- [ ] A stranger can repeat the one-liner after hearing it once. **Not tested.**
- [ ] The elevator pitch runs under 60 seconds out loud and ends with one clear ask. **Not tested:** the three-line script is 116 words since 2026-10-14, about 46 to 54 seconds by word count.
- [x] The deck has 10–12 slides; anything extra is in an appendix. 10 slides.
- [ ] Every slide passes the three-second test and uses 30-point text or larger. **Not tested:** the designed draft has not been checked against it, and slides 1 and 10 are over 25 words.
- [ ] The market size shows its bottom-up calculation and data source. **Partly:** the SOM is bottom-up, from the pilot teams, and every layer shows its calculation and source. The TAM and SAM are top-down.
- [ ] SOM is reachable from current traction, or the gap is explained. **Partly:** the SOM is the pilot itself, so it is reachable if the ask is met. There is no traction yet, and the slide says later years wait for the pilot.
- [x] The competition slide names real alternatives. Four on the slide, seven in the input sheet.
- [ ] Every figure matches across all slides (price, margin, traction, ask). **Partly:** the price, the estimated cost, the margin and the ask agree across slides 1, 4, 5, 7, 9 and 10. Traction does not exist.
- [ ] Use-of-funds shares add up to 100% and each links to the milestone. **Does not apply as written:** no funds are requested. The milestone is stated on slide 10.
- [x] The ask appears early and is repeated at the close, with contact details on screen. The ask is on slides 1 and 10, and the contact details are on slide 10.
- [x] Every AI-generated number has been checked against a source or removed. The checks were re-run on 2026-10-10 over every quoted claim and every calculation.

---

## For the second pass

1. **Before the pilot starts on 1 January 2027:** confirm that the tool reports findings on the working model, give teams a way to install it, and add a LICENSE file. Also decide what you want from the jury itself.
2. **Traction:** the slide the guide gives to it has none. A first pilot team or a signed letter of intent would change it more than anything else in the deck.
3. **Team:** skills and experience behind each level, and the spelling of one name.
4. **Market:** the share of pilot seats that pay and the teams reachable after the pilot, to extend the SOM past year 1.
5. **Financials:** our own seats and investment, to replace the theoretical forecast; a real server choice in place of the assumed one.
6. **Business model:** whether Graphite belongs in the price average, and what happens past the review allowance.
7. **Cost:** the three larger pull-request sizes on Gemini 3.8 Flash, which need a paid key or more days on the free one.
8. **Competition:** a profile of Cubic.
9. **Pilot readiness:** a LICENSE file.
