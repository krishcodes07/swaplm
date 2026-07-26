"""Anthropic Messages API protocol.

Translates SwapLM's unified format to/from Anthropic's ``/v1/messages``
endpoint format.
"""

from __future__ import annotations

from typing import Any

from swaplm.exceptions import (
    AuthenticationError,
    ProviderError,
    RateLimitError,
    SwapLMError,
    TimeoutError,
)
from swaplm.models.messages import FunctionCall, Message, ToolCall
from swaplm.models.provider import ProviderInfo
from swaplm.models.request import ChatRequest
from swaplm.models.response import ChatResponse, Choice, Usage
from swaplm.models.stream import ChoiceDelta, ChunkChoice, StreamChunk
from swaplm.protocols.base import BaseProtocol


class AnthropicProtocol(BaseProtocol):
    """Protocol implementation for the Anthropic Messages API."""

    @property
    def id(self) -> str:
        return "anthropic"

    # ── Request building ──────────────────────────────────────────────

    def build_request_url(
        self,
        request: ChatRequest,
        provider: ProviderInfo,
    ) -> str:
        base = (request.base_url or provider.base_url).rstrip("/")
        return f"{base}/messages"

    def build_request_headers(
        self,
        request: ChatRequest,
        provider: ProviderInfo,
        api_key: str,
    ) -> dict[str, str]:
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        }
        if request.extra_headers:
            headers.update(request.extra_headers)
        return headers

    def build_request_body(
        self,
        request: ChatRequest,
    ) -> dict[str, Any]:
        # Anthropic separates system from messages
        system_text: str | None = None
        messages: list[dict[str, Any]] = []
        for m in request.messages:
            if m.role == "system":
                system_text = m.content if isinstance(m.content, str) else None
            else:
                messages.append(m.model_dump(exclude_none=True, exclude={"name"}))

        body: dict[str, Any] = {
            "model": request.model_id,
            "messages": messages,
        }
        if system_text:
            body["system"] = system_text
        if request.max_tokens is not None:
            body["max_tokens"] = request.max_tokens
        else:
            # Anthropic requires max_tokens
            body["max_tokens"] = 4096
        if request.stream:
            body["stream"] = True
        if request.temperature is not None:
            body["temperature"] = request.temperature
        if request.top_p is not None:
            body["top_p"] = request.top_p
        if request.stop is not None:
            body["stop_sequences"] = (
                request.stop if isinstance(request.stop, list) else [request.stop]
            )
        if request.tools:
            body["tools"] = [
                {
                    "name": t.function.name,
                    "description": t.function.description or "",
                    "input_schema": t.function.parameters or {},
                }
                for t in request.tools
            ]
        if request.tool_choice is not None:
            body["tool_choice"] = self._translate_tool_choice(request.tool_choice)
        if request.provider_options:
            body.update(request.provider_options)
        return body

    # ── Response parsing ──────────────────────────────────────────────

    def parse_response(
        self,
        data: dict[str, Any],
        provider_id: str,
    ) -> ChatResponse:
        # Anthropic returns content as a list of blocks
        content_blocks = data.get("content", [])
        text_parts: list[str] = []
        tool_calls: list[ToolCall] = []

        for block in content_blocks:
            if block.get("type") == "text":
                text_parts.append(block.get("text", ""))
            elif block.get("type") == "tool_use":
                import json

                tool_calls.append(
                    ToolCall(
                        id=block["id"],
                        type="function",
                        function=FunctionCall(
                            name=block["name"],
                            arguments=json.dumps(block.get("input", {})),
                        ),
                    )
                )

        message = Message(
            role="assistant",
            content="\n".join(text_parts) if text_parts else None,
            tool_calls=tool_calls or None,
        )

        usage_data = data.get("usage", {})
        usage = Usage(
            prompt_tokens=usage_data.get("input_tokens", 0),
            completion_tokens=usage_data.get("output_tokens", 0),
            total_tokens=(usage_data.get("input_tokens", 0) + usage_data.get("output_tokens", 0)),
        )

        return ChatResponse(
            id=data.get("id", ""),
            choices=[
                Choice(
                    index=0,
                    message=message,
                    finish_reason=self._map_stop_reason(data.get("stop_reason")),
                )
            ],
            usage=usage,
            model=data.get("model", ""),
            provider=provider_id,
        )

    def parse_stream_chunk(
        self,
        data: dict[str, Any],
        provider_id: str,
    ) -> StreamChunk | None:
        event_type = data.get("type")
        if not event_type:
            return None

        if event_type == "content_block_delta":
            delta_data = data.get("delta", {})
            content = delta_data.get("text")
            if content is not None:
                return StreamChunk(
                    choices=[
                        ChunkChoice(
                            index=data.get("index", 0),
                            delta=ChoiceDelta(content=content),
                        )
                    ],
                    provider=provider_id,
                )

        if event_type == "message_delta":
            delta_data = data.get("delta", {})
            usage_data = data.get("usage", {})
            return StreamChunk(
                choices=[
                    ChunkChoice(
                        delta=ChoiceDelta(),
                        finish_reason=self._map_stop_reason(delta_data.get("stop_reason")),
                    )
                ],
                usage=Usage(
                    completion_tokens=usage_data.get("output_tokens", 0),
                )
                if usage_data
                else None,
                provider=provider_id,
            )

        if event_type == "message_start":
            msg = data.get("message", {})
            return StreamChunk(
                id=msg.get("id"),
                model=msg.get("model"),
                choices=[
                    ChunkChoice(delta=ChoiceDelta(role="assistant")),
                ],
                provider=provider_id,
            )

        return None

    # ── Error mapping ─────────────────────────────────────────────────

    def map_error(
        self,
        status_code: int,
        data: dict[str, Any],
        *,
        provider: str | None = None,
        model: str | None = None,
    ) -> SwapLMError:
        error_data = data.get("error", {})
        message = error_data.get("message", "Unknown error")

        if status_code == 401:
            return AuthenticationError(
                message, provider=provider, model=model, status_code=status_code
            )
        if status_code == 429:
            return RateLimitError(message, provider=provider, model=model, status_code=status_code)
        if status_code == 408:
            return TimeoutError(message, provider=provider, model=model, status_code=status_code)
        return ProviderError(message, provider=provider, model=model, status_code=status_code)

    # ── Internal helpers ──────────────────────────────────────────────

    @staticmethod
    def _map_stop_reason(reason: str | None) -> str | None:
        """Map Anthropic stop reasons to OpenAI-style finish reasons."""
        mapping = {
            "end_turn": "stop",
            "max_tokens": "length",
            "stop_sequence": "stop",
            "tool_use": "tool_calls",
        }
        return mapping.get(reason, reason) if reason else None

    @staticmethod
    def _translate_tool_choice(choice: str | dict[str, Any]) -> dict[str, Any]:
        """Translate OpenAI-style tool_choice to Anthropic format."""
        if isinstance(choice, str):
            mapping: dict[str, dict[str, Any]] = {
                "auto": {"type": "auto"},
                "none": {"type": "auto"},  # Anthropic has no "none"
                "required": {"type": "any"},
            }
            return mapping.get(choice, {"type": "auto"})
        return choice
