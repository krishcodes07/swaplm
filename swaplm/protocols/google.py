"""Google Gemini API protocol.

Translates SwapLM's unified format to/from Google's
``generateContent`` / ``streamGenerateContent`` endpoints.
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


class GoogleProtocol(BaseProtocol):
    """Protocol implementation for the Google Gemini API."""

    @property
    def id(self) -> str:
        return "google"

    # ── Request building ──────────────────────────────────────────────

    def build_request_url(
        self,
        request: ChatRequest,
        provider: ProviderInfo,
    ) -> str:
        base = (request.base_url or provider.base_url).rstrip("/")
        model = request.model_id
        action = "streamGenerateContent?alt=sse" if request.stream else "generateContent"
        return f"{base}/models/{model}:{action}"

    def build_request_headers(
        self,
        request: ChatRequest,
        provider: ProviderInfo,
        api_key: str,
    ) -> dict[str, str]:
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        }
        if request.extra_headers:
            headers.update(request.extra_headers)
        return headers

    def build_request_body(
        self,
        request: ChatRequest,
        model_info: ModelInfo | None = None,
    ) -> dict[str, Any]:
        contents: list[dict[str, Any]] = []
        system_instruction: dict[str, Any] | None = None

        for m in request.messages:
            if m.role == "system":
                if model_info is None or model_info.supports_system_message:
                    system_instruction = {
                        "parts": [{"text": m.content if isinstance(m.content, str) else ""}]
                    }
            else:
                role = "model" if m.role == "assistant" else "user"
                parts: list[dict[str, Any]] = []
                if m.content:
                    parts.append({"text": m.content if isinstance(m.content, str) else ""})
                if m.tool_calls:
                    for tc in m.tool_calls:
                        import json

                        parts.append(
                            {
                                "functionCall": {
                                    "name": tc.function.name,
                                    "args": json.loads(tc.function.arguments),
                                }
                            }
                        )
                contents.append({"role": role, "parts": parts})

        body: dict[str, Any] = {"contents": contents}
        if system_instruction:
            body["systemInstruction"] = system_instruction

        # Generation config
        gen_config: dict[str, Any] = {}
        if request.max_tokens is not None:
            gen_config["maxOutputTokens"] = request.max_tokens

        if (
            model_info is None or model_info.supports_temperature
        ) and request.temperature is not None:
            gen_config["temperature"] = request.temperature

        if request.top_p is not None:
            gen_config["topP"] = request.top_p

        if request.stop is not None:
            gen_config["stopSequences"] = (
                request.stop if isinstance(request.stop, list) else [request.stop]
            )

        if (model_info is None or model_info.supports_seed) and request.seed is not None:
            gen_config["seed"] = request.seed

        if gen_config:
            body["generationConfig"] = gen_config

        # Tools
        if (model_info is None or model_info.supports_tool_calling) and request.tools:
            body["tools"] = [
                {
                    "functionDeclarations": [
                        {
                            "name": t.function.name,
                            "description": t.function.description or "",
                            "parameters": t.function.parameters or {},
                        }
                        for t in request.tools
                    ]
                }
            ]

        if request.provider_options:
            opts = dict(request.provider_options)
            if model_info is not None and not model_info.supports_thinking:
                opts.pop("thinkingConfig", None)
            body.update(opts)

        return body

    # ── Response parsing ──────────────────────────────────────────────

    def parse_response(
        self,
        data: dict[str, Any],
        provider_id: str,
    ) -> ChatResponse:
        candidates = data.get("candidates", [])
        choices: list[Choice] = []

        for i, candidate in enumerate(candidates):
            content_data = candidate.get("content", {})
            parts = content_data.get("parts", [])

            text_parts: list[str] = []
            tool_calls: list[ToolCall] = []

            for part in parts:
                if "text" in part:
                    text_parts.append(part["text"])
                elif "functionCall" in part:
                    import json

                    fc = part["functionCall"]
                    tool_calls.append(
                        ToolCall(
                            id=f"call_{i}_{fc['name']}",
                            type="function",
                            function=FunctionCall(
                                name=fc["name"],
                                arguments=json.dumps(fc.get("args", {})),
                            ),
                        )
                    )

            message = Message(
                role="assistant",
                content="\n".join(text_parts) if text_parts else None,
                tool_calls=tool_calls or None,
            )

            choices.append(
                Choice(
                    index=i,
                    message=message,
                    finish_reason=self._map_finish_reason(candidate.get("finishReason")),
                )
            )

        usage_data = data.get("usageMetadata", {})
        usage = Usage(
            prompt_tokens=usage_data.get("promptTokenCount", 0),
            completion_tokens=usage_data.get("candidatesTokenCount", 0),
            total_tokens=usage_data.get("totalTokenCount", 0),
        )

        return ChatResponse(
            id=data.get("id", ""),
            choices=choices,
            usage=usage,
            model=data.get("modelVersion", ""),
            provider=provider_id,
        )

    def parse_stream_chunk(
        self,
        data: dict[str, Any],
        provider_id: str,
    ) -> StreamChunk | None:
        candidates = data.get("candidates", [])
        if not candidates:
            return None

        choices: list[ChunkChoice] = []
        for candidate in candidates:
            content = candidate.get("content", {})
            parts = content.get("parts", [])
            text = parts[0].get("text", "") if parts else None

            choices.append(
                ChunkChoice(
                    index=candidate.get("index", 0),
                    delta=ChoiceDelta(
                        role="assistant" if not choices else None,
                        content=text,
                    ),
                    finish_reason=self._map_finish_reason(candidate.get("finishReason")),
                )
            )

        usage_data = data.get("usageMetadata")
        usage = (
            Usage(
                prompt_tokens=usage_data.get("promptTokenCount", 0),
                completion_tokens=usage_data.get("candidatesTokenCount", 0),
                total_tokens=usage_data.get("totalTokenCount", 0),
            )
            if usage_data
            else None
        )

        return StreamChunk(
            choices=choices,
            usage=usage,
            model=data.get("modelVersion"),
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
        message = error_data.get("message", "Unknown error")
        status = error_data.get("status", "")

        if status_code in (401, 403) or status == "UNAUTHENTICATED":
            return AuthenticationError(
                message, provider=provider, model=model, status_code=status_code
            )
        if status_code == 429 or status == "RESOURCE_EXHAUSTED":
            return RateLimitError(message, provider=provider, model=model, status_code=status_code)
        if status_code == 408:
            return TimeoutError(message, provider=provider, model=model, status_code=status_code)
        if status_code == 404 or status == "NOT_FOUND":
            return InvalidModelError(message, model=model)

        return ProviderError(message, provider=provider, model=model, status_code=status_code)

    # ── Internal helpers ──────────────────────────────────────────────

    @staticmethod
    def _map_finish_reason(reason: str | None) -> str | None:
        """Map Google finish reasons to OpenAI-style finish reasons."""
        mapping = {
            "STOP": "stop",
            "MAX_TOKENS": "length",
            "SAFETY": "content_filter",
            "RECITATION": "content_filter",
        }
        return mapping.get(reason, reason) if reason else None
