"""Tests for Client and AsyncClient connection lifecycle management."""

import pytest

from swaplm.client import AsyncClient, Client


class TestClientLifecycle:
    def test_sync_client_context_manager(self):
        with Client() as client:
            assert client._closed is False
            assert client._transport is not None

        assert client._closed is True
        assert client._transport._client is None or client._transport._client.is_closed

    def test_sync_client_explicit_close(self):
        client = Client(timeout=30.0, retries=2)
        assert client._closed is False
        client.close()
        assert client._closed is True

        # Re-closing is safe idempotent
        client.close()
        assert client._closed is True

    @pytest.mark.asyncio
    async def test_async_client_context_manager(self):
        async with AsyncClient() as client:
            assert client._closed is False
            assert client._transport is not None

        assert client._closed is True

    @pytest.mark.asyncio
    async def test_async_client_explicit_close(self):
        client = AsyncClient(timeout=45.0)
        assert client._closed is False
        await client.close()
        assert client._closed is True

        # Idempotent re-close
        await client.close()
        assert client._closed is True
