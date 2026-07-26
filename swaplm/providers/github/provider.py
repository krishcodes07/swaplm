"""GitHub Models provider adapter."""

from swaplm.models.provider import ProviderInfo
from swaplm.providers.base import BaseProvider


class GitHubProvider(BaseProvider):
    """GitHub Models LLM provider adapter."""

    info = ProviderInfo(
        id="github",
        name="GitHub",
        protocol="openai",
        base_url="https://models.inference.ai.azure.com",
        env_var="GITHUB_TOKEN",
        display_name="GitHub Models",
        website="https://github.com/marketplace/models",
        documentation="https://docs.github.com/en/github-models",
        requires_api_key=True,
        is_free=True,
        supports_byok=True,
        supports_streaming=True,
        supports_tools=True,
        supports_reasoning=True,
    )
