"""Abstract Base Transport interface for SwapLM."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Iterator
from typing import Any


class BaseTransport(ABC):
    """Abstract base class for HTTP transport adapters.

    Allows replacing the transport layer for custom proxying, mock testing,
    caching, or enterprise security enforcement.
    """

    @abstractmethod
    def send(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
        retries: int = 0,
    ) -> tuple[int, dict[str, Any]]:
        """Send a synchronous HTTP request and return (status_code, response_json)."""
        pass

    @abstractmethod
    async def asend(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
        retries: int = 0,
    ) -> tuple[int, dict[str, Any]]:
        """Send an asynchronous HTTP request and return (status_code, response_json)."""
        pass

    @abstractmethod
    def send_stream(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Send a synchronous HTTP SSE stream request and yield parsed JSON events."""
        pass

    @abstractmethod
    async def asend_stream(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """Send an asynchronous HTTP SSE stream request and yield parsed JSON events."""
        pass

    def close(self) -> None:  # noqa: B027
        """Close synchronous network resources."""
        pass

    async def aclose(self) -> None:  # noqa: B027
        """Close asynchronous network resources."""
        pass
