"""OpenAI-compatible protocol.

Handles OpenAI itself **and** every provider that exposes an
OpenAI-compatible ``/v1/chat/completions`` endpoint (Groq, Together,
NVIDIA, Cerebras, OpenRouter, GitHub Models, etc.).
"""

from __future__ import annotations

from typing import Any

from swaplm.exceptions import (
    AuthenticationError,
    InvalidModelError,
    ProviderError,
    RateLimitError,
    SwapLMError,
    TimeoutError,
)
from swaplm.models.messages import FunctionCall, Message, ToolCall
from swaplm.models.model import ModelInfo
from swaplm.models.provider import ProviderInfo
from swaplm.models.request import ChatRequest
from swaplm.models.response import ChatResponse, Choice, Usage
from swaplm.models.stream import ChoiceDelta, ChunkChoice, StreamChunk
from swaplm.protocols.base import BaseProtocol


class OpenAIProtocol(BaseProtocol):
    """Protocol implementation for the OpenAI chat completions format."""

    @property
    def id(self) -> str:
        return "openai"

    # ── Request building ──────────────────────────────────────────────

    def build_request_url(
        self,
        request: ChatRequest,
        provider: ProviderInfo,
    ) -> str:
        base = (request.base_url or provider.base_url).rstrip("/")
        return f"{base}/chat/completions"

    def build_request_headers(
        self,
        request: ChatRequest,
        provider: ProviderInfo,
        api_key: str,
    ) -> dict[str, str]:
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        if request.extra_headers:
            headers.update(request.extra_headers)
        return headers

    def build_request_body(
        self,
        request: ChatRequest,
        model_info: ModelInfo | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "model": request.model_id,
            "messages": [m.model_dump(exclude_none=True) for m in request.messages],
        }
        if request.stream:
            body["stream"] = True
        if request.max_tokens is not None:
            body["max_tokens"] = request.max_tokens
        if (
            model_info is None or model_info.supports_temperature
        ) and request.temperature is not None:
            body["temperature"] = request.temperature
        if request.top_p is not None:
            body["top_p"] = request.top_p
        if request.stop is not None:
            body["stop"] = request.stop
        if (model_info is None or model_info.supports_seed) and request.seed is not None:
            body["seed"] = request.seed
        if model_info is None or model_info.supports_tool_calling:
            if request.tools:
                body["tools"] = [t.model_dump(exclude_none=True) for t in request.tools]
            if request.tool_choice is not None:
                body["tool_choice"] = request.tool_choice

        if (
            model_info is None
            or model_info.supports_json_mode
            or model_info.supports_structured_output
        ) and request.response_format is not None:
            body["response_format"] = request.response_format

        if request.provider_options:
            opts = dict(request.provider_options)
            if model_info is not None:
                if not model_info.supports_thinking:
                    opts.pop("thinking", None)
                if not model_info.supports_reasoning_effort:
                    opts.pop("reasoning_effort", None)
                if not model_info.supports_json_mode and not model_info.supports_structured_output:
                    opts.pop("response_format", None)
            body.update(opts)
        return body

    # ── Response parsing ──────────────────────────────────────────────

    def parse_response(
        self,
        data: dict[str, Any],
        provider_id: str,
    ) -> ChatResponse:
        choices: list[Choice] = []
        for c in data.get("choices", []):
            msg_data = c.get("message", {})
            tool_calls = None
            if raw_tc := msg_data.get("tool_calls"):
                tool_calls = [
                    ToolCall(
                        id=tc["id"],
                        type=tc.get("type", "function"),
                        function=FunctionCall(
                            name=tc["function"]["name"],
                            arguments=tc["function"]["arguments"],
                        ),
                    )
                    for tc in raw_tc
                ]
            message = Message(
                role=msg_data.get("role", "assistant"),
                content=msg_data.get("content"),
                tool_calls=tool_calls,
                refusal=msg_data.get("refusal"),
            )
            choices.append(
                Choice(
                    index=c.get("index", 0),
                    message=message,
                    finish_reason=c.get("finish_reason"),
                )
            )

        usage_data = data.get("usage")
        usage = (
            Usage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0),
            )
            if usage_data
            else None
        )

        return ChatResponse(
            id=data.get("id", ""),
            choices=choices,
            usage=usage,
            model=data.get("model", ""),
            provider=provider_id,
            created=data.get("created"),
        )

    def parse_stream_chunk(
        self,
        data: dict[str, Any],
        provider_id: str,
    ) -> StreamChunk | None:
        # Skip [DONE] sentinel or empty payloads
        if not data or not data.get("choices"):
            return None

        choices: list[ChunkChoice] = []
        for c in data["choices"]:
            delta_data = c.get("delta", {})
            delta = ChoiceDelta(
                role=delta_data.get("role"),
                content=delta_data.get("content"),
            )
            choices.append(
                ChunkChoice(
                    index=c.get("index", 0),
                    delta=delta,
                    finish_reason=c.get("finish_reason"),
                )
            )

        usage_data = data.get("usage")
        usage = (
            Usage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0),
            )
            if usage_data
            else None
        )

        return StreamChunk(
            id=data.get("id"),
            choices=choices,
            usage=usage,
            model=data.get("model"),
            provider=provider_id,
        )

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
        message = error_data.get("message", data.get("message", "Unknown error"))

        code = error_data.get("code") if isinstance(error_data, dict) else None

        if status_code == 401:
            return AuthenticationError(
                message, provider=provider, model=model, status_code=status_code
            )
        if status_code == 429:
            return RateLimitError(message, provider=provider, model=model, status_code=status_code)
        if status_code == 408:
            return TimeoutError(message, provider=provider, model=model, status_code=status_code)
        if (
            status_code == 404
            or code in ("model_not_found", "invalid_model")
            or ("model" in message.lower() and "not found" in message.lower())
        ):
            return InvalidModelError(message, model=model)

        return ProviderError(message, provider=provider, model=model, status_code=status_code)
