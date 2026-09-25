"""The `.agentic-review.yml` model (data-model §7, `Docs/design/04-contracts.md` §7).

The whole documented schema is modelled, including sections for capabilities not built yet, so a file written now stays
valid later (FR-1.2d). Every section forbids unknown keys: a misspelt field must never fall back to its default
silently. There is deliberately no field that could hold a credential (FR-1.3a).
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel

ScopeSetting = Literal["working-tree", "staged", "range"]

DEFAULT_MODEL = "meta/llama-3.3-70b-instruct"  # PLACEHOLDER - chosen by test S-1 (research R-21)
DEFAULT_BASE_URL = "https://integrate.api.nvidia.com/v1"  # NVIDIA NIM free tier (SRS §2.3)


class _Section(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        alias_generator=to_camel,
        validate_by_name=True,
        validate_by_alias=True,
        frozen=True,
    )


class ContextSettings(_Section):
    """Accepted and validated; no effect until feature 004."""

    depth: Annotated[int, Field(ge=0)] = 1
    node: str = "node"


class CheckSettings(_Section):
    """Accepted and validated; no effect until feature 002."""

    command: Annotated[list[str], Field(min_length=1)] | None = None  # None = discovered from the project
    timeout_seconds: Annotated[int, Field(ge=1)] = 120  # PLACEHOLDER - SRS §8, TBD-4


class ChecksSettings(_Section):
    tests: CheckSettings = CheckSettings()
    typecheck: CheckSettings = CheckSettings()


class AgentSettings(_Section):
    tool_call_ceiling: Annotated[int, Field(ge=1)] = 25  # PLACEHOLDER - SRS §8, TBD-8
    investigation_tools: bool = False  # true is accepted, has no effect until feature 005, and is reported
    model: Annotated[str, Field(min_length=1)] = DEFAULT_MODEL
    base_url: str = DEFAULT_BASE_URL
    temperature: Annotated[float, Field(ge=0, le=2)] = 0
    request_timeout_seconds: Annotated[int, Field(ge=1)] = 60  # PLACEHOLDER - additive field, plan D-9
    rate_limit_retry_seconds: Annotated[int, Field(ge=0)] = 60  # how long to wait before retrying a 429

    @field_validator("base_url")
    @classmethod
    def _http_url(cls, value: str) -> str:
        if not value.startswith(("http://", "https://")):
            raise ValueError("must be an http:// or https:// URL")
        return value


class BudgetSettings(_Section):
    max_tokens: Annotated[int, Field(ge=1)] = 20000  # PLACEHOLDER - SRS §8, TBD-3


class Settings(_Section):
    schema_version: Literal[1] = 1
    scope: ScopeSetting = "working-tree"
    exclude: list[str] = []  # added to the default exclusion list, never replacing it (FR-3.5)
    context: ContextSettings = ContextSettings()
    checks: ChecksSettings = ChecksSettings()
    agent: AgentSettings = AgentSettings()
    budget: BudgetSettings = BudgetSettings()
