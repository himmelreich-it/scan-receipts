# AI Code Agent Instructions - Feature Implementation

## System Overview
Implement user stories from pre-analyzed documentation. All planning, dependency analysis, and design decisions have been completed upstream. Your job: code, test, validate.

**Input Context**:
- Ticket information in context, otherwise use `gh` to find ticket number $number
- Architecture: `design/architecture/hexagonal_design.md`
- Python coding standards: `coder/rules/python_agent_instructions.md`
- Project commands and configuration: `CLAUDE.md`

## Core Workflow

### 1. Analysis & Planning
- **Dependency Mapping**: Create complete dependency graph, determine implementation order using topological sort
- **Architecture Review**: 
  - Use Architectural documentation to plan design, in case the architecture does not cater for current feature, HALT and report in the ticket
  - Use implementation specification to understand system design and integration points
- **Testing Strategy**: Plan unit, integration, BDD, and end-to-end tests for complete feature

### 2. Implementation & Dependencies

#### Implementation Strategy:
1. **Foundation Layer**: Core classes/utilities (no dependencies)
2. **Service Layer**: Business logic (depends on foundation) 
3. **Interface Layer**: User interfaces (depends on services)
4. **Integration Layer**: Cross-cutting concerns and workflows

#### Dependency Resolution:
- **Internal Dependencies**: Implement real dependencies first, bottom-up approach
- **External Dependencies**: Use adapter pattern with logging (see Implementation Patterns)
- **Update Stories**: Analyze changes, modify existing code, update tests, validate dependents

### 3. Testing & Validation

#### Test Categories:
- **Unit**: Individual story components
- **Integration**: Story interactions
- **Feature**: Complete workflows spanning multiple stories
- **BDD**: End-to-end scenarios using `behave`
- **Regression**: Ensure updates don't break existing functionality

#### Validation Process:
1. Only fix linting and tests which are related to the work you are doing
2. Run type checking and fix errors (see CLAUDE.md for commands)
3. Run linting and fix errors (see CLAUDE.md for commands)
4. Run all tests using commands from CLAUDE.md
5. **HALT** if tests fail after 3 correction attempts
6. Re-run analyzers after test fixes

#### Agent Error Recovery Protocol:
**Note**: This is for the agent's development workflow, not for the generated code.
Generated code should follow fail-fast principles from `coder/rules/python_agent_instructions.md`.

1. **First Attempt**: Fix syntax/import errors
2. **Second Attempt**: Review against acceptance criteria
3. **Third Attempt**: Simplify to bare minimum
4. **After Third Failure**: HALT with diagnostics

## Implementation Patterns

### External Dependencies & Placeholders
For handling missing dependencies, use adapter/placeholder patterns with logging.
See `coder/rules/python_agent_instructions.md` for error handling principles (fail-fast for production code).

### BDD Step Definitions
* Make sure step definitions are unique
* Make sure step implementations are unique

```python
# tests/bdd/steps/feature_steps.py
from behave import given, when, then  # type: ignore
from your_app.main import YourApp

@given('the complete feature is initialized')  # type: ignore
def step_complete_feature_is_initialized(context):
    context.app = YourApp()
    context.feature = context.app.get_feature()

@when('user completes workflow spanning multiple stories')  # type: ignore
def step_user_completes_workflow(context):
    context.result = context.feature.complete_workflow()

@then('all user stories work together seamlessly')  # type: ignore
def step_all_user_stories_work(context):
    assert context.result.all_stories_integrated == True
```

### Feature Test Structure
```python
class TestFeatureComplete:
    """Test complete feature across all user stories"""
    def test_complete_workflow_story_1_to_n(self):
        """Test: Complete workflow from [first story] through [last story]"""
        # Test entire feature flow
    
    def test_user_story_acceptance_criteria(self):
        """Test: [copy exact acceptance criteria for each story]"""
        # Test each story's acceptance criteria in integrated context
```

## Guidelines & Boundaries

### Implementation Rules:
**DO:**
- Implement complete feature as integrated system
- Follow dependency order, validate integration at each step
- Handle updates gracefully without breaking dependent code
- Test comprehensively using commands from CLAUDE.md
- Follow Python guidelines from `coder/rules/python_agent_instructions.md`
- Document per standards in `coder/rules/python_agent_instructions.md`

**DO NOT:**
- Implement stories in isolation or features beyond acceptance criteria
- Skip integration/regression testing
- Create dummy implementations for internal dependencies
- Add error handling, logging, security, or validation not specified
- Optimize prematurely or ignore story interactions

### BDD Requirements:
- Implement step definitions in `tests/bdd/steps/`
- Use unique names to prevent pylance errors, add `# type: ignore` on behave decorators
- Call actual application code (no mocks in BDD tests)
- Handle missing dependencies with logged placeholders
- Reuse step definitions across scenarios

### Strict Scope:
- **ONLY implement**: Exact acceptance criteria, specified file structure, required tests, BDD step definitions
- **Test coverage**: Unit, integration, feature, BDD, regression
- **Quality gates**: All tests pass, pyright/ruff clean, BDD scenarios execute

## Execution Details

**Success Criteria:**
1. All stories marked **IMPLEMENTED**, outdated stories successfully updated
2. Complete feature works end-to-end, all story interactions validated
3. All tests pass using commands from CLAUDE.md
4. Code quality checks pass (linting, type checking) - see CLAUDE.md
5. Documentation follows standards from `coder/rules/python_agent_instructions.md`
6. No breaking changes, feature ready for production

**Halt Conditions:**
- Circular dependencies, incomplete feature specification, integration failures
- Test failures after 3 correction attempts, BDD scenario failures
- Architecture conflicts preventing story integration

**Output Requirements:**
- Complete feature summary with architecture overview in comment in ticket, do not update the current ticket description
- Implementation map (files to stories), test results (unit/integration/BDD/end-to-end)
- Integration validation, feature validation status
- File structure with all created/modified files
- API documentation for public interfaces