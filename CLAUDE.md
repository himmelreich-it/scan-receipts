# Claude Development Guidelines

## Python Development
Please refer to `coder/rules/python_agent_instructions.md` for comprehensive Python coding standards and best practices.

## Architecture
Please refer to `design/rules/hexagonal_architecture_guide.md` for architectural patterns and practices when:
- Designing features and breaking down requirements into features or stories
- Creating domain models and bounded contexts

## Quality Checks & Testing Commands
- **Run all quality checks and tests**: `uv run nox -s quality`
  - This runs all the following checks automatically:
    - Run linting on source: `uv run ruff check src`
    - Run linting on tests: `uv run ruff check tests`
    - Run type checking: `npx pyright`
    - Run unit tests: `uv run --env-file .env.testing pytest tests/unit/ -v`
    - Run integration tests: `uv run --env-file .env.testing pytest tests/integration/ -v`
    - Run BDD tests: `uv run --env-file .env.testing behave tests/bdd`

## Individual Testing Commands
- Run unit tests: `uv run --env-file .env.testing pytest tests/unit/`
- Run integration tests: `uv run --env-file .env.testing pytest tests/integration/`
- Run BDD tests: `uv run --env-file .env.testing behave tests/bdd`
- Run all tests: `uv run pytest`
- Run with coverage: `uv run pytest --cov=src`
- Do NOT run tests using `python` or `uv python` command directly, for testing, create and remove a file rather than passing python code to the command line.

## Individual Code Quality Commands
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
- Use `gh api` to retrieve all PR comments (including inline)
- Make sure tickets and PRs are associated with the project

### Project Configuration
- project_number: 2
- project_name: scan-receipts
- main branch: main

## Jupyter notebooks and Interactive Python
- Keep separate pieces of functionality in separate blocks so we can run apart
- For configuration, parameters, hardcoded lists: keep them in a cell at the top so we can easily change then
- Keep imports at the top of the notebook in a cell so they are easily visible and available to the whole notebook
- Use `display(df)` for pandas dataframes
- (Jupyter) Each block should have a markdown header:
  ```markdown
  ### {short title}
  {concise description of what the block does}
  ```
- Verify if the information you need is already made available in a cell above, do not load data you already have in another variable
- Do NOT create any tests for notebooks and interactive python files
- Notebooks are not production code, do not try and catch exceptions, unless it is useful for the full process:
  - We do not need to test whether files exist if the cell will not function without it
  - We can put things in try/catch when the cell can continue without it
- Do NOT invent print statements without being asked to do so, summaries are part of the design/instruction
- For output, use Pandas (Dataframes) if possible, we want to levarage VS Code UI and extensions
- Refactor common utilities into *.py files and import them instead of duplicating code