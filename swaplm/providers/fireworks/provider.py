"""Fireworks AI provider adapter."""

from swaplm.models.provider import ProviderInfo
from swaplm.providers.base import BaseProvider


class FireworksProvider(BaseProvider):
    """Fireworks AI LLM provider adapter."""

    info = ProviderInfo(
        id="fireworks",
        name="Fireworks",
        protocol="openai",
        base_url="https://api.fireworks.ai/inference/v1",
        env_var="FIREWORKS_API_KEY",
        display_name="Fireworks AI",
        website="https://fireworks.ai",
        documentation="https://docs.fireworks.ai",
        requires_api_key=True,
        supports_byok=True,
        supports_streaming=True,
        supports_tools=True,
        supports_reasoning=True,
    )
