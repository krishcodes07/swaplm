"""Mistral AI provider adapter."""

from swaplm.models.provider import ProviderInfo
from swaplm.providers.base import BaseProvider


class MistralProvider(BaseProvider):
    """Mistral AI LLM provider adapter."""

    info = ProviderInfo(
        id="mistral",
        name="Mistral",
        protocol="openai",
        base_url="https://api.mistral.ai/v1",
        env_var="MISTRAL_API_KEY",
        display_name="Mistral AI",
        website="https://mistral.ai",
        documentation="https://docs.mistral.ai",
        requires_api_key=True,
        supports_byok=True,
        supports_streaming=True,
        supports_tools=True,
        supports_reasoning=False,
    )
