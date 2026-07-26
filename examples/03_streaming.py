"""Streaming response example using SwapLM."""

from swaplm import chat


def main():
    print("Streaming response from Groq...\n")
    stream = chat(
        model="groq/llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Write a short poem about open source software."}],
        stream=True,
    )

    for chunk in stream:
        if chunk.delta:
            print(chunk.delta, end="", flush=True)

    print("\n\nStream finished!")


if __name__ == "__main__":
    main()
