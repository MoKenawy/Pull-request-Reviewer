# ADR-0010 — Agents live in their own package; `core/` is framework-free

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-09-20 |
| **Deciders** | Project maintainers |
| **Amends** | [ADR-0009 — the pipeline is a declared graph](./0009-pipeline-as-declared-graph.md) |
| **Supersedes detail** | FR-5.8's and AC-10's package *names*; the repository layout in `technical_stack.md` §4 |

> **What this record does not change.** Which modules may touch the agent framework is unchanged in substance: exactly two of them did before, exactly two do now. ADR-0001's "our code owns orchestration" and ADR-0009's declared graph both stand. What moves is **where those modules live and what they are called**.

---

## The question

[ADR-0009](./0009-pipeline-as-declared-graph.md) allowed a second module to import LangGraph. Both modules sat under `core/`: `core/pipeline/run.py` and `core/agent/graph.py`. So **what does `core/` mean?**

It had come to mean two different things at once — framework-free capability code (CF-1…CF-9), *and* the framework-bearing orchestration that composes it. A reader could not tell which a given `core/` module was without opening it.

## Vocabulary

| Term | Meaning here |
|---|---|
| **Core function** | A plain Python function or type. No LangGraph, no LangChain, no provider client. Callable and testable on its own. |
| **Agent** | A module whose job is to *declare a graph* over core functions, or to construct the client that talks to a model. |
| **Main agent** | The graph covering the whole review: the fixed pipeline of SRS §2.1. |
| **Subagent** | A graph invoked by the main agent for one step. Today there is exactly one: the review reporting agent. |

---

## Context

### The naming had stopped carrying information

`core/agent/graph.py` was named when it was the only graph in the repository. After ADR-0009 there were two, and the name no longer said which. Worse, the *other* graph lived in a file called `run.py`, which gave no hint that it contained a `StateGraph` at all. The two builders of structurally identical objects were called `build_graph()` and `build_pipeline()` — nothing connected them.

### The import contract had to be written as a list

Because framework-bearing and framework-free modules were siblings, the "no framework here" rule could not be stated over a package. It had to enumerate:

```
source_modules = [cli, core.changeset, core.assembly, core.findings, core.output, core.config]
```

Every new core package is a line someone must remember to add. A rule you can forget to extend is a rule that decays.

### What is actually being separated

The distinction is **kind, not layer**. `core/pipeline/preflight.py` and `core/pipeline/timing.py` are ordinary functions that happen to be used by the orchestrator; `core/agent/accounting.py` is ordinary counting logic that happens to be used by the review step. None of the three import a framework, so none of them is an agent. Only three modules were ever genuinely framework-bearing.

---

## Options considered

### Option A — Leave it; rename the functions only

| | |
|---|---|
| **For** | Nothing moves. No path references to update across four ADRs, the stack document, the seams contract and the task list. |
| **Against** | `core/` keeps meaning two things, and the framework rule keeps being an enumeration. Fixes the symptom (names) and not the cause (two kinds of module in one namespace). |

### Option B — A package per agent, each self-contained

`agents/pipeline_agent/` and `agents/review_reporting_agent/`, each holding its own helpers.

| | |
|---|---|
| **For** | Each agent is one directory; fewer cross-package hops when reading. |
| **Against** | Drags `preflight.py`, `timing.py` and `accounting.py` — all framework-free — inside `agents/`, which is exactly the conflation this record exists to remove. |

### Option C — Flat `agents/`; every pure module stays in `core/` ✅

| | |
|---|---|
| **For** | The rule becomes one line over one package: **nothing under `core/` imports a framework.** New core packages are covered automatically. Each module's kind is legible from its path. The main-agent / subagent relationship is visible in the file names. |
| **Against** | Three files move, and their paths are cited in four ADRs, the stack document, the seams contract, the task list, `CLAUDE.md` and the notebook. One more top-level package. |

---

## Decision

**`agents/` holds every module that declares a graph or constructs a provider client. `core/` holds pure functions and nothing else.**

```
agentic_review/
  agents/
    pipeline_agent.py          the main agent — the whole review, as a graph
    review_reporting_agent.py  the subagent — CF-6, the one step that calls a model
    review_port.py             the provider client behind ReviewPort
  core/
    pipeline/   preflight.py · timing.py          ← plain functions, no framework
    review/     accounting.py                     ← plain functions, no framework
    changeset/ · assembly/ · findings/ · output/ · config/
  cli/
```

### The rules

**`core/` is framework-free, as one contract over one package.** Import contract 3 is now `agentic_review.core` in a single line, not an enumeration that decays.

**The provider client stays out of the main agent.** Contract 3b keeps `pipeline_agent` away from `langchain_*` and `openai`: it declares the order, it does not talk to a model.

**Agents compose core functions; core functions never know an agent exists.** The layering contract enforces the direction.

### Why the subagent is *not* a LangGraph subgraph

LangGraph supports adding a compiled graph directly as a node. **We deliberately do not**, and this is worth recording because it looks like an obvious improvement:

The review graph binds a chat model built from the resolved credential, base URL, model name, temperature, timeout and retry wait. Those come from `preflight`, which is **node 1 of the main graph**. At the moment the main graph is constructed, none of them exists — so the compiled subgraph cannot exist either. Passing it to `add_node()` would require either hoisting preflight out of the graph (reversing ADR-0009) or carrying the bound model on the pipeline's state and merging the two state schemas, which would put CF-6's per-turn accumulators (`messages`, `calls_by_turn`, `named_files`) on `PipelineRun` and dissolve the `ReviewPort` seam that FR-0.3 and `internal-seams.md` §4 depend on.

So the `review` node invokes the subagent through `ReviewPort` as an ordinary call. **One visible consequence:** `compiled.get_graph(xray=True)` does *not* reveal the subagent's nodes, because LangGraph cannot see inside a plain function. Rendering the two graphs nested is a documentation concern, not a runtime one.

---

## Consequences

### Good

- **The framework rule is now structural.** "Nothing under `core/` imports a framework" is checkable over a package and cannot be out-grown by adding a core package.
- **A module's kind is legible from its path.** `agents/` declares graphs; `core/` computes.
- **The main-agent / subagent relationship is in the file names**, not only in prose.
- **Every core function stayed put and stayed testable** — `preflight`, `timing` and `accounting` did not become agent code just because agents call them.

### Bad

- **Three files moved and their paths are cited widely** — ADR-0001, ADR-0009, `technical_stack.md` §4, `contracts/internal-seams.md`, `tasks.md`, `CLAUDE.md`, the notebook. Every one is a chance for a stale reference.
- **One more top-level package** for a reader to place.
- **`core/review/` holds a single module.** It is the right home for CF-6's framework-free half, but a one-file package looks arbitrary until CF-6 grows a second one.

### Neutral

- Test layout follows: `tests/unit/agent/` → `tests/unit/agents/`.
- The Pattern-1 question above will be asked again by someone. The answer is recorded so it is settled by reading, not by trying.

---

## How we would know this decision was violated

- Any module under `core/` imports `langgraph`, `langchain_*` or `openai`.
- `agents/pipeline_agent.py` imports a provider client.
- A core function takes a graph state type as a parameter, or cannot be called without one.
- An agent grows logic that is not graph declaration or client construction — that logic belongs in a core function.

## What the requirements need to change

| Document | Change |
|---|---|
| **FR-5.8**, **AC-10** | Same rule, new names: the framework is confined to `agents/`; no `core/` package may import it |
| **`technical_stack.md` §4** | Repository layout and import contracts 1, 2, 3, 3b, 6 |
| **`contracts/internal-seams.md`** §1, §4 | `core/pipeline/` → `agents/pipeline_agent.py`; `core/agent/` → `agents/review_port.py` |
| **`CLAUDE.md`** | Architecture section and the FR-5.8 bullet |
