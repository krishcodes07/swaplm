"""Tests for Phase 10: explicit provider parameter, stream convenience properties, and response helpers."""

from typing import Any

import httpx
import pytest

from swaplm import (
    ChatResponse,
    StreamResponse,
    achat,
    chat,
)
from swaplm._client import _Client
from swaplm.models.request import ChatRequest
from swaplm.models.response import Choice, Message
from swaplm.models.stream import ChoiceDelta, ChunkChoice, StreamChunk
from swaplm.transport.http import HTTPTransport


def _create_mock_client(handler: Any) -> _Client:
    mock_httpx = httpx.Client(transport=httpx.MockTransport(handler))
    mock_async_httpx = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    transport = HTTPTransport(client=mock_httpx, async_client=mock_async_httpx)
    return _Client(http_transport=transport)


def _ok_handler(request: httpx.Request) -> httpx.Response:
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
                    "message": {"role": "assistant", "content": "Hello from Groq!"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10},
        },
    )


# ── 1. Explicit provider parameter ────────────────────────────────────────


class TestExplicitProvider:
    def test_explicit_provider_sync(self, monkeypatch):
        def handler(request: httpx.Request) -> httpx.Response:
            return _ok_handler(request)

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        response = chat(
            provider="groq",
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Hello"}],
            api_key="gsk_mock",
        )

        assert isinstance(response, ChatResponse)
        assert response.content == "Hello from Groq!"
        assert response.provider == "groq"

    def test_explicit_provider_backward_compat(self, monkeypatch):
        """Both APIs produce identical results."""
        captured_bodies: list[dict[str, Any]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            import json

            captured_bodies.append(json.loads(request.read().decode("utf-8")))
            return _ok_handler(request)

        # API 1: combined model string
        client1 = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client1)
        chat(
            model="groq/llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Hi"}],
            api_key="gsk_mock",
        )

        # API 2: explicit provider
        client2 = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client2)
        chat(
            provider="groq",
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Hi"}],
            api_key="gsk_mock",
        )

        assert len(captured_bodies) == 2
        # Both should send the same model ID in the body
        assert captured_bodies[0]["model"] == captured_bodies[1]["model"]

    def test_explicit_provider_with_nested_model_id(self, monkeypatch):
        """Provider IDs with slashes in the model (e.g. nvidia)."""

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={
                    "id": "c1",
                    "model": "deepseek-ai/deepseek-v4-flash",
                    "choices": [
                        {
                            "index": 0,
                            "message": {"role": "assistant", "content": "Nested model works!"},
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10},
                },
            )

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        response = chat(
            provider="nvidia",
            model="deepseek-ai/deepseek-v4-flash",
            messages=[{"role": "user", "content": "Hello"}],
            api_key="nv_mock",
        )

        assert response.content == "Nested model works!"
        assert response.provider == "nvidia"

    @pytest.mark.asyncio
    async def test_explicit_provider_async(self, monkeypatch):
        def handler(request: httpx.Request) -> httpx.Response:
            return _ok_handler(request)

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        response = await achat(
            provider="groq",
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Hello"}],
            api_key="gsk_mock",
        )

        assert isinstance(response, ChatResponse)
        assert response.content == "Hello from Groq!"
        assert response.provider == "groq"


# ── 2. ChatRequest explicit provider fields ───────────────────────────────


class TestChatRequestProvider:
    def test_provider_id_from_explicit_provider(self):
        req = ChatRequest(
            model="llama-3.3-70b-versatile",
            messages=[Message(role="user", content="Hi")],
            provider="groq",
        )
        assert req.provider_id == "groq"
        assert req.model_id == "llama-3.3-70b-versatile"

    def test_provider_id_from_model_string(self):
        req = ChatRequest(
            model="groq/llama-3.3-70b-versatile",
            messages=[Message(role="user", content="Hi")],
        )
        assert req.provider_id == "groq"
        assert req.model_id == "llama-3.3-70b-versatile"

    def test_explicit_provider_takes_precedence(self):
        req = ChatRequest(
            model="some-model",
            messages=[Message(role="user", content="Hi")],
            provider="groq",
        )
        assert req.provider_id == "groq"
        assert req.model_id == "some-model"


# ── 3. Router explicit resolution ─────────────────────────────────────────


class TestRouterExplicit:
    def test_resolve_explicit(self):
        from swaplm.models.model import ModelInfo
        from swaplm.models.provider import ProviderInfo
        from swaplm.providers.base import BaseProvider
        from swaplm.providers.registry import ProviderRegistry
        from swaplm.router.router import Router

        class _FakeProvider(BaseProvider):
            info = ProviderInfo(
                id="fake",
                name="Fake",
                protocol="openai",
                base_url="https://api.fake.com/v1",
                env_var="FAKE_API_KEY",
            )

            def __init__(self, models=None):
                self._models = models or [ModelInfo(id="my-model")]

        registry = ProviderRegistry()
        registry._discovered = True
        provider = _FakeProvider()
        registry.register(provider)

        router = Router(provider_registry=registry)
        resolved_provider, model_id = router.resolve_explicit("fake", "my-model")
        assert resolved_provider is provider
        assert model_id == "my-model"


# ── 4. StreamChunk convenience properties ─────────────────────────────────


class TestStreamChunkConvenience:
    def test_content(self):
        chunk = StreamChunk(choices=[ChunkChoice(delta=ChoiceDelta(content="Hello"))])
        assert chunk.content == "Hello"

    def test_content_none(self):
        chunk = StreamChunk(choices=None)
        assert chunk.content is None

    def test_reasoning(self):
        chunk = StreamChunk(choices=[ChunkChoice(delta=ChoiceDelta(reasoning="Thinking..."))])
        assert chunk.reasoning == "Thinking..."

    def test_reasoning_none(self):
        chunk = StreamChunk(choices=[ChunkChoice(delta=ChoiceDelta(content="Hello"))])
        assert chunk.reasoning is None

    def test_finish_reason(self):
        chunk = StreamChunk(choices=[ChunkChoice(delta=ChoiceDelta(), finish_reason="stop")])
        assert chunk.finish_reason == "stop"

    def test_finish_reason_none(self):
        chunk = StreamChunk(choices=[ChunkChoice(delta=ChoiceDelta())])
        assert chunk.finish_reason is None

    def test_tool_calls(self):
        from swaplm.models.messages import FunctionCallDelta, ToolCallDelta

        tc = ToolCallDelta(
            index=0,
            id="call_123",
            type="function",
            function=FunctionCallDelta(name="get_weather", arguments='{"city":"NYC"}'),
        )
        chunk = StreamChunk(choices=[ChunkChoice(delta=ChoiceDelta(tool_calls=[tc]))])
        assert chunk.tool_calls is not None
        assert len(chunk.tool_calls) == 1
        assert chunk.tool_calls[0].id == "call_123"


# ── 5. StreamResponse.text alias ──────────────────────────────────────────


class TestStreamResponseText:
    def test_text_alias(self, monkeypatch):
        sse_lines = [
            'data: {"choices": [{"index": 0, "delta": {"content": "Hello "}}]}\n\n',
            'data: {"choices": [{"index": 0, "delta": {"content": "world"}}]}\n\n',
            "data: [DONE]\n\n",
        ]

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, content="".join(sse_lines).encode("utf-8"))

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        stream = chat(
            model="groq/llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Hi"}],
            api_key="gsk_mock",
            stream=True,
        )

        assert isinstance(stream, StreamResponse)
        chunks = list(stream)
        assert len(chunks) == 2

        # text and accumulated_content should be identical
        assert stream.text == stream.accumulated_content
        assert stream.text == "Hello world"

    def test_text_alias_async(self, monkeypatch):
        sse_lines = [
            'data: {"choices": [{"index": 0, "delta": {"content": "Async "}}]}\n\n',
            'data: {"choices": [{"index": 0, "delta": {"content": "text"}}]}\n\n',
            "data: [DONE]\n\n",
        ]

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, content="".join(sse_lines).encode("utf-8"))

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        async def run():
            stream = await achat(
                model="groq/llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": "Hi"}],
                api_key="gsk_mock",
                stream=True,
            )
            chunks = []
            async for chunk in stream:
                chunks.append(chunk)
            return stream

        import asyncio

        stream = asyncio.run(run())
        assert stream.text == stream.accumulated_content
        assert stream.text == "Async text"


# ── 6. Response convenience properties ────────────────────────────────────


class TestResponseConvenience:
    def test_content_shortcut(self):
        response = ChatResponse(
            id="c1",
            choices=[Choice(index=0, message=Message(role="assistant", content="Hello!"))],
            model="test",
            provider="test",
        )
        assert response.content == "Hello!"

    def test_finish_reason_shortcut(self):
        response = ChatResponse(
            id="c1",
            choices=[
                Choice(
                    index=0,
                    message=Message(role="assistant", content="Hi"),
                    finish_reason="stop",
                )
            ],
            model="test",
            provider="test",
        )
        assert response.finish_reason == "stop"

    def test_tool_calls_shortcut(self):
        from swaplm.models.messages import FunctionCall, ToolCall

        tc = ToolCall(
            id="call_1",
            type="function",
            function=FunctionCall(name="fn", arguments="{}"),
        )
        response = ChatResponse(
            id="c1",
            choices=[
                Choice(
                    index=0,
                    message=Message(role="assistant", content=None, tool_calls=[tc]),
                )
            ],
            model="test",
            provider="test",
        )
        assert response.tool_calls is not None
        assert len(response.tool_calls) == 1

    def test_reasoning_shortcut(self):
        response = ChatResponse(
            id="c1",
            choices=[
                Choice(
                    index=0,
                    message=Message(
                        role="assistant", content="Answer", refusal="I cannot help with that"
                    ),
                )
            ],
            model="test",
            provider="test",
        )
        assert response.reasoning == "I cannot help with that"

    def test_reasoning_none(self):
        response = ChatResponse(
            id="c1",
            choices=[
                Choice(
                    index=0,
                    message=Message(role="assistant", content="Hello"),
                )
            ],
            model="test",
            provider="test",
        )
        assert response.reasoning is None

    def test_empty_choices(self):
        response = ChatResponse(
            id="c1",
            choices=[],
            model="test",
            provider="test",
        )
        assert response.content is None
        assert response.tool_calls is None
        assert response.finish_reason is None
        assert response.reasoning is None


# ── 7. StreamChunk in live streaming ──────────────────────────────────────


class TestStreamChunkLive:
    def test_chunk_content_during_streaming(self, monkeypatch):
        sse_lines = [
            'data: {"choices": [{"index": 0, "delta": {"role": "assistant", "content": "Hi"}}]}\n\n',
            'data: {"choices": [{"index": 0, "delta": {"content": " there"}, "finish_reason": "stop"}]}\n\n',
            "data: [DONE]\n\n",
        ]

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, content="".join(sse_lines).encode("utf-8"))

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        stream = chat(
            model="groq/llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Hi"}],
            api_key="gsk_mock",
            stream=True,
        )

        contents = []
        finish_reasons = []
        for chunk in stream:
            # Use convenience properties
            if chunk.content:
                contents.append(chunk.content)
            if chunk.finish_reason:
                finish_reasons.append(chunk.finish_reason)

        assert contents == ["Hi", " there"]
        assert finish_reasons == ["stop"]
