"""xAI provider adapter."""

from swaplm.models.provider import ProviderInfo
from swaplm.providers.base import BaseProvider


class XAIProvider(BaseProvider):
    """xAI LLM provider adapter."""

    info = ProviderInfo(
        id="xai",
        name="xAI",
        protocol="openai",
        base_url="https://api.x.ai/v1",
        env_var="XAI_API_KEY",
        display_name="xAI Grok",
        website="https://x.ai",
        documentation="https://docs.x.ai",
        requires_api_key=True,
        supports_byok=True,
        supports_streaming=True,
        supports_tools=True,
        supports_reasoning=False,
    )
