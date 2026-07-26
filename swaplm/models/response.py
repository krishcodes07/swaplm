"""Unified chat response models."""

from __future__ import annotations

from pydantic import BaseModel

from swaplm.models.messages import Message, ToolCall


class Usage(BaseModel):
    """Token usage statistics."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class Choice(BaseModel):
    """A single completion choice."""

    index: int = 0
    message: Message
    finish_reason: str | None = None


class ChatResponse(BaseModel):
    """Provider-agnostic chat completion response."""

    id: str
    choices: list[Choice]
    usage: Usage | None = None
    model: str
    provider: str
    created: int | None = None

    # ── Convenience properties ────────────────────────────────────────

    @property
    def content(self) -> str | None:
        """Shortcut: content of the first choice's message."""
        if self.choices:
            c = self.choices[0].message.content
            return c if isinstance(c, str) else None
        return None

    @property
    def tool_calls(self) -> list[ToolCall] | None:
        """Shortcut: tool calls from the first choice's message."""
        if self.choices:
            return self.choices[0].message.tool_calls
        return None

    @property
    def finish_reason(self) -> str | None:
        """Shortcut: finish reason of the first choice."""
        if self.choices:
            return self.choices[0].finish_reason
        return None

    @property
    def reasoning(self) -> str | None:
        """Shortcut: reasoning/thinking content from the first choice's message.

        Some providers return reasoning in a separate field. This property
        checks ``message.refusal`` as a fallback. For providers that return
        reasoning in ``content`` as a structured object, access it via
        ``choices[0].message`` directly.
        """
        if self.choices:
            msg = self.choices[0].message
            if msg.refusal:
                return msg.refusal
        return None
