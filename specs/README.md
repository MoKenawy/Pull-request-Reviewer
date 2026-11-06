# Feature Specs

Spec Kit features for v1. Each one follows the delivery sequence in
[SRS Appendix A](../Docs/agentic-code-review-srs-v1.md#appendix-a--delivery-sequence), and each
**selects** requirements from the SRS — none adds one. Rules: [`.specify/memory/constitution.md`](../.specify/memory/constitution.md).

```mermaid
flowchart LR
    F1["<b>001</b><br/>Walking skeleton"] --> F2["<b>002</b><br/>Execution evidence"]
    F2 --> F3["<b>003</b><br/>Rule library"]
    F3 --> F7["<b>007</b><br/>Regression harness"]
    F7 --> F4["<b>004</b><br/>Context quality"]
    F4 --> F5["<b>005</b><br/>Investigation<br/>experiment"]
    F5 --> F6["<b>006</b><br/>Hardening"]

    style F1 fill:#fff4e0
    style F3 fill:#e8f7e8
    style F7 fill:#e8f7e8
    style F5 fill:#f2f2f2
```

**Read the arrows, not the numbers.** 003 and 007 are both Appendix A step 3, split in two on
2026-11-06, and **007 runs before 004** — a feature's number is its identifier, not its place in the
queue, as 005 (step 4.5) already showed.

| # | Feature | Appendix A step | Core functions | Acceptance criteria it completes | Status |
|---|---|---|---|---|---|
| **001** | [Walking skeleton](./001-walking-skeleton/spec.md) | 1 | CF-1, CF-5, CF-7 · minimum of CF-6, CF-9 | AC-9, AC-13, AC-15, AC-16 · *starts* AC-1, AC-3, AC-10 | **In progress** — User Stories 1–2 and Phases 10–11 built; 35 of 149 tasks open ([plan](./001-walking-skeleton/plan.md), [tasks](./001-walking-skeleton/tasks.md)) |
| 002 | Execution evidence | 2 | CF-3 | AC-2, AC-7 | Not started |
| 003 | Rule library | 3 (part one) | **CF-8** — the library, scoping and attribution | AC-4, AC-18 | Not started |
| 007 | Regression harness | 3 (part two) — **runs before 004** | **CF-8** — the corpus, the catch rate, the `regression` command | AC-5 | Not started |
| 004 | Context quality | 4 | CF-2, CF-4 | AC-1, AC-3, AC-6, AC-8, AC-10, AC-12, AC-14 | Not started |
| 005 | Investigation experiment | 4.5 | CF-6 | AC-11 | Not started — **may end in a revert**, by design |
| 006 | Hardening | 5 | CF-6 tuning, CF-9, FR-11.x | Re-verifies all eighteen | Not started |

**Why measurement is third, not last:** after step 3, every change can be measured instead of argued
about — and 004 can be judged at depth 0 versus depth 1 on a fixed corpus.

**Why step 3 is two features, and what it costs.** 003 builds the rule mechanism; 007 builds the
instrument that says whether it works. Splitting them means 003 ships with nothing measuring it,
which is the position the Commit-First decision in
[`Draft/Agentic_Code_Review_Problem_Definition_v1.md`](../Docs/Draft/Agentic_Code_Review_Problem_Definition_v1.md)
argues hardest against. The mitigation is the schedule: 007 is next, not last.

**Before 001 is planned:** test S-1 from [`technical_stack.md`](../Docs/technical_stack.md) §7 — does
the default model call the finding tool reliably? — should run early in 001's plan. It is the
cheapest check in the project and it decides whether FR-5.6b's fallback is needed.
