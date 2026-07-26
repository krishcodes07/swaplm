"""Asynchronous chat completion example using SwapLM."""

import asyncio

from swaplm import achat


async def main():
    # Execute an async chat completion with OpenAI
    response = await achat(
        model="openai/gpt-4o-mini",
        messages=[
            {"role": "user", "content": "What are three key benefits of asynchronous programming?"}
        ],
    )

    print("Model:", response.model)
    print("Provider:", response.provider)
    print("Response:\n", response.content)


if __name__ == "__main__":
    asyncio.run(main())
