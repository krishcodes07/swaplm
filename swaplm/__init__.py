"""SwapLM — Universal Python SDK for LLM providers.

Public API
----------
.. code-block:: python

    from swaplm import chat

    response = chat(
        model="groq/llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Hello!"}],
    )
    print(response.content)
"""

from __future__ import annotations

from typing import Any

from swaplm.config import SDKConfig, configure, get_config, reset_config
from swaplm.discovery import model, models, provider, providers
from swaplm.exceptions import (
    AmbiguousModelError,
    AuthenticationError,
    ConfigurationError,
    InvalidModelError,
    InvalidProviderError,
    ModelCapabilityError,
    ProviderError,
    RateLimitError,
    RegistryValidationError,
    SwapLMError,
    TimeoutError,
    ToolCallError,
)
from swaplm.models.messages import Message, Tool
from swaplm.models.model import ModelInfo
from swaplm.models.provider import ProviderInfo
from swaplm.models.request import ChatRequest
from swaplm.models.response import ChatResponse
from swaplm.models.stream import StreamChunk
from swaplm.streaming.iterator import StreamResponse
from swaplm.version import __version__


def chat(
    *,
    model: str,
    messages: list[dict[str, Any] | Message],
    stream: bool = False,
    api_key: str | None = None,
    base_url: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
    top_p: float | None = None,
    tools: list[dict[str, Any] | Tool] | None = None,
    tool_choice: str | dict[str, Any] | None = None,
    stop: str | list[str] | None = None,
    seed: int | None = None,
    timeout: float | None = None,
    retries: int = 0,
    extra_headers: dict[str, str] | None = None,
    provider_options: dict[str, Any] | None = None,
) -> ChatResponse | StreamResponse:
    """Send a chat completion request to any LLM provider.

    Args:
        model: Model identifier in ``"provider/model"``, ``"free/model"``, or alias format.
        messages: Conversation messages (dicts or ``Message`` objects).
        stream: Whether to stream the response.
        api_key: Explicit API key (overrides env var).
        base_url: Override the provider's default API base URL.
        max_tokens: Maximum tokens to generate.
        temperature: Sampling temperature.
        top_p: Nucleus sampling parameter.
        tools: Tool definitions for function calling.
        tool_choice: Tool selection strategy.
        stop: Stop sequences.
        seed: Random seed for reproducibility.
        timeout: Request timeout in seconds.
        retries: Number of retries on transient failures.
        extra_headers: Additional HTTP headers.
        provider_options: Provider-specific options (pass-through).

    Returns:
        ``ChatResponse`` for non-streaming requests, or
        ``StreamResponse`` for streaming requests.
    """
    from swaplm._client import _default_client

    normalised_messages = [
        Message.model_validate(m) if isinstance(m, dict) else m for m in messages
    ]

    normalised_tools = None
    if tools:
        normalised_tools = [Tool.model_validate(t) if isinstance(t, dict) else t for t in tools]

    request = ChatRequest(
        model=model,
        messages=normalised_messages,
        stream=stream,
        api_key=api_key,
        base_url=base_url,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        tools=normalised_tools,
        tool_choice=tool_choice,
        stop=stop,
        seed=seed,
        timeout=timeout,
        retries=retries,
        extra_headers=extra_headers,
        provider_options=provider_options,
    )

    return _default_client.chat(request)


__all__ = [
    # Exceptions
    "AmbiguousModelError",
    "AuthenticationError",
    # Models
    "ChatRequest",
    "ChatResponse",
    "ConfigurationError",
    "InvalidModelError",
    "InvalidProviderError",
    "Message",
    "ModelCapabilityError",
    "ModelInfo",
    "ProviderError",
    "ProviderInfo",
    "RateLimitError",
    "RegistryValidationError",
    # Configuration
    "SDKConfig",
    "StreamChunk",
    "StreamResponse",
    "SwapLMError",
    "TimeoutError",
    "Tool",
    "ToolCallError",
    # Version
    "__version__",
    # Public API
    "chat",
    "configure",
    "get_config",
    # Discovery
    "model",
    "models",
    "provider",
    "providers",
    "reset_config",
]
