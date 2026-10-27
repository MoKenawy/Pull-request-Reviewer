# Developer documentation site

A [Docusaurus](https://docusaurus.io/) site that presents the developer-facing parts of this repository's documentation.

## The pages are generated

Nothing under `docs/` or `static/img/diagrams/` is written by hand, and both are gitignored. [`scripts/sync-docs.mjs`](scripts/sync-docs.mjs) builds them from the repository's own documents, which stay the only copy:

| Page | Source |
|---|---|
| Overview | `README.md` |
| Operation guide | `Docs/operation_guidelines.md` |
| Component design | `Docs/design/Component-design/README.md`, without §1.1 (the mermaid redraw of level 3) |
| Domain model | `Docs/design/02-domain-model.md`, §1 only |
| Contract map | `Docs/design/schemas-and-contracts.md`, §1 only |
| Architecture overview | [`content/architecture/levels.md`](content/architecture/levels.md), showing `Docs/design/Component-design/level-{1,2,3}.svg` |
| `emit_finding` | `specs/001-walking-skeleton/contracts/emit-finding.md` |
| Review report JSON | `specs/001-walking-skeleton/contracts/review-report.md` |

Pages written for this site alone, such as the level-by-level architecture walkthrough, live in [`content/`](content/), which is tracked, and are copied into `docs/` as they are.

To change a page, edit its source. To add or remove a page, update [`Docs/developer-documentation-candidates.md`](../Docs/developer-documentation-candidates.md), then the `PAGES` manifest in the script and [`sidebars.ts`](sidebars.ts).

Relative links between synced sources become links between pages; every other relative link points at the file on GitHub.

## Commands

Requires Node 20 or later.

```
npm install
npm start          # sync, then serve with live reload at http://localhost:3000
npm run build      # sync, then build the static site into build/
npm run serve      # serve the last build
npm run sync       # regenerate docs/ only
```

`npm start` syncs once at startup; after editing a source document, run `npm run sync` again and the dev server reloads.

The build fails on a broken link, so a source that links to a moved file is caught here.
