# Final Pitch — Progress Report

**Date:** 2026-10-10 · **Status: non-normative.** A working status note, written to be copied into the "Final Pitch" page in Notion.

## Where things stand

- **All 16 rework tasks are done or closed except one.** Still partly done: the cost measurement (task 5), which has two of five pull-request sizes.
- **The deck is in the guide's ten-slide order, and still not ready to present.** Four of the guide's twelve pre-delivery checks pass, and no bracketed blank is left on any slide. Two slides do not yet do what the guide asks of them, market and traction, and two do it only in part: the team slide gives levels, not skills, and the financial forecast is theoretical. Missing: any traction.
- **The price is $22 per seat per month,** the average of CodeRabbit's $24 and Graphite's $20, kept under CodeRabbit's price, with Greptile's $30 left out as an anomaly. It is the third rule of the day: per review at cost plus a margin came first, then $27 a seat.
- **Serving a seat is estimated at $1.14 to $5.81 a month,** so a seat leaves $16 to $21, and five to six seats cover an estimated $96.36 a month of always-on infrastructure. The estimate rests on two measured runs and one assumed server.
- **The differentiator did not survive the re-check as worded.** Rivals already run sandboxed checks and show how a finding was verified, and our own test run is not built. What is left is narrower: nothing is dropped silently, and the review reports its own gaps. Price is a small difference: we are $2 under CodeRabbit.
- **The cost measurement stopped halfway.** The key is on Gemini's free tier, which allows 20 requests a day. Two of five pull-request sizes are measured.
- **On Gemini, no measured run reported a finding.** Five runs, two small pull requests. The build cannot tell "nothing to report" from "did not use the finding tool".

Designed deck: https://claude.ai/artifact/QgbA42frcVNN3T1m3hrC2s (private until shared from the page).

## Done so far

| Date | What | Result |
|---|---|---|
| 2026-10-03 | Pitch pack built from the DEPI guide | `0061-pitch-input.md`, `0062-one-liner-and-elevator-pitch.md`, `0063-pitch-deck.md`, all in `Docs/Draft/enterpenuership/0060-final-pitch/` |
| 2026-10-03 | Business model decided: open core | Free open-source command-line tool, paid hosted review service |
| 2026-10-08 | Market study checked, corrected and filed | `004-market-study.md`. TAM $10.5B–$13.1B a year as a ceiling; SAM 7.0M–11.2M developers, $2.0B–$4.0B a year |
| 2026-10-08 | Price proxy decided | Rivals' entry price, $24–30 per developer per month, stands in for ours |
| 2026-10-09 | Designed deck, first draft | 11 slides, with speaker notes. Restructured to the guide's ten on 2026-10-10 |
| 2026-10-09 | Rework list agreed | 16 tasks, ordered by what unblocks what |
| 2026-10-09 | Task 7: the ask | Merged into the closing slide, at the end of the deck |
| 2026-10-09 | Task 5, first half: review volume | `review-volume-report.md` in `0050-financial-planning/0051-cost-structure/` |
| 2026-10-09 | Task 8: MVP slide | A real pull request and the tool's output, on one slide |
| 2026-10-10 | Task 1: one problem definition and one audience | `000-problem-and-audience.md` |
| 2026-10-10 | Reviewers measured | Who reviewed the same 7,670 pull requests: `review-volume-report.md` §2.5 |
| 2026-10-10 | Task 11: one-sentence pitch | `0062-one-liner-and-elevator-pitch.md`: 22 words. It no longer names TypeScript, and its last part is "by showing the evidence for every finding" |
| 2026-10-10 | Task 12: elevator pitch in three lines | Same file: hook, story, ask, 120 words, about 48 to 55 seconds by word count. The hook is the software crisis of 1968, checked against the conference report |
| 2026-10-10 | Task 2: differentiator re-checked | `competitive-landscape.md`, new section. Each rival's own pages were read. "Rivals verify with a model; ours runs the tests" is withdrawn |
| 2026-10-10 | Task 3: the model | Reopened and settled as a working assumption: Gemini 3.8 Flash. The model and its price stay parameters of the cost formula |
| 2026-10-10 | Task 4: pricing unit | A monthly price per seat, at the average of rivals' prices, under CodeRabbit's $24 and without Greptile's $30: $22. It replaced a per-review, cost-plus rule and a $27 average set earlier the same day |
| 2026-10-10 | Task 5, second half: the token ladder | Started on Gemini 3.8 Flash and stopped by the free tier's daily limit. Five runs completed, on two of five sizes: `review-volume-report.md` §1.3 and §3.4 |
| 2026-10-10 | Task 6: financials | `0050-financial-planning/0052-unit-economics-and-financials.md`: the $22 seat price and how it is averaged, our estimated cost per seat, the margin, the break-even in seats, and the three-year totals left as a formula |
| 2026-10-10 | Tasks 9 and 15: team and contact | Six developers on the team slide; the team leader's address and the repository on the closing slide |
| 2026-10-10 | Task 16: logo | Three prototypes in `0060-final-pitch/assets/`; prototype A is on the first and last slides |
| 2026-10-10 | Task 10: slide rework | Nine slides changed in the specification and the designed deck |
| 2026-10-10 | Calculation basis | `Calculation_basis.md`: how every number on the slides was reached, with its inputs, arithmetic and assumptions |
| 2026-10-10 | Deck clean-up, by your decisions | Off the slides: the traction row, roles and per-person lines on the team slide, the note on what the hosted service adds, and the note on installing the build. A three-year scenario was offered and rejected as baseless. The review allowance is set at 150 reviews a seat a month, pooled across the team |
| 2026-10-10 | Ten-slide format | The deck follows the DEPI ten-slide order: title, problem, solution, market, business model, traction, competition, team, financials, the ask. The real run was merged into the solution slide, and the built-so-far slide took the traction slot |
| 2026-10-10 | Team levels | Four junior software engineers, a senior Oracle developer and a sales manager, on the team slide |
| 2026-10-10 | Theoretical forecast | For lack of traction, the financials slide applies CodeRabbit's capital efficiency to each $1M invested: 313 seats and $82,500 a year by year 2, 986 seats and $260,400 by year 3. In `0052` §6 |
| 2026-10-10 | SOM | Bottom-up from the pilot alone, by your decision: 6 pilot teams × 5 seats = 30 seats; half of them paying is 15 seats, $3,960 a year. The slide says later years wait for the pilot |
| 2026-10-10 | Arabic script | `0065-presentation-script-ar.md`: what to say on each of the ten slides, 868 words, about 7 to 9 minutes by word count, with eight expected questions and their answers |
| 2026-10-10 | Task 14: the ask | 6 teams, for 8 weeks from 1 January 2027, reaching 1,000 pull requests reviewed, with reviewers acting on at least 20% of the findings, by 28 February 2027. On slides 1 and 10, in the elevator pitch and in the Arabic script |
| 2026-10-10 | Task 13: business model canvas |
| 2026-10-14 | Problem statement in business words | `000-problem-and-audience.md` §1, "For a business audience": a written statement, a spoken one and a slide headline, "Cheap to write. Flawless to look at. Five times as long to check." Slide 2 now shows Faros AI's figures (about 5× as long to review, 31% more changes unreviewed) in place of LinearB's merge rates; the auth-backend story moved to its notes. Also in the Arabic script, the input sheet and `Calculation_basis.md` |
| 2026-10-14 | One-liner in business words | "We help reviewers catch AI-written software that looks right but isn't, by showing the evidence for every finding": 18 words. On slides 1 and 10, in the elevator pitch (now 116 words, about 46 to 54 seconds) and in the Arabic script. The title slide's speaker notes now open on review time and the reviewing bottleneck |

## Numbers found so far

- **Usage:** a core developer opens about 11 to 13 pull requests a month, measured across ten public TypeScript repositories in September 2026. For a team of five that is 55 to 65 reviews a month if each pull request is reviewed once, and up to about three times that if every push is re-reviewed.
- **Cost of a review on Gemini 3.8 Flash:** $0.0184 for a 50-line pull request (three runs) and $0.0418 for a 160-line one (two runs, $0.0226 and $0.0611), at $0.75 and $3.75 per 1M tokens. Both double on 2027-01-01 with the provider's prices.
- **Thinking tokens are 99% of the billed output, and the tool does not count them.** It recorded 264 output tokens over the five runs; 33,936 were billed.
- **Price:** $22 per seat per month (Calculated: ($24 + $20) ÷ 2, CodeRabbit and Graphite). Greptile's $30 and Cubic's $40 are left out.
- **Estimated cost of a seat:** $1.14 to $5.81 a month through 2026, $2.19 to $8.95 from 2027. That is 25 to 75 reviews, the average for a developer's month, each $0.0418 in model tokens plus a repository download of $0.0038 to $0.0357.
- **Margin:** $16.19 to $20.86 a seat, 74% to 95% of the price; 59% to 90% from 2027.
- **Break-even:** always-on infrastructure is estimated at $96.36 a month with one assumed small server; five to six seats cover it. People are not in that figure.
- **Review allowance:** 150 reviews a seat a month, pooled across the team. A seat that uses all of them costs an estimated $6.85 to $11.63 through 2026 and $13.12 to $17.90 from 2027, under the $22 price.
- **Market:** TAM $10.5B–$13.1B a year at rivals' prices, SAM $2.0B–$4.0B. At our $22: $9.6B and $1.8B to $2.9B.
- **Reviewers:** in the ten repositories, 182 core reviewers did 97.7% of the reviewing, a median of 21.5 pull requests each a month, against 13 opened per core developer.
- **Who already reviews there:** a bot account reviewed 5,711 of the 7,670 human pull requests. By account: Cubic 2,064, Greptile 901, CodeRabbit 521, and a reviewer bundled with the code host 2,481.
- **Rivals' price per review:** Greptile $0.60 inside its plan and $1.00 beyond it; Claude Code Review $15 to $25.
- **The budget limit:** the build's default was raised from 20,000 to 200,000 in the working tree (staged, not committed). At 20,000 a quarter of real pull requests would be refused; at 200,000, 1.9%.

## Task status

| # | Task | Status |
|---|---|---|
| 1 | One problem definition and one target audience | Done. Two readings wait for your confirmation (below) |
| 2 | Re-check the differentiator behind the competition slide | Done. The old headline claim is withdrawn; four narrower differences are named |
| 3 | Model the hosted service is costed on | Settled as a working assumption: Gemini 3.8 Flash |
| 4 | Pricing unit for the hosted service | Done: $22 per seat per month, under CodeRabbit's $24 |
| 5 | Measure average review volume | Partly done. Usage is measured. The token ladder has two of five sizes; the other three need a paid key or more days |
| 6 | Financials slide | Done: price, estimated cost, margin and break-even per seat, and a theoretical three-year forecast per $1M invested |
| 7 | Merge the ask into the closing slide | Done |
| 8 | MVP-run slide | Done, first version |
| 9 | Team slide and its script | Done: six names, each with a level |
| 10 | Rework the slides touched by 1–6 | Done for today's inputs, and the deck then restructured to the guide's ten-slide order |
| 11 | One-sentence pitch | Done, first version. Still missing: a reviewer's own words, and the repeat-back test |
| 12 | Elevator pitch in three lines | Done, first version. The ask's numbers wait for 14; not yet timed aloud |
| 13 | Refresh the business model canvas | Done |
| 14 | The pilot ask's numbers | Done: 6 teams, 8 weeks from 1 January 2027, and a milestone for 28 February 2027 |
| 15 | Contact details | Done |
| 16 | Logo | Prototype done; a final logo is your choice |

## Waiting on a decision or input

1. **Before the pilot starts on 1 January 2027:** a check that the tool reports findings on Gemini 3.8 Flash, a way for teams to install the build, and a LICENSE file. The milestone of 20% of findings acted on depends on the first.
2. **How to finish the cost measurement:** turn on billing for the Gemini key, at an estimated cost under $1 for the nine remaining runs, or run them over later days inside the free limit of 20 requests.
3. **Which rivals go in the price average.** With Greptile out and the price held under $24, I averaged CodeRabbit's $24 and Graphite's $20, which gives $22. Graphite is a workflow tool with only limited AI review at that price, so it is a weak comparison. Without it there is nothing to average, and the price is simply a figure under $24 that you pick.
3. **Whether the market study's price range should drop Greptile too.** It still runs from $24 to $30.
3. **What happens when a team passes its review allowance,** and whether the price is billed monthly or annually.
4. **What the hosted service offers that the free tool does not.** At $22 a seat the free tool on a team's own key gives the same review for the cost of the tokens, an estimated $1.05 to $3.14 a month.
5. **Two assumptions of mine in the cost estimate:** that what runs all the time is a fixed cost the margin covers, and that the server is one t3.medium. The break-even figure rests on both.
6. **Which logo,** or none of the three.
7. **The spelling of "Abderhman":** the address supplied with it spells the name differently.
8. **Two readings in the problem definition:** that the lost signal is the headline pain, and that the reviewer is the one in a company or funded team.
9. **Three to five reviewer interviews,** to replace the team's wording of the pain with a reviewer's own. Three questions are ready in `0062`.
10. **Whether the specification should now list the reviewer as a v1 user.** SRS §2.2 and R-5 still say v1's primary user is the author.
11. **Which trigger to assume:** one review per pull request, or one per push. Both are carried.

## Known issues

- **The tool under-reports cost on Gemini.** It adds up the provider's input and output fields, and Gemini reports thinking tokens only in its total. An engineering fix, not made here.
- **The tagline is true but not ours alone.** Rivals also show evidence. The clause that is ours is the second half: "or say the finding is unverified".
- **A rival is missing from the landscape.** Cubic reviewed more of our sample than CodeRabbit and Greptile together, and has no profile.
- **The MVP slide's run still has no model or token count,** and its pull request was closed without merging on 2026-10-09.
- **The paid product is not designed.** The requirement catalogue calls a hosted app out of scope, and ADR-0005 says the product is deliberately not a hosted service.
- **The repository has no LICENSE file,** so "open source" is not yet true in the legal sense, and a pilot needs one.
- **The entrepreneurship problem statement is missing on the current branch;** it exists only on `main`.
- **Links broke when the entrepreneurship files moved:** three in `Docs/README.md`, three in the competitive landscape, five in the feature inventory.
- **Copies are stale:** the `.docx` versions of the canvas, landscape and feature inventory, and the Arabic translation of the requirement catalogue. None was re-synced today.
