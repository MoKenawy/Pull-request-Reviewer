"""The finding model — what the model may emit, and what the system accepts (data-model §3, FR-5.2, FR-5.2a–c).

``FindingDraft`` is the single definition behind the ``emit_finding`` tool schema, the ``findings`` section of the
report schema, and call validation (SRS §5: one definition, not two).
"""

from __future__ import annotations

from typing import Annotated, Any, ClassVar, Literal

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    SerializerFunctionWrapHandler,
    field_validator,
    model_serializer,
    model_validator,
)
from pydantic.alias_generators import to_camel
from pydantic.json_schema import SkipJsonSchema
from pydantic_core import PydanticCustomError

Severity = Literal["blocking", "important", "nit"]
Category = Literal[
    "correctness",
    "error-handling",
    "interface-contract",
    "test-evidence",
    "security",
    "performance",
    "maintainability",
]


def _optional_str(value: Any) -> Any:
    # Checked before the `str | None` union, so a bad value yields one error at the field, not one per union branch.
    if value is not None and not isinstance(value, str):
        raise PydanticCustomError("string_type", "Input should be a valid string")
    return value


def _optional_non_negative_int(value: Any) -> Any:
    if value is None:
        return value
    if isinstance(value, bool) or not isinstance(value, int):
        raise PydanticCustomError("int_type", "Input should be a valid integer")
    if value < 0:
        raise PydanticCustomError("greater_than_equal", "Input should be greater than or equal to 0")
    return value


class WireModel(BaseModel):
    """camelCase on the wire, snake_case in Python; optional fields listed in ``_omit_when_none`` are left out."""

    model_config = ConfigDict(
        extra="forbid",
        alias_generator=to_camel,
        validate_by_name=True,
        validate_by_alias=True,
        frozen=True,
    )

    _omit_when_none: ClassVar[frozenset[str]] = frozenset()

    @model_serializer(mode="wrap")
    def _omit_absent(self, handler: SerializerFunctionWrapHandler):  # noqa: ANN202 - no annotation keeps the model schema
        data = handler(self)
        if isinstance(data, dict) and self._omit_when_none:
            for name in self._omit_when_none:
                for key in (name, to_camel(name)):
                    if key in data and data[key] is None:
                        del data[key]
        return data


class CheckEvidence(WireModel):
    """A check that was executed in this review. Not reachable until feature 002 runs checks."""

    _omit_when_none = frozenset({"failing_test"})

    kind: Literal["check"]
    check_id: Annotated[
        Literal["tests", "typecheck"],
        Field(description="The check whose result shows the problem. Rejected while no checks are run."),
    ]
    failing_test: Annotated[
        str | SkipJsonSchema[None],
        BeforeValidator(_optional_str),
        Field(description="Name of the failing test, when one identifies the problem."),
    ] = None


class ContextEvidence(WireModel):
    """Related code gathered for this review. Not reachable until feature 004 gathers context."""

    kind: Literal["context"]
    file: Annotated[str, Field(min_length=1, description="Path of the related file that was gathered.")]
    start_line: Annotated[int, Field(ge=1, description="First line of the gathered range.")]
    end_line: Annotated[int, Field(ge=1, description="Last line of the gathered range.")]


class DiffEvidence(WireModel):
    """The usual evidence: the diff you were shown demonstrates the problem."""

    _omit_when_none = frozenset({"hunk_index"})

    kind: Literal["diff"]
    file: Annotated[
        str,
        Field(min_length=1, description="A reviewed file whose diff shows the problem; usually the finding's file."),
    ]
    hunk_index: Annotated[
        int | SkipJsonSchema[None],
        BeforeValidator(_optional_non_negative_int),
        Field(
            json_schema_extra={"minimum": 0},
            description="The number i of the '[hunk i]' block you are citing in that file. Omit to cite the file.",
        ),
    ] = None


class UnverifiedEvidence(WireModel):
    """An honest admission: the finding goes beyond what this review could see."""

    kind: Literal["unverified"]
    reason: Annotated[
        str,
        Field(
            min_length=1,
            description="What you could not check here, for example 'callers of this function were not shown'.",
        ),
    ]


EvidenceRef = Annotated[
    CheckEvidence | ContextEvidence | DiffEvidence | UnverifiedEvidence,
    Field(discriminator="kind"),
]


class FindingDraft(WireModel):
    """One review finding: a single specific problem, at one location, in one file of the change under review."""

    # This docstring and every field description below travel to the provider inside the generated tool schema
    # (contracts/emit-finding.md), so they are written for the model: instructions to the caller, not notes to
    # ourselves. Developer notes belong in comments like this one, which the schema does not carry.

    _omit_when_none = frozenset({"rule_id"})

    file: Annotated[
        str,
        Field(
            min_length=1,
            description="Repository-relative path of the reviewed file the problem is in, exactly as the diff shows it.",
        ),
    ]
    start_line: Annotated[
        int,
        Field(
            ge=1,
            description=(
                "First line of the problem in the NEW version of the file. Each hunk's '@@ -old +new @@' header gives "
                "the line number of its first line; count added (+) and context ( ) lines from there."
            ),
        ),
    ]
    end_line: Annotated[
        int,
        Field(ge=1, description="Last line of the problem, at or after startLine. Keep the range as small as possible."),
    ]
    severity: Annotated[
        Severity,
        Field(
            description=(
                "blocking = likely to break behaviour, lose data or open a vulnerability, so do not merge; "
                "important = a real defect to fix that does not by itself block the merge; "
                "nit = minor and local. When unsure, choose the lower severity."
            )
        ),
    ]
    category: Annotated[
        Category,
        Field(
            description=(
                "The kind of problem: correctness (wrong result), error-handling (errors swallowed, lost or escaping), "
                "interface-contract (a change callers rely on), test-evidence (behaviour changed without a test), "
                "security (untrusted input, secrets, missing authorisation), performance (avoidable work), "
                "maintainability (dead code, unused values, misleading names)."
            )
        ),
    ]
    rationale: Annotated[
        str,
        Field(
            min_length=1,
            description=(
                "One or two sentences: name the symbol involved, say what is wrong and what it causes. "
                "Do not restate the diff."
            ),
        ),
    ]
    rule_id: Annotated[
        str | SkipJsonSchema[None],
        BeforeValidator(_optional_str),
        Field(description="Leave unset. No pattern rules are loaded, so any value here is rejected."),
    ] = None
    evidence: Annotated[
        EvidenceRef,
        Field(
            description=(
                "Required. What supports this finding: cite the diff hunk that shows it, or mark the finding "
                "unverified with the reason you could not check it here."
            )
        ),
    ]

    @field_validator("rationale")
    @classmethod
    def _rationale_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise PydanticCustomError("blank", "must contain text other than whitespace")
        return value

    @model_validator(mode="after")
    def _end_not_before_start(self) -> FindingDraft:
        if self.end_line < self.start_line:
            raise PydanticCustomError("end_before_start", "must be greater than or equal to startLine")
        return self


class Finding(FindingDraft):
    """A draft the system accepted, plus the fields the model cannot set (data-model §3)."""

    # Report consumers must ignore unknown fields, so the published finding does not forbid them.
    model_config = ConfigDict(extra="ignore")

    id: str
    schema_version: str
    turn_index: Annotated[int, Field(ge=0)]
    fingerprint: Annotated[str, Field(pattern=r"^[0-9a-f]{12}$")]


class ToolObservation(WireModel):
    # FR-5.9. No requirement ID in this docstring: WireModel docstrings travel into the JSON schema (FR-5.6a's
    # tool_schema() generates from FindingDraft only today, so this one doesn't leak yet — keep it that way).
    """The structured result handed back to the model for every tool call."""

    status: Literal["ok", "error", "denied"]
    reason: str | None = None
    content: str | None = None

    @model_validator(mode="after")
    def _reason_when_not_ok(self) -> ToolObservation:
        if self.status != "ok" and not self.reason:
            raise ValueError("reason is required when status is not ok")
        return self
