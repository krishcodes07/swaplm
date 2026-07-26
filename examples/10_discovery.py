"""Provider and model discovery API example using SwapLM."""

from swaplm.discovery import model, models, provider, providers


def main():
    print("=== Registered Providers ===")
    all_providers = providers()
    for p in all_providers:
        print(f"- {p.display_name} (ID: {p.id}, Protocol: {p.protocol}, Free: {p.is_free})")

    print("\n=== Specific Provider Lookup ===")
    groq_p = provider("groq")
    if groq_p:
        print(f"Found Provider: {groq_p.name} -> Base URL: {groq_p.base_url}")

    print("\n=== Model Discovery ===")
    all_models = models()
    print(f"Total Available Models: {len(all_models)}")

    # Filter models by capability
    tool_capable = models(capability="tools")
    print(f"Tool-Capable Models Count: {len(tool_capable)}")

    # Specific model lookup
    m_info = model("groq/llama-3.3-70b-versatile")
    if m_info:
        print(
            f"Model '{m_info.id}': Context={m_info.context_window}, Tool Calling={m_info.supports_tool_calling}"
        )


if __name__ == "__main__":
    main()
