"""SambaNova provider adapter."""

from swaplm.models.provider import ProviderInfo
from swaplm.providers.base import BaseProvider


class SambaNovaProvider(BaseProvider):
    """SambaNova LLM provider adapter."""

    info = ProviderInfo(
        id="sambanova",
        name="SambaNova",
        protocol="openai",
        base_url="https://api.sambanova.ai/v1",
        env_var="SAMBANOVA_API_KEY",
        display_name="SambaNova AI",
        website="https://sambanova.ai",
        documentation="https://docs.sambanova.ai",
        requires_api_key=True,
        supports_byok=True,
        supports_streaming=True,
        supports_tools=True,
        supports_reasoning=True,
    )
