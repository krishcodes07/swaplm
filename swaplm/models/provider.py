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

    requires_api_key: bool = True
    """Whether the provider needs an API key to function."""

    supports_byok: bool = True
    """Whether the provider supports Bring Your Own Key."""
