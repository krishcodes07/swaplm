"""Cerebras provider adapter."""

from swaplm.models.provider import ProviderInfo
from swaplm.providers.base import BaseProvider


class CerebrasProvider(BaseProvider):
    """Cerebras LLM provider adapter."""

    info = ProviderInfo(
        id="cerebras",
        name="Cerebras",
        protocol="openai",
        base_url="https://api.cerebras.ai/v1",
        env_var="CEREBRAS_API_KEY",
        display_name="Cerebras AI",
        website="https://cerebras.ai",
        documentation="https://inference-docs.cerebras.ai",
        requires_api_key=True,
        supports_byok=True,
        supports_streaming=True,
        supports_tools=True,
        supports_reasoning=False,
    )
