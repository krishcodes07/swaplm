"""Unified message, tool, and function-call models.

These types are provider-independent.  Every protocol is responsible for
translating its native format to and from these models.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Function / Tool definitions
# ---------------------------------------------------------------------------


class FunctionCall(BaseModel):
    """A resolved function call (name + serialised arguments)."""

    name: str
    arguments: str
    """JSON-encoded string of the function arguments."""


class ToolCall(BaseModel):
    """A tool invocation attached to an assistant message."""

    id: str
    type: str = "function"
    function: FunctionCall


class ToolCallDelta(BaseModel):
    """Partial tool-call data received during streaming."""

    index: int = 0
    id: str | None = None
    type: str | None = None
    function: FunctionCallDelta | None = None


class FunctionCallDelta(BaseModel):
    """Partial function-call data received during streaming."""

    name: str | None = None
    arguments: str | None = None


# ---------------------------------------------------------------------------
# Tool definitions (sent in the request)
# ---------------------------------------------------------------------------


class FunctionDefinition(BaseModel):
    """Schema describing a callable function."""

    name: str
    description: str | None = None
    parameters: dict[str, Any] | None = None


class Tool(BaseModel):
    """A tool the model can invoke."""

    type: str = "function"
    function: FunctionDefinition


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------


class Message(BaseModel):
    """A single message in a conversation.

    Compatible with the OpenAI message format by design; protocols are
    responsible for converting to/from provider-native formats.
    """

    role: str
    """One of ``"system"``, ``"user"``, ``"assistant"``, or ``"tool"``."""

    content: str | list[dict[str, Any]] | None = None
    """Text content, or a list of content parts (future multi-modal)."""

    name: str | None = None
    """Optional participant name."""

    tool_calls: list[ToolCall] | None = None
    """Tool calls requested by the assistant."""

    tool_call_id: str | None = None
    """ID of the tool call this message responds to (role ``"tool"``)."""

    refusal: str | None = None
    """Model refusal text, if any."""

    model_config = {"extra": "allow"}
    """Allow extra fields so provider-specific data is not silently lost."""


# ---------------------------------------------------------------------------
# Content part helpers (forward-looking, for multi-modal)
# ---------------------------------------------------------------------------


class TextContent(BaseModel):
    """Text content part."""

    type: str = "text"
    text: str


class ImageContent(BaseModel):
    """Image content part (URL or base64)."""

    type: str = "image_url"
    image_url: ImageURL


class ImageURL(BaseModel):
    """Image URL descriptor."""

    url: str
    detail: str | None = Field(default=None, description="low | high | auto")
