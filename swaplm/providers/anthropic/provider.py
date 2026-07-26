"""Anthropic provider adapter."""

from swaplm.models.provider import ProviderInfo
from swaplm.providers.base import BaseProvider


class AnthropicProvider(BaseProvider):
    """Anthropic LLM provider adapter."""

    info = ProviderInfo(
        id="anthropic",
        name="Anthropic",
        protocol="anthropic",
        base_url="https://api.anthropic.com/v1",
        env_var="ANTHROPIC_API_KEY",
        display_name="Anthropic Claude",
        website="https://www.anthropic.com",
        documentation="https://docs.anthropic.com",
        requires_api_key=True,
        supports_byok=True,
        supports_streaming=True,
        supports_tools=True,
        supports_reasoning=True,
    )
