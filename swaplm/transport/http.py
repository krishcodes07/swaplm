"""HTTP transport layer using httpx.

Handles sync requests, connection management, timeout configuration,
and SSE event parsing for streaming responses.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Any

import httpx

from swaplm.exceptions import ProviderError, TimeoutError


class HTTPTransport:
    """HTTP client wrapper handling non-streaming and streaming requests."""

    def __init__(
        self,
        *,
        default_timeout: float = 60.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.default_timeout = default_timeout
        self._client = client

    def _get_client(self) -> httpx.Client:
        if self._client is None or self._client.is_closed:
            self._client = httpx.Client(
                timeout=httpx.Timeout(self.default_timeout),
                follow_redirects=True,
            )
        return self._client

    def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        body: dict[str, Any],
        timeout: float | None = None,
    ) -> tuple[int, dict[str, Any]]:
        """Execute a non-streaming HTTP POST request.

        Returns:
            Tuple of ``(status_code, response_json)``.
        """
        client = self._get_client()
        req_timeout = timeout if timeout is not None else self.default_timeout

        try:
            response = client.post(
                url,
                headers=headers,
                json=body,
                timeout=req_timeout,
            )
        except httpx.TimeoutException as exc:
            raise TimeoutError(f"Request to {url} timed out after {req_timeout}s") from exc
        except httpx.RequestError as exc:
            raise ProviderError(f"Network error requesting {url}: {exc}") from exc

        try:
            data = response.json()
        except Exception:
            data = {"message": response.text or "Empty or non-JSON response"}

        return response.status_code, data

    def post_stream(
        self,
        url: str,
        *,
        headers: dict[str, str],
        body: dict[str, Any],
        timeout: float | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Execute a streaming HTTP POST request and yield parsed SSE payloads.

        Yields:
            Parsed JSON payloads from ``data: <json>`` SSE lines.
        """
        client = self._get_client()
        req_timeout = timeout if timeout is not None else self.default_timeout

        try:
            with client.stream(
                "POST",
                url,
                headers=headers,
                json=body,
                timeout=req_timeout,
            ) as response:
                if response.status_code >= 400:
                    try:
                        content = response.read()
                        data = json.loads(content)
                    except Exception:
                        data = {"message": response.text or "Error response"}
                    yield {"_http_error": True, "status_code": response.status_code, "data": data}
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
                                yield json.loads(payload)
                            except json.JSONDecodeError:
                                continue

        except httpx.TimeoutException as exc:
            raise TimeoutError(f"Streaming request to {url} timed out") from exc
        except httpx.RequestError as exc:
            raise ProviderError(f"Network error during stream to {url}: {exc}") from exc


# Module-level singleton
default_http_transport = HTTPTransport()
