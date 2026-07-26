"""Integration-style unit tests for the Anthropic provider via swaplm.chat()."""

import os
from typing import Any

import httpx
import pytest

from swaplm import (
    AuthenticationError,
    ChatResponse,
    InvalidModelError,
    StreamResponse,
    Tool,
    chat,
)
from swaplm._client import _Client
from swaplm.transport.http import HTTPTransport


def _create_mock_client(handler: Any) -> _Client:
    mock_httpx = httpx.Client(transport=httpx.MockTransport(handler))
    transport = HTTPTransport(client=mock_httpx)
    return _Client(http_transport=transport)


class TestAnthropicIntegration:
    def setup_method(self):
        os.environ.pop("ANTHROPIC_API_KEY", None)

    def teardown_method(self):
        os.environ.pop("ANTHROPIC_API_KEY", None)

    def test_successful_non_streaming_chat(self, monkeypatch):
        captured_request: dict[str, Any] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            import json

            captured_request["url"] = str(request.url)
            captured_request["headers"] = dict(request.headers)
            captured_request["body"] = json.loads(request.read().decode("utf-8"))

            return httpx.Response(
                200,
                json={
                    "id": "msg_123",
                    "type": "message",
                    "role": "assistant",
                    "model": "claude-3-5-sonnet-20241022",
                    "content": [{"type": "text", "text": "Hello from Claude!"}],
                    "stop_reason": "end_turn",
                    "usage": {"input_tokens": 10, "output_tokens": 15},
                },
            )

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        response = chat(
            model="anthropic/claude-3-5-sonnet-20241022",
            messages=[
                {"role": "system", "content": "Be concise."},
                {"role": "user", "content": "Hi"},
            ],
            api_key="sk-ant-mock_key",
        )

        assert isinstance(response, ChatResponse)
        assert response.content == "Hello from Claude!"
        assert response.provider == "anthropic"
        assert response.finish_reason == "stop"
        assert response.usage.prompt_tokens == 10
        assert response.usage.completion_tokens == 15
        assert response.usage.total_tokens == 25

        assert captured_request["url"] == "https://api.anthropic.com/v1/messages"
        assert captured_request["headers"]["x-api-key"] == "sk-ant-mock_key"
        assert captured_request["headers"]["anthropic-version"] == "2023-06-01"
        assert captured_request["body"]["system"] == "Be concise."

    def test_streaming_chat(self, monkeypatch):
        sse_lines = [
            'data: {"type":"message_start","message":{"id":"msg_1","model":"claude-3-5-sonnet-20241022"}}\n\n',
            'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"Hello"}}\n\n',
            'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" world!"}}\n\n',
            'data: {"type":"message_delta","delta":{"stop_reason":"end_turn"},"usage":{"output_tokens":5}}\n\n',
        ]

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, content="".join(sse_lines).encode("utf-8"))

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        response = chat(
            model="anthropic/claude-3-5-sonnet-20241022",
            messages=[{"role": "user", "content": "Hi"}],
            api_key="sk-ant-mock_key",
            stream=True,
        )

        assert isinstance(response, StreamResponse)
        chunks = list(response)
        assert len(chunks) == 4
        assert response.accumulated_content == "Hello world!"

    def test_auth_from_env_var(self, monkeypatch):
        os.environ["ANTHROPIC_API_KEY"] = "sk-ant-env-key"
        captured_auth: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured_auth.append(request.headers.get("x-api-key", ""))
            return httpx.Response(
                200,
                json={
                    "id": "msg_1",
                    "content": [{"type": "text", "text": "OK"}],
                    "usage": {"input_tokens": 5, "output_tokens": 2},
                },
            )

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        chat(
            model="anthropic/claude-3-5-sonnet-20241022",
            messages=[{"role": "user", "content": "Hi"}],
        )

        assert captured_auth[0] == "sk-ant-env-key"

    def test_tool_calling(self, monkeypatch):
        captured_tools: list[dict] = []

        def handler(request: httpx.Request) -> httpx.Response:
            import json

            body = json.loads(request.read().decode("utf-8"))
            captured_tools.extend(body.get("tools", []))
            return httpx.Response(
                200,
                json={
                    "id": "msg_tc",
                    "type": "message",
                    "role": "assistant",
                    "model": "claude-3-5-sonnet-20241022",
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "toolu_123",
                            "name": "lookup_stock",
                            "input": {"ticker": "AAPL"},
                        }
                    ],
                    "stop_reason": "tool_use",
                    "usage": {"input_tokens": 15, "output_tokens": 10},
                },
            )

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        stock_tool = Tool.model_validate(
            {
                "type": "function",
                "function": {
                    "name": "lookup_stock",
                    "description": "Lookup stock price",
                    "parameters": {
                        "type": "object",
                        "properties": {"ticker": {"type": "string"}},
                    },
                },
            }
        )

        response = chat(
            model="anthropic/claude-3-5-sonnet-20241022",
            messages=[{"role": "user", "content": "Stock price of AAPL?"}],
            api_key="sk-ant-mock_key",
            tools=[stock_tool],
        )

        assert response.content is None
        assert response.tool_calls is not None
        assert response.tool_calls[0].id == "toolu_123"
        assert response.tool_calls[0].function.name == "lookup_stock"
        assert "AAPL" in response.tool_calls[0].function.arguments
        assert captured_tools[0]["input_schema"]["properties"]["ticker"]["type"] == "string"

    def test_error_mapping_401(self, monkeypatch):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                401,
                json={"error": {"type": "authentication_error", "message": "Invalid API Key"}},
            )

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        with pytest.raises(AuthenticationError) as exc_info:
            chat(
                model="anthropic/claude-3-5-sonnet-20241022",
                messages=[{"role": "user", "content": "Hi"}],
                api_key="bad_key",
            )
        assert exc_info.value.provider == "anthropic"

    def test_error_mapping_404_invalid_model(self, monkeypatch):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                404,
                json={"error": {"type": "not_found_error", "message": "Model not found"}},
            )

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        with pytest.raises(InvalidModelError):
            chat(
                model="anthropic/claude-nonexistent",
                messages=[{"role": "user", "content": "Hi"}],
                api_key="sk-ant-mock_key",
            )
