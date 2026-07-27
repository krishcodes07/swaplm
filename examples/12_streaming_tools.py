"""Example 12: Streaming Tool Calls.

Demonstrates receiving tool call deltas in real-time during streaming.
"""

from swaplm import chat


def main():
    weather_tool = {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {"location": {"type": "string", "description": "City name"}},
                "required": ["location"],
            },
        },
    }

    print("Streaming request with tools...")
    try:
        stream = chat(
            provider="groq",
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
            tools=[weather_tool],
            stream=True,
        )

        for chunk in stream:
            # High-level convenience property for tool calls
            if chunk.tool_calls:
                for tc in chunk.tool_calls:
                    if tc.function and tc.function.name:
                        print(f"\nTool call requested: {tc.function.name}")
                    if tc.function and tc.function.arguments:
                        print(f"Arg delta: {tc.function.arguments}", end="", flush=True)
            elif chunk.content:
                print(chunk.content, end="", flush=True)

        print("\n\nStream finished.")
    except Exception as err:
        print(f"API Call Note: {err}")


if __name__ == "__main__":
    main()
