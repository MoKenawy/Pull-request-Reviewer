# ADR-0011 — The CLI may read a public pull request; nothing else of GitHub moves into v1

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-09 |
| **Deciders** | Project maintainers |
| **Amends** | [ADR-0006 — local CLI core, Action as adapter](./0006-local-cli-core-action-as-adapter.md) — one consequence only: v1's CLI gains a change-set producer that reads from GitHub |
| **Constrained by** | [ADR-0003 — untrusted code isolation](./0003-untrusted-code-isolation-and-fork-triggers.md) — its exposure must stay closed |
| **Supersedes detail** | SRS §1.2 and §7: "GitHub integration of any kind" is v3 |

> **What this record does not change.** The GitHub Action is still v3. Nothing is posted to GitHub: no comment, no status check, no suggested change. ADR-0006's rule that an adapter only translates stands, and so does its seam — the change set (FR-10.3c). This record adds one more way to **produce** a change set, on the surface v1 already has.

---

## The question

v1 reviews work that is on the developer's own disk. **Should the same command also review a pull request that is on GitHub, named by its URL, before the Action exists?**

The SRS said no in so many words: "GitHub integration of any kind (v3)". That sentence was written to defer the Action and everything it drags in — triggers, tokens, comments, a stranger's code running next to our credentials. Reading a public pull request's diff needs none of those.

## Vocabulary

| Term | Meaning here |
|---|---|
| **Pull-request scope** | A change scope selected by a pull request URL. It compares the pull request's head with the branch it targets. |
| **Blobless clone** | `git clone --filter=blob:none`: commits and directory listings are downloaded, file contents only when something asks for them. |
| **No-checkout clone** | `git clone --no-checkout`: no working tree is written. The repository's files never exist on disk as files. |
| **Pull-request source** | The one interface behind which a pull request is read. Today it has one implementation. |

---

## Context

### What the change set already promised

FR-10.3c exists so that "PR head against base" can replace "my working tree" with nothing downstream noticing. That promise was made for the v3 Action. It holds equally for a CLI flag: the files-and-hunks structure does not care who filled it.

### What was actually being deferred

ADR-0003 describes the danger of pull requests precisely: the system "executes attacker-controllable code on a machine that holds our credentials" — because running a test suite means installing dependencies, and installing runs `postinstall`. That danger comes from **checking out and executing**, not from **reading**. A design that never checks out cannot run anything.

There is a second, quieter route to the same credential, and it is specific to this tool: the configuration file names the provider URL (`agent.baseUrl`). A pull request that could supply the configuration could point the reviewer — and the API key it sends — at any server.

### The primary persona

SRS R-5 states that v1 serves the author, not the reviewer clearing a queue. Reviewing someone else's pull request from a terminal is the first thing v1 does for that reviewer. It does not close R-5 — there is still no comment on the pull request — but it stops being true that v1 cannot look at one.

---

## Options considered

### Option A — Wait for v3

| | |
|---|---|
| **For** | The SRS as written. No new exposure to reason about. |
| **Against** | The seam built for this exact substitution goes unexercised until the Action, which is when a mistake in it is most expensive. The reviewer persona gets nothing from v1 or v2. |

### Option B — Use the GitHub API now

| | |
|---|---|
| **For** | The API knows the pull request's real base branch and returns the diff directly. Private repositories become reachable. |
| **Against** | It needs a token: a second credential, and the end of FR-10.1's "without requiring GitHub API access or repository credentials". It puts a GitHub client in the dependency list — ADR-0006's first named sign of a breached seam. Unauthenticated use is rate-limited to the point of being a demo. |

### Option C — Read it with git, behind an interface, and never check it out ✅

| | |
|---|---|
| **For** | No token, no API, no new dependency: git is already a prerequisite. A no-checkout clone cannot execute anything, so ADR-0003's exposure is not opened. The reader sits behind one interface, so a better one can replace it. |
| **Against** | git cannot know which branch a pull request targets. It reads public repositories only. A clone costs seconds and a network connection the tool otherwise never needed for anything but the model. |

---

## Decision

**Option C.** v1's CLI gains a pull-request scope, selected by `--pr <URL>`.

### The rules

1. **Git transport only.** The pull request is read with `git clone --filter=blob:none --no-checkout`, then its head is fetched from `refs/pull/<n>/head` — the ref GitHub publishes for every pull request, including those opened from forks. No GitHub API is called and no token is read.
2. **Nothing from the pull request is executed.** There is no working tree, so there is nothing to run, no hook and no install step. Checks are therefore **not executed** under this scope; each is recorded as skipped (FR-4.8).
3. **No configuration is read from the pull request** (FR-10.3d). Settings come from a file the user names, or from the defaults.
4. **git may not ask for credentials.** No credential helper, no prompt. A repository that is private or missing is a failure with a message, never a login dialog.
5. **Failing to read the pull request is a preflight failure.** It is a prerequisite that could not be met, so the run stops before any model call (exit 3), like a missing repository.
6. **The base is the repository's default branch unless the user names another.** The output states which was used.
7. **The temporary clone is removed** when the run ends, however it ends.
8. **Everything pull-request-specific sits behind one interface** — `PullRequestSource` — and the rest of the system sees only the change set it produces.

### This implementation is interim

Rule 1 is what makes this buildable today; it is not the destination. The git-based reader is **hand-written plumbing for something the official GitHub MCP server (`github/github-mcp-server`) already provides**, and it is intended to be replaced by a `PullRequestSource` backed by that server. Rule 8 exists so that the replacement is a second implementation, not a rewrite.

That replacement is **not** decided here. It will need its own record, because it changes three things this one holds fixed:

| What changes | Why it needs deciding |
|---|---|
| A **GitHub token** becomes necessary | The MCP server does not work anonymously. That is a second credential under FR-1.3a's rules, and an exception to FR-10.1 for this scope |
| An **MCP client** enters the dependency list | A framework and network dependency. It may not live under `core/` (FR-5.8), and `technical_stack.md` must name it |
| Rule 1 is withdrawn | Private repositories and the pull request's true base branch become reachable — and with them, the question of what a token-bearing run may be pointed at |

Until then, the hand-written reader is kept deliberately thin. It should not grow a feature the MCP server already has.

---

## Consequences

### Good

- **The FR-10.3c seam is exercised now**, by a second and a third producer (a branch range, a pull request), before v3 depends on it.
- **A reviewer can run v1 on someone else's pull request**, from any directory, with one flag.
- **No new credential and no new dependency.**
- **The trust boundary is drawn where it is cheap to hold**: nothing is checked out, and the configuration cannot come from the stranger.

### Bad

- **The tool makes a network call that is not to the model provider.** Until now "offline except for the model" was true of every run.
- **The base branch can be wrong.** A pull request aimed at a release branch is compared with the default branch unless the user says otherwise. The output says which base was used; it cannot say whether that was the right one.
- **No checks ever run for a pull request**, so its findings are text-derived or unverified. This is the price of rule 2 and it is permanent for this implementation.
- **Public repositories only.**
- **A blobless clone still downloads the whole commit history.** On a very large repository that is slow.

### Neutral

- The local `range` scope gains a nameable head (`--head`), because the pull-request scope is the same three-dot comparison run somewhere else.
- ADR-0003 remains scoped to the Action and remains Proposed. This record borrows its reasoning; it does not activate it.

---

## How we would know this decision was violated

- Any module under `core/` or `cli/` imports a GitHub client, or reads a GitHub token.
- The pull-request path creates a working tree, runs a hook, or runs a check.
- A setting takes effect that came from a file inside the pull request.
- git opens a credential prompt during a review.
- Anything outside `core/changeset/` learns how a pull request was fetched — a path, a remote name, a ref that only the git reader would have.
- A temporary clone outlives the run that made it.

## What the requirements need to change

| Document | Change |
|---|---|
| **FR-10.3a** | A fifth selection: a public pull request named by its URL. A range may name its head |
| **FR-10.3d** *(new)* | Nothing from a pull request is executed; no configuration is read from it |
| **FR-4.8** | Extended to the pull-request scope |
| **SRS §1.2, §7** | "GitHub integration of any kind" narrowed: reading a public pull request's change set is in v1; everything else stays v3 |
| **FR-10.1** | Unchanged, and still true: no API access and no repository credentials |
