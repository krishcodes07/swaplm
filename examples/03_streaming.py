"""Streaming response example using SwapLM."""

from swaplm import chat


def main():
    print("Streaming response from Groq...\n")
    stream = chat(
        provider="groq",
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Write a short poem about open source software."}],
        stream=True,
    )

    for chunk in stream:
        print(chunk.content, end="", flush=True)

    print("\n\nStream finished!")
    print("Full text:", stream.text)


if __name__ == "__main__":
    main()
