"""Shared runtime types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Role = Literal["system", "user", "assistant", "tool"]


@dataclass
class Message:
    role: Role
    content: str
    name: str | None = None
    tool_call_id: str | None = None


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class ModelChunk:
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    done: bool = False


@dataclass
class ModelResponse:
    text: str
    tool_calls: list[ToolCall] = field(default_factory=list)


@dataclass
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, Any]
