"""Cohere provider adapter."""

from swaplm.models.provider import ProviderInfo
from swaplm.providers.base import BaseProvider


class CohereProvider(BaseProvider):
    """Cohere LLM provider adapter."""

    info = ProviderInfo(
        id="cohere",
        name="Cohere",
        protocol="openai",
        base_url="https://api.cohere.com/v2",
        env_var="COHERE_API_KEY",
        display_name="Cohere",
        website="https://cohere.com",
        documentation="https://docs.cohere.com",
        requires_api_key=True,
        supports_byok=True,
        supports_streaming=True,
        supports_tools=True,
        supports_reasoning=False,
    )
