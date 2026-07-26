"""Internal client orchestrator.

Wires the complete request pipeline::

    chat() → _client → router → auth → protocol → (HTTP) → response

HTTP execution is not yet implemented — this module currently builds
the request and validates the pipeline.  The actual ``httpx`` call
will be added in Phase 3 alongside the first providers.
"""

from __future__ import annotations

from swaplm.auth.manager import AuthManager
from swaplm.models.request import ChatRequest
from swaplm.models.response import ChatResponse
from swaplm.protocols.registry import default_protocol_registry
from swaplm.router.router import Router
from swaplm.streaming.iterator import StreamResponse


class _Client:
    """Internal SDK client — not part of the public API."""

    def __init__(self) -> None:
        self._router = Router()
        self._auth = AuthManager()

    def chat(self, request: ChatRequest) -> ChatResponse | StreamResponse:
        """Execute a chat completion request.

        Pipeline:
            1. Route ``model`` → provider + model_id
            2. Resolve API key
            3. Look up protocol
            4. Build HTTP request (url, headers, body)
            5. Execute HTTP call (TODO: Phase 3)
            6. Parse response → ``ChatResponse``

        Returns:
            ``ChatResponse`` for non-streaming, ``StreamResponse`` for streaming.

        Raises:
            InvalidModelError: Bad model string format.
            InvalidProviderError: Provider not found.
            AuthenticationError: No API key available.
        """
        # 1. Resolve provider
        provider, model_id = self._router.resolve(request.model)

        # 2. Resolve API key
        api_key = self._auth.resolve_api_key(provider, request.api_key)

        # 3. Get protocol
        protocol = default_protocol_registry.get(provider.info.protocol)

        # 4. Build request components
        url = protocol.build_request_url(request, provider.info)
        headers = protocol.build_request_headers(request, provider.info, api_key)
        body = protocol.build_request_body(request)

        # 5. HTTP execution — placeholder for Phase 3
        # This is where httpx.post(url, headers=headers, json=body) will go.
        # For now, the pipeline validates that everything compiles and wires
        # correctly up to the HTTP boundary.
        _ = url, headers, body  # suppress unused warnings

        raise NotImplementedError(
            "HTTP execution is not yet implemented. "
            "Provider implementations will be added in Phase 3. "
            f"Pipeline validated: provider={provider.info.id}, "
            f"model={model_id}, protocol={provider.info.protocol}, url={url}"
        )


# Module-level singleton
_default_client = _Client()
