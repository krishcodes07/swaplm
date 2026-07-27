"""Provider metadata model.

Each provider exposes a ``ProviderInfo`` that the registry and router
use to look up configuration without importing heavy provider code.
"""

from __future__ import annotations

from pydantic import BaseModel


class ProviderInfo(BaseModel):
    """Static metadata describing an LLM provider."""

    id: str
    """Unique slug used in model strings, e.g. ``"openai"``."""

    name: str
    """Human-readable name, e.g. ``"OpenAI"``."""

    protocol: str
    """Protocol ID this provider uses (``"openai"``, ``"anthropic"``, ``"google"``)."""

    base_url: str
    """Default API base URL."""

    env_var: str
    """Environment variable holding the API key."""

    display_name: str | None = None
    """Friendly display name."""

    website: str | None = None
    """Official provider website URL."""

    documentation: str | None = None
    """Official developer documentation URL."""

    requires_api_key: bool = True
    """Whether the provider needs an API key to function."""

    supports_byok: bool = True
    """Whether the provider supports Bring Your Own Key."""

    supports_streaming: bool = True
    """Whether the provider supports response streaming."""

    supports_tools: bool = True
    """Whether the provider supports function / tool calling."""

    supports_images: bool = False
    """Whether the provider supports image inputs/outputs."""

    supports_audio: bool = False
    """Whether the provider supports audio inputs/outputs."""

    supports_embeddings: bool = False
    """Whether the provider supports text embeddings."""

    supports_reasoning: bool = False
    """Whether the provider supports reasoning / thinking models."""
