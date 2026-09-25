from __future__ import annotations

from collections.abc import Callable, Sequence

import pytest
from langchain_core.messages import AIMessage

from agentic_review.agents.review_port import LangGraphReviewPort, build_review_port
from agentic_review.core.config.credentials import Credential
from agentic_review.core.config.settings import AgentSettings
from agentic_review.core.findings.port import ReviewContext, ReviewedFile, RunMaterial
from tests.conftest import CANARY_KEY
from tests.support.scripted_chat_model import ScriptedChatModel

CONTEXT = ReviewContext(
    instructions="instructions",
    material_statement="No checks were run. No related context was gathered.",
    diff_section="src/app.ts (modified)\n[hunk 0] @@ -1 +1 @@\n-a\n+b\n",
    estimated_tokens=40,
    material=RunMaterial(reviewed_files={"src/app.ts": ReviewedFile(line_count=40, hunk_count=2)}),
)

PortFactory = Callable[..., tuple[LangGraphReviewPort, ScriptedChatModel]]


@pytest.fixture
def make_port() -> PortFactory:
    def factory(
        script: Sequence[AIMessage | BaseException], **agent: object
    ) -> tuple[LangGraphReviewPort, ScriptedChatModel]:
        model = ScriptedChatModel(script)
        credential = Credential(CANARY_KEY, source="environment", location="AGENTIC_REVIEW_API_KEY")
        port = build_review_port(AgentSettings.model_validate(agent), credential, chat_model=model)
        return port, model

    return factory
