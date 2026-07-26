"""Protocol registry.

Maps protocol IDs (``"openai"``, ``"anthropic"``, ``"google"``) to
singleton protocol instances.
"""

from __future__ import annotations

from swaplm.protocols.anthropic import AnthropicProtocol
from swaplm.protocols.base import BaseProtocol
from swaplm.protocols.google import GoogleProtocol
from swaplm.protocols.openai import OpenAIProtocol


class ProtocolRegistry:
    """Registry mapping protocol IDs to ``BaseProtocol`` instances."""

    def __init__(self) -> None:
        self._protocols: dict[str, BaseProtocol] = {}

    def register(self, protocol: BaseProtocol) -> None:
        """Register a protocol instance."""
        self._protocols[protocol.id] = protocol

    def get(self, protocol_id: str) -> BaseProtocol:
        """Retrieve a protocol by ID.

        Raises:
            KeyError: If the protocol ID is not registered.
        """
        if protocol_id not in self._protocols:
            available = ", ".join(sorted(self._protocols)) or "(none)"
            msg = f"Unknown protocol '{protocol_id}'. Available protocols: {available}"
            raise KeyError(msg)
        return self._protocols[protocol_id]

    def list_protocols(self) -> list[str]:
        """Return all registered protocol IDs."""
        return list(self._protocols)


def _create_default_registry() -> ProtocolRegistry:
    """Build the default registry with built-in protocols."""
    registry = ProtocolRegistry()
    registry.register(OpenAIProtocol())
    registry.register(AnthropicProtocol())
    registry.register(GoogleProtocol())
    return registry


# Module-level singleton
default_protocol_registry = _create_default_registry()
