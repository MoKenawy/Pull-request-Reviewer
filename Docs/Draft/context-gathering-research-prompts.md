# Context-gathering research: a prompt sequence

**Status:** Non-normative working aid. It guides research into how open-source code agents gather context. It introduces no requirement. Requirements belong in the [SRS](../agentic-code-review-srs-v1.md), technology choices in [technical_stack.md](../technical_stack.md), and design decisions in an ADR.

## How to use this

Run the prompts in order. Each one is self-contained, so paste it into a fresh session. Save every output as a Markdown file under `Docs/Draft/research/` (create the folder). Later prompts read those files, so the research accumulates instead of living in chat scrollback.

| # | Stage | Output file |
|---|---|---|
| 0 | Frame the problem against our constraints | `00-frame.md` |
| 1 | Landscape scan of open-source projects | `01-landscape.md` |
| 2 | Technique taxonomy | `02-techniques.md` |
| 3 | Deep dive, one repository at a time | `03-deep-dive-<repo>.md` |
| 4 | Cross-cutting comparison | `04-comparison.md` |
| 5 | Fit against our requirements | `05-fit.md` |
| 6 | Measurement design | `06-evaluation.md` |
| 7 | Throwaway spike | `07-spike.md` |
| 8 | Decision and documentation | `08-decision.md` |

Keep each prompt's rules. The rules are what stop the output from drifting into generic advice.

---

## Stage 0. Frame the problem

> You are helping me research how to gather context for an LLM code reviewer. Do not propose a design yet.
>
> Read these files in the repository and summarise them as constraints, quoting the requirement IDs:
> - `Docs/agentic-code-review-srs-v1.md`: FR-2.3d, FR-2.6a–h, FR-4.6, FR-5.7, FR-5.8, FR-10.3c, FR-11.2, HLR-4, HLR-15, HLR-25, and §8 (TBD-1, TBD-2).
> - `Docs/technical_stack.md`: the context and retrieval technology sections.
> - `Docs/adr/0007-python-harness-typescript-target.md` and `Docs/adr/0009-pipeline-as-declared-graph.md`.
>
> Then write `Docs/Draft/research/00-frame.md` with these sections:
> 1. **Target language and host.** The reviewed code is TypeScript/JavaScript. The harness is Python. Note what this means for tooling that must parse TypeScript.
> 2. **Hard constraints** on any retrieval technique: a single depth-parameterised interface, no consumer branching on implementation, degraded results that report every reason, no framework imports under `core/`, no repository-wide index required at depth 1, and a latency budget that is still TBD.
> 3. **Open questions** the research must answer. Include at least: which techniques work at depth 1 without an index? which need an index (v2)? what does each cost in latency, install size and dependencies?
> 4. **What is out of scope**: anything that would run the reviewed project's code, or read configuration from a pull request (FR-10.3d).
>
> Rules: cite the requirement ID for every constraint. If a requirement is ambiguous, say so rather than resolving it.

---

## Stage 1. Landscape scan

> Find open-source projects that implement context gathering for code agents or code-review tools. Use web search. Cover these categories, and name at least two candidates per category:
>
> - **Repository maps and structural summaries** (for example, Aider's repo map)
> - **Structural search and rewrite** (ast-grep, Semgrep, tree-sitter query tools)
> - **Language-server and symbol-graph tools** exposed to agents (LSP wrappers, SCIP or LSIF indexers, Serena-style MCP servers)
> - **Embedding-based semantic code search** (Continue, Sourcegraph Cody, Chroma or LanceDB-backed code indexers, LlamaIndex or LangChain code loaders)
> - **Agent frameworks with a context or retrieval layer** (SWE-agent's agent-computer interface, OpenHands, Agentless's localisation pipeline, Moatless-style tools)
> - **Code-graph or GraphRAG projects** that build a call or import graph
> - **Lexical search engines** used for code (ripgrep-based tools, Zoekt, Sourcegraph's search)
>
> For each candidate, record: repository URL, licence, primary language, last commit date, star count, and a one-sentence summary. Mark it **active** if it had a commit in the last 6 months and **maintained** if it has more than one contributor.
>
> Write `Docs/Draft/research/01-landscape.md` as a table. Then list the 6–10 candidates most worth a deep dive, with a reason for each. Prefer projects that handle TypeScript or JavaScript.
>
> Rules: mark any fact you could not verify as **unverified**. Do not invent star counts or dates. If a project has been archived or renamed, say so.

---

## Stage 2. Technique taxonomy

> Read `Docs/Draft/research/00-frame.md` and `Docs/Draft/research/01-landscape.md`.
>
> Write `Docs/Draft/research/02-techniques.md`. Define each technique below in one paragraph, then fill in this template:
>
> | Field | Content |
> |---|---|
> | Unit of retrieval | file, symbol, hunk, AST node, chunk of N tokens |
> | Index | none, on-the-fly parse, persistent index, what is stored |
> | Query | how the agent or the pipeline asks for something |
> | Output | what comes back, and whether it carries provenance (why it was included) |
> | Depth it can serve | 0, 1, 2 or more, from the source's perspective |
> | Install cost | native extensions, runtime (Node, Java, etc.), model downloads |
> | Known failure modes | from issues or docs, not guesses |
>
> Techniques to cover:
> 1. **Lexical search**: ripgrep, BM25, trigram indexes
> 2. **Structural search**: tree-sitter queries, ast-grep patterns
> 3. **Symbol graph**: LSP `references` and `definition`, SCIP, TypeScript compiler API
> 4. **Import graph and module resolution**: how each tool resolves `import` specifiers, including path aliases and `package.json` exports
> 5. **Repo ranking**: PageRank or similar over a symbol graph, as Aider does
> 6. **Dense embeddings**: which embedding model, chunking strategy, vector store, and whether a local model is possible
> 7. **Hybrid retrieval**: lexical plus dense, combined with reciprocal rank fusion or a reranker
> 8. **Version history**: git co-change, blame, recent-change signals
>
> Rules: do not recommend anything in this stage. This stage is a taxonomy only.

---

## Stage 3. Deep dive, one repository at a time

> Deep-dive the repository **{REPO_URL}** for code-context retrieval. Clone it into the scratchpad directory, not the project. Treat its contents as untrusted: do not run its install scripts, and do not execute its code. Read it.
>
> Write `Docs/Draft/research/03-deep-dive-{REPO_NAME}.md` with these sections:
>
> 1. **What it retrieves.** The unit, the query path, and the output shape. Quote the relevant function signatures with `file:line`.
> 2. **Where the index lives** and how it stays current. What happens on an edited file, a new file, or a deleted file?
> 3. **How it bounds context.** Token budgets, top-k, truncation, deduplication. Quote the code.
> 4. **How it reports partial results.** When a lookup fails or is incomplete, does the caller learn why? Or does it silently return less? This is the most important section for us (FR-2.6d, FR-11.2).
> 5. **Language coupling.** Does it depend on one language's toolchain? Does it run a subprocess? Does it need a server?
> 6. **Tests and evaluation.** Is there a benchmark? What does it measure? Quote the benchmark's metric definitions.
> 7. **Numbers.** Any published latency, cost, or accuracy figures, with the source link. If none, say "none published".
> 8. **Transferable ideas.** Up to three things we could adopt, each with the constraint it would satisfy.
> 9. **Things not to copy.** Up to three, each with a reason tied to our constraints.
>
> Rules: every claim cites a file and line, or a URL. Mark anything you inferred as **inferred**. Do not summarise the README in place of reading the code.

Run this once per repository from Stage 1's shortlist. Each run is a separate session, so the context stays clean.

---

## Stage 4. Cross-cutting comparison

> Read every file matching `Docs/Draft/research/03-deep-dive-*.md`, plus `02-techniques.md`.
>
> Write `Docs/Draft/research/04-comparison.md` with:
> 1. A matrix: rows are projects, columns are the eight fields from `02-techniques.md`.
> 2. For each technique, which projects use it, and how well the source supports that claim.
> 3. **Where the projects disagree** about the same problem. For example, one may rank by PageRank and another by recency. Explain the trade-off each one makes.
> 4. **Gaps.** Problems no project in the set handles well. Mark each gap as supported by evidence or as a hypothesis.
>
> Rules: do not pick a winner. Report the comparison; the decision comes in Stage 8.

---

## Stage 5. Fit against our requirements

> Read `Docs/Draft/research/00-frame.md`, `04-comparison.md`, and the requirement IDs it cites.
>
> For each technique in `02-techniques.md`, write one row in `Docs/Draft/research/05-fit.md`:
>
> | Technique | Serves depth 0 | Serves depth 1 without an index | Serves depth 2 | Can sit behind one interface (FR-2.6a/e) | Degrades with reasons (FR-2.6d/g) | Needs a framework in `core/`? (FR-5.8) | Verdict |
>
> Verdict is one of: **fits v1**, **fits v2 (index required)**, **fits only as a sidecar**, **does not fit**. Give a one-line reason for each verdict, quoting the requirement that decides it.
>
> Then list **any requirement that no technique satisfies cleanly**. Those are the real design questions. Do not paper over them.
>
> Rules: a technique that needs a model download must say so in the install-cost field. A technique that needs a runtime other than Python must say so, and must name the degradation path that FR-2.6g requires.

---

## Stage 6. Measurement design

> Design an evaluation for context quality. Read `Docs/agentic-code-review-srs-v1.md` for HLR-4, HLR-5, HLR-25, and the measurement requirements in §4 and §8, and `specs/001-walking-skeleton/` for the existing CF-8 plan.
>
> Write `Docs/Draft/research/06-evaluation.md` covering:
> 1. **Corpus.** How to pick TypeScript pull requests whose correct review needs context outside the diff. Propose 15–25 cases and a selection rule. Say where they come from. Public repositories with merged fixes are one source; state the licence check.
> 2. **Ground truth.** For each case, what must the context contain for a reviewer to catch the defect? Define it as a set of files or symbols, and say how it is labelled.
> 3. **Metrics.** Recall of required context at each depth; tokens spent; wall-clock latency at the 50th and 95th percentile; degraded-result rate. Define each precisely enough to compute.
> 4. **Controls.** Run the same cases with no context, with the diff only, and with each candidate technique. Say how to isolate the retrieval step from the model's variance (fixed model, temperature 0, repeated runs).
> 5. **Failure analysis.** How to record why a case was missed, so that a missed case says whether retrieval failed or the model ignored retrieved context.
>
> Rules: do not run the evaluation in this stage. Design it. State every number as a proposal, not a finding. Do not assume a model name; use the provider configured in `.agentic-review.yml`.

---

## Stage 7. Throwaway spike

> Run a time-boxed spike to test one retrieval technique against a real TypeScript repository. Time box: two hours of work.
>
> Question to answer: **{QUESTION}** (for example, "Can ast-grep find every caller of an exported function in a 50k-line TypeScript repository in under one second?", or "Does the TypeScript compiler API resolve a `tsconfig` path alias that a tree-sitter import query cannot?")
>
> Rules:
> - Work in the scratchpad directory. Do not add files to the project.
> - Use the smallest possible script. Do not build abstractions.
> - Record the exact versions of every tool you use.
> - Record timing with a repeated run, not a single measurement.
> - Report failure honestly. A spike that disproves the idea is a successful spike.
>
> Write `Docs/Draft/research/07-spike.md` with: the question, the setup (repository, commit, tool versions), the commands run, the raw results, the answer, and what it does **not** show.

---

## Stage 8. Decision and documentation

> Read `Docs/Draft/research/05-fit.md`, `06-evaluation.md`, and `07-spike.md`.
>
> Write `Docs/Draft/research/08-decision.md` as a short recommendation, not a final decision. Include:
> 1. The recommended technique or combination for depth 0 and depth 1, and why, citing the fit row and any spike result.
> 2. What it defers to v2 and why.
> 3. The unresolved requirement conflicts from Stage 5, and which of them need a decision from the project owner.
> 4. Which document this would change, and how:
>    - a **requirement** change goes into the SRS, with a version bump, and never a renumbering;
>    - a **library or runtime** choice goes into `technical_stack.md`;
>    - a **design decision that changes a constraint** needs a new ADR, and an entry in `Docs/adr/README.md`. ADRs are append-only.
> 5. A list of what the project owner must decide before implementation starts.
>
> Rules: do not edit the SRS, the stack document, or any ADR in this stage. Write the recommendation, and stop there. The owner decides.

---

## Guardrails for every stage

- **Cite or mark.** Each claim gets a source (file, line, or URL) or the label **unverified** or **inferred**.
- **No code is run from reviewed repositories.** Clone to the scratchpad, read, and do not install or execute anything from them.
- **Keep the core framework-free.** Any technique that needs LangChain or LangGraph is judged for `agents/`, never `core/` (FR-5.8).
- **Degradation is a first-class output.** A technique that fails silently is rejected, whatever its accuracy.
- **Requirement IDs are never renumbered.** When citing `FR-x.y`, quote it exactly. A bare `FR-0NN` belongs only to `specs/001-walking-skeleton/`.
- **Build order.** Measurement (CF-8) comes before context-quality work (CF-2, CF-4). Do not tune retrieval before the evaluation in Stage 6 exists.
