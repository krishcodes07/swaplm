"""Streaming chunk models.

Each ``StreamChunk`` represents one server-sent event parsed and
normalised by a protocol implementation.
"""

from __future__ import annotations

from pydantic import BaseModel

from swaplm.models.messages import ToolCallDelta
from swaplm.models.response import Usage


class ChoiceDelta(BaseModel):
    """Incremental content received during streaming."""

    role: str | None = None
    content: str | None = None
    tool_calls: list[ToolCallDelta] | None = None


class ChunkChoice(BaseModel):
    """A single choice inside a stream chunk."""

    index: int = 0
    delta: ChoiceDelta
    finish_reason: str | None = None


class StreamChunk(BaseModel):
    """Provider-agnostic streaming chunk."""

    id: str | None = None
    choices: list[ChunkChoice] | None = None
    usage: Usage | None = None
    model: str | None = None
    provider: str | None = None
