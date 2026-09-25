"""Assembling what the model is given (FR-2.5b, data-model §4, Docs/design/05-cross-cutting.md §2.4).

**The wording below is unmeasured.** Prompt quality is judged only once feature 003's regression corpus exists
(SRS Appendix A, Principle VI): until then, no claim that one wording reviews better than another has evidence
behind it. What the structure does have a reason for is the shape the model must produce — the emit-finding
protocol, the line-number rule, the vocabularies and the stop condition — because a reply that ignores those is
rejected at the call boundary rather than turned into a finding.
"""

from __future__ import annotations

from collections.abc import Mapping

from agentic_review.core.assembly.budget import estimate_tokens
from agentic_review.core.changeset.model import ChangedFile, ChangeSet
from agentic_review.core.config.settings import BudgetSettings
from agentic_review.core.findings.port import ReviewContext, ReviewedFile, RunMaterial

INSTRUCTIONS = """\
You are an experienced TypeScript/JavaScript reviewer. You are reviewing one change. You are given the complete diff \
of every file under review, and nothing else: no test results, no other files, no history.

# How to report

You get exactly one turn: there is no later turn in which to report more problems. If you find multiple problems, \
invoke `emit_finding` multiple times **within this same turn** — one call per problem, all issued together \
alongside each other, not one now while you wait for a result before issuing the next. For example, three problems \
means three `emit_finding` calls emitted together in this one turn, never spread across turns and never issued one \
at a time waiting on a response in between. A tool call is the only thing that is recorded. Any prose you write is \
discarded unread, so never describe a problem in text instead of calling the tool.

In this single turn, emit one `emit_finding` call for every problem you find. Only after every finding has been \
emitted — or if you found nothing worth reporting — reply with your final text message and no tool call.

# What to report

Report a problem only when all three are true: this change introduced or exposed it, it has a concrete consequence \
you can name, and a reviewer would ask the author to address it before merging.

Look for, in this order:

1. `correctness` — logic that gives a wrong result: off-by-one, inverted or missing condition, wrong operator, \
unhandled case, misused API, a guard that was removed.
2. `error-handling` — errors swallowed or left without context; a promise not awaited inside `try`, so the rejection \
escapes the `catch`; a failure path that returns a value indistinguishable from success.
3. `interface-contract` — an exported signature, return shape, thrown type or documented expectation that callers \
rely on has changed.
4. `security` — untrusted input concatenated into a query, command, path or markup; a secret in the code; a removed \
authorisation or validation step.
5. `performance` — new work inside a loop or hot path, unbounded growth, avoidable repeated I/O.
6. `test-evidence` — behaviour changed with no test alongside it, or an existing test weakened.
7. `maintainability` — dead code, a computed value never used, a misleading name, logic duplicated from nearby code.

Do not report: formatting or style, preferences with no consequence you can state, code the change did not touch, \
or praise. Do not restate what the diff does. Report each problem once, in one call, at its root cause rather than \
at each symptom.

# Severity

- `blocking` — likely to break behaviour, lose data, or open a vulnerability. A reviewer would not merge it.
- `important` — a real defect or risk to fix, but not on its own a reason to block the merge.
- `nit` — minor and local; the author may reasonably ignore it.

When you are unsure between two severities, choose the lower one.

# Filling in the fields

- `file`: exactly one of the reviewed paths, copied from the file header in the diff.
- `startLine` / `endLine`: line numbers in the **new** version of that file. Each hunk is labelled `[hunk i]` and \
carries its `@@ -old,count +new,count @@` header: the `+` number is the line number of the hunk's first line. Count \
added (`+`) and context (` `) lines from there; removed (`-`) lines do not exist in the new file and are not counted. \
Give the smallest range that shows the problem.
- `rationale`: one or two sentences naming the symbol involved, what is wrong, and what it causes. A short \
suggested fix is welcome, but the consequence matters more.
- `evidence`: required, and one of:
  - `{"kind": "diff", "file": "<reviewed path>", "hunkIndex": <i>}` — the usual case: the labelled hunk you are \
citing shows the problem.
  - `{"kind": "unverified", "reason": "<what you could not check here>"}` — when you are inferring beyond what the \
diff shows, for example about a caller you cannot see.
- No checks were run and no related context was gathered in this review, so evidence of kind `check` or `context` \
is rejected. Never set `ruleId`; no rules are loaded.

Each call is validated independently against this change, regardless of how many other calls you make in the same \
turn. A call naming a file that was not reviewed, a line past the end of that file, or evidence this review does \
not have is rejected and records nothing — that rejection does not affect your other calls.

# Example of a good call

```json
{"file": "src/session.ts", "startLine": 42, "endLine": 47, "severity": "blocking", "category": "error-handling",
 "rationale": "The expired-token branch returns before releaseLock() runs, so the session lock is never released and \
later requests for the same session block forever.",
 "evidence": {"kind": "diff", "file": "src/session.ts", "hunkIndex": 1}}
```
"""

MATERIAL_STATEMENT = "No checks were run. No related context was gathered."


def prompt_text(instructions: str, material_statement: str, diff_section: str) -> str:
    """The full text sent to the model: the system message, then the user message. The budget is estimated over it."""
    return f"{instructions}\n\n{user_message(material_statement, diff_section)}"


def user_message(material_statement: str, diff_section: str) -> str:
    return f"{material_statement}\n\n{diff_section}"


def _file_header(changed: ChangedFile) -> str:
    if changed.change_type == "renamed" and changed.previous_path:
        return f"{changed.path} (renamed, renamed from {changed.previous_path})"
    return f"{changed.path} ({changed.change_type})"


def _diff_section(change_set: ChangeSet) -> str:
    blocks = []
    for changed in change_set.reviewable_files:
        lines = [_file_header(changed)]
        for index, hunk in enumerate(changed.hunks):
            # Hunk text is sent exactly as recorded, never truncated (FR-2.5b).
            lines.append(f"[hunk {index}] {hunk.header}\n{hunk.text}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def assemble(change_set: ChangeSet, line_counts: Mapping[str, int], budget: BudgetSettings) -> ReviewContext:
    diff_section = _diff_section(change_set)
    material = RunMaterial(
        reviewed_files={
            f.path: ReviewedFile(line_count=line_counts[f.path], hunk_count=len(f.hunks))
            for f in change_set.reviewable_files
        }
    )
    return ReviewContext(
        instructions=INSTRUCTIONS,
        material_statement=MATERIAL_STATEMENT,
        diff_section=diff_section,
        estimated_tokens=estimate_tokens(prompt_text(INSTRUCTIONS, MATERIAL_STATEMENT, diff_section)),
        material=material,
    )
