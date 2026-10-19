# Contract: `.agentic-review.yml` and the Credential (001)

**Parent contract**: [`Docs/design/04-contracts.md`](../../../Docs/design/04-contracts.md) §7 and
[`05-cross-cutting.md`](../../../Docs/design/05-cross-cutting.md) §4. Stability: 📦 versioned by `schemaVersion`.

The other side of this contract is **the user's repository**: a file written against 001 must stay valid in 006.

---

## The file

Read from the repository root, or from `--config PATH`. **For a `--pr` review it is read only from `--config PATH`**
— never from the pull request, whose author could otherwise choose the provider URL the credential is sent to, and
never from the current directory, which is not the repository under review (SRS FR-10.3d). Every field is optional. The types, defaults and
per-field effect in 001 are in [data-model.md §7](../data-model.md#7--cf-9--configuration).

```yaml
schemaVersion: 1

scope: working-tree                  # working-tree | staged | range (commit and pull-request are flags only)
exclude:                             # ADDED to the default list below, never replacing it
  - "**/*.generated.ts"

context:                             # accepted and validated; no effect until feature 004
  depth: 1
  node: node

checks:                              # accepted and validated; no effect until feature 002
  tests:
    command: ["npm", "test"]
    timeoutSeconds: 120              # PLACEHOLDER, not a finding - SRS section 8, TBD-4
  typecheck:
    command: ["npx", "tsc", "--noEmit"]

agent:
  toolCallCeiling: 25                # PLACEHOLDER - SRS section 8, TBD-8
  investigationTools: false          # true is accepted, has no effect until feature 005, and is reported
  model: "meta/llama-3.3-70b-instruct"   # PLACEHOLDER - chosen by test S-1
  baseUrl: "https://integrate.api.nvidia.com/v1"
  temperature: 0
  requestTimeoutSeconds: 60          # PLACEHOLDER - additive field, see plan D-9

budget:
  maxTokens: 20000                   # PLACEHOLDER - SRS section 8, TBD-3
```

## Rules

| Rule | Requirement |
|---|---|
| File absent → built-in defaults | FR-1.2b |
| Field absent → that field's default; merging is **per field**, never whole-section replacement | FR-1.2c, 05 §4.1 |
| Invalid value, **unknown field**, **duplicate key**, or YAML syntax error → exit 3, naming the file and the dotted field path (or line and column for syntax) | FR-1.2d, spec Assumptions, R-8 |
| `exclude` is **added to** the defaults | FR-008, SC-009 |
| Order of precedence: defaults → file → CLI flags | 05 §4.1 |
| Settings for unbuilt capabilities: validated, no effect, **one** stderr notice listing the dotted paths that were set | FR-003 |
| **There is no credential field.** A key such as `apiKey` anywhere in this file is an unknown field, so exit 3 | FR-1.3a, FR-004 |

## Default exclusion list

The rule names appear in the report's `changeSummary.excluded[].rule`. Glob semantics: `**` matches zero or more
path segments; `*` and `?` stay within one segment; a pattern with no `/` matches at any depth.

| Rule | Patterns |
|---|---|
| `default:dependencies` | `node_modules/**` · `**/node_modules/**` · `vendor/**` · `bower_components/**` |
| `default:build-output` | `dist/**` · `build/**` · `out/**` · `coverage/**` · `.next/**` · `.nuxt/**` · `.turbo/**` |
| `default:generated` | `**/*.generated.*` · `**/*.gen.ts` · `**/__generated__/**` |
| `default:minified` | `**/*.min.js` · `**/*.min.mjs` · `**/*.map` |
| `default:lockfile` | `package-lock.json` · `yarn.lock` · `pnpm-lock.yaml` · `bun.lockb` |

A configured pattern `p` is recorded as `config:p`. If a path matches both a default and a configured pattern, the
**default** rule is recorded, because defaults are applied first.

## The credential

| Order | Source | Location |
|---|---|---|
| 1 | Environment | `AGENTIC_REVIEW_API_KEY` |
| 2 | User-level file | Windows `%APPDATA%\agentic-review\credentials.yml`; otherwise `$XDG_CONFIG_HOME/agentic-review/credentials.yml`, falling back to `~/.config/agentic-review/credentials.yml`. Contents: `apiKey: <key>` |

- If the user-level file resolves to a path **inside the repository root**, it is refused (exit 3), because FR-1.3a
  forbids reading it from a file in the repository.
- Neither source available → exit 3, naming both locations.
- The value **never** appears in stdout, stderr, the report, a log record, or an exception message shown to the
  user (SC-007).
