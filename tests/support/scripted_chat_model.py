"""The stand-in model (research R-19).

It drives the **real** review graph: the repair, ceiling and no-call logic run as shipped. ``GenericFakeChatModel``
raises ``NotImplementedError`` from ``bind_tools``, so this subclass records the binding and returns itself.
"""

from __future__ import annotations

import itertools
from collections.abc import Iterable, Sequence
from typing import Any

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult

_call_ids = itertools.count(1)


class ScriptedChatModel(GenericFakeChatModel):
    """Replays scripted replies in order. A scripted ``BaseException`` instance is raised instead of returned."""

    script: list[Any]
    call_count: int = 0
    bound_tools: list[Any] | None = None
    bound_kwargs: dict[str, Any] | None = None
    received: list[list[BaseMessage]] = []

    def __init__(self, script: Sequence[AIMessage | BaseException], **kwargs: Any) -> None:
        super().__init__(messages=iter(()), script=list(script), received=[], **kwargs)

    def bind_tools(self, tools: Sequence[Any], **kwargs: Any) -> ScriptedChatModel:  # type: ignore[override]
        self.bound_tools = list(tools)
        self.bound_kwargs = dict(kwargs)
        return self

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        self.received.append(list(messages))
        index = self.call_count
        self.call_count += 1
        if index >= len(self.script):
            raise AssertionError(f"the stand-in model was called {self.call_count} times; only {len(self.script)} scripted")
        reply = self.script[index]
        if isinstance(reply, BaseException):
            raise reply
        return ChatResult(generations=[ChatGeneration(message=reply)])


def finding_args(**fields: Any) -> dict[str, Any]:
    """A valid ``emit_finding`` argument object for ``src/app.ts``; override any field by its JSON name."""
    file = fields.get("file", "src/app.ts")
    args: dict[str, Any] = {
        "file": file,
        "startLine": 1,
        "endLine": 1,
        "severity": "important",
        "category": "correctness",
        "rationale": "The new branch returns before the value is validated.",
        "evidence": {"kind": "diff", "file": file, "hunkIndex": 0},
    }
    args.update(fields)
    return args


def finding_call(name: str = "emit_finding", **fields: Any) -> dict[str, Any]:
    return {"name": name, "args": finding_args(**fields), "id": f"call_{next(_call_ids)}", "type": "tool_call"}


def invalid_json_call(raw: str = '{"file": "src/app.ts", ') -> dict[str, Any]:
    return {
        "name": "emit_finding",
        "args": raw,
        "id": f"call_{next(_call_ids)}",
        "error": "Function emit_finding arguments are not valid JSON",
        "type": "invalid_tool_call",
    }


def ai_reply(
    tool_calls: Iterable[dict[str, Any]] = (),
    *,
    invalid_tool_calls: Iterable[dict[str, Any]] = (),
    content: str = "",
    usage: tuple[int, int] | None = None,
    finish_reason: str | None = None,
) -> AIMessage:
    extra: dict[str, Any] = {}
    if usage is not None:
        extra["usage_metadata"] = {"input_tokens": usage[0], "output_tokens": usage[1], "total_tokens": sum(usage)}
    if finish_reason is not None:
        extra["response_metadata"] = {"finish_reason": finish_reason}
    return AIMessage(
        content=content,
        tool_calls=list(tool_calls),
        invalid_tool_calls=list(invalid_tool_calls),
        **extra,
    )
