"""NVIDIA NIM provider adapter."""

from swaplm.models.provider import ProviderInfo
from swaplm.providers.base import BaseProvider


class NvidiaProvider(BaseProvider):
    """NVIDIA NIM LLM provider adapter."""

    info = ProviderInfo(
        id="nvidia",
        name="NVIDIA",
        protocol="openai",
        base_url="https://integrate.api.nvidia.com/v1",
        env_var="NVIDIA_API_KEY",
        display_name="NVIDIA NIM",
        website="https://build.nvidia.com",
        documentation="https://docs.nvidia.com/nim",
        requires_api_key=True,
        supports_byok=True,
        supports_streaming=True,
        supports_tools=True,
        supports_reasoning=True,
    )
