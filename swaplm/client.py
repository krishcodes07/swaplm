"""Public client classes with lifecycle management.

Provides ``Client`` and ``AsyncClient`` as context-managed wrappers
around the internal ``_Client`` orchestrator::

    from swaplm import Client

    with Client() as client:
        response = client.chat(
            provider="groq",
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Hello!"}],
        )
"""

from __future__ import annotations

from typing import Any

from swaplm.models.messages import Message, Tool
from swaplm.models.response import ChatResponse
from swaplm.streaming.iterator import StreamResponse
from swaplm.transport.http import HTTPTransport


class Client:
    """Synchronous SwapLM client with connection lifecycle management.

    Use as a context manager to ensure HTTP connections are closed::

        with Client() as client:
            response = client.chat(provider="groq", model="...", messages=[...])
    """

    def __init__(
        self,
        *,
        timeout: float | None = None,
        retries: int = 0,
        max_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
    ) -> None:
        self._timeout = timeout
        self._retries = retries
        self._max_tokens = max_tokens
        self._temperature = temperature
        self._top_p = top_p
        self._transport = HTTPTransport()
        self._closed = False

    def chat(
        self,
        *,
        model: str,
        messages: list[dict[str, Any] | Message],
        provider: str | None = None,
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
        retries: int | None = None,
        extra_headers: dict[str, str] | None = None,
        provider_options: dict[str, Any] | None = None,
    ) -> ChatResponse | StreamResponse:
        """Send a synchronous chat completion request."""
        from swaplm._client import _Client
        from swaplm.models.request import ChatRequest

        normalised_messages = [
            Message.model_validate(m) if isinstance(m, dict) else m for m in messages
        ]

        normalised_tools = None
        if tools:
            normalised_tools = [Tool.model_validate(t) if isinstance(t, dict) else t for t in tools]

        request = ChatRequest(
            model=model,
            messages=normalised_messages,
            provider=provider,
            stream=stream,
            api_key=api_key,
            base_url=base_url,
            max_tokens=max_tokens or self._max_tokens,
            temperature=temperature if temperature is not None else self._temperature,
            top_p=top_p if top_p is not None else self._top_p,
            response_format=response_format,
            tools=normalised_tools,
            tool_choice=tool_choice,
            stop=stop,
            seed=seed,
            timeout=timeout or self._timeout,
            retries=retries if retries is not None else self._retries,
            extra_headers=extra_headers,
            provider_options=provider_options,
        )

        client = _Client(http_transport=self._transport)
        return client.chat(request)

    def close(self) -> None:
        """Close the underlying HTTP transport and release connections."""
        if not self._closed:
            self._transport.close()
            self._closed = True

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()


class AsyncClient:
    """Asynchronous SwapLM client with connection lifecycle management.

    Use as an async context manager to ensure HTTP connections are closed::

        async with AsyncClient() as client:
            response = await client.chat(provider="groq", model="...", messages=[...])
    """

    def __init__(
        self,
        *,
        timeout: float | None = None,
        retries: int = 0,
        max_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
    ) -> None:
        self._timeout = timeout
        self._retries = retries
        self._max_tokens = max_tokens
        self._temperature = temperature
        self._top_p = top_p
        self._transport = HTTPTransport()
        self._closed = False

    async def chat(
        self,
        *,
        model: str,
        messages: list[dict[str, Any] | Message],
        provider: str | None = None,
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
        retries: int | None = None,
        extra_headers: dict[str, str] | None = None,
        provider_options: dict[str, Any] | None = None,
    ) -> ChatResponse | StreamResponse:
        """Send an asynchronous chat completion request."""
        from swaplm._client import _Client
        from swaplm.models.request import ChatRequest

        normalised_messages = [
            Message.model_validate(m) if isinstance(m, dict) else m for m in messages
        ]

        normalised_tools = None
        if tools:
            normalised_tools = [Tool.model_validate(t) if isinstance(t, dict) else t for t in tools]

        request = ChatRequest(
            model=model,
            messages=normalised_messages,
            provider=provider,
            stream=stream,
            api_key=api_key,
            base_url=base_url,
            max_tokens=max_tokens or self._max_tokens,
            temperature=temperature if temperature is not None else self._temperature,
            top_p=top_p if top_p is not None else self._top_p,
            response_format=response_format,
            tools=normalised_tools,
            tool_choice=tool_choice,
            stop=stop,
            seed=seed,
            timeout=timeout or self._timeout,
            retries=retries if retries is not None else self._retries,
            extra_headers=extra_headers,
            provider_options=provider_options,
        )

        client = _Client(http_transport=self._transport)
        return await client.achat(request)

    async def close(self) -> None:
        """Close the underlying HTTP transport and release connections."""
        if not self._closed:
            await self._transport.aclose()
            self._closed = True

    async def __aenter__(self) -> AsyncClient:
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()
