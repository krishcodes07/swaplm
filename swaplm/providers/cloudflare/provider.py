"""Cloudflare Workers AI provider adapter."""

from swaplm.models.provider import ProviderInfo
from swaplm.providers.base import BaseProvider


class CloudflareProvider(BaseProvider):
    """Cloudflare Workers AI LLM provider adapter."""

    info = ProviderInfo(
        id="cloudflare",
        name="Cloudflare",
        protocol="openai",
        base_url="https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1",
        env_var="CLOUDFLARE_API_KEY",
        display_name="Cloudflare Workers AI",
        website="https://ai.cloudflare.com",
        documentation="https://developers.cloudflare.com/workers-ai",
        requires_api_key=True,
        supports_byok=True,
        supports_streaming=True,
        supports_tools=True,
        supports_reasoning=False,
    )
