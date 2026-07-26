"""Unit tests for transport retries and exponential backoff."""

import httpx
import pytest

from swaplm.transport.http import HTTPTransport


class TestTransportRetries:
    def test_sync_retry_on_500_success_after_retries(self):
        attempts = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                return httpx.Response(500, json={"error": "Internal Server Error"})
            return httpx.Response(200, json={"ok": True})

        mock_httpx = httpx.Client(transport=httpx.MockTransport(handler))
        transport = HTTPTransport(client=mock_httpx)

        status_code, data = transport.send(
            "POST",
            "https://api.groq.com/v1/test",
            retries=3,
            retry_delay=0.01,
        )

        assert attempts == 3
        assert status_code == 200
        assert data == {"ok": True}

    def test_sync_no_retry_on_400_client_error(self):
        attempts = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal attempts
            attempts += 1
            return httpx.Response(400, json={"error": "Bad Request"})

        mock_httpx = httpx.Client(transport=httpx.MockTransport(handler))
        transport = HTTPTransport(client=mock_httpx)

        status_code, _data = transport.send(
            "POST",
            "https://api.groq.com/v1/test",
            retries=3,
            retry_delay=0.01,
        )

        assert attempts == 1
        assert status_code == 400

    @pytest.mark.asyncio
    async def test_async_retry_on_503(self):
        attempts = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal attempts
            attempts += 1
            if attempts < 2:
                return httpx.Response(503, json={"error": "Service Unavailable"})
            return httpx.Response(200, json={"ok": True})

        mock_httpx = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        transport = HTTPTransport(async_client=mock_httpx)

        status_code, _data = await transport.asend(
            "POST",
            "https://api.groq.com/v1/test",
            retries=2,
            retry_delay=0.01,
        )

        assert attempts == 2
        assert status_code == 200
