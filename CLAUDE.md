# Claude Development Guidelines

## Python Development
Please refer to `coder/rules/python_agent_instructions.md` for comprehensive Python coding standards and best practices.

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

## Code Quality Commands
- Run linting on source: `uv run ruff check src`
- Run linting on tests: `uv run ruff check tests`
- Run formatting: `uv run ruff format`
- Run type checking: `npx pyright`
- Fix linting issues: `uv run ruff check --fix`

## Development Setup
- Use `uv` for dependency management
- Create virtual environment: `uv venv`
- Install dependencies: `uv sync`
- Add new dependencies: `uv add <package>`

## GitHub Operations

### Working with Issues
- View issue details: `gh issue view $number`
- Create issue: `gh issue create --title "$title" --body "$body" --project "scan-receipts"`
- Edit issue: `gh issue edit $number --title "$title" --body "$body"`
- Start work on issue: `gh issue develop $number --checkout`
- Add label to issue: `gh issue edit $number --add-label "implemented"`
- Comment on issue: `gh issue comment $number --body "$comment"`

### Working with Pull Requests
- Create PR: `gh pr create --title "$title" --body "$body" --project "scan-receipts"`
- View PR: `gh pr view $number`
- Comment on PR: `gh pr comment $number --body "$comment"`

### Git Operations
- Pull latest from main: `git pull origin main`
- Push branch: `git push -u origin branch-name`
- Check status: `git status`
- Stage changes: `git add .`
- Commit with message: `git commit -m "feat: description (#$number)"`

### Project Configuration
- project_number: 2
- project_name: scan-receipts
- main branch: main