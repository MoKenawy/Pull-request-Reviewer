# Documentation

## Start here

| Document | What it is |
|---|---|
| **[`agentic-code-review-srs-v1.md`](./agentic-code-review-srs-v1.md)** | **The specification for the version being built.** Normative — if you are implementing or reviewing an implementation, this is the document. Currently **v1.1**; §10 records what the design review changed and why. |
| [`technical_stack.md`](./technical_stack.md) | **What the system is built with** — libraries, protocols, repository layout, and the checks that enforce the seams. Subordinate to the specification: it never relaxes a requirement. |
| [`adr/`](./adr/) | Architecture decision records. Why the system is shaped the way it is. Start with [ADR-0006](./adr/0006-local-cli-core-action-as-adapter.md), then [ADR-0007](./adr/0007-python-harness-typescript-target.md), then the [index](./adr/README.md). |
| [`operation_guidelines.md`](./operation_guidelines.md) | **How to install, configure, run and troubleshoot the tool, and how to work on it.** Describes what the code does today, not the specification. Non-normative. |
| [`design/`](./design/) | **How the system is put together** — components, types, behaviour, contracts. Subordinate to both documents above: it introduces no requirement and no library. Start with [the design plan](./design/README.md). |

Places where the analysis hand-off contradicts itself, or stops short of a decision design cannot make alone, are collected in [`DESIGN_BLOCKERS.md`](../DESIGN_BLOCKERS.md) at the repository root, with a response log for the analysis team.

## Background and working documents

Everything in [`Draft/`](./Draft/) is **non-normative**. It records analysis, rationale, and requirements for versions that do not exist yet. Where any of it conflicts with the baselined specification, the specification wins.

| Document | What it is |
|---|---|
| [`Draft/agentic-code-review-srs.md`](./Draft/agentic-code-review-srs.md) | The full requirement catalogue across v1–v3. The identifier registry the ADRs cite. |
| [`Draft/agentic-code-review-srs-ar.md`](./Draft/agentic-code-review-srs-ar.md) | Arabic translation of the catalogue. |
| [`Draft/mvp-scope.md`](./Draft/mvp-scope.md) | The analysis that selected v1's scope. Explains every inclusion and every cut. |
| [`Draft/agent-harness-design.md`](./Draft/agent-harness-design.md) | Plain-language guide to the agent harness — tools, memory, environments, model selection. |
| [`Draft/agentic-architecture-review.md`](./Draft/agentic-architecture-review.md) | Assessment of an external agentic-architecture review of [ADR-0001](./adr/0001-fixed-pipeline-with-bounded-agency.md): what to adopt, when, and what to reject. |
| [`Draft/agent-loop-v1-v2.md`](./Draft/agent-loop-v1-v2.md) | The review step visualised before and after the tool loop is enabled, with a worked trace of the same change reviewed both ways. |
| [`Draft/system-analysis/`](./Draft/system-analysis/system_analysis.md) | System analysis of v1: actors and use cases, requirement and domain models, workflows, a degradation and traceability matrix, and open questions raised against the specification. |
| [`Draft/Agentic_Code_Review_Problem_Definition_v1.md`](./Draft/Agentic_Code_Review_Problem_Definition_v1.md) | Problem definition, personas, and the commit-first decision. |
| [`Draft/enterpenuership/000-problem-and-audience.md`](./Draft/enterpenuership/000-problem-and-audience.md) | **The one place the audience, the problem and the tagline are worded** (2026-10-09). The problem definition above is the reasoning behind it. |
| [`Draft/competitive-landscape.md`](./Draft/competitive-landscape.md) | Where this project sits against existing tools. |
| [`Draft/enterpenuership/004-market-study.md`](./Draft/enterpenuership/004-market-study.md) | Market study: sizing, the category leader, competitors, demand signals and academic evidence, each figure with a confidence label. |
| [`Draft/enterpenuership/0050-financial-planning/0052-unit-economics-and-financials.md`](./Draft/enterpenuership/0050-financial-planning/0052-unit-economics-and-financials.md) | Unit economics of the hosted review service: measured cost per review, price and margin at three markups, break-even, and the three-year formula. |
| [`Draft/business-model-canvas.md`](./Draft/business-model-canvas.md) | Business Model Canvas. Marks every block where no information exists, and names the three riskiest. |
| [`Draft/tool-reference.md`](./Draft/tool-reference.md) | Neutral descriptions of seven comparable tools. |
| [`Draft/feature-inventory.md`](./Draft/feature-inventory.md) | Feature tables with complexity estimates, planned and candidate. |
| [`Draft/chat_result_*.md`](./Draft/) | Research and analysis session records. |

## How the documents relate

```mermaid
flowchart TD
    P["Draft/Agentic_Code_Review_Problem_Definition_v1.md<br/>the problem"] --> C["Draft/agentic-code-review-srs.md<br/>full catalogue, v1–v3"]
    L["Draft/competitive-landscape.md<br/>Draft/tool-reference.md<br/>the market"] --> C
    C --> H["Draft/agent-harness-design.md<br/>how the agent layer works"]
    H --> A["adr/<br/>decisions"]
    C --> M["Draft/mvp-scope.md<br/>what ships first"]
    A --> M
    M ==>|"adopted and made normative"| S["agentic-code-review-srs-v1.md<br/>THE BUILD TARGET"]
    A -.->|"cited by"| S
    S ==>|"what must be true"| T["technical_stack.md<br/>what it is built with"]
    A -.->|"ADR-0007 decides<br/>the stack"| T
    S ==>|"what must be true"| D["design/<br/>how it is put together"]
    T -.->|"constrains"| D
    D -.->|"what design cannot<br/>decide alone"| B["DESIGN_BLOCKERS.md"]
    B -.->|"answered by analysis"| S
    D --> F["specs/001-walking-skeleton/<br/>feature spec, plan, tasks"]
    F ==>|"implemented by"| Code["src/agentic_review/"]
    S -.->|"describes what<br/>Code does today"| G["operation_guidelines.md"]

    style S fill:#e8f7e8
    style T fill:#eef3fa
    style D fill:#eef3fa
    style B fill:#ffe6e6
    style Code fill:#eef3fa
```

**The three documents an implementer needs** are the specification (what must be true), the stack (what to build it with), and ADR-0007 (why that stack). [`design/`](./design/) sits between those and the code: it decides how the parts fit together, and it may not change what any of the three says. Everything else is background.

## Conventions

- **Requirement identifiers are stable.** A requirement keeps its identifier across versions; a version tag says when it applies. Nothing is renumbered, so ADR cross-references stay valid.
- **Must / Should.** Must = required for the version to be complete. Should = included if time allows.
- **One normative source.** Exactly one document defines what to build at any time. Everything else explains or anticipates.
- **Behaviour and technology are separate documents.** [`agentic-code-review-srs-v1.md`](./agentic-code-review-srs-v1.md) says what must be true; [`technical_stack.md`](./technical_stack.md) says what it is built with. If a library cannot satisfy a requirement, the library is wrong — changing the requirement is a specification change, not a stack change.
