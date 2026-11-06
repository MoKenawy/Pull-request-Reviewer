"""Per-run overrides of the agent's model and endpoint, read from the process environment.

The repository file is the project's choice; the environment is the developer's. Setting ``AGENTIC_REVIEW_MODEL`` or
``AGENTIC_REVIEW_BASE_URL`` lets one person point the same checkout at another model or another OpenAI-compatible
provider without editing — and without accidentally committing — ``.agentic-review.yml``. Resolution order is
defaults → file → environment → CLI flags (`Docs/design/05-cross-cutting.md` §4.1).

Neither variable can hold a credential: the key has its own variable, and nothing here is ever printed as a value in
a failure message beyond what the user themselves set. An invalid value fails as loudly as a bad field in the file
(FR-1.2d), because a mistyped endpoint is where the API key would otherwise be sent.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from pydantic import ValidationError

from agentic_review.core.config.loader import ConfigError
from agentic_review.core.config.settings import AgentSettings, Settings

MODEL_ENV_VAR = "AGENTIC_REVIEW_MODEL"
BASE_URL_ENV_VAR = "AGENTIC_REVIEW_BASE_URL"

_FIELD_FOR_VAR = {MODEL_ENV_VAR: "model", BASE_URL_ENV_VAR: "base_url"}
_FOOTER = "Nothing was reviewed. Fix the value above and re-run."


@dataclass(frozen=True)
class AgentOverrides:
    """What the environment says about the agent section, before it has been validated."""

    model: str | None = None
    base_url: str | None = None

    @property
    def is_empty(self) -> bool:
        return self.model is None and self.base_url is None


def agent_overrides(env: Mapping[str, str]) -> AgentOverrides:
    """A blank variable counts as unset: a `.env` line written as ``AGENTIC_REVIEW_MODEL=`` is not a choice."""
    return AgentOverrides(model=_value(env, MODEL_ENV_VAR), base_url=_value(env, BASE_URL_ENV_VAR))


def _value(env: Mapping[str, str], name: str) -> str | None:
    raw = env.get(name)
    if raw is None:
        return None
    stripped = raw.strip()
    return stripped or None


def apply_agent_overrides(settings: Settings, overrides: AgentOverrides) -> Settings:
    """``settings`` with the environment's agent fields applied, revalidated as if they had come from the file.

    Raises ``ConfigError`` naming the variable, so the message reads like the one a bad field in the file produces.
    """
    if overrides.is_empty:
        return settings

    update = {field: value for field, value in vars(overrides).items() if value is not None}
    try:
        agent = AgentSettings.model_validate({**settings.agent.model_dump(), **update})
    except ValidationError as error:
        raise ConfigError(_message(error)) from None
    return settings.model_copy(update={"agent": agent})


def _message(error: ValidationError) -> str:
    lines: list[str] = []
    for problem in error.errors():
        field = str(problem["loc"][0]) if problem["loc"] else ""
        variable = next((name for name, target in _FIELD_FOR_VAR.items() if target == field), field)
        lines.append(f"Error in the environment variable {variable}\n  {problem['msg']}")
    return "\n".join([*lines, _FOOTER])
