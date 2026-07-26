"""Tests for the HTTP transport layer."""

import httpx
import pytest

from swaplm.exceptions import ProviderError, TimeoutError
from swaplm.transport.http import HTTPTransport


class TestHTTPTransport:
    def test_post_success(self):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url == "https://api.example.com/test"
            assert request.headers["Authorization"] == "Bearer secret"
            return httpx.Response(200, json={"status": "ok"})

        mock_client = httpx.Client(transport=httpx.MockTransport(handler))
        transport = HTTPTransport(client=mock_client)

        status, data = transport.post(
            "https://api.example.com/test",
            headers={"Authorization": "Bearer secret"},
            body={"key": "val"},
        )
        assert status == 200
        assert data == {"status": "ok"}

    def test_post_non_json_error(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(500, text="Internal Error")

        mock_client = httpx.Client(transport=httpx.MockTransport(handler))
        transport = HTTPTransport(client=mock_client)

        status, data = transport.post(
            "https://api.example.com/test",
            headers={},
            body={},
        )
        assert status == 500
        assert data == {"message": "Internal Error"}

    def test_post_timeout(self):
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.TimeoutException("Timed out")

        mock_client = httpx.Client(transport=httpx.MockTransport(handler))
        transport = HTTPTransport(client=mock_client)

        with pytest.raises(TimeoutError, match="timed out"):
            transport.post("https://api.example.com/test", headers={}, body={})

    def test_post_network_error(self):
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.NetworkError("Connection refused")

        mock_client = httpx.Client(transport=httpx.MockTransport(handler))
        transport = HTTPTransport(client=mock_client)

        with pytest.raises(ProviderError, match="Network error"):
            transport.post("https://api.example.com/test", headers={}, body={})

    def test_post_stream_sse_parsing(self):
        sse_lines = [
            'data: {"choices": [{"delta": {"content": "Hello"}}]}\n\n',
            'data: {"choices": [{"delta": {"content": " world"}}]}\n\n',
            "data: [DONE]\n\n",
        ]

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, content="".join(sse_lines).encode("utf-8"))

        mock_client = httpx.Client(transport=httpx.MockTransport(handler))
        transport = HTTPTransport(client=mock_client)

        chunks = list(transport.post_stream("https://api.example.com/stream", headers={}, body={}))
        assert len(chunks) == 2
        assert chunks[0]["choices"][0]["delta"]["content"] == "Hello"
        assert chunks[1]["choices"][0]["delta"]["content"] == " world"

    def test_post_stream_error_status(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(401, json={"error": {"message": "Unauthorized"}})

        mock_client = httpx.Client(transport=httpx.MockTransport(handler))
        transport = HTTPTransport(client=mock_client)

        chunks = list(transport.post_stream("https://api.example.com/stream", headers={}, body={}))
        assert len(chunks) == 1
        assert chunks[0]["_http_error"] is True
        assert chunks[0]["status_code"] == 401
        assert chunks[0]["data"]["error"]["message"] == "Unauthorized"
