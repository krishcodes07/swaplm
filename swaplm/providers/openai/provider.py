"""OpenAI provider adapter."""

from swaplm.models.provider import ProviderInfo
from swaplm.providers.base import BaseProvider


class OpenAIProvider(BaseProvider):
    """OpenAI LLM provider adapter."""

    info = ProviderInfo(
        id="openai",
        name="OpenAI",
        protocol="openai",
        base_url="https://api.openai.com/v1",
        env_var="OPENAI_API_KEY",
        display_name="OpenAI",
        website="https://openai.com",
        documentation="https://platform.openai.com/docs",
        requires_api_key=True,
        supports_byok=True,
        supports_streaming=True,
        supports_tools=True,
        supports_reasoning=True,
    )
