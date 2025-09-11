# Claude Development Guidelines

## Python Development
Please refer to `design/rules/python_agent_instructions.md` for comprehensive Python coding standards and best practices.

## Architecture
Please refer to `design/rules/hexagonal_architecture_guide.md` for architectural patterns and practices when:
- Designing features and breaking down requirements into features or stories
- Creating domain models and bounded contexts


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
- Run type checking: `npx pyright`

## Design and Implement Next Feature
When the user instructs "design and implement next feature", we walk the user through the following process. See chapters in this file
1. Design Next Feature
2. Implement User Story (with the user stories file just created)
3. Create Implementation Design Documentation (with the user stories file just created)
4. Implement Feature (with the user stories file just created)
5. Integrate Implemented Feature (just created feature)

## Github CLI
- Tickets can be found in Github and the `gh` cli is available
- Tickets can be created by `gh issue create --title "$title" --body "$body" --project "project_name"`
- Working on a ticket requires creating a branch for given ticket: `gh issue develop $number --checkout`
- Once tickets are done, a pr is created: `gh pr create --title "$title" --body "$body" --project "project_name"`
- Tickets need to be assigned to the project given:
  - project_number: 2
  - project_name: scan-receipts