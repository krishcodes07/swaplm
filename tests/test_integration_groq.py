"""Integration-style unit tests for the Groq provider via swaplm.chat()."""

import os
from typing import Any

import httpx
import pytest

from swaplm import (
    AuthenticationError,
    ChatResponse,
    InvalidModelError,
    RateLimitError,
    StreamResponse,
    Tool,
    chat,
)
from swaplm._client import _Client
from swaplm.transport.http import HTTPTransport


def _create_mock_client(handler: Any) -> _Client:
    """Helper to instantiate _Client with a mock httpx transport."""
    mock_httpx = httpx.Client(transport=httpx.MockTransport(handler))
    transport = HTTPTransport(client=mock_httpx)
    return _Client(http_transport=transport)


class TestGroqIntegration:
    def setup_method(self):
        os.environ.pop("GROQ_API_KEY", None)

    def teardown_method(self):
        os.environ.pop("GROQ_API_KEY", None)

    def test_successful_non_streaming_chat(self, monkeypatch):
        captured_request: dict[str, Any] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured_request["url"] = str(request.url)
            captured_request["headers"] = dict(request.headers)
            captured_request["body"] = request.read().decode("utf-8")

            return httpx.Response(
                200,
                json={
                    "id": "chatcmpl-123",
                    "object": "chat.completion",
                    "created": 1700000000,
                    "model": "llama-3.3-70b-versatile",
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": "Hello! I am Llama on Groq.",
                            },
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {
                        "prompt_tokens": 12,
                        "completion_tokens": 8,
                        "total_tokens": 20,
                    },
                },
            )

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        response = chat(
            model="groq/llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Hello"}],
            api_key="gsk_mock_key",
            temperature=0.7,
            max_tokens=100,
        )

        assert isinstance(response, ChatResponse)
        assert response.content == "Hello! I am Llama on Groq."
        assert response.provider == "groq"
        assert response.finish_reason == "stop"
        assert response.usage.total_tokens == 20

        assert captured_request["url"] == "https://api.groq.com/openai/v1/chat/completions"
        assert captured_request["headers"]["authorization"] == "Bearer gsk_mock_key"

    def test_streaming_chat(self, monkeypatch):
        sse_lines = [
            'data: {"id":"c1","model":"llama-3.3-70b-versatile","choices":[{"index":0,"delta":{"role":"assistant","content":"Hello"}}]}\n\n',
            'data: {"id":"c1","model":"llama-3.3-70b-versatile","choices":[{"index":0,"delta":{"content":" world!"},"finish_reason":"stop"}]}\n\n',
            "data: [DONE]\n\n",
        ]

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, content="".join(sse_lines).encode("utf-8"))

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        response = chat(
            model="groq/llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Hi"}],
            api_key="gsk_mock_key",
            stream=True,
        )

        assert isinstance(response, StreamResponse)
        chunks = list(response)
        assert len(chunks) == 2
        assert response.accumulated_content == "Hello world!"

    def test_auth_from_environment_variable(self, monkeypatch):
        os.environ["GROQ_API_KEY"] = "gsk_env_key"
        captured_auth: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured_auth.append(request.headers.get("authorization", ""))
            return httpx.Response(
                200,
                json={
                    "id": "c1",
                    "model": "llama-3.3-70b-versatile",
                    "choices": [{"index": 0, "message": {"role": "assistant", "content": "OK"}}],
                },
            )

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        chat(
            model="groq/llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Hi"}],
        )

        assert captured_auth[0] == "Bearer gsk_env_key"

    def test_missing_api_key_raises_auth_error(self):
        with pytest.raises(AuthenticationError, match="GROQ_API_KEY"):
            chat(
                model="groq/llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": "Hi"}],
            )

    def test_error_mapping_401_authentication_error(self, monkeypatch):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                401,
                json={"error": {"message": "Invalid API Key", "code": "invalid_api_key"}},
            )

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        with pytest.raises(AuthenticationError) as exc_info:
            chat(
                model="groq/llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": "Hi"}],
                api_key="invalid_key",
            )
        assert exc_info.value.provider == "groq"
        assert exc_info.value.status_code == 401

    def test_error_mapping_429_rate_limit(self, monkeypatch):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                429,
                json={"error": {"message": "Rate limit exceeded"}},
            )

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        with pytest.raises(RateLimitError) as exc_info:
            chat(
                model="groq/llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": "Hi"}],
                api_key="gsk_mock_key",
            )
        assert exc_info.value.provider == "groq"

    def test_error_mapping_invalid_model(self, monkeypatch):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                404,
                json={
                    "error": {"message": "Model non-existent not found", "code": "model_not_found"}
                },
            )

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        with pytest.raises(InvalidModelError):
            chat(
                model="groq/non-existent",
                messages=[{"role": "user", "content": "Hi"}],
                api_key="gsk_mock_key",
            )

    def test_tool_calling(self, monkeypatch):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={
                    "id": "c1",
                    "model": "llama-3.3-70b-versatile",
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [
                                    {
                                        "id": "call_abc123",
                                        "type": "function",
                                        "function": {
                                            "name": "get_weather",
                                            "arguments": '{"location": "San Francisco"}',
                                        },
                                    }
                                ],
                            },
                            "finish_reason": "tool_calls",
                        }
                    ],
                },
            )

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        weather_tool = Tool.model_validate(
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get weather for location",
                    "parameters": {
                        "type": "object",
                        "properties": {"location": {"type": "string"}},
                    },
                },
            }
        )

        response = chat(
            model="groq/llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "What is weather in SF?"}],
            api_key="gsk_mock_key",
            tools=[weather_tool],
            tool_choice="auto",
        )

        assert response.content is None
        assert response.tool_calls is not None
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].function.name == "get_weather"
        assert "San Francisco" in response.tool_calls[0].function.arguments

    def test_provider_options_forwarding(self, monkeypatch):
        captured_body: dict[str, Any] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            import json

            captured_body.update(json.loads(request.read().decode("utf-8")))
            return httpx.Response(
                200,
                json={
                    "id": "c1",
                    "model": "llama-3.3-70b-versatile",
                    "choices": [{"index": 0, "message": {"role": "assistant", "content": "OK"}}],
                },
            )

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        chat(
            model="groq/llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Hi"}],
            api_key="gsk_mock_key",
            provider_options={"top_k": 10, "reasoning_format": "parsed"},
        )

        assert captured_body.get("top_k") == 10
        assert captured_body.get("reasoning_format") == "parsed"
