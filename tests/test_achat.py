"""Unit tests for asynchronous chat execution (achat)."""

from typing import Any

import httpx
import pytest

from swaplm import ChatResponse, StreamResponse, achat
from swaplm._client import _Client
from swaplm.transport.http import HTTPTransport


def _create_mock_client(handler: Any) -> _Client:
    mock_httpx = httpx.Client(transport=httpx.MockTransport(handler))
    mock_async_httpx = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    transport = HTTPTransport(client=mock_httpx, async_client=mock_async_httpx)
    return _Client(http_transport=transport)


@pytest.mark.asyncio
async def test_achat_non_streaming(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "id": "chatcmpl-123",
                "object": "chat.completion",
                "created": 123456,
                "model": "llama-3.3-70b-versatile",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "Async response!"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10},
            },
        )

    client = _create_mock_client(handler)
    monkeypatch.setattr("swaplm._client._default_client", client)

    response = await achat(
        model="groq/llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Hello"}],
        api_key="gsk_mock",
    )

    assert isinstance(response, ChatResponse)
    assert response.content == "Async response!"
    assert response.provider == "groq"


@pytest.mark.asyncio
async def test_achat_streaming(monkeypatch):
    sse_lines = [
        'data: {"choices": [{"index": 0, "delta": {"role": "assistant", "content": "Async "}}]}\n\n',
        'data: {"choices": [{"index": 0, "delta": {"content": "stream!"}}]}\n\n',
        "data: [DONE]\n\n",
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content="".join(sse_lines).encode("utf-8"))

    client = _create_mock_client(handler)
    monkeypatch.setattr("swaplm._client._default_client", client)

    stream = await achat(
        model="groq/llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Hello"}],
        api_key="gsk_mock",
        stream=True,
    )

    assert isinstance(stream, StreamResponse)
    chunks = []
    async for chunk in stream:
        chunks.append(chunk)

    assert len(chunks) == 2
    assert stream.accumulated_content == "Async stream!"
