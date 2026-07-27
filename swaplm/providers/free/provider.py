"""Free provider adapter.

Routes to curated free-tier models via OpenRouter's public API.
No API key is required for these models.
"""

from swaplm.models.provider import ProviderInfo
from swaplm.providers.base import BaseProvider


class FreeProvider(BaseProvider):
    """Free-tier LLM provider adapter.

    Provides access to curated, genuinely free models through
    OpenRouter's free-tier API. No API key is required.
    """

    info = ProviderInfo(
        id="free",
        name="Free",
        protocol="openai",
        base_url="https://openrouter.ai/api/v1",
        env_var="SWAPLM_FREE_API_KEY",
        display_name="Free (OpenRouter)",
        website="https://openrouter.ai",
        documentation="https://openrouter.ai/docs",
        requires_api_key=False,
        supports_byok=False,
        supports_streaming=True,
        supports_tools=True,
        supports_reasoning=True,
    )
