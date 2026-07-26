"""Base protocol interface.

A *protocol* encapsulates the full HTTP lifecycle for a family of
LLM APIs that share the same request/response format.

For example, ``OpenAIProtocol`` handles OpenAI **and** every
OpenAI-compatible provider (Groq, Together, NVIDIA, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from swaplm.exceptions import SwapLMError
from swaplm.models.provider import ProviderInfo
from swaplm.models.request import ChatRequest
from swaplm.models.response import ChatResponse
from swaplm.models.stream import StreamChunk


class BaseProtocol(ABC):
    """Abstract base defining the provider-agnostic HTTP lifecycle.

    Every concrete protocol must implement these methods.  Providers
    themselves contain **no** request/response logic — that all lives here.
    """

    @property
    @abstractmethod
    def id(self) -> str:
        """Unique protocol identifier, e.g. ``"openai"``."""

    # ── Request building ──────────────────────────────────────────────

    @abstractmethod
    def build_request_url(
        self,
        request: ChatRequest,
        provider: ProviderInfo,
    ) -> str:
        """Return the full URL for the chat completion endpoint."""

    @abstractmethod
    def build_request_headers(
        self,
        request: ChatRequest,
        provider: ProviderInfo,
        api_key: str,
    ) -> dict[str, str]:
        """Return HTTP headers including authorisation."""

    @abstractmethod
    def build_request_body(
        self,
        request: ChatRequest,
    ) -> dict[str, Any]:
        """Translate a ``ChatRequest`` into the provider's JSON body."""

    # ── Response parsing ──────────────────────────────────────────────

    @abstractmethod
    def parse_response(
        self,
        data: dict[str, Any],
        provider_id: str,
    ) -> ChatResponse:
        """Translate a provider JSON response into a ``ChatResponse``."""

    @abstractmethod
    def parse_stream_chunk(
        self,
        data: dict[str, Any],
        provider_id: str,
    ) -> StreamChunk | None:
        """Translate one SSE event payload into a ``StreamChunk``.

        Return ``None`` for keep-alive or ignorable events.
        """

    # ── Error mapping ─────────────────────────────────────────────────

    @abstractmethod
    def map_error(
        self,
        status_code: int,
        data: dict[str, Any],
        *,
        provider: str | None = None,
        model: str | None = None,
    ) -> SwapLMError:
        """Convert an HTTP error response into a typed ``SwapLMError``."""
