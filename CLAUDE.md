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

## Feature Extraction
When asked to extract high-level features:
- Use `design/product_requirements.md` to extract features from
- Use `design/prompts/feature_extraction_prompt.md` as the prompt/context for analysis
- Use `design/rules/ddd_agent_instructions.md` as design principles
- Write all extracted features to the file specified in the user's instruction


## Design Next Feature
When the user types "design next feature":
- Read `design/high_level_features.md` to understand available features
- Read `design/product_requirements.md` for context
- Apply `design/rules/ddd_agent_instructions.md` principles
- Use `design/prompts/user_story_creation_prompt.md` to start an interactive session
- Guide the user through feature selection and user story creation

## Create API Documentation
When the user instructs "create API for {user_stories_file}":
- Use `design/prompts/api_design_instructions.md` as the main prompt/context for API design
- Apply DDD principles from `design/rules/ddd_agent_instructions.md`
- Reference feature descriptions from `design/high_level_features.md`
- Use requirements context from `design/product_requirements.md`
- Follow Python coding standards from `design/rules/python_agent_instructions.md`
- Create comprehensive API documentation following the package-based structure outlined in the API design instructions