"""Assembling what the model is given (FR-2.5b, data-model §4, Docs/design/05-cross-cutting.md §2.4).

**The wording below is unmeasured.** Prompt quality is judged only once feature 007's regression corpus exists
(SRS Appendix A, Principle VI): until then, no claim that one wording reviews better than another has evidence
behind it. What the structure does have a reason for is the shape the model must produce, because a reply that
ignores it is rejected at the call boundary rather than turned into a finding. The prompt carries only the
one-turn protocol and the stop condition. How to fill in a call — the line-number rule, the severity and category
vocabularies, the evidence kinds, an example — travels with the bound ``emit_finding`` tool itself: its description
is ``TOOL_DESCRIPTION`` and each argument's rules are its schema description on ``FindingDraft``.

**Where the system prompt comes from.** When Langfuse credentials are in the environment, the system prompt is the
Langfuse-managed prompt ``pr-agent-system-prompt`` (its ``production`` label), so the wording can be iterated on
without a release. ``INSTRUCTIONS`` below is the fallback: it is used when Langfuse is not configured, and when the
fetch fails for any reason. A missing or unreachable prompt store never fails a review (FR-11.2 in spirit).
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

from agentic_review.core.assembly.budget import BudgetExhausted, estimate_tokens
from agentic_review.core.changeset.model import ChangedFile, ChangeSet
from agentic_review.core.config.settings import BudgetSettings
from agentic_review.core.findings.port import ReviewContext, ReviewedFile, RunMaterial

INSTRUCTIONS = """\
You are an experienced TypeScript/JavaScript reviewer. You are reviewing one change. You are given the complete diff \
of every file under review, together with the review rules below. You are given nothing else: no test results, no \
other files, no history.

# How to report

Report every problem with the `emit_finding` tool. You get exactly one turn: there is no later turn in which to \
report more problems. If you find multiple problems, invoke `emit_finding` multiple times **within this same turn** \
— one call per problem, all issued together, not one now while you wait for a result before issuing the next. For \
example, three problems means three `emit_finding` calls emitted together in this one turn. Any prose you write is \
discarded unread, so never describe a problem in text instead of calling the tool.

Only after every finding has been emitted — or if you found nothing worth reporting — reply with your final text \
message and no tool call.

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
or praise. Do not restate what the diff does. Report each problem once.

# The review rules

The rules at the end of this message are guidance to apply while you read the diff, **not a checklist to work \
through**. Do not report a rule as violated unless the three conditions above hold for it as well, and do not \
remark that a rule was satisfied. A change that matches no rule may still have problems worth reporting, and a \
change a rule covers may have none.

Each rule carries an identifier and the paths it applies to. When a finding comes from one of these rules, put \
that rule's identifier in the `ruleId` argument, spelled exactly as it appears. When a finding is your own \
observation rather than a rule's, leave `ruleId` out: an identifier that names no rule listed here is rejected.
"""

MATERIAL_STATEMENT = "No checks were run. No related context was gathered."

SYSTEM_PROMPT_NAME = "pr-agent-system-prompt"
"""The Langfuse-managed system prompt. A chat prompt whose system message is the instructions."""

_PROMPT_FETCH_TIMEOUT_SECONDS = 5


@dataclass(frozen=True)
class Instructions:
    """The system prompt a review uses, and where it came from."""

    text: str
    source: str
    """``langfuse:<name>@v<version>``, or ``built-in``."""
    problem: str | None = None
    """Why the built-in prompt was used although Langfuse is configured; ``None`` otherwise."""


def load_instructions(env: Mapping[str, str], *, name: str = SYSTEM_PROMPT_NAME) -> Instructions:
    """The Langfuse prompt ``name`` when Langfuse is configured in ``env``, else ``INSTRUCTIONS``. Never raises."""
    public_key, secret_key = env.get("LANGFUSE_PUBLIC_KEY"), env.get("LANGFUSE_SECRET_KEY")
    if not public_key or not secret_key:
        return Instructions(INSTRUCTIONS, "built-in")
    try:
        from langfuse import Langfuse  # imported only when configured: a review without Langfuse never loads it

        client = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            base_url=env.get("LANGFUSE_BASE_URL") or env.get("LANGFUSE_HOST"),
            tracing_enabled=False,  # this client only reads prompts; tracing is attached separately
        )
        prompt = client.get_prompt(
            name, type="chat", max_retries=1, fetch_timeout_seconds=_PROMPT_FETCH_TIMEOUT_SECONDS
        )
        text = _system_text(prompt.prompt)
    except Exception as error:  # any failure falls back: the prompt store is optional
        return Instructions(INSTRUCTIONS, "built-in", problem=f"{type(error).__name__}: {error}")
    return Instructions(text, f"langfuse:{name}@v{prompt.version}")


def _system_text(prompt: object) -> str:
    if isinstance(prompt, str):
        text = prompt
    else:
        assert isinstance(prompt, list)
        text = "\n\n".join(m["content"] for m in prompt if m.get("role") == "system" and m.get("content"))
    if not text.strip():
        raise ValueError("the prompt has no system message")
    # The stored text was copied from this module's source, so its ``\``-newline line continuations came with it;
    # join them the way Python would have, so the model sees the same text as INSTRUCTIONS.
    return text.replace("\\\n", "")


def system_message(instructions: str, rules_block: str = "") -> str:
    """The prompt's **static prefix**: the instructions, then the whole rule library (FR-006, FR-007, research R-2).

    Both halves are run-independent, which is what makes this a constant rather than a figure that moves with the
    change set — and the precondition for any prompt caching, which stays an unverified benefit rather than a
    claimed one. The instructions may come from the managed prompt store or from the built-in fallback; the rules
    block is **always ours**, so a fetch timeout can degrade the wording but can never drop the library.

    An empty block reproduces the behaviour before the library existed, byte for byte.
    """
    return instructions if not rules_block else f"{instructions}\n{rules_block}"


def fixed_section_tokens(instructions: str, rules_block: str = "") -> int:
    """The static prefix's estimated size — the fixed section of ``Docs/design/05-cross-cutting.md`` §1.1.

    This lives beside ``system_message`` rather than in ``budget.py`` because ``budget.py`` is imported *by* this
    module: putting it there would need either an import cycle or a second copy of the join, and the join is the
    thing that must not be duplicated. What ``budget.py`` owns is the limit; what this owns is the shape.

    Per-section allocation and eviction are **not** built: FR-2.5a's budgeting is feature 004's (research R-8).
    """
    return estimate_tokens(system_message(instructions, rules_block))


def prompt_text(system: str, material_statement: str, diff_section: str) -> str:
    """The full text sent to the model: ``system`` (see ``system_message``), then the user message.

    The budget is estimated over this, so the rules block cannot beat the budget by being uncounted (FR-009).
    """
    return f"{system}\n\n{user_message(material_statement, diff_section)}"


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


def assemble(
    change_set: ChangeSet,
    line_counts: Mapping[str, int],
    budget: BudgetSettings,
    instructions: str | None = None,
    rules_block: str = "",
    rule_ids: frozenset[str] = frozenset(),
) -> ReviewContext | BudgetExhausted:
    """``instructions`` overrides the system prompt; by default it is loaded as ``load_instructions`` describes.

    ``rules_block`` is CF-8's library, **already rendered** by the ``load_patterns`` node, and ``rule_ids`` are the
    identifiers that render showed the model. They arrive as a plain string and a plain set of strings for the same
    reason CF-1 receives plain glob tuples: the capability owns its data, and nothing downstream needs to know the
    rule types exist (research R-3, R-7). Both empty reproduces the behaviour before the library existed.

    **Every** loaded rule is in the block, every review, with no per-run selection of a subset (FR-006) — the
    library does not vary, so it belongs in the static prefix whole.

    The whole prompt, or ``BudgetExhausted`` when its estimate exceeds ``budget.maxTokens`` — never a part of it
    (FR-2.5b, FR-11.2). A static prefix raises every prompt's floor, so a change set that fitted before may now be
    refused; that is reported with the fixed section's share named, never silent (research R-8).
    """
    if instructions is None:
        instructions = load_instructions(os.environ).text
    diff_section = _diff_section(change_set)
    fixed = fixed_section_tokens(instructions, rules_block)
    system = system_message(instructions, rules_block)
    estimated = estimate_tokens(prompt_text(system, MATERIAL_STATEMENT, diff_section))
    if estimated > budget.max_tokens:
        return BudgetExhausted(estimated_tokens=estimated, limit=budget.max_tokens, fixed_section_tokens=fixed)
    material = RunMaterial(
        reviewed_files={
            f.path: ReviewedFile(line_count=line_counts[f.path], hunk_count=len(f.hunks))
            for f in change_set.reviewable_files
        },
        rule_ids=rule_ids,
    )
    return ReviewContext(
        instructions=instructions,
        rules_block=rules_block,
        material_statement=MATERIAL_STATEMENT,
        diff_section=diff_section,
        estimated_tokens=estimated,
        material=material,
    )
