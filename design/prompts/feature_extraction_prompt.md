# Feature Extraction Prompt

## Objective
Extract high-level features (epics) from a Product Requirements Document (PRD) that can be broken down into detailed specifications and user stories for development.

## Instructions

You are analyzing a Product Requirements Document to identify the core features that need to be built. Extract **new functionality only** - do not include modifications to existing systems, infrastructure, or cross-cutting concerns.

### Feature Identification Guidelines

1. **Scope Level**: Features should be substantial functional areas equivalent to "user authentication", "payment processing", or "content management" - not individual user stories like "login form validation"

2. **Maximum Count**: Extract no more than **12 features** total. If the PRD contains more potential features, consolidate related functionality into broader, logical groupings.

3. **Completeness**: Be exhaustive - capture all new functionality described in the PRD, consolidating as needed to stay within the 12-feature limit.

### Output Format

For each feature, provide:

## Feature: Clear, descriptive name
**Description**: 2-3 sentence functional description of what this feature accomplishes
**Dependencies**: List any hard dependencies (must be completed first) and soft dependencies (would benefit from being completed first) on other features from your extracted list

### Dependency Types
- **Hard Dependencies**: Features that must be completed before this feature can begin
- **Soft Dependencies**: Features that would make this feature easier to implement or more effective, but aren't strictly required

### Quality Checks
Each feature should be:
- Substantial enough to warrant its own detailed specification document
- Decomposable into multiple user stories for development
- Testable as a complete, contained unit of functionality
- Appropriately sized for review by a human before breaking into user stories

### Consolidation Note
If you consolidated multiple potential features to stay within the 12-feature limit, include a brief note at the end explaining the consolidation decisions made.

## Example Output Structure

## Feature: User Authentication

**Description**: Comprehensive user authentication system allowing users to register, login, logout, and manage their account credentials. Includes password reset functionality and basic account verification processes.

**Dependencies**: None

## Feature: User Profile Management  
**Description**: Enables users to create, view, edit, and manage their personal profiles including personal information, preferences, and account settings. Provides the foundation for personalized user experiences.
**Dependencies**: Hard - User Authentication

---

Now analyze the provided PRD and extract the features following these guidelines.