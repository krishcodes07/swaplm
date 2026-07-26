"""DeepInfra provider adapter."""

from swaplm.models.provider import ProviderInfo
from swaplm.providers.base import BaseProvider


class DeepInfraProvider(BaseProvider):
    """DeepInfra LLM provider adapter."""

    info = ProviderInfo(
        id="deepinfra",
        name="DeepInfra",
        protocol="openai",
        base_url="https://api.deepinfra.com/v1/openai",
        env_var="DEEPINFRA_API_KEY",
        display_name="DeepInfra",
        website="https://deepinfra.com",
        documentation="https://deepinfra.com/docs",
        requires_api_key=True,
        supports_byok=True,
        supports_streaming=True,
        supports_tools=True,
        supports_reasoning=True,
    )
