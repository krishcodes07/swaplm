"""Public provider and model discovery APIs."""

from __future__ import annotations

from swaplm.models.model import ModelInfo
from swaplm.models.provider import ProviderInfo
from swaplm.providers.registry import default_provider_registry
from swaplm.router.router import Router


def providers() -> list[ProviderInfo]:
    """Return static metadata for all registered providers.

    Example::

        import swaplm

        all_providers = swaplm.providers()
        for p in all_providers:
            print(p.id, p.name)
    """
    return [p.info for p in default_provider_registry.list_instances()]


def models() -> list[tuple[ProviderInfo, ModelInfo]]:
    """Return metadata for all models across all registered providers.

    Example::

        import swaplm

        all_models = swaplm.models()
        for provider_info, model_info in all_models:
            print(f"{provider_info.id}/{model_info.id}")
    """
    results: list[tuple[ProviderInfo, ModelInfo]] = []
    for p in default_provider_registry.list_instances():
        for m in p.get_models():
            results.append((p.info, m))
    return results


def provider(provider_id: str) -> ProviderInfo:
    """Retrieve metadata for a specific provider.

    Example::

        import swaplm

        groq_info = swaplm.provider("groq")
        print(groq_info.base_url)
    """
    return default_provider_registry.get(provider_id).info


def model(model_string: str) -> tuple[ProviderInfo, ModelInfo]:
    """Retrieve metadata for a specific model string or alias.

    Example::

        import swaplm

        provider_info, model_info = swaplm.model("groq/llama-3.3-70b-versatile")
        print(model_info.context_window)
    """
    router = Router(provider_registry=default_provider_registry)
    provider_inst, model_id = router.resolve(model_string)
    model_info = provider_inst.get_model(model_id)

    if model_info is None:
        # Fallback for pass-through providers without models.json
        model_info = ModelInfo(id=model_id)

    return provider_inst.info, model_info
