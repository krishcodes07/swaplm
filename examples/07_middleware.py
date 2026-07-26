"""Middleware interceptor example using SwapLM."""

import time

from swaplm import BaseMiddleware, ChatRequest, ChatResponse, add_middleware, chat


class TimingMiddleware(BaseMiddleware):
    """Custom middleware measuring total request execution time."""

    def process_request(self, request: ChatRequest) -> ChatRequest:
        request.extra["_start_time"] = time.time()
        print(f"[Middleware] Request payload targeting model: {request.model}")
        return request

    def process_response(self, response: ChatResponse, request: ChatRequest) -> ChatResponse:
        start_time = request.extra.get("_start_time", time.time())
        duration = time.time() - start_time
        print(
            f"[Middleware] Response received in {duration:.3f}s from provider: {response.provider}"
        )
        return response


def main():
    # Register custom middleware
    add_middleware(TimingMiddleware())

    # Chat execution automatically runs through registered middlewares
    response = chat(
        model="groq/llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Hello!"}],
    )

    print("Response Content:", response.content)


if __name__ == "__main__":
    main()
