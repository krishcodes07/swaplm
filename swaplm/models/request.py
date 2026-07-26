"""Unified chat request model.

``ChatRequest`` normalises every parameter the SDK accepts before
handing it to a protocol for provider-specific translation.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, computed_field

from swaplm.models.messages import Message, Tool


class ChatRequest(BaseModel):
    """Provider-agnostic chat completion request."""

    # ── Required ──────────────────────────────────────────────────────
    model: str
    """Model identifier. Format depends on whether ``provider`` is set."""

    messages: list[Message]
    """Conversation history."""

    # ── Explicit provider (optional) ──────────────────────────────────
    provider: str | None = Field(default=None, exclude=True)
    """Explicit provider slug. When set, ``model`` is treated as a raw
    model ID and routing bypasses model-string parsing."""

    # ── Generation parameters ─────────────────────────────────────────
    stream: bool = False
    max_tokens: int | None = None
    temperature: float | None = None
    top_p: float | None = None
    stop: str | list[str] | None = None
    seed: int | None = None
    response_format: dict[str, Any] | None = None

    # ── Tool calling ──────────────────────────────────────────────────
    tools: list[Tool] | None = None
    tool_choice: str | dict[str, Any] | None = None

    # ── Auth / transport ──────────────────────────────────────────────
    api_key: str | None = Field(default=None, exclude=True)
    """Explicit API key (overrides env var)."""

    base_url: str | None = None
    """Override the provider's default base URL."""

    timeout: float | None = None
    """Request timeout in seconds."""

    retries: int = 0
    """Number of retries on transient failures."""

    extra_headers: dict[str, str] | None = None
    """Additional HTTP headers merged into the request."""

    # ── Escape hatch ──────────────────────────────────────────────────
    provider_options: dict[str, Any] | None = None
    """Provider-specific options passed through verbatim."""

    # ── Computed helpers ──────────────────────────────────────────────

    @computed_field  # type: ignore[prop-decorator]
    @property
    def provider_id(self) -> str:
        """Extract provider ID.

        When ``provider`` is set explicitly, returns it directly.
        Otherwise parses from ``"provider/model"`` string.
        """
        if self.provider:
            return self.provider
        if "/" in self.model:
            return self.model.split("/", 1)[0]
        return ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def model_id(self) -> str:
        """Extract model ID.

        When ``provider`` is set explicitly, returns ``model`` as-is.
        Otherwise parses from ``"provider/model"`` string.
        """
        if self.provider:
            return self.model
        if "/" in self.model:
            return self.model.split("/", 1)[1]
        return self.model
