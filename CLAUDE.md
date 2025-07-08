# Claude Development Guidelines

## Python Development
Please refer to `design/PYTHON.md` for comprehensive Python coding standards and best practices.

## Testing Commands
- Run unit tests: `uv run pytest tests/unit/`
- Run integration tests: `uv run pytest tests/integration/`
- Run all tests: `uv run pytest`
- Run with coverage: `uv run pytest --cov=src`

## Development Setup
- Use `uv` for dependency management
- Create virtual environment: `uv venv`
- Install dependencies: `uv sync`
- Add new dependencies: `uv add <package>`

## Code Quality
- Run linting: `uv run ruff check`
- Run formatting: `uv run ruff format`
- Run type checking: `uv run mypy src/`