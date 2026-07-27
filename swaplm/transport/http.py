"""HTTP transport layer using httpx with sync/async, connection pooling, and retries."""

from __future__ import annotations

import asyncio
import json as _json
import time
from collections.abc import AsyncIterator, Iterator
from typing import Any

import httpx

from swaplm.exceptions import ProviderError, TimeoutError
from swaplm.hooks import aemit, emit
from swaplm.transport.base import BaseTransport


class HTTPTransport(BaseTransport):
    """HTTP client wrapper handling sync/async non-streaming and streaming requests."""

    def __init__(
        self,
        *,
        default_timeout: float = 60.0,
        client: httpx.Client | None = None,
        async_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.default_timeout = default_timeout
        self._client = client
        self._async_client = async_client

    def _get_client(self) -> httpx.Client:
        if self._client is None or self._client.is_closed:
            self._client = httpx.Client(
                timeout=httpx.Timeout(self.default_timeout),
                follow_redirects=True,
            )
        return self._client

    def _get_async_client(self) -> httpx.AsyncClient:
        if self._async_client is None or self._async_client.is_closed:
            self._async_client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.default_timeout),
                follow_redirects=True,
            )
        return self._async_client

    def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        body: dict[str, Any],
        timeout: float | None = None,
        retries: int = 0,
        retry_delay: float = 0.5,
    ) -> tuple[int, dict[str, Any]]:
        """Backward compatible helper forwarding to send()."""
        return self.send(
            "POST",
            url,
            headers=headers,
            json=body,
            timeout=timeout,
            retries=retries,
            retry_delay=retry_delay,
        )

    def post_stream(
        self,
        url: str,
        *,
        headers: dict[str, str],
        body: dict[str, Any],
        timeout: float | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Backward compatible helper forwarding to send_stream()."""
        return self.send_stream(
            "POST",
            url,
            headers=headers,
            json=body,
            timeout=timeout,
        )

    # ── BaseTransport Synchronous Implementation ───────────────────────────

    def send(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
        retries: int = 0,
        retry_delay: float = 0.5,
    ) -> tuple[int, dict[str, Any]]:
        client = self._get_client()
        req_timeout = timeout if timeout is not None else self.default_timeout
        attempt = 0
        current_delay = retry_delay

        while True:
            attempt += 1
            try:
                response = client.request(
                    method,
                    url,
                    headers=headers,
                    json=json,
                    timeout=req_timeout,
                )
                status_code = response.status_code

                if (status_code >= 500 or status_code == 429) and attempt <= retries:
                    emit("before_retry", url, status_code, attempt)
                    time.sleep(current_delay)
                    emit("after_retry", url, status_code, attempt)
                    current_delay *= 2.0
                    continue

                try:
                    data = response.json()
                except Exception:
                    data = {"message": response.text or "Empty or non-JSON response"}

                return status_code, data

            except (httpx.TimeoutException, httpx.RequestError) as exc:
                if attempt <= retries:
                    emit("before_retry", url, exc, attempt)
                    time.sleep(current_delay)
                    emit("after_retry", url, exc, attempt)
                    current_delay *= 2.0
                    continue

                if isinstance(exc, httpx.TimeoutException):
                    raise TimeoutError(f"Request to {url} timed out after {req_timeout}s") from exc
                raise ProviderError(f"Network error requesting {url}: {exc}") from exc

    # ── BaseTransport Asynchronous Implementation ──────────────────────────

    async def asend(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
        retries: int = 0,
        retry_delay: float = 0.5,
    ) -> tuple[int, dict[str, Any]]:
        async_client = self._get_async_client()
        req_timeout = timeout if timeout is not None else self.default_timeout
        attempt = 0
        current_delay = retry_delay

        while True:
            attempt += 1
            try:
                response = await async_client.request(
                    method,
                    url,
                    headers=headers,
                    json=json,
                    timeout=req_timeout,
                )
                status_code = response.status_code

                if (status_code >= 500 or status_code == 429) and attempt <= retries:
                    await aemit("before_retry", url, status_code, attempt)
                    await asyncio.sleep(current_delay)
                    await aemit("after_retry", url, status_code, attempt)
                    current_delay *= 2.0
                    continue

                try:
                    data = response.json()
                except Exception:
                    data = {"message": response.text or "Empty or non-JSON response"}

                return status_code, data

            except (httpx.TimeoutException, httpx.RequestError) as exc:
                if attempt <= retries:
                    await aemit("before_retry", url, exc, attempt)
                    await asyncio.sleep(current_delay)
                    await aemit("after_retry", url, exc, attempt)
                    current_delay *= 2.0
                    continue

                if isinstance(exc, httpx.TimeoutException):
                    raise TimeoutError(f"Request to {url} timed out after {req_timeout}s") from exc
                raise ProviderError(f"Network error requesting {url}: {exc}") from exc

    # ── Streaming Implementation ──────────────────────────────────────────

    def send_stream(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
        retries: int = 0,
        retry_delay: float = 0.5,
    ) -> Iterator[dict[str, Any]]:
        client = self._get_client()
        req_timeout = timeout if timeout is not None else self.default_timeout
        attempt = 0
        current_delay = retry_delay

        while True:
            attempt += 1
            try:
                with client.stream(
                    method,
                    url,
                    headers=headers,
                    json=json,
                    timeout=req_timeout,
                ) as response:
                    if response.status_code >= 400:
                        # Retry on server errors before any data is yielded
                        if (
                            response.status_code >= 500 or response.status_code == 429
                        ) and attempt <= retries:
                            emit("before_retry", url, response.status_code, attempt)
                            time.sleep(current_delay)
                            emit("after_retry", url, response.status_code, attempt)
                            current_delay *= 2.0
                            continue

                        try:
                            data = response.json()
                        except Exception:
                            data = {"message": response.text or "Error response"}
                        yield {
                            "_http_error": True,
                            "status_code": response.status_code,
                            "data": data,
                        }
                        return

                    for line in response.iter_lines():
                        line = line.strip()
                        if not line or line.startswith(":") or line.startswith("event:"):
                            continue
                        if line.startswith("data:"):
                            payload = line[5:].strip()
                            if payload == "[DONE]":
                                break
                            if payload:
                                try:
                                    yield _json.loads(payload)
                                except _json.JSONDecodeError:
                                    continue

                return  # Stream completed successfully

            except (httpx.TimeoutException, httpx.RequestError) as exc:
                if attempt <= retries:
                    emit("before_retry", url, exc, attempt)
                    time.sleep(current_delay)
                    emit("after_retry", url, exc, attempt)
                    current_delay *= 2.0
                    continue

                if isinstance(exc, httpx.TimeoutException):
                    raise TimeoutError(f"Streaming request to {url} timed out") from exc
                raise ProviderError(f"Network error during stream to {url}: {exc}") from exc

    async def asend_stream(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
        retries: int = 0,
        retry_delay: float = 0.5,
    ) -> AsyncIterator[dict[str, Any]]:
        async_client = self._get_async_client()
        req_timeout = timeout if timeout is not None else self.default_timeout
        attempt = 0
        current_delay = retry_delay

        while True:
            attempt += 1
            try:
                async with async_client.stream(
                    method,
                    url,
                    headers=headers,
                    json=json,
                    timeout=req_timeout,
                ) as response:
                    if response.status_code >= 400:
                        # Retry on server errors before any data is yielded
                        if (
                            response.status_code >= 500 or response.status_code == 429
                        ) and attempt <= retries:
                            await aemit("before_retry", url, response.status_code, attempt)
                            await asyncio.sleep(current_delay)
                            await aemit("after_retry", url, response.status_code, attempt)
                            current_delay *= 2.0
                            continue

                        try:
                            data = response.json()
                        except Exception:
                            data = {"message": response.text or "Error response"}
                        yield {
                            "_http_error": True,
                            "status_code": response.status_code,
                            "data": data,
                        }
                        return

                    async for line in response.aiter_lines():
                        line = line.strip()
                        if not line or line.startswith(":") or line.startswith("event:"):
                            continue
                        if line.startswith("data:"):
                            payload = line[5:].strip()
                            if payload == "[DONE]":
                                break
                            if payload:
                                try:
                                    yield _json.loads(payload)
                                except _json.JSONDecodeError:
                                    continue

                return  # Stream completed successfully

            except (httpx.TimeoutException, httpx.RequestError) as exc:
                if attempt <= retries:
                    await aemit("before_retry", url, exc, attempt)
                    await asyncio.sleep(current_delay)
                    await aemit("after_retry", url, exc, attempt)
                    current_delay *= 2.0
                    continue

                if isinstance(exc, httpx.TimeoutException):
                    raise TimeoutError(f"Streaming request to {url} timed out") from exc
                raise ProviderError(f"Network error during stream to {url}: {exc}") from exc

    def close(self) -> None:
        if self._client is not None and not self._client.is_closed:
            self._client.close()

    async def aclose(self) -> None:
        if self._async_client is not None and not self._async_client.is_closed:
            await self._async_client.aclose()


default_http_transport = HTTPTransport()
