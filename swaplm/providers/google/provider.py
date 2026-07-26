"""Google Gemini provider adapter."""

from swaplm.models.provider import ProviderInfo
from swaplm.providers.base import BaseProvider


class GoogleProvider(BaseProvider):
    """Google Gemini LLM provider adapter."""

    info = ProviderInfo(
        id="google",
        name="Google",
        protocol="google",
        base_url="https://generativelanguage.googleapis.com/v1beta",
        env_var="GEMINI_API_KEY",
        display_name="Google Gemini",
        website="https://ai.google.dev",
        documentation="https://ai.google.dev/docs",
        requires_api_key=True,
        supports_byok=True,
        supports_streaming=True,
        supports_tools=True,
        supports_reasoning=True,
    )
