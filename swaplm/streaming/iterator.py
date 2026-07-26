"""Streaming response iterator.

``StreamResponse`` wraps an HTTP response and yields ``StreamChunk``
objects.  Full SSE parsing will be implemented in a future phase.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING

from swaplm.models.stream import StreamChunk

if TYPE_CHECKING:
    from swaplm.protocols.base import BaseProtocol


class StreamResponse:
    """Streaming wrapper that yields normalised ``StreamChunk`` objects.

    Supports both sync and async iteration::

        # Sync
        for chunk in stream:
            print(chunk.choices[0].delta.content, end="")

        # Async
        async for chunk in stream:
            print(chunk.choices[0].delta.content, end="")
    """

    def __init__(
        self,
        *,
        protocol: BaseProtocol,
        provider_id: str,
        raw_chunks: Iterator[dict] | None = None,
        raw_async_chunks: AsyncIterator[dict] | None = None,
    ) -> None:
        self._protocol = protocol
        self._provider_id = provider_id
        self._raw_chunks = raw_chunks
        self._raw_async_chunks = raw_async_chunks
        self._accumulated_content: list[str] = []

    def __iter__(self) -> Iterator[StreamChunk]:
        """Synchronous iteration over stream chunks."""
        if self._raw_chunks is None:
            return
        for raw in self._raw_chunks:
            chunk = self._protocol.parse_stream_chunk(raw, self._provider_id)
            if chunk is not None:
                self._accumulate(chunk)
                yield chunk

    async def __aiter__(self) -> AsyncIterator[StreamChunk]:
        """Asynchronous iteration over stream chunks."""
        if self._raw_async_chunks is None:
            return
        async for raw in self._raw_async_chunks:
            chunk = self._protocol.parse_stream_chunk(raw, self._provider_id)
            if chunk is not None:
                self._accumulate(chunk)
                yield chunk

    @property
    def accumulated_content(self) -> str:
        """Content accumulated from all received chunks."""
        return "".join(self._accumulated_content)

    def _accumulate(self, chunk: StreamChunk) -> None:
        """Collect content deltas for post-stream access."""
        if chunk.choices:
            for choice in chunk.choices:
                if choice.delta.content:
                    self._accumulated_content.append(choice.delta.content)
