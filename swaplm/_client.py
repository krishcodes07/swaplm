"""Internal client orchestrator.

Wires the complete request pipeline::

    chat() / achat() → middleware (req) → router → auth → protocol → transport → middleware (res) → response
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import Any

from swaplm.auth.manager import AuthManager
from swaplm.config import get_config
from swaplm.exceptions import SwapLMError
from swaplm.hooks import aemit, emit
from swaplm.logging import log_debug, redact_body, redact_headers
from swaplm.middleware import get_middlewares
from swaplm.models.request import ChatRequest
from swaplm.models.response import ChatResponse
from swaplm.protocols.registry import default_protocol_registry
from swaplm.router.router import Router
from swaplm.streaming.iterator import StreamResponse
from swaplm.transport.http import HTTPTransport, default_http_transport


class _Client:
    """Internal SDK client — not part of the public API."""

    def __init__(
        self,
        *,
        router: Router | None = None,
        auth: AuthManager | None = None,
        http_transport: HTTPTransport | None = None,
    ) -> None:
        self._router = router or Router()
        self._auth = auth or AuthManager()
        self._http = http_transport or default_http_transport

    def chat(self, request: ChatRequest) -> ChatResponse | StreamResponse:
        """Execute a synchronous chat request through the runtime pipeline."""
        cfg = get_config()
        self._apply_config_defaults(request, cfg)

        middlewares = get_middlewares()

        try:
            # Middleware request processing (M1 -> M2)
            for m in middlewares:
                request = m.process_request(request)

            emit("before_request", request)

            # Resolve routing & credentials
            if request.provider:
                provider, model_id = self._router.resolve_explicit(request.provider, request.model)
            else:
                provider, model_id = self._router.resolve(request.model)
            api_key = self._auth.resolve_api_key(provider, request.api_key)
            protocol = default_protocol_registry.get(provider.info.protocol)
            model_info = provider.get_model(model_id)

            # Build request payload with capability filtering
            url = protocol.build_request_url(request, provider.info)
            headers = protocol.build_request_headers(request, provider.info, api_key)
            body = protocol.build_request_body(request, model_info=model_info)

            log_debug(
                f"Executing {provider.info.id}/{model_id} via {protocol.id} | "
                f"URL: {url} | Headers: {redact_headers(headers)} | "
                f"Body: {redact_body(body, debug=cfg.debug)}",
                debug=cfg.debug or cfg.logging,
            )

            # Select transport
            transport = cfg.transport or self._http

            if request.stream:
                emit("before_stream", request)
                if hasattr(transport, "send_stream"):
                    raw_stream = transport.send_stream(
                        "POST",
                        url,
                        headers=headers,
                        json=body,
                        timeout=request.timeout,
                        retries=request.retries,
                    )
                else:
                    raw_stream = transport.post_stream(
                        url,
                        headers=headers,
                        body=body,
                        timeout=request.timeout,
                    )

                processed = self._process_stream_chunks(
                    raw_stream,
                    protocol=protocol,
                    provider_id=provider.info.id,
                    model_id=model_id,
                )
                emit("after_stream", request)
                return StreamResponse(
                    protocol=protocol,
                    provider_id=provider.info.id,
                    raw_chunks=processed,
                )

            # Non-streaming request
            if hasattr(transport, "send"):
                status_code, data = transport.send(
                    "POST",
                    url,
                    headers=headers,
                    json=body,
                    timeout=request.timeout,
                    retries=request.retries,
                )
            else:
                status_code, data = transport.post(
                    url,
                    headers=headers,
                    body=body,
                    timeout=request.timeout,
                )

            if status_code >= 400:
                raise protocol.map_error(
                    status_code,
                    data,
                    provider=provider.info.id,
                    model=model_id,
                )

            response = protocol.parse_response(data, provider_id=provider.info.id)

            # Middleware response processing (M2 -> M1)
            for m in reversed(middlewares):
                response = m.process_response(response)

            emit("after_request", request, response)
            return response

        except SwapLMError as err:
            for m in reversed(middlewares):
                err = m.process_error(err)
            emit("on_error", request, err)
            raise err

    async def achat(self, request: ChatRequest) -> ChatResponse | StreamResponse:
        """Execute an asynchronous chat request through the runtime pipeline."""
        cfg = get_config()
        self._apply_config_defaults(request, cfg)

        middlewares = get_middlewares()

        try:
            # Middleware request processing (M1 -> M2)
            for m in middlewares:
                request = await m.aprocess_request(request)

            await aemit("before_request", request)

            # Resolve routing & credentials
            if request.provider:
                provider, model_id = self._router.resolve_explicit(request.provider, request.model)
            else:
                provider, model_id = self._router.resolve(request.model)
            api_key = self._auth.resolve_api_key(provider, request.api_key)
            protocol = default_protocol_registry.get(provider.info.protocol)
            model_info = provider.get_model(model_id)

            # Build request payload with capability filtering
            url = protocol.build_request_url(request, provider.info)
            headers = protocol.build_request_headers(request, provider.info, api_key)
            body = protocol.build_request_body(request, model_info=model_info)

            log_debug(
                f"[Async] Executing {provider.info.id}/{model_id} via {protocol.id} | "
                f"URL: {url} | Headers: {redact_headers(headers)} | "
                f"Body: {redact_body(body, debug=cfg.debug)}",
                debug=cfg.debug or cfg.logging,
            )

            transport = cfg.transport or self._http

            if request.stream:
                await aemit("before_stream", request)
                if hasattr(transport, "asend_stream"):
                    raw_async_stream = transport.asend_stream(
                        "POST",
                        url,
                        headers=headers,
                        json=body,
                        timeout=request.timeout,
                        retries=request.retries,
                    )
                else:
                    # Fallback for sync transports or custom transports
                    raw_async_stream = self._http.asend_stream(
                        "POST",
                        url,
                        headers=headers,
                        json=body,
                        timeout=request.timeout,
                        retries=request.retries,
                    )

                processed_async = self._process_async_stream_chunks(
                    raw_async_stream,
                    protocol=protocol,
                    provider_id=provider.info.id,
                    model_id=model_id,
                )
                await aemit("after_stream", request)
                return StreamResponse(
                    protocol=protocol,
                    provider_id=provider.info.id,
                    raw_async_chunks=processed_async,
                )

            # Non-streaming async request
            if hasattr(transport, "asend"):
                status_code, data = await transport.asend(
                    "POST",
                    url,
                    headers=headers,
                    json=body,
                    timeout=request.timeout,
                    retries=request.retries,
                )
            else:
                status_code, data = await self._http.asend(
                    "POST",
                    url,
                    headers=headers,
                    json=body,
                    timeout=request.timeout,
                    retries=request.retries,
                )

            if status_code >= 400:
                raise protocol.map_error(
                    status_code,
                    data,
                    provider=provider.info.id,
                    model=model_id,
                )

            response = protocol.parse_response(data, provider_id=provider.info.id)

            # Middleware response processing (M2 -> M1)
            for m in reversed(middlewares):
                response = await m.aprocess_response(response)

            await aemit("after_request", request, response)
            return response

        except SwapLMError as err:
            for m in reversed(middlewares):
                err = await m.aprocess_error(err)
            await aemit("on_error", request, err)
            raise err

    @staticmethod
    def _apply_config_defaults(request: ChatRequest, cfg: Any) -> None:
        """Merge global SDK configuration defaults into request."""
        if request.timeout is None and cfg.timeout is not None:
            request.timeout = cfg.timeout
        if request.retries == 0 and cfg.retries != 0:
            request.retries = cfg.retries
        if request.max_tokens is None and cfg.max_tokens is not None:
            request.max_tokens = cfg.max_tokens
        if request.temperature is None and cfg.temperature is not None:
            request.temperature = cfg.temperature
        if request.top_p is None and cfg.top_p is not None:
            request.top_p = cfg.top_p

    @staticmethod
    def _process_stream_chunks(
        stream: Iterator[dict[str, Any]],
        *,
        protocol: Any,
        provider_id: str,
        model_id: str,
    ) -> Iterator[dict[str, Any]]:
        for chunk in stream:
            if chunk.get("_http_error"):
                raise protocol.map_error(
                    chunk["status_code"],
                    chunk["data"],
                    provider=provider_id,
                    model=model_id,
                )
            yield chunk

    @staticmethod
    async def _process_async_stream_chunks(
        stream: AsyncIterator[dict[str, Any]],
        *,
        protocol: Any,
        provider_id: str,
        model_id: str,
    ) -> AsyncIterator[dict[str, Any]]:
        async for chunk in stream:
            if chunk.get("_http_error"):
                raise protocol.map_error(
                    chunk["status_code"],
                    chunk["data"],
                    provider=provider_id,
                    model=model_id,
                )
            yield chunk


_default_client = _Client()
