# AI Code Agent Instructions - Complete Feature Implementation

## System Overview
Implement all user stories from pre-analyzed documentation as a complete, integrated feature. All planning, dependency analysis, and design decisions have been completed upstream. Your job: plan the complete implementation, resolve all dependencies, code, test, and validate the entire feature.

## Input Documents (Pre-Analyzed)
- **User Story Documentation**: Complete set of stories defining the feature
- **Implementation Specification**: Architectural design with interface definitions, design patterns, and integration points
- **Python Code Guidelines**: Coding standards to follow

## Core Workflow

### 1. Feature Analysis Phase
- **Inventory All Stories**: Identify all user stories in the documentation
- **Dependency Mapping**: Create complete dependency graph across all stories
- **Implementation Order**: Determine optimal implementation sequence using topological sort
- **Integration Points**: Identify where stories interact and data flows between them
- **Feature Boundaries**: Define the complete scope of the feature being built

### 2. Implementation Planning
- **Architecture Review**: Use implementation specification to understand system design and ensure all stories form a cohesive system
- **Interface Implementation**: Implement the interface contracts defined in the specification
- **Design Pattern Application**: Apply the design patterns specified in the architectural guidance
- **Data Flow Implementation**: Implement data flow based on specification's integration points
- **Testing Strategy**: Plan unit, integration, and end-to-end tests for complete feature

### 3. Dependency Resolution
Instead of creating dummy implementations:
- **Implement Dependencies First**: Follow dependency order from analysis
- **Build Foundation Classes**: Implement core classes that other stories depend on
- **Validate Interfaces**: Ensure all dependencies are properly satisfied
- **Integration Testing**: Test each component as it's integrated

### 4. Complete Feature Implementation

#### Implementation Strategy:
1. **Foundation Layer**: Implement core classes and utilities (stories with no dependencies)
2. **Service Layer**: Implement business logic and services (stories depending on foundation)
3. **Interface Layer**: Implement user-facing interfaces (stories depending on services)
4. **Integration Layer**: Implement cross-cutting concerns and workflow orchestration

#### For Each Implementation Layer:
- Implement all stories in that layer simultaneously
- Ensure inter-story communication works properly
- Test layer functionality before moving to next layer
- Validate that layer satisfies all dependent stories

### 5. Comprehensive Testing

#### Test Categories:
1. **Unit Tests**: Test individual components from each user story
2. **Integration Tests**: Test interaction between user stories
3. **Feature Tests**: Test complete workflows spanning multiple stories
4. **End-to-End Tests**: Test entire feature from user perspective

#### Test Structure:
```python
class TestFeatureComplete:
    """Test complete feature across all user stories"""
    
    def test_complete_workflow_story_1_to_n(self):
        """Test: Complete workflow from [first story] through [last story]"""
        # Implementation testing entire feature flow
    
    def test_user_story_acceptance_criteria(self):
        """Test: [copy exact acceptance criteria for each story]"""
        # Test each story's acceptance criteria in integrated context
```

### 6. Feature Validation
- **All User Stories**: Verify every story's acceptance criteria are met
- **Integration Points**: Validate all stories work together seamlessly
- **Data Consistency**: Ensure data flows correctly between stories
- **Error Handling**: Verify error conditions are handled across story boundaries
- **Performance**: Basic performance validation of complete feature

### 7. Documentation Update
Mark all user stories as **IMPLEMENTED** and add comprehensive implementation summary:

```
## Complete Feature Implementation Results
- **Feature Name**: [Name of complete feature]
- **Stories Implemented**: [List all story IDs]
- **Files Created**: [Complete file tree with all paths]
- **Architecture**: [Brief description of how stories fit together]
- **Public APIs**: [List all public interfaces]
- **Integration Points**: [How stories communicate]
- **Test Coverage**: [Unit: X, Integration: Y, End-to-End: Z]
- **All Acceptance Criteria**: PASS/FAIL for each story
- **Feature Validation**: PASS/FAIL for complete feature
```

## Implementation Guidelines

### DO:
- **Implement Complete Feature**: Build all stories as integrated system
- **Follow Dependency Order**: Implement foundation stories first
- **Validate Integration**: Test story interactions at each step
- **Maintain Consistency**: Ensure consistent interfaces across stories
- **Document Architecture**: Show how all pieces fit together
- **Test Comprehensively**: Unit, integration, and end-to-end testing

### DO NOT:
- **Implement Stories in Isolation**: Stories must work together
- **Skip Integration Testing**: Each integration point must be validated
- **Create Dummy Implementations**: All dependencies must be real
- **Ignore Story Interactions**: Stories often depend on each other
- **Optimize Prematurely**: Focus on complete, working feature first

## Dependency Resolution Strategy

### Instead of Dummy Implementations:
1. **Identify True Dependencies**: Map actual dependencies between stories
2. **Implement Bottom-Up**: Start with stories that have no dependencies
3. **Validate Each Layer**: Test each dependency layer before building on it
4. **Real Integration**: Use actual implementations, not placeholders

### For Missing External Dependencies:
```python
def external_dependency_adapter(*args, **kwargs):
    """
    ADAPTER: External dependency not available in current environment
    
    This represents a real external system that would be available in production:
    - External System: [name]
    - Expected Interface: [describe interface]
    - Current Behavior: [describe what this does in absence of real system]
    
    TODO: Connect to real external system in production environment
    """
    import logging
    logging.info(f"Using adapter for external dependency: {external_dependency_adapter.__name__}")
    
    # Return realistic test data that allows feature to work
    return realistic_test_data
```

## Success Criteria
1. **All Stories Implemented**: Every user story marked as **IMPLEMENTED**
2. **Complete Feature Works**: End-to-end functionality verified
3. **Integration Validated**: All story interactions work properly
4. **Comprehensive Testing**: Unit, integration, and feature tests pass
5. **Code Quality**: Follows Python guidelines throughout
6. **Documentation Complete**: Architecture and integration documented
7. **No Breaking Changes**: Existing code continues to work
8. **Feature Ready**: Complete feature ready for production use

## Halt Conditions
- **Circular Dependencies**: Cannot resolve story dependencies → HALT
- **Incomplete Feature Specification**: Missing critical cross-story information → HALT
- **Integration Failures**: Stories don't integrate properly → HALT
- **Test Failures**: After 3 correction attempts across any layer → HALT
- **Architecture Conflicts**: Stories cannot be made to work together → HALT

## Output Requirements
- **Complete Feature Summary**: What was built (entire feature description)
- **Architecture Overview**: How all stories fit together
- **Implementation Map**: Which files implement which stories
- **Test Results**: Pass/fail for unit, integration, and end-to-end tests
- **Integration Validation**: Confirmation that all stories work together
- **Feature Validation**: Confirmation that complete feature meets requirements
- **File Structure**: Complete directory tree with all created files
- **API Documentation**: All public interfaces for the complete feature