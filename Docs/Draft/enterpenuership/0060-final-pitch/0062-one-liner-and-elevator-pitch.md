# One-liner and Elevator Pitch — Agentic Code Review

**Status: non-normative.** A business-side working document, not a specification. It defines nothing to build.

Steps 1 and 2 of the *Pitch Implementation Guidelines* (2026-10-03). Every fact comes from [`0061-pitch-input.md`](./0061-pitch-input.md), which names the file behind it, with one exception: the 1968 conference report quoted in the hook, which is an outside source read for this file. Audience: the DEPI final-pitch jury. The ask is pilot teams, not money.

**Updated 2026-10-09.** Who has the problem, the pain and the tagline are worded in one place, [`000-problem-and-audience.md`](../000-problem-and-audience.md). The tagline is **"Review that shows its evidence"**.

**Updated 2026-10-14.** The problem slide and the ten-minute talk now use a business wording, for listeners who are not engineers ([`000-problem-and-audience.md`](../000-problem-and-audience.md), section 1, "For a business audience"). The elevator pitch does not carry that spoken statement: it is about 63 words, and adding it would take the pitch past 60 seconds at either pace. The one-liner and the pitch's story line took the new "Pain, in a sentence" instead: AI-written software "that looks right but isn't", in place of code "that passes its tests but doesn't fit their codebase".

**Updated 2026-10-10 (tasks 11 and 12 in [`0064-progress-report.md`](./0064-progress-report.md)).** The one-liner's last part, how we do it, is now the tagline's claim. The five-part script is replaced by three lines: hook, story, ask. The hook is the software crisis of 1968, chosen by the founder and checked against the conference report; "Green no longer means right" is no longer spoken. The statistic on AI review comments is kept in reserve. Neither the one-liner nor the elevator pitch names TypeScript (founder, 2026-10-10): it narrows who listens and is not needed to catch attention. One thing still waits: a reviewer's own words. The ask's numbers were set on 2026-10-10: six teams for eight weeks. The differentiator was re-checked the same day; its result is under the one-liner below.

---

## Step 1: the one-liner

> We help reviewers catch AI-written software that looks right but isn't, by showing the evidence for every finding.

| Part of the formula | Our words | Where it comes from |
|---|---|---|
| Who | Reviewers | "Who, in a sentence" in [`000-problem-and-audience.md`](../000-problem-and-audience.md), section 1, is "reviewers on TypeScript teams". The one-liner and the elevator pitch drop "on TypeScript teams" (founder, 2026-10-10): it narrows who listens and is not needed to catch attention. In full: "an engineer who reviews a teammate's AI-assisted TypeScript or JavaScript pull request, in a company or funded team" |
| Problem | AI-written software that looks right but isn't | "Pain, in a sentence" in the same place, since 2026-10-14; until then "AI-written code that passes its tests but doesn't fit their codebase". In full: reviewers "can no longer tell, from clean code and passing tests, whether a change fits the codebase" |
| How | Showing the evidence for every finding | "What we do" in the same place: "Review the change and show the evidence for every finding, or say the finding is unverified." It is the tagline's claim, and the build already does it (see the second challenge below) |

**Length.** 18 words, down from 22 on 2026-10-14 and from 30 before that; the guide's laundry example is 22. The guide asks for about 10 seconds.

**What changed in the "how", and why.** Until 2026-10-10 it read "by checking every change against the project's own rules and test results". Today's build runs no tests and loads no project rules: both are "specified, not built" ([`000-problem-and-audience.md`](../000-problem-and-audience.md), section 3). The new wording claims only what the build does.

**After the differentiator re-check (task 2, 2026-10-10).** The one-liner stays as it is: it says what the product does, and that is true of today's build. It is not something only we do. Rivals' own pages show Claude Code Review telling the reader "how it verified the problem" and Greptile attaching logs and traces ([`competitive-landscape.md`](../competitive-landscape.md), "Differentiator re-check"). The part that is ours is the second half of the definition, "or say the finding is unverified": three of four rivals say they filter such findings out. If the one-liner should carry the difference and not only the method, a 25-word form is: "We help reviewers catch AI-written software that looks right but isn't, by showing the evidence for every finding and flagging what it could not verify." That choice is the founder's.

**Done when:** you say it to someone outside the project and they repeat it back without notes. This test has not been run.

### The customer's own words

`[MISSING: a reviewer's own words]`. The guide asks for the pain as the customer says it. The pain above is the team's wording: no reviewer has been interviewed, and every quotation in the references is second-hand.

Three to five short interviews would supply the words. Who to ask: people who match "Who" above. What to ask:

1. Tell me about the last AI-assisted pull request you reviewed that worried you. What happened?
2. What did you check by hand on it that you wish you had not had to?
3. When an AI reviewer commented on a pull request, how did you decide whether to act on the comment?

Write down their exact phrases. The phrase most of them use for the pain replaces "looks right but isn't" here, and then in [`000-problem-and-audience.md`](../000-problem-and-audience.md), which every other document copies.

### Three things a listener may challenge

1. **"How do you know it catches that code?"** We do not know yet. There is one real run (see the story below) and no measured catch rate: the regression set that would measure one is not built.
2. **"What is the evidence, today?"** The part of the change the finding rests on, or the word "unverified" with a reason. In the real run, the one finding cited a hunk of the diff. Evidence from a test run or from the surrounding code is specified, not built: the build rejects such a reference with "no checks were run in this review; cite the diff or mark the finding unverified" ([`schemas-and-contracts.md`](../../../design/schemas-and-contracts.md)).
3. **"Showing evidence does not catch anything by itself."** True. The review finds the problem; the evidence is what lets a reviewer check the finding quickly. The definition says it this way: "a finding that carries its evidence can be checked quickly, and one that has none says so."

---

## Step 2: the elevator pitch in three lines

The guide's formula: a **hook** (a surprising fact or a question about the problem), a **story** (who suffers, what you do, proof it works) and an **ask** (exactly what you want from this listener), about 20 seconds each and under 60 in all.

### The script

| Part | Seconds | What we say | Words |
|---|---|---|---|
| Hook | 18 | In 1968, at a NATO conference, experts argued about what some called the "software crisis". One said the industry's demands seemed to be "going ahead a good deal faster than our progress." Today AI writes code faster than a team can read it. | 43 |
| Story | 19 | Reviewers face AI-written software that looks right but isn't. Agentic Code Review reads each change and shows the evidence for every finding, or says it is unverified. On an open pull request in Microsoft's Playwright, it reported one finding, with its evidence, in about two minutes. | 46 |
| Ask | 11 | That is one run, not a measured result. So we ask for teams, not money: six teams to run it on their real changes for eight weeks. | 27 |
| **Total** | **48** | Under a minute, and it ends on the ask | **116** |

**Timing check (Calculated).** Seconds are words ÷ 150 words a minute × 60, rounded up: 43 → 17.2, 46 → 18.4, 27 → 10.8. In all, 116 ÷ 150 × 60 = 46.4 seconds. At a slower 130 words a minute: 116 ÷ 130 × 60 = 53.5 seconds. Both paces are assumptions, not source figures. A quotation is usually said more slowly than plain speech, so the margin at the slow pace is about six seconds. If a stopwatch says it is over, cut "with its evidence" from the story first. Only a stopwatch settles it.

**"About two minutes" (Calculated).** 125.4 seconds ÷ 60 = 2.09 minutes, including the time to clone the repository.

### Where each line comes from

| Part | Source | What to know before saying it |
|---|---|---|
| Hook, 1968 | *Software Engineering: Report on a conference sponsored by the NATO Science Committee, Garmisch, Germany, 7th to 11th October 1968*, section 7.1.2, pp. 120–121. An outside source, read for this file on 2026-10-10 (details below) | "What some called": the report says members debated the term and disagreed on how serious things were. The second sentence quotes nine of Fraser's words exactly and paraphrases the rest of his sentence. "Experts" stands for the report's "more than fifty people", "all concerned professionally with software" |
| Hook, today | "Why now" in [`000-problem-and-audience.md`](../000-problem-and-audience.md), section 1: "AI writes code faster than a team can read it." | The team's wording of a framing that the background study calls "asserted by every source and measured by none". The hook sets 1968 beside today; it does not say the crisis has returned. That it has is the founder's view, and should be said as a view if it is said |
| Story, who suffers | [`000-problem-and-audience.md`](../000-problem-and-audience.md), section 1 | The team's wording, not a reviewer's. The definition's "on TypeScript teams" is left out on purpose |
| Story, what we do | The same place, "What we do"; SRS FR-5.2c | True of today's build. The evidence today is the part of the change itself (challenge 2 above) |
| Story, proof | The run on microsoft/playwright#43199, 2026-10-09: 16 files, 10 reviewed, 1 finding, 125.4 seconds ([`0063-pitch-deck.md`](./0063-pitch-deck.md), slide 3) | One run on one pull request. The finding is a nit and the tool's own claim: Playwright's maintainers have not confirmed it. No checks ran, and 6 of the 16 files were listed but not reviewed. It shows the tool runs end to end on real code, not that it catches defects |
| Ask | Founder, 2026-10-03; the numbers, 2026-10-10; slide 10 | Six teams for eight weeks, from 1 January 2027. The start date and the milestone are on the slide and are left out of the sixty seconds. It no longer says "TypeScript teams", but the tool reviews only TypeScript and JavaScript (SRS §1.2: "in a TS/JS repository"), so a team that comes forward must have such code. Say so at that point, not in the pitch. The first sentence is there so the proof is not heard as more than it is |

**Rehearsal test:** say it out loud with a timer. If you run out of breath or pass 60 seconds, cut words. This test has not been run.

### The hook: three candidates, one chosen

Chosen by the founder on 2026-10-10: the software crisis.

| Candidate | For | Against | Decision |
|---|---|---|---|
| **The software crisis of 1968** | Memorable, and it makes the problem larger than one tool. The 1968 side is checked against the report and quotable | The 1968 debate was about building large systems, not reviewing code. That our time is a second crisis is our view, measured by nobody | **Chosen.** Worded as a comparison, so it needs no claim we cannot source |
| **The MSR statistic** (developers act on about 60% of human review comments, 0.9% to 19.2% of AI comments) | The best-sourced figure we hold: peer-reviewed, re-read at the source on 2026-10-09. It leads straight to the tagline: comments are ignored, so show the evidence | Second-hand inside the paper. It is about the supporting pain, not the headline pain. Two percentages are hard to say aloud | **Kept in reserve**, worded below, for questions and for the ten-minute talk |
| **"Green no longer means right"** | Short and already familiar to the team | The team's own summary, not a fact and not a customer's words. "Green" is jargon to a listener who has not used a test runner. It was withdrawn as a tagline and a headline on 2026-10-09 | **Dropped** from the script |

### The software-crisis hook: what was checked

Checked on 2026-10-10.

- **The 1968 side, against the report itself.** *Software Engineering: Report on a conference sponsored by the NATO Science Committee, Garmisch, Germany, 7th to 11th October 1968*, editors Peter Naur and Brian Randell, January 1969. Read in the 2001 edition reset by Robert M. McClure from a scan of the original ([PDF](https://www.scrummanager.com/files/nato1968e.pdf)); its own note warns that some scanning errors may remain. Page numbers below are the original edition's.
  - The conference did not declare a crisis. Section 7.1.2 (p. 120) says: "There was a considerable amount of debate on what some members chose to call the 'software crisis' or the 'software gap'", and that members "had widely differing views on the seriousness, or otherwise, of the situation". So say "what some called", not "the conference named".
  - What the crisis was (David and Fraser, p. 120): "There is a widening gap between ambitions and achievements in software engineering", between promises and performance, and "between estimates of software costs and expenditures". It was about large systems that arrived late, over cost and unreliable.
  - The line the hook draws on is Fraser's (p. 121), in full: "We are making great progress, but nevertheless the demands in the industry as a whole seem to be going ahead a good deal faster than our progress."
  - Other quotable lines. McClure (p. 122): "It seems almost automatic that software is never produced on time, never meets specification, and always exceeds its estimated cost." Dijkstra (p. 16): "The dissemination of knowledge is of obvious value — the massive dissemination of error-loaded software is frightening." Dijkstra's is the sharpest, but used about AI-written code it implies a defect rate that no source of ours measures.
  - A line to expect in reply. Kolence (p. 121): "I do not like the use of the word 'crisis'. It's a very emotional word."
  - A figure, if one is wanted (David, p. 15): OS/360 "cost IBM over $50 million dollars a year during its preparation, and at least 5000 man-years' investment".
- **Fit with our problem.** Partial. In 1968 the demand for software ran ahead of the ability to build it well. Today code is produced faster than it can be checked: "Generation got cheap; verification and maintenance did not" (background study A1, a framing "asserted by every source and measured by none"). The shared idea is one activity outrunning the discipline that keeps it sound. It is a comparison, not a return of the same crisis, and that our time is a second crisis is the founder's view, not a finding.
- **The three "modern crisis" traits.** Non-deterministic software and scaling and data demands describe building AI systems, not reviewing AI-written code, and no reference of ours supports either. They are not in the script. The black-box trait fits and has support in the references: "patches the authors cannot explain and fixes for problems that don't exist" (OpenTofu, one project, in the background study), and rivals whose "engine is a hosted black box" (competitive landscape). The claim that QA is becoming "obsolete" has no source and should not be said.
- **Modern figures that could follow the 1968 line in a longer talk.** All are in [`004-market-study.md`](../004-market-study.md), all are comparisons and none shows a cause: median review duration up 441.5% at teams with high AI adoption, and incidents per pull request up 242.7% (both Faros AI through O'Reilly, vendor data); about 4x the code for about 12% more delivered value (GitClear through O'Reilly). The primary reports have not been read. Gartner's forecast is not used: it is unverified.
- **A date, if the pitch falls in October.** The conference ran from 7 to 11 October 1968, which is 58 years before this month (Calculated: 2026 − 1968 = 58). "In October 1968" adds one word to the hook.

### The hook in reserve: the MSR statistic

39 words (Calculated: 39 ÷ 150 × 60 = 15.6 seconds). Source: earlier work cited by Chowdhury et al., MSR 2026; [`000-problem-and-audience.md`](../000-problem-and-audience.md), section 6, and [`004-market-study.md`](../004-market-study.md): "developers act on human review comments about 60% of the time, against 0.9%–19.2% for AI comments". It is peer-reviewed but second-hand, compares two kinds of comment without saying why they differ, and supports the supporting pain "an AI second opinion they cannot rely on", not the headline pain.

> When a human reviewer comments on code, the developer acts on it about 60% of the time. When an AI reviewer comments, the figure is between 0.9% and 19.2%. Most of what AI reviewers say is not acted on.

### The guide's three fixes, checked

| Fix | Status |
|---|---|
| Do not start with yourself | Met: the script opens with a moment in the history of the problem. The product's name first appears in the story. Names and titles do not appear |
| No jargon | **Check for this jury.** The script contains "NATO conference" and "pull request". For a non-technical listener, "a proposed change to Microsoft's Playwright project" is a plain reading of "pull request". "Codebase" and "passes its tests" left the script on 2026-10-14. The words of the old script, "legacy v1 auth backend", "diff", "command-line" and "open-source", are gone |
| Always end with an ask | Met: it ends on six teams for eight weeks |

### The ask changes per listener

The script above speaks to someone who can bring a team: a team lead, an engineering manager, a partner company. To the jury itself, say what you want the jury to do: `[MISSING: what the jury can do to get you those teams]`.
