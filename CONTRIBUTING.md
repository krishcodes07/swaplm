# Contributing to SwapLM

Thank you for your interest in contributing to SwapLM! This guide will help you get started.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git

### Development Setup

1. **Fork and clone** the repository:

   ```bash
   git clone https://github.com/<your-username>/swaplm.git
   cd swaplm
   ```

2. **Create a virtual environment** and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -e ".[dev]"
   ```

3. **Verify your setup**:

   ```bash
   ruff check .
   pytest
   ```

## Development Workflow

### Branching

- Create a feature branch from `main`:

  ```bash
  git checkout -b feature/your-feature-name
  ```

- Use descriptive branch names: `feature/add-openai-provider`, `fix/streaming-timeout`, `docs/update-readme`.

### Making Changes

1. Write your code following the project's style and conventions.
2. Add or update tests for any new functionality.
3. Run the full check suite before committing:

   ```bash
   ruff check .
   ruff format .
   pytest
   ```

### Commit Messages

Use clear, descriptive commit messages:

```
feat: add OpenAI provider implementation
fix: handle empty response from Anthropic API
docs: update installation instructions
test: add streaming integration tests
chore: update CI configuration
```

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Pull Requests

1. Push your branch and open a pull request against `main`.
2. Fill out the PR template with a clear description of your changes.
3. Ensure all CI checks pass.
4. Request a review from a maintainer.

## Code Style

### Formatting and Linting

SwapLM uses **Ruff** for both formatting and linting. Do not use Black, Flake8, or isort.

```bash
# Check for lint errors
ruff check .

# Auto-fix lint errors
ruff check --fix .

# Format code
ruff format .
```

### Type Annotations

- Use type annotations for all function signatures.
- Use `from __future__ import annotations` where appropriate.
- Prefer standard library types (`list`, `dict`, `tuple`) over `typing` equivalents in Python 3.10+.

### Documentation

- Write docstrings for all public modules, classes, and functions.
- Use Google-style docstrings.
- Keep docstrings concise and focused.

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test file
pytest tests/test_example.py

# Run tests matching a pattern
pytest -k "test_pattern"
```

### Writing Tests

- Place tests in the `tests/` directory, mirroring the source structure.
- Name test files with the `test_` prefix.
- Write focused, descriptive test names: `test_chat_returns_response_content`.
- Aim for high coverage of public API surfaces.

## Project Structure

```
swaplm/               # Source package
├── auth/             # API key management
├── protocols/        # Shared API protocols
├── providers/        # Vendor-specific adapters
├── models/           # Pydantic schemas
├── router/           # Model → provider routing
├── streaming/        # Streaming utilities
├── utils/            # Shared helpers
└── resources/        # Static assets

docs/                 # Documentation
examples/             # Usage examples
tests/                # Test suite
```

## Reporting Issues

- Use [GitHub Issues](https://github.com/krishcodes07/swaplm/issues) to report bugs or request features.
- Include reproduction steps, expected behavior, and actual behavior.
- Attach relevant logs or error messages.

## Code of Conduct

Be respectful and inclusive. We are committed to providing a welcoming and harassment-free experience for everyone.

## Questions?

If you have questions or need help, open a [Discussion](https://github.com/krishcodes07/swaplm/discussions) on GitHub.

---

Thank you for helping make SwapLM better! 🚀
