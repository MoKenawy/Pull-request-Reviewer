# Code Review Tooling — Reference Notes

A neutral, descriptive reference on seven tools in and around the automated code-review space. This document does **not** compare them to Agentic Code Review or take a competitive stance; it simply describes what each tool is, how it works, and how it is priced and licensed. For competitive framing, see `competitive-landscape.md`.

All facts were gathered from the tools' own sites and repositories in September 2026. Pricing and feature details change frequently — treat figures as a snapshot, not a contract, and re-verify before relying on them.

---

## Greptile

**What it is.** An AI pull-request review bot organized around whole-codebase understanding. It connects to a repository, indexes it, and posts review feedback on pull requests, aiming to reason about a change in the context of the surrounding code rather than the diff alone.

**How it works / notable features.**
- Repository-wide context as the central design idea, rather than line-local feedback.
- A "TREX" runtime-validation capability (in beta) alongside standard reviews. *Re-read 2026-10-10:* the changelog entry of 2026-06-15 says it "writes and runs targeted tests in a sandbox" against "the services, dependencies, and framework your repo already uses", and "attaches logs, screenshots, traces, scripts, or videos when something fails."
- Custom rules, external-app connections, a CLI, and a knowledge base.
- Self-hosting is available on the Enterprise tier.

**Pricing (snapshot).**
- **Starter** — Free, for one active developer. Unlimited repositories and 50 credits per month, where 1 credit = 1 standard review and 3 credits = 1 TREX review.
- **Pro** — $30 per seat per month. Unlimited repositories and users, 50 credits included per seat, $1 per additional credit, custom rules.
- **Enterprise** — Custom pricing. Self-hosting, SSO/SAML, GitHub Enterprise support, compliance and custom terms.
- **Programs** — Free for qualified non-commercial projects under MIT or Apache licenses; 50% discount for pre-Series-A startups under $2M revenue.

**Model.** Hosted service, credit-metered per review. Closed-source engine.

---

## CodeRabbit

**What it is.** A widely adopted AI-first pull-request reviewer that has expanded into a broader "agentic change management" platform. It reports being used by 17,000 customers across 6 million repositories and describes itself as the most-installed AI app on GitHub and GitLab.

**How it works / notable features.**
- **Review** — Automated line-by-line review on every PR, with committable one-click suggestions and an agentic chat for follow-up.
- **Triage** — Scores, ranks, and routes PRs by priority, risk, reward, effort, and complexity; a Kanban-style queue view; auto-assignment of reviewers. "Blast radius" is a named feature on higher tiers.
- **Change Stack** — Code-explainability layer for large diffs, including semantic diffs, blast-radius context, and architectural diagrams.
- **Security** — Continuous monitoring, per-PR security review, dependency-vulnerability detection, and finding verification to reduce false positives.
- **Context engine** — A deterministic "codegraph," adaptive learning of team conventions ("Learnings"), business context from PRDs/issues, and an ensemble of models and tools.
- **Verification** *(added 2026-10-10)* — The vendor's blog of 2025-07-17 says it "runs verification scripts on the review comments provided by the LLMs", that these "are generated in the sandbox", and that "any low value feedback is automatically filtered out and not passed on to the user". Its tools documentation says 50+ linters and scanners "run automatically in secure sandboxed environments".
- Also offers IDE reviews, CLI reviews, a Slack agent, and a cloud coding agent.

**Pricing (snapshot, billed annually).**
- **Essentials** — $24/developer/month. Reviews, triage, change stack, security monitoring, 1-click fixes, learnings, MCP connections (5), single-repo analysis.
- **Team** — $48/developer/month. Adds multi-repo analysis (5), custom pre-merge checks, finishing touches (unit tests, merge-conflict resolution, simplify), post-merge actions, higher limits.
- **Advanced** — $72/developer/month. Adds continuous security monitoring, per-PR security review, blast radius, architectural impact.
- **Enterprise** — Custom. RBAC, SSO, audit logging, API access, self-hosting, multi-org, SLA.
- **Add-ons** — Usage-based security scans, pay-as-you-go reviews, a cloud coding agent ($0.4/agent-minute after a first included turn), and a Slack agent.
- A free plan exists for open-source projects.

**Model.** Hosted service, per-seat subscription with usage-based add-ons. Closed-source. Recently raised $143M.

---

## Qodo (formerly Codium)

**What it is.** An agentic code-quality and governance platform spanning the IDE, pull requests, CLI, and Git workflows. It positions itself around standardizing and enforcing code quality and review across the whole SDLC ("govern code at the speed AI writes it"). Its PR-review engine has an open-source lineage (PR-Agent / Qodo Merge).

**How it works / notable features.**
- **AI code review** — Specialized review agents reason over full codebase context to flag bugs, rule violations, and requirements gaps, aiming for low noise.
- **Rules system** — Self-learning, machine-readable coding standards derived from a codebase and PR history; effectiveness is measured continuously, with rule conflicts and "decay" surfaced over time.
- **Context engine** — Pulls from rules, codebase structure and dependencies, indexed PR history, and business requirements from tickets and specs. Cross-repo context to surface breaking changes and dependency conflicts.
- **Governance layer** — Centralized visibility into findings, resolution rates, and risk concentration; an audit trail; repo-relationship mapping; a "system of record" for code-quality decisions.
- Ships across VS Code, JetBrains IDEs, and Git providers; supports major languages.

**Pricing / security.**
- Uses a credit-based system; specific tiers are on the pricing page (not enumerated here). Free for open-source projects.
- Security posture emphasized: zero data retention (code analyzed and discarded), SOC 2 Type II, on-premises and single-tenant deployment options.

**Model.** Hosted platform with enterprise/self-host options; open-source lineage in the PR-review component (PR-Agent). *Re-read 2026-10-10:* the PR-Agent repository is MIT-licensed and describes itself as "a community-maintained legacy project of Qodo"; "Qodo has donated PR-Agent to the open-source community." Qodo's code-review documentation says "a judge agent merges their findings, removes duplicates, and filters out anything low-confidence", and does not say that it runs tests or executes code.

---

## Claude Code — Code Review

**What it is.** Anthropic's managed pull-request review feature within Claude Code. A fleet of specialized agents analyze PR changes in the context of the full codebase, looking for logic errors, security vulnerabilities, broken edge cases, and subtle regressions. It is in research preview for Team and Enterprise subscriptions; a local `/code-review` command is available on other plans.

**How it works / notable features.**
- Multiple agents analyze the diff and surrounding code in parallel; a **verification step checks candidate findings against actual code behavior** to filter false positives; results are deduplicated and ranked by severity.
- Findings post as **inline comments** on the specific lines, with a summary in the review body and a collapsible extended-reasoning section. *Re-read 2026-10-10:* "Findings include a collapsed **Why this was flagged** section that you can expand to read why Claude flagged the issue and how it verified the problem."
- **Severity levels**: Important (🔴), Nit (🟡), and Pre-existing (🟣).
- **Non-blocking by design** — the check run always completes with a neutral conclusion, so it never blocks merges through branch protection.
- A **machine-readable comment** on the last line of the check-run details can be parsed (with `gh` and `jq`) for per-severity counts.
- Triggers: once on PR creation, on every push, or manually via `@claude review`. Reviews of fork PRs run only on explicit request.
- Tunable via `CLAUDE.md` (shared project context; violations treated as nits) and `REVIEW.md` (review-only instructions covering severity calibration, nit caps, skip rules, verification bars, and re-review convergence).
- A local `/code-review` command reviews a diff in the terminal, with flags to apply fixes (`--fix`), post inline comments (`--comment`), or escalate to a deeper cloud "ultrareview."

**Pricing (snapshot).** Billed on token usage, separate from a plan's included usage. Each review averages **$15–25**, scaling with PR size, codebase complexity, and how many findings require verification. Review triggers affect total cost (every-push multiplies it); a monthly spend cap can be configured.

**Model.** Managed service on Anthropic infrastructure (with a local mode). Not available for Zero-Data-Retention organizations in the managed form.

---

## Danger / DangerJS

**What it is.** An open-source tool that runs during CI to automate routine code-review chores. It does not perform semantic or AI analysis; it lets a team codify its process norms as executable rules. DangerJS is the JavaScript/TypeScript port (the original Danger is Ruby); there is also a Swift version.

**How it works / notable features.**
- Runs as a step in the CI pipeline and comments on the PR/MR.
- Rules are written in a "Dangerfile" using the tool's DSL, with a plugin system for sharing common checks.
- Typical uses: enforcing CHANGELOG entries, requiring links to JIRA/Trello in PR bodies, requiring descriptive labels, flagging common anti-patterns, highlighting build artifacts, and drawing extra attention to specific files.
- Works across GitHub, GitLab, and Bitbucket and multiple CI systems.

**Pricing / license.** Free and open source under the MIT license. The Ruby repository shows roughly 5.7k stars and a mature, long-running history.

**Model.** Self-hosted library that runs in your own CI. Deterministic and rule-based; no model inference.

---

## Graphite

**What it is.** A developer-productivity platform built around the **stacked pull request** (stacked diffs) workflow — the practice of breaking a large branch into a series of small, individually reviewable PRs. Over time it added AI review; "Diamond" (its AI reviewer) and "Chat" were unified in October 2025 into **Graphite Agent**. Graphite was acquired by Cursor (Anysphere) in December 2025 and continues to operate as an independent product.

**How it works / notable features.**
- **Create** — Stacked PRs via a CLI and VS Code extension, keeping each diff small.
- **Review** — A modern PR interface, AI reviews, and conversational chat that can apply changes in the diff; the vendor cites less than 3% of AI comments rated unhelpful.
- **Merge** — A stack-aware merge queue that keeps merges conflict-free and avoids redundant CI runs.
- Lets teams define codebase-specific patterns and set filters for sensitive information.
- Reports 100K+ developers across 500+ companies (e.g., Shopify, Snowflake, Figma).

**Pricing (snapshot).**
- **Hobby** — Free, for personal projects.
- **Starter** — $20/user/month.
- **Team** — $40/user/month.
- **Enterprise** — Custom.
- The AI reviewer has also been offered as an add-on priced per active contributor.

**Model.** Hosted platform (GitHub-native) with a free tier; workflow tool first, AI reviewer second. Closed-source.

---

## Quick reference table

| Tool | Category | Core mechanism | Open source | Free tier | Entry paid price |
|------|----------|----------------|-------------|-----------|------------------|
| Greptile | AI PR reviewer | Whole-repo context, credit-metered reviews | No | Yes (1 dev) + OSS program | $30/seat/mo |
| CodeRabbit | AI review + change-management platform | Codegraph, triage, learnings, security | No | Yes (OSS) | $24/dev/mo |
| Qodo | AI review + governance platform | Context engine + self-learning rules | Partial (PR-Agent) | Yes (OSS) | Credit-based |
| Claude Code Review | Managed multi-agent reviewer | Parallel agents + behavior verification | No | Local `/code-review` only | ~$15–25/review (usage) |
| Danger / DangerJS | CI process-rule automation | Deterministic Dangerfile rules | Yes (MIT) | Free | Free |
| Graphite | Stacked-diffs workflow + AI reviewer | Stacked PRs, merge queue, Graphite Agent | No | Yes (Hobby) | $20/user/mo |

*Snapshot as of September 2026. Re-verify pricing and features before citing.*
