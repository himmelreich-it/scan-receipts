# Receipt Processing System

## AI-Enabled Development Process

This project uses meta-prompts and Claude Code for structured development. Follow these steps:

### 1. Extract Features
```
@extract-features
```
Extracts high-level features from `design/product_requirements.md`. When PRD is updated, use this command to update existing features in `design/high_level_features.md`.

### 2. Design Feature
```
@design-feature
```
Creates user stories for a selected feature. Guides you through feature selection and stores user stories in `design/user_stories/`. Use when starting work on a new feature or when requirements change.

### 3. Design Implementation
```
@design-implementation [FEATURE_CODE]
```
Creates implementation design documentation for the feature. Stores designs in `design/implementation/`. Use when technical approach needs updating.

### 4. Implement Code
Choose one approach:

**Individual User Stories:**
```
@implement-userstory [USER_STORY_NAME]
```

**Complete Feature:**
```
@implement-feature [FEATURE_CODE]
```

### 5. Integrate Feature
```
@integrate-feature [FEATURE_CODE]
```
Integrates the completed feature into the system. Use when feature implementation is complete.

## Development Commands

**Setup:**
- `uv sync` - Install dependencies
- `uv venv` - Create virtual environment

**Testing:**
- `uv run pytest tests/unit/` - Unit tests
- `uv run pytest tests/integration/` - Integration tests
- `uv run pytest --cov=src` - With coverage

**Code Quality:**
- `uv run ruff check` - Linting
- `uv run ruff format` - Formatting  
- `uv run mypy src/` - Type checking

## Architecture

Follow hexagonal architecture principles in `design/rules/hexagonal_architecture_guide.md` and Python standards in `design/rules/python_agent_instructions.md`.