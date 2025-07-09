# AI Code Agent Instructions - User Story Implementation

## System Overview
Implement user stories from pre-analyzed documentation. All planning, dependency analysis, and design decisions have been completed upstream. Your job: code, test, validate.

## Input Documents (Pre-Analyzed)
- **User Story Documentation**: Ready-to-implement stories with dependencies resolved
- **Implementation Documentation**: Complete API specification with class structures
- **Python Code Guidelines**: Coding standards to follow

## Core Workflow

### 1. Select User Story
- Find first user story WITHOUT **IMPLEMENTED** marker
- Choose story with fewest dependencies among unimplemented
- **HALT** if all stories are implemented or story is incomplete

### 2. Implement Code
- Follow implementation documentation exactly
- Follow Python code guidelines for all code decisions
- Create files in specified package structure
- Implement MVP only - no extras
- **HALT** after 3 failed correction attempts

### 3. Generate Tests
- Create module-level test files (`test_value_objects.py`, etc.)
- Test all acceptance criteria (happy path + edge cases)
- Unit tests: mock external dependencies
- Integration tests: test class interactions
- Use pytest framework

### 4. Validate
- Run new tests first
- Run all existing tests
- **HALT** if any tests fail after corrections
- Verify acceptance criteria are met

### 5. Update Documentation
- Add **IMPLEMENTED** below user story name
- Add implementation results at bottom of user story

## Halt Conditions
- **Missing Dependencies**: Referenced classes/modules don't exist → Accept and continue
- **Circular Dependencies**: Detected → HALT
- **Test Failures**: After 3 correction attempts → HALT
- **Incomplete Stories**: Missing critical information → HALT
- **File System Errors**: Cannot create required files → HALT

## Error Handling
- **Recoverable**: Log error, continue processing
- **Critical**: HALT with diagnostic information
- Follow error handling specified in user stories

## Success Criteria
1. All acceptance criteria implemented
2. All tests pass (new and existing)
3. Code follows Python guidelines
4. User story marked **IMPLEMENTED**
5. No breaking changes to existing code

## Output Requirements
- **Implementation Summary**: What was built
- **Test Results**: Pass/fail status
- **File Locations**: Where code was created
- **Any Issues**: Problems and resolutions