"""Groq provider adapter."""

from swaplm.models.provider import ProviderInfo
from swaplm.providers.base import BaseProvider


class GroqProvider(BaseProvider):
    """Groq LLM provider adapter."""

    info = ProviderInfo(
        id="groq",
        name="Groq",
        protocol="openai",
        base_url="https://api.groq.com/openai/v1",
        env_var="GROQ_API_KEY",
        requires_api_key=True,
        supports_byok=True,
    )
