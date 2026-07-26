"""Lifecycle hooks example using SwapLM."""

from swaplm import ChatRequest, ChatResponse, chat, on


def on_before_request(request: ChatRequest):
    print(f"[Hook: before_request] Sending request to model: {request.model}")


def on_after_request(response: ChatResponse, request: ChatRequest):
    print(f"[Hook: after_request] Request complete! Provider used: {response.provider}")


def main():
    # Register lifecycle event hooks
    on("before_request", on_before_request)
    on("after_request", on_after_request)

    response = chat(
        provider="groq",
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "What is Python?"}],
    )

    print("Result:", response.content[:100], "...")


if __name__ == "__main__":
    main()
