"""Model capability metadata.

Each provider ships a ``models.json`` whose entries are validated
against ``ModelInfo``.  This gives the SDK rich, queryable knowledge
about what each model supports.
"""

from __future__ import annotations

from pydantic import BaseModel


class ModelInfo(BaseModel):
    """Rich capability metadata for a single model."""

    # ── Identity ──────────────────────────────────────────────────────
    id: str
    """Model identifier as used in API calls, e.g. ``"gpt-5"``."""

    display_name: str | None = None
    """Human-friendly label, e.g. ``"GPT-5"``."""

    type: str = "chat"
    """Model type: ``"chat"``, ``"completion"``, ``"embedding"``, etc."""

    # ── Limits ────────────────────────────────────────────────────────
    context_window: int | None = None
    """Maximum total tokens (prompt + completion)."""

    max_tokens: int | None = None
    """Maximum completion tokens the model can generate."""

    # ── Capability flags ──────────────────────────────────────────────
    supports_streaming: bool = True
    supports_tool_calling: bool = False
    supports_structured_output: bool = False
    supports_thinking: bool = False
    supports_reasoning_effort: bool = False
    supports_json_mode: bool = False
    supports_temperature: bool = True
    supports_seed: bool = False
    supports_system_message: bool = True

    # ── Future multi-modal flags ──────────────────────────────────────
    supports_vision: bool = False
    supports_audio: bool = False
    supports_images: bool = False

    # ── Defaults ──────────────────────────────────────────────────────
    default_temperature: float | None = None
    default_max_tokens: int | None = None
