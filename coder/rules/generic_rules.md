# Claude Development Guidelines

## Python Development
Please refer to `design/rules/python_agent_instructions.md` for comprehensive Python coding standards and best practices.

## Architecture
Please refer to `design/rules/hexagonal_architecture_guide.md` for architectural patterns and practices when:
- Designing features and breaking down requirements into features or stories
- Creating domain models and bounded contexts

## Testing Commands
- Run unit tests: `uv run --env-file .env.testing pytest tests/unit/`
- Run integration tests: `uv run --env-file .env.testing pytest tests/integration/`
- Run BDD tests: `uv run --env-file .env.testing behave tests/bdd`
- Run all tests: `uv run pytest`
- Run with coverage: `uv run pytest --cov=src`
- Do NOT run tests using `python` or `uv python` command directly, for testing, create and remove a file rather than passing python code to the command line.

## Development Setup
- Use `uv` for dependency management
- Create virtual environment: `uv venv`
- Install dependencies: `uv sync`
- Add new dependencies: `uv add <package>`

## Code Quality
- Run linting: `uv run ruff check`
- Run formatting: `uv run ruff format`
- Run type checking: `npx pyright`

## Github CLI
- Tickets can be found in Github and the `gh` cli is available
- Tickets can be created by `gh issue create --title "$title" --body "$body" --project "$github_project_name"`
- Tickets can be edited by `gh issue edit $ticket_number --title "$title" --body "$body" --project "$github_project_name"`
- Working on a ticket requires creating a branch for given ticket: `gh issue develop $ticket_number --checkout`
- Once tickets are done, a pr is created: `gh pr create --title "$title" --body "$body" --project "$github_project_name"`
- Tickets need to be assigned to the project given:
  - project_number: 2
  - project_name: scan-receipts