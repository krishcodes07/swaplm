"""SwapLM — Universal Python SDK for LLM providers.

Public API
----------
.. code-block:: python

    from swaplm import achat, chat

    # Sync
    response = chat(
        model="groq/llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Hello!"}],
    )

    # Async
    response = await achat(
        model="anthropic/claude-3-5-sonnet-20241022",
        messages=[{"role": "user", "content": "Hello!"}],
    )
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
from swaplm.hooks import off, on, reset_hooks
from swaplm.middleware import (
    BaseMiddleware,
    add_middleware,
    get_middlewares,
    remove_middleware,
    reset_middlewares,
)
from swaplm.models.messages import Message, Tool
from swaplm.models.model import ModelInfo
from swaplm.models.provider import ProviderInfo
from swaplm.models.request import ChatRequest
from swaplm.models.response import ChatResponse
from swaplm.models.stream import StreamChunk
from swaplm.streaming.iterator import StreamResponse
from swaplm.transport.base import BaseTransport
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
    response_format: dict[str, Any] | None = None,
    tools: list[dict[str, Any] | Tool] | None = None,
    tool_choice: str | dict[str, Any] | None = None,
    stop: str | list[str] | None = None,
    seed: int | None = None,
    timeout: float | None = None,
    retries: int = 0,
    extra_headers: dict[str, str] | None = None,
    provider_options: dict[str, Any] | None = None,
) -> ChatResponse | StreamResponse:
    """Send a synchronous chat completion request to any LLM provider."""
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
        response_format=response_format,
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


async def achat(
    *,
    model: str,
    messages: list[dict[str, Any] | Message],
    stream: bool = False,
    api_key: str | None = None,
    base_url: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
    top_p: float | None = None,
    response_format: dict[str, Any] | None = None,
    tools: list[dict[str, Any] | Tool] | None = None,
    tool_choice: str | dict[str, Any] | None = None,
    stop: str | list[str] | None = None,
    seed: int | None = None,
    timeout: float | None = None,
    retries: int = 0,
    extra_headers: dict[str, str] | None = None,
    provider_options: dict[str, Any] | None = None,
) -> ChatResponse | StreamResponse:
    """Send an asynchronous chat completion request to any LLM provider."""
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
        response_format=response_format,
        tools=normalised_tools,
        tool_choice=tool_choice,
        stop=stop,
        seed=seed,
        timeout=timeout,
        retries=retries,
        extra_headers=extra_headers,
        provider_options=provider_options,
    )

    return await _default_client.achat(request)


__all__ = [
    "AmbiguousModelError",
    "AuthenticationError",
    "BaseMiddleware",
    "BaseTransport",
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
    "SDKConfig",
    "StreamChunk",
    "StreamResponse",
    "SwapLMError",
    "TimeoutError",
    "Tool",
    "ToolCallError",
    "__version__",
    "achat",
    "add_middleware",
    "chat",
    "configure",
    "get_config",
    "get_middlewares",
    "model",
    "models",
    "off",
    "on",
    "provider",
    "providers",
    "remove_middleware",
    "reset_config",
    "reset_hooks",
    "reset_middlewares",
]
