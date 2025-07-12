# Claude Development Guidelines

## Python Development
Please refer to `design/rules/python_agent_instructions.md` for comprehensive Python coding standards and best practices.

## Domain-Driven Design (DDD)
Please refer to `design/rules/ddd_agent_instructions.md` for comprehensive DDD patterns and practices when:
- Designing features and breaking down requirements into features or stories
- Creating domain models and bounded contexts
- Implementing tactical DDD patterns (entities, value objects, aggregates, etc.)

## C4 Architecture Diagrams
When creating C4-like diagrams, follow the DDD guidelines in `design/rules/ddd_agent_instructions.md` to ensure:
- Proper bounded context identification and boundaries
- Correct context mapping relationships
- Domain-focused component naming and descriptions

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



## Implement User Story
When the user instructs "implement next user story from file YY":
- Use `design/prompts/ai_code_agent_instructions.md` as the main implementation guide
- Follow Python coding standards from `design/rules/python_agent_instructions.md`
- Reference feature descriptions from `design/high_level_features.md` for additional context
- Apply DDD principles from `design/rules/ddd_agent_instructions.md` for domain modeling
- Follow the exact workflow outlined in the AI code agent instructions





## Design and Implement Next Feature
When the user instructs "design and implement next feature", we walk the user through the following process. See chapters in this file
1. Design Next Feature
2. Implement User Story (with the user stories file just created)
3. Create Implementation Design Documentation (with the user stories file just created)
4. Implement Feature (with the user stories file just created)
5. Integrate Implemented Feature (just created feature)
