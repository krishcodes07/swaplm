# Contributing to SwapLM

Thank you for your interest in contributing to **SwapLM**! We welcome contributions from developers of all skill levels.

---

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/krishcodes07/swaplm.git
   cd swaplm
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/macOS
   source .venv/bin/activate
   ```

3. **Install dependencies in editable mode**:
   ```bash
   pip install -e ".[dev]"
   ```

---

## Coding Guidelines & Standards

- **Code Formatting & Linting**: We use [Ruff](https://github.com/astral-sh/ruff) for linting and code formatting.
  ```bash
  ruff check .
  ruff format --check .
  ```
- **Type Annotations**: All code must be typed using standard Python type hints.
- **Pydantic v2**: All data schemas should extend `pydantic.BaseModel`.

---

## Testing

Run the test suite using `pytest`:
```bash
pytest -v
```

Before submitting a Pull Request, verify that all checks pass:
```bash
ruff check .
ruff format --check .
pytest
```

---

## Adding a New Provider Adapter

Adding a new OpenAI-compatible provider adapter is metadata-driven and requires no code logic changes:
1. Create `swaplm/providers/<provider_id>/`
2. Add `__init__.py` exporting your Provider class.
3. Add `provider.py` implementing `BaseProvider` with `ProviderInfo`.
4. Add `models.json` listing supported models and capability flags.
5. Register unit tests in `tests/test_openai_providers_expansion.py`.
