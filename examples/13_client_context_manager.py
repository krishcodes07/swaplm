"""Example 13: Client Connection Lifecycle.

Demonstrates using Client and AsyncClient as context managers to guarantee
underlying HTTP connections are properly closed without resource leaks.
"""

import asyncio

from swaplm import AsyncClient, Client


def sync_example():
    print("--- Sync Client Context Manager ---")
    with Client(timeout=30.0) as client:
        try:
            response = client.chat(
                provider="groq",
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": "Say hello in 3 words."}],
            )
            print(f"Response: {response.content}")
        except Exception as err:
            print(f"Sync Note: {err}")
    # HTTP transport is automatically closed here


async def async_example():
    print("\n--- Async Client Context Manager ---")
    async with AsyncClient(timeout=30.0) as client:
        try:
            response = await client.chat(
                provider="groq",
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": "Say hi in 3 words."}],
            )
            print(f"Async Response: {response.content}")
        except Exception as err:
            print(f"Async Note: {err}")
    # Async HTTP transport is automatically closed here


def main():
    sync_example()
    asyncio.run(async_example())


if __name__ == "__main__":
    main()
