"""Example 11: First-Class Free Provider.

Demonstrates using SwapLM's built-in free provider without needing an API key.
"""

from swaplm import chat, models, provider


def main():
    # 1. Inspect free provider metadata
    free_info = provider("free")
    print(f"Provider: {free_info.name} (requires_api_key={free_info.requires_api_key})")

    # 2. List available free models
    all_models = models()
    free_models = [m.id for p, m in all_models if p.id == "free"]
    print(f"Available Free Models ({len(free_models)}):")
    for m_id in free_models[:5]:
        print(f" - {m_id}")

    # 3. Call free provider model (explicit provider style)
    try:
        response = chat(
            provider="free",
            model="meta-llama/llama-3.3-70b-instruct:free",
            messages=[{"role": "user", "content": "Explain quantum computing in one sentence."}],
        )
        print("\nResponse:")
        print(response.content)
    except Exception as err:
        print(f"\nAPI Call Note: {err}")


if __name__ == "__main__":
    main()
