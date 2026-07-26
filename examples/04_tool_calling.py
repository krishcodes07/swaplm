"""Function / Tool calling example using SwapLM."""

from swaplm import Tool, chat


def get_current_weather(location: str, unit: str = "celsius"):
    """Mock weather function."""
    return f"The weather in {location} is 22°{unit.upper()} and sunny."


def main():
    # Define tool definition
    weather_tool = Tool(
        name="get_current_weather",
        description="Get the current weather for a given location",
        parameters={
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and state, e.g. San Francisco, CA",
                },
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["location"],
        },
    )

    response = chat(
        provider="groq",
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "What is the weather in Tokyo?"}],
        tools=[weather_tool],
    )

    if response.tool_calls:
        print("Tool call requested by LLM:")
        for tool_call in response.tool_calls:
            print(f"- Function: {tool_call.function.name}")
            print(f"  Arguments: {tool_call.function.arguments}")


if __name__ == "__main__":
    main()
