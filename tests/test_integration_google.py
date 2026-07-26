"""Integration-style unit tests for the Google Gemini provider via swaplm.chat()."""

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


class TestGoogleIntegration:
    def setup_method(self):
        os.environ.pop("GEMINI_API_KEY", None)

    def teardown_method(self):
        os.environ.pop("GEMINI_API_KEY", None)

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
                    "candidates": [
                        {
                            "content": {
                                "parts": [{"text": "Hello from Gemini!"}],
                                "role": "model",
                            },
                            "finishReason": "STOP",
                            "index": 0,
                        }
                    ],
                    "usageMetadata": {
                        "promptTokenCount": 8,
                        "candidatesTokenCount": 12,
                        "totalTokenCount": 20,
                    },
                    "modelVersion": "gemini-2.5-pro",
                },
            )

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        response = chat(
            model="google/gemini-2.5-pro",
            messages=[
                {"role": "system", "content": "You are helpful."},
                {"role": "user", "content": "Hi"},
            ],
            api_key="AIzaSyMockKey",
            temperature=0.7,
        )

        assert isinstance(response, ChatResponse)
        assert response.content == "Hello from Gemini!"
        assert response.provider == "google"
        assert response.finish_reason == "stop"
        assert response.usage.prompt_tokens == 8
        assert response.usage.completion_tokens == 12
        assert response.usage.total_tokens == 20

        assert "models/gemini-2.5-pro:generateContent" in captured_request["url"]
        assert captured_request["headers"]["x-goog-api-key"] == "AIzaSyMockKey"
        assert (
            captured_request["body"]["systemInstruction"]["parts"][0]["text"] == "You are helpful."
        )

    def test_streaming_chat(self, monkeypatch):
        sse_lines = [
            'data: {"candidates":[{"content":{"parts":[{"text":"Hello"}]}}],"modelVersion":"gemini-2.5-pro"}\n\n',
            'data: {"candidates":[{"content":{"parts":[{"text":" world!"}],"role":"model"},"finishReason":"STOP"}]}\n\n',
        ]

        captured_request: dict[str, Any] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured_request["url"] = str(request.url)
            return httpx.Response(200, content="".join(sse_lines).encode("utf-8"))

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        response = chat(
            model="google/gemini-2.5-pro",
            messages=[{"role": "user", "content": "Hi"}],
            api_key="AIzaSyMockKey",
            stream=True,
        )

        assert isinstance(response, StreamResponse)
        chunks = list(response)
        assert len(chunks) == 2
        assert response.accumulated_content == "Hello world!"
        assert "models/gemini-2.5-pro:streamGenerateContent?alt=sse" in captured_request["url"]

    def test_auth_from_env_var(self, monkeypatch):
        os.environ["GEMINI_API_KEY"] = "AIzaSyEnvKey"
        captured_auth: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured_auth.append(request.headers.get("x-goog-api-key", ""))
            return httpx.Response(
                200,
                json={
                    "candidates": [
                        {
                            "content": {"parts": [{"text": "OK"}], "role": "model"},
                            "finishReason": "STOP",
                        }
                    ]
                },
            )

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        chat(
            model="google/gemini-2.5-pro",
            messages=[{"role": "user", "content": "Hi"}],
        )

        assert captured_auth[0] == "AIzaSyEnvKey"

    def test_tool_calling(self, monkeypatch):
        captured_body: dict[str, Any] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            import json

            captured_body.update(json.loads(request.read().decode("utf-8")))
            return httpx.Response(
                200,
                json={
                    "candidates": [
                        {
                            "content": {
                                "parts": [
                                    {
                                        "functionCall": {
                                            "name": "calculate_tax",
                                            "args": {"amount": 100},
                                        }
                                    }
                                ],
                                "role": "model",
                            },
                            "finishReason": "STOP",
                        }
                    ]
                },
            )

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        tax_tool = Tool.model_validate(
            {
                "type": "function",
                "function": {
                    "name": "calculate_tax",
                    "description": "Calculate tax for amount",
                    "parameters": {
                        "type": "object",
                        "properties": {"amount": {"type": "number"}},
                    },
                },
            }
        )

        response = chat(
            model="google/gemini-2.5-pro",
            messages=[{"role": "user", "content": "Tax for 100?"}],
            api_key="AIzaSyMockKey",
            tools=[tax_tool],
        )

        assert response.content is None
        assert response.tool_calls is not None
        assert response.tool_calls[0].function.name == "calculate_tax"
        assert "100" in response.tool_calls[0].function.arguments
        assert captured_body["tools"][0]["functionDeclarations"][0]["name"] == "calculate_tax"

    def test_error_mapping_403_unauthenticated(self, monkeypatch):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                403,
                json={
                    "error": {
                        "code": 403,
                        "message": "API key not valid",
                        "status": "UNAUTHENTICATED",
                    }
                },
            )

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        with pytest.raises(AuthenticationError) as exc_info:
            chat(
                model="google/gemini-2.5-pro",
                messages=[{"role": "user", "content": "Hi"}],
                api_key="invalid_key",
            )
        assert exc_info.value.provider == "google"

    def test_error_mapping_404_not_found(self, monkeypatch):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                404,
                json={
                    "error": {
                        "code": 404,
                        "message": "models/gemini-nonexistent is not found",
                        "status": "NOT_FOUND",
                    }
                },
            )

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        with pytest.raises(InvalidModelError):
            chat(
                model="google/gemini-nonexistent",
                messages=[{"role": "user", "content": "Hi"}],
                api_key="AIzaSyMockKey",
            )
