# Contract: `emit_finding` and Tool Observations (001)

**Parent contract**: [`Docs/design/04-contracts.md`](../../../Docs/design/04-contracts.md) §4. Stability: 📦
versioned with the finding model. A change is visible to the provider.

The other side of this contract is **the model**, which cannot be changed together with our code.

---

## The tool

- **Name**: `emit_finding`
- **Declaration**: `emit_finding` in `agents/review_port.py`, a LangChain `@tool` bound with
  `chat_model.bind_tools([emit_finding])`. Its body is never executed: the review graph's `validate_calls` node answers
  every call, because validation needs the run's material. *(Changed 2026-09-24 from a hand-built tool dict.)*
- **Description**: as `TOOL_DESCRIPTION` in `core/findings/schema.py`. It states that one call records one specific
  problem at one location, that several problems mean several calls in the same reply, that the call is the only way a
  finding is recorded and prose is discarded unread, and that every call is validated on its own against the change
  under review, so a rejected call records nothing and does not affect the others. It ends with one example call.
  *(Reworded during implementation, 2026-09-17: the description and the per-field descriptions are what the provider
  reads, and the original one sentence left the model to guess the rest. Unmeasured — see the note at the end.)*
- **Parameters**: **generated** from `FindingDraft` (see [data-model.md §3](../data-model.md#3--cf-5--findings)),
  with `$ref`s inlined (R-11), and passed to `@tool` as a JSON-schema `args_schema` — passing `FindingDraft` itself
  would send snake_case names. Each field and each evidence arm also carries a `description` generated from the model,
  so the field rules the model must follow (line numbers in the new version, the severity rubric, the category list,
  the evidence kinds, `ruleId` left unset) reach it **only** with the tool, not in the system prompt *(since
  2026-09-24; the prompt previously repeated them)*. Types, required fields and enums equal 04 §4.1:

```jsonc
{
  "type": "object",
  "additionalProperties": false,
  "required": ["file", "startLine", "endLine", "severity", "category", "rationale", "evidence"],
  "properties": {
    "file":      {"type": "string", "minLength": 1},
    "startLine": {"type": "integer", "minimum": 1},
    "endLine":   {"type": "integer", "minimum": 1},
    "severity":  {"enum": ["blocking", "important", "nit"]},
    "category":  {"enum": ["correctness", "error-handling", "interface-contract",
                           "test-evidence", "security", "performance", "maintainability"]},
    "rationale": {"type": "string", "minLength": 1},
    "ruleId":    {"type": "string"},
    "evidence":  {"oneOf": [
      {"kind": "check",      "checkId": "tests|typecheck", "failingTest?": "string"},
      {"kind": "context",    "file": "string", "startLine": "integer", "endLine": "integer"},
      {"kind": "diff",       "file": "string", "hunkIndex?": "integer ≥ 0"},
      {"kind": "unverified", "reason": "string, minLength 1"}
    ]}
  }
}
```

*(The `oneOf` arms are shown compressed. The generated schema carries full object schemas with
`additionalProperties: false` and a `kind` discriminator.)*

**Test obligation**: the parameters sent to the provider equal `inline_refs(FindingDraft.model_json_schema(by_alias=True))`,
less the top-level `description`, which LangChain's tool conversion drops in favour of the tool description.
A hand-edited schema fails the test. Descriptions are therefore edited on the Pydantic model, never in the schema.

> **The wording of the description and of the instructions is unmeasured** (Principle VI). Feature 003's corpus is what
> decides whether one wording reviews better than another; until then no such claim is made here. What is not a matter of
> wording is the *shape* the model must produce: a call that ignores the field rules is rejected at the call boundary.

## Binding rules

| Rule | Requirement | Test |
|---|---|---|
| `emit_finding` is the **only** tool bound | FR-011 | Bound tool list has length 1 |
| **No `tool_choice`** is ever set | FR-018 / FR-5.10 | Bound kwargs contain no `tool_choice` |
| A reply may carry many calls; each is validated as it arrives, in order | ADR-0004 | Mixed valid and invalid calls in one reply |
| Prose (`AIMessage.content`) is discarded, never parsed | FR-013 | A reply whose prose contains finding-like JSON yields 0 findings |

## Observations

Every tool call, valid or not, receives exactly one `ToolMessage` whose content is this JSON:

```jsonc
{"status": "ok",     "reason": null, "content": "accepted as f-2"}
{"status": "error",  "reason": "severity: Input should be 'blocking', 'important' or 'nit'", "content": null}
{"status": "denied", "reason": "tool-call ceiling of 25 reached; this call was not processed", "content": null}
```

`reason` is required whenever `status != "ok"`. An `ok` observation's `content` may carry a note after the finding id,
when validation discarded a field (see [Discarded fields](#discarded-fields)). When several fields fail, the reasons are joined with `; `, and
each is prefixed with its dotted JSON field path.

## Rejection reasons

Shape failures reuse Pydantic's message behind the field path. Reference failures (FR-013, gap D-1) use these
fixed forms, so the model can act on them and tests can assert them:

| Condition | `reason` |
|---|---|
| Unknown tool name | `name: unknown tool '<name>'; the only tool is emit_finding` |
| Arguments not valid JSON | `arguments: not valid JSON` |
| File not reviewed | `file: '<file>' was not part of this review; reviewed files: <a>, <b>` |
| End beyond file | `endLine: <n> is past the end of '<file>' (<count> lines)` |
| End before start | `endLine: must be greater than or equal to startLine` |
| Diff evidence names an unreviewed file | `evidence.file: '<file>' was not part of this review` |
| Hunk out of range | `evidence.hunkIndex: '<file>' has hunks 0–<k>` |
| Check evidence | `evidence.kind: no checks were run in this review; cite the diff or mark the finding unverified` |
| Context evidence | `evidence.kind: no related context was gathered in this review; cite the diff or mark the finding unverified` |
| Rule named that is not loaded, with rules loaded *(not reachable in 001)* | `ruleId: '<id>' is not a loaded rule` |

## Discarded fields

*(Changed 2026-10-09. Until then a `ruleId` was a rejection, `ruleId: no pattern rules are loaded in this review; omit
ruleId`.)*

A `ruleId` sent while **no** pattern rules are loaded is **discarded, and the finding is accepted without it** — it is
not a rejection. The observation says what was done:

```jsonc
{"status": "ok", "reason": null, "content": "accepted as f-1; ruleId discarded: no pattern rules are loaded in this review"}
```

Why this one field is treated differently from every row above:

- **Nothing in the finding depends on it.** A dangling evidence reference makes an unevidenced finding look evidenced
  (gap D-1), so it must be rejected. A rule label backs no claim: with it removed, the file, lines, rationale and
  evidence are exactly what the model sent.
- **There is nothing to correct it to.** With no rules loaded the only valid correction is to leave the field out,
  which the system can do itself, deterministically. Spending the one repair turn on it cost a whole review in
  practice: the model sent one well-formed finding with an invented `ruleId`, answered the repair turn in prose, and
  the run ended with no finding and no judgement.
- **A dangling label never reaches the report** either way, so FR-6.2a is unaffected.

With rules loaded (feature 003) an unknown `ruleId` **is** still rejected, as in the table above: there the model may
have meant a real rule, and the repair turn lets it name the right one.

## The repair turn (FR-016 / FR-5.6c)

- Taken **at most once per review**, only if ≥1 call was rejected **and** the ceiling was not reached.
- Messages sent: the system instructions, the original user message, the assistant reply, one `ToolMessage` per call,
  then a user message: *"One or more emit_finding calls were rejected; the reasons are in the tool results.
  Re-emit only the rejected findings, corrected. Do not repeat accepted findings. Reply without a tool call when done."*
- It does **not** consume a ceiling slot. Calls made **within** it do (R-13).
- Findings accepted in it have `turnIndex: 1`.
- If any call in it is rejected, or it makes no call at all, the rejected findings stay uncorrected and
  `invalid-model-output` is recorded (R-14, R-17).
