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
    reasoning: str | None = None
    tool_calls: list[ToolCallDelta] | None = None


class ChunkChoice(BaseModel):
    """A single choice inside a stream chunk."""

    index: int = 0
    delta: ChoiceDelta
    finish_reason: str | None = None


class StreamChunk(BaseModel):
    """Provider-agnostic streaming chunk.

    Provides convenience properties that proxy the first choice's delta
    for quick access::

        for chunk in stream:
            print(chunk.content, end="")
    """

    id: str | None = None
    choices: list[ChunkChoice] | None = None
    usage: Usage | None = None
    model: str | None = None
    provider: str | None = None

    # ── Convenience properties ────────────────────────────────────────

    @property
    def content(self) -> str | None:
        """Shortcut: incremental text content from the first choice's delta."""
        if self.choices:
            return self.choices[0].delta.content
        return None

    @property
    def reasoning(self) -> str | None:
        """Shortcut: incremental reasoning content from the first choice's delta."""
        if self.choices:
            return self.choices[0].delta.reasoning
        return None

    @property
    def tool_calls(self) -> list[ToolCallDelta] | None:
        """Shortcut: tool call deltas from the first choice's delta."""
        if self.choices:
            return self.choices[0].delta.tool_calls
        return None

    @property
    def finish_reason(self) -> str | None:
        """Shortcut: finish reason of the first choice."""
        if self.choices:
            return self.choices[0].finish_reason
        return None
