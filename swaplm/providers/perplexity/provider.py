"""Perplexity AI provider adapter."""

from swaplm.models.provider import ProviderInfo
from swaplm.providers.base import BaseProvider


class PerplexityProvider(BaseProvider):
    """Perplexity AI LLM provider adapter."""

    info = ProviderInfo(
        id="perplexity",
        name="Perplexity",
        protocol="openai",
        base_url="https://api.perplexity.ai",
        env_var="PERPLEXITY_API_KEY",
        display_name="Perplexity AI",
        website="https://perplexity.ai",
        documentation="https://docs.perplexity.ai",
        requires_api_key=True,
        supports_byok=True,
        supports_streaming=True,
        supports_tools=False,
        supports_reasoning=True,
    )
