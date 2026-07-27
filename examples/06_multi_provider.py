"""Multi-provider switching example using SwapLM."""

from swaplm import chat


def query_provider(model_string: str, prompt: str):
    print(f"\n--- Querying [{model_string}] ---")
    try:
        response = chat(
            model=model_string,
            messages=[{"role": "user", "content": prompt}],
        )
        print(f"Provider: {response.provider}")
        print(f"Content: {response.content[:150]}...")
    except Exception as e:
        print(f"Error querying {model_string}: {e}")


def main():
    prompt = "In 2 sentences, what is the core mission of open source?"

    # List of models across different providers
    models_to_test = [
        "groq/llama-3.3-70b-versatile",
        "google/gemini-2.0-flash",
        "anthropic/claude-3-5-sonnet-20241022",
        "openrouter/inclusionai/ling-3.0-flash:free",
    ]

    for model_string in models_to_test:
        query_provider(model_string, prompt)


if __name__ == "__main__":
    main()
