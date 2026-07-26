"""Together AI provider adapter."""

from swaplm.models.provider import ProviderInfo
from swaplm.providers.base import BaseProvider


class TogetherProvider(BaseProvider):
    """Together AI LLM provider adapter."""

    info = ProviderInfo(
        id="together",
        name="Together",
        protocol="openai",
        base_url="https://api.together.xyz/v1",
        env_var="TOGETHER_API_KEY",
        display_name="Together AI",
        website="https://www.together.ai",
        documentation="https://docs.together.ai",
        requires_api_key=True,
        supports_byok=True,
        supports_streaming=True,
        supports_tools=True,
        supports_reasoning=True,
    )
