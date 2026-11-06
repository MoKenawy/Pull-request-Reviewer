# Contract — The rules file

**Feature**: [003 rule library](../spec.md) · **Date**: 2026-11-06
**Serves**: FR-001…FR-004, FR-024…FR-028 · SRS FR-6.1, FR-6.3a, FR-1.2b–d

The format of a rule document, where rule documents come from, and exactly how a bad one fails. This is the contract a project author writes against, so its error messages are part of it.

---

## 1 · Sources, and how they combine

| Order | Source | Required |
|---|---|---|
| 1 | The shipped library — package data inside the wheel | Always present |
| 2 | A file named by the configuration key below | Optional |

**Configured rules are added to the shipped ones.** They never replace them, following the merge semantics configured exclusions already use. There is no precedence order to learn, because there is no override: an identifier belongs to exactly one rule, and a collision is an error rather than a winner.

```yaml
# .agentic-review.yml
patterns:
  rules: ./review-rules.yml     # optional; absent means the shipped library alone
```

| Key | Type | Default | Notes |
|---|---|---|---|
| `patterns.rules` | path | *(unset)* | Relative to the repository root. Unset is not an error and is not reported as missing anything |

Unknown keys under `patterns` are errors, as everywhere else in the configuration.

---

## 2 · The document

A rules file is a YAML mapping with one key, `rules`, holding a list of rule mappings.

```yaml
rules:
  - id: no-unawaited-promise
    title: A promise created inside try is not awaited, so its rejection escapes the catch
    category: error-handling
    defaultSeverity: blocking
    appliesWhen:
      include: ["**/*.ts", "**/*.tsx"]
      exclude: ["**/*.test.ts"]
    wrong: |
      try {
        void save(record);          // rejection escapes this try
      } catch (error) {
        report(error);
      }
    correct: |
      try {
        await save(record);
      } catch (error) {
        report(error);
      }
```

| Field | Required | Shape |
|---|---|---|
| `id` | yes | Lowercase alphanumerics joined by single hyphens. Unique across the whole loaded library |
| `title` | yes | One non-empty line |
| `category` | yes | One of the finding model's categories |
| `defaultSeverity` | yes | One of the finding model's severities |
| `wrong` | yes | Non-empty. The violating example |
| `correct` | yes | Non-empty. The compliant counterpart |
| `appliesWhen` | no | `include` and `exclude` lists of path patterns. Omitted means every file |

Field names are `camelCase` in the file, as in every other serialised surface of this system. **Unknown keys are errors**, so a misspelt `appliesWen` fails loudly rather than silently leaving the rule universal.

### Path patterns

The same dialect as the configuration's `exclude` list, and **case-sensitive**:

| Pattern | Matches |
|---|---|
| `**/*.ts` | any `.ts` file at any depth |
| `src/**` | everything under `src/` |
| `*.config.ts` | a `.config.ts` file **at any depth** — a pattern with no `/` is not anchored |
| `src/api/handler.ts` | exactly that path |

Patterns are repo-relative, POSIX-separated, and match the whole path. A leading `/` and a Windows separator are both rejected. There is no such thing as an invalid pattern beyond that — any accepted string becomes a matcher, and one that matches nothing is a rule that never applies, not an error.

---

## 3 · Failure

Every failure below stops the run at **preflight**, with **exit 3**, **no provider call** and **no check execution** — the same shape a malformed configuration already has.

| Cause | Message |
|---|---|
| The file does not exist | `patterns.rules: './review-rules.yml' does not exist` |
| Not valid YAML | `review-rules.yml: not valid YAML: <parser message>` |
| Top level is not a mapping with `rules` | `review-rules.yml: expected a mapping with a 'rules' list` |
| A rule is not a mapping | `review-rules.yml: rules[2]: expected a mapping` |
| A required field is missing | `review-rules.yml: rules[2].title: required` |
| An unknown key | `review-rules.yml: rules[2].appliesWen: unknown field` |
| A bad identifier | `review-rules.yml: rules[2].id: 'No Unawaited': expected a slug like 'no-unawaited-promise'` |
| A category outside the vocabulary | `review-rules.yml: rules[2].category: 'perf' is not a category` |
| An empty include list | `review-rules.yml: rules[2].appliesWhen.include: must name at least one pattern` |
| An absolute or Windows-separated pattern | `review-rules.yml: rules[2].appliesWhen.include[0]: '/src/**': expected a repo-relative POSIX pattern` |
| Two rules share an identifier | `review-rules.yml: rules[2].id: 'no-unawaited-promise' is already defined by a built-in rule` |

The identifier of the offending rule is named where one exists; the index is given where the identifier itself is the problem. **A malformed shipped library is a programming error**, not a user error: it fails the same way, and a test asserts the shipped library loads so it cannot ship broken.

---

## 4 · What the model is shown

Every loaded rule, every review, in identifier order, in the static part of the prompt. The rendering is not a wire format and may change without a version bump, but three properties are contractual:

1. Each rule's `id` appears verbatim, because the model is asked to cite it.
2. Each rule's declared scope appears with it, so the model can tell which files it covers.
3. The block is **byte-identical** for the same library across different change sets — the property SC-004 checks and the precondition for any prompt caching.
