"""Internal client orchestrator.

Wires the complete request pipeline::

    chat() → _client → router → auth → protocol → HTTP transport → response
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from swaplm.auth.manager import AuthManager
from swaplm.config import get_config
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
        """Execute a chat completion request.

        Pipeline:
            1. Apply global configuration defaults
            2. Route ``model`` → provider + model_id
            3. Resolve API key
            4. Look up protocol
            5. Build HTTP request (url, headers, body with capability filtering)
            6. Execute HTTP call via HTTP transport
            7. Parse response → ``ChatResponse`` or ``StreamResponse``
        """
        # 1. Apply global config defaults for unset parameters
        cfg = get_config()
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

        # 2. Resolve provider
        provider, model_id = self._router.resolve(request.model)

        # 3. Resolve API key
        api_key = self._auth.resolve_api_key(provider, request.api_key)

        # 4. Get protocol & model info
        protocol = default_protocol_registry.get(provider.info.protocol)
        model_info = provider.get_model(model_id)

        # 5. Build request components (with capability filtering)
        url = protocol.build_request_url(request, provider.info)
        headers = protocol.build_request_headers(request, provider.info, api_key)
        body = protocol.build_request_body(request, model_info=model_info)

        # 6. Execute HTTP request
        if request.stream:
            raw_stream = self._http.post_stream(
                url,
                headers=headers,
                body=body,
                timeout=request.timeout,
            )
            processed_stream = self._process_stream_chunks(
                raw_stream,
                protocol=protocol,
                provider_id=provider.info.id,
                model_id=model_id,
            )
            return StreamResponse(
                protocol=protocol,
                provider_id=provider.info.id,
                raw_chunks=processed_stream,
            )

        status_code, data = self._http.post(
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

        return protocol.parse_response(data, provider_id=provider.info.id)

    @staticmethod
    def _process_stream_chunks(
        stream: Iterator[dict[str, Any]],
        *,
        protocol: Any,
        provider_id: str,
        model_id: str,
    ) -> Iterator[dict[str, Any]]:
        """Wrap stream iterator to intercept HTTP errors sent during stream initialization."""
        for chunk in stream:
            if chunk.get("_http_error"):
                raise protocol.map_error(
                    chunk["status_code"],
                    chunk["data"],
                    provider=provider_id,
                    model=model_id,
                )
            yield chunk


# Module-level singleton
_default_client = _Client()
