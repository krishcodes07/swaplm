"""Authentication manager.

Resolves API keys in priority order:

1. Explicit key passed via ``api_key`` parameter.
2. Environment variable defined by the provider.
3. ``AuthenticationError`` if neither is found.
"""

from __future__ import annotations

import os

from swaplm.exceptions import AuthenticationError
from swaplm.providers.base import BaseProvider


class AuthManager:
    """Stateless API-key resolver."""

    def resolve_api_key(
        self,
        provider: BaseProvider,
        explicit_key: str | None = None,
    ) -> str:
        """Return an API key for the given provider.

        Args:
            provider: The provider whose key is needed.
            explicit_key: Key passed directly by the user (highest priority).

        Returns:
            A non-empty API key string.

        Raises:
            AuthenticationError: If no key can be found and the provider
                requires one.
        """
        # 1. Explicit key
        if explicit_key:
            return explicit_key

        # 2. Environment variable
        env_var = provider.info.env_var
        env_key = os.environ.get(env_var, "")
        if env_key:
            return env_key

        # 3. Provider doesn't require a key
        if not provider.info.requires_api_key:
            return ""

        # 4. No key found
        raise AuthenticationError(
            f"No API key found for provider '{provider.info.id}'. "
            f"Set the {env_var} environment variable or pass api_key directly.",
            provider=provider.info.id,
        )
