"""Basic synchronous chat completion example using SwapLM."""

from swaplm import chat


def main():
    # Execute a simple chat completion with Groq
    response = chat(
        model="groq/llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Explain quantum computing in one sentence."},
        ],
        temperature=0.7,
    )

    print("Model:", response.model)
    print("Provider:", response.provider)
    print("Content:", response.content)
    if response.usage:
        print("Input Tokens:", response.usage.prompt_tokens)
        print("Output Tokens:", response.usage.completion_tokens)


if __name__ == "__main__":
    main()
