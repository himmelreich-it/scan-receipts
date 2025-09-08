# AI Code Agent Instructions - User Story Implementation

## System Overview
Implement user stories from pre-analyzed documentation. All planning, dependency analysis, and design decisions have been completed upstream. Your job: code, test, validate.

## Input Documents (Pre-Analyzed)
- **User Story Documentation**: Ready-to-implement stories with dependencies resolved
- **Implementation Specification**: Architectural design with interface definitions and design patterns
- **Python Code Guidelines**: Coding standards to follow

## Core Workflow

### 1. Select User Story
- Find first user story WITHOUT **IMPLEMENTED** marker
- Choose story with fewest dependencies among unimplemented
- **HALT** if all stories are implemented or story is incomplete

### 2. Implement Code
- Use implementation specification as architectural guidance - interface definitions, design patterns, algorithms
- Implement actual working code based on the specification's contracts and user story acceptance criteria
- If specification is ambiguous or incomplete, **HALT** with specific questions
- Follow Python code guidelines for all code decisions
- Create files in specified package structure only
- Implement MVP only - no extras beyond acceptance criteria
- **HALT** after 3 failed correction attempts

### 3. Handle Missing Dependencies
When encountering calls to unimplemented functionality:

#### Create Dummy Implementation
```python
def missing_feature_placeholder(*args, **kwargs):
    """
    PLACEHOLDER: This feature is not yet implemented.
    
    Expected implementation based on user story analysis:
    - User Story Reference: [US-XXX]
    - Expected functionality: [describe what this should do]
    - Expected parameters: [list expected args/kwargs]
    - Expected return: [describe expected return value/type]
    
    TODO: Implement this when [referenced user story] is completed
    """
    import logging
    logging.warning(f"Called unimplemented feature: {missing_feature_placeholder.__name__}")
    
    # Return appropriate dummy data based on expected return type
    # For collections: return empty list/dict
    # For objects: return None or minimal mock object
    # For primitives: return sensible default
    return None  # Adjust based on expected return type
```

#### Logging Requirements
```python
import logging

# Log every call to unimplemented functionality
logging.warning(
    f"UNIMPLEMENTED_DEPENDENCY: {function_name} "
    f"from story {current_story_id} "
    f"requires {dependency_story_id}"
)
```

### 4. Generate Tests
- Test ONLY acceptance criteria explicitly stated in user story
- DO NOT invent additional test cases or edge cases
- Unit tests: mock external dependencies using dummy implementations
- Integration tests: test only class interactions specified in story
- BDD tests: implement step definitions for scenarios from implementation design
- Use pytest framework for unit/integration, behave for BDD
- Test structure:
  ```python
  def test_acceptance_criteria_1():
      """Test: [copy exact acceptance criteria text]"""
      # Implementation
  ```

### 5. Validate
- Run new tests first
- Run all existing tests
- Run BDD scenarios: `behave tests/bdd/`
- **HALT** if any tests fail after corrections
- Verify acceptance criteria are met exactly as written

### 6. Update Documentation
- Add `**Status:**: IMPLEMENTED  ` below user story name
- Add implementation results at bottom of user story:
  ```
  ## Implementation Results
  - Files created: [list with paths]
  - Dependencies mocked: [list with references to user stories]
  - Tests created: [count and types]
  - BDD scenarios: [count and status]
  - All acceptance criteria: PASS/FAIL
  ```

## BDD Implementation Guidelines

### Step Definition Creation
- Implement step definitions in `tests/bdd/steps/`
- Map each step to corresponding application functionality
- Use page object pattern for UI interactions where applicable
- Reuse step definitions across scenarios where possible
- Only implement step definitions for scenarios related to current user story
- Prevent pylance errors:
  - Use unique names for step implementations, prevent
  - Use `# type: ignore` comment on behave decorator

### BDD Test Structure
```python
# tests/bdd/steps/feature_steps.py
from behave import given, when, then
from your_app.main import YourApp

@given('the system is initialized')
def step_impl(context):
    context.app = YourApp()

@when('user performs action')
def step_impl(context):
    context.result = context.app.perform_action()

@then('expected outcome occurs')
def step_impl(context):
    assert context.result.status == "expected_value"
```

### BDD Run instructions
Run `behave` from the root of the project with `src` as `PYTHONPATH`. This ensures all imports are implemented correctly.

### BDD Validation Requirements
- Step definitions must call actual application code (no mocks in BDD tests)
- Use context object to share state between steps
- Clear assertion messages for failed scenarios
- Handle missing dependencies with logged placeholders in step definitions

## Strict Boundaries

### DO NOT:
- Implement features not explicitly in acceptance criteria
- Add error handling not specified in user story
- Create additional classes/methods beyond specification
- Optimize code beyond basic functionality
- Add logging/monitoring beyond dummy dependency tracking
- Implement security features unless explicitly required
- Add input validation beyond what's specified

### ONLY DO:
- Implement exact acceptance criteria
- Follow provided Python code guidelines
- Create specified file structure
- Generate tests for stated acceptance criteria
- Implement BDD step definitions for current user story scenarios
- Handle missing dependencies with logged placeholders

## Halt Conditions
- **Missing/Ambiguous Specification**: Cannot determine exact requirements → HALT
- **Circular Dependencies**: Detected → HALT
- **Test Failures**: After 3 correction attempts → HALT
- **BDD Scenario Failures**: Scenarios don't match application behavior → HALT
- **Missing Step Definitions**: Scenarios can't execute → HALT
- **Incomplete Stories**: Missing critical information → HALT
- **File System Errors**: Cannot create required files → HALT

## Error Handling Protocol
1. **First Attempt**: Fix obvious syntax/import errors
2. **Second Attempt**: Review against acceptance criteria
3. **Third Attempt**: Simplify implementation to bare minimum
4. **After Third Failure**: HALT with diagnostic information

## Dummy Implementation Guidelines

### For Missing Classes:
```python
class PlaceholderClass:
    """
    PLACEHOLDER: Class not yet implemented
    User Story: [US-XXX]
    Expected interface: [list methods/properties from analysis]
    """
    def __init__(self, *args, **kwargs):
        logging.warning(f"Using placeholder for {self.__class__.__name__}")
        
    def expected_method(self, *args, **kwargs):
        logging.warning(f"Called unimplemented method: {self.expected_method.__name__}")
        return None
```

### For Missing Functions:
```python
def placeholder_function(*args, **kwargs):
    """
    PLACEHOLDER: Function not yet implemented
    User Story: [US-XXX]
    Expected behavior: [describe from analysis]
    """
    logging.warning(f"Called unimplemented function: {placeholder_function.__name__}")
    return None  # or appropriate default
```

### For Missing Constants/Config:
```python
# PLACEHOLDER: Configuration not yet implemented
# User Story: [US-XXX]
# Expected values: [describe from analysis]
PLACEHOLDER_CONFIG = {
    'default_value': None,
    'placeholder_note': 'Implement when US-XXX is completed'
}
```

## Success Criteria
1. All acceptance criteria implemented exactly as written
2. All tests pass (unit, integration, and BDD)
3. All BDD scenarios execute successfully
4. Code follows Python guidelines exactly
5. User story marked **IMPLEMENTED**
6. No breaking changes to existing code
7. All missing dependencies properly logged with references

## Output Requirements
- **Implementation Summary**: What was built (only features in acceptance criteria)
- **Test Results**: Pass/fail status with test names
- **BDD Results**: Pass/fail status for scenarios
- **File Locations**: Exact paths where code was created
- **Placeholder Dependencies**: List of dummy implementations with user story references
- **Any Issues**: Problems and resolutions
- **Acceptance Criteria Status**: PASS/FAIL for each criterion