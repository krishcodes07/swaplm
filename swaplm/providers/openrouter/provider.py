"""OpenRouter provider adapter."""

from swaplm.models.provider import ProviderInfo
from swaplm.providers.base import BaseProvider


class OpenRouterProvider(BaseProvider):
    """OpenRouter LLM provider adapter."""

    info = ProviderInfo(
        id="openrouter",
        name="OpenRouter",
        protocol="openai",
        base_url="https://openrouter.ai/api/v1",
        env_var="OPENROUTER_API_KEY",
        display_name="OpenRouter",
        website="https://openrouter.ai",
        documentation="https://openrouter.ai/docs",
        requires_api_key=False,
        is_free=True,
        supports_byok=True,
        supports_streaming=True,
        supports_tools=True,
        supports_reasoning=True,
    )
