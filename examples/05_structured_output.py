"""Structured JSON response example using SwapLM."""

import json

from pydantic import BaseModel

from swaplm import chat


class MovieRecommendation(BaseModel):
    title: str
    year: int
    genre: str
    summary: str


def main():
    # Request structured JSON output conforming to a Pydantic schema
    response = chat(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": "Recommend a classic sci-fi movie."}],
        response_format={"type": "json_object"},
    )

    print("Raw Content:", response.content)
    parsed = json.loads(response.content)
    print("Parsed Keys:", list(parsed.keys()))


if __name__ == "__main__":
    main()
