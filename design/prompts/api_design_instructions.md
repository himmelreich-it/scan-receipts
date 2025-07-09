# AI Agent Instructions: API Documentation Generation from User Stories

## Objective
Generate comprehensive API documentation for Python applications based on user stories and acceptance criteria. The documentation serves as a contract for AI coding agents and ensures consistency across multiple features.

## Input Files Expected
- **User Stories File**: Contains user stories with acceptance criteria and dependency references
- **Feature Document**: Contains higher-level feature requirements and inter-feature dependencies
- **Product Requirements**: Contains business context and constraints
- **DDD Design Principles**: Contains domain-driven design guidelines
- **Python Guidelines**: Contains Python-specific coding standards and patterns

## Core Responsibilities

### 1. User Story Analysis
- Process all user stories in topological order (dependencies first)
- Extract acceptance criteria for each story
- Identify dependent user stories and cross-feature dependencies
- Map acceptance criteria to required API contracts (not implementations)

### 2. API Contract Design
Design API contracts for all granularity levels:
- **HTTP APIs**: Endpoint signatures, request/response schemas
- **Python Modules and Classes**: Module structure, class definitions, and method signatures
- **Event/Message Interfaces**: Event schemas and publisher/consumer contracts
- **Configuration Interfaces**: Settings schemas and validation rules

### 3. Dependency Management
- Build dependency graph from user story references and feature dependencies
- Ensure all dependent user stories' API requirements are met
- Validate API contract compatibility with existing features
- Flag contract changes that would break existing consumers

## File Structure Organization

### Package-Based Documentation
**IMPORTANT**: Create one separate API documentation file for each Python package that will be created or modified based on the user stories. DO NOT create a single documentation file for all user stories.

For each Python package:
- **Create**: `[package_name]_api_documentation.md`
- **Content scope**: All modules, classes, and internal APIs within that specific package only
- **Grouping logic**: Keep related functionality together by package boundaries
- **One file per package**: Each package gets its own dedicated documentation file

### Documentation Updates
- **Existing Files**: Update existing package documentation files when processing user stories
- **New Additions**: Add new API sections to existing files when user stories extend existing packages
- **Merge Strategy**: Preserve existing API documentation while adding new requirements
- **Consistency**: Ensure new APIs follow established patterns within the package

## Processing Workflow

### Step 1: Dependency Analysis
1. Parse all user stories to extract dependency references
2. Parse feature documents for inter-feature dependencies
3. Create dependency graph and determine processing order
4. Identify potential conflicts between dependent stories
5. Identify which Python packages will be affected

### Step 2: Package Analysis
1. **Identify Python packages** that will be created or modified based on user stories
2. **Determine which existing package documentation files** exist for these packages
3. **Analyze existing API patterns** within each existing package
4. **Plan new package documentation files** for packages that don't have documentation yet

### Step 3: API Contract Design
For each user story (in dependency order):
1. Analyze acceptance criteria to determine API contract requirements
2. Check contract requirements of all dependent user stories
3. Design API contracts that satisfy all requirements
4. Ensure contract consistency with existing API patterns within the package
5. Handle contract conflicts by proposing solutions or halting for resolution

### Step 4: API Documentation Generation
**For each Python package identified**:
- Generate a new `[package_name]_api_documentation.md` file, OR
- Update an existing `[package_name]_api_documentation.md` file
- Each file contains only the APIs for that specific package
- Do not create a single documentation file covering multiple packages

## Documentation Format

### API Documentation Principles
- **Minimal and Concise**: Only document the public API surface
- **No Implementation Details**: Focus on contracts, not code
- **Pseudo-code Style**: Use Python-looking syntax without full implementations
- **Public API Focus**: Only include imports/decorators that are part of the public API
- **No Internal Code**: Avoid showing internal methods, private functions, or implementation logic

### For Each API, Include:

#### API Specification
- **Function/Method Signatures**: Signature only with type hints, no implementation
- **HTTP Endpoints**: Method, path, parameters (no route decorators unless part of public API)
- **Request/Response Schemas**: Structure and types, not full examples
- **Error Handling**: What errors are returned, not how they're implemented
- **Authentication/Authorization**: Requirements only
- **Rate Limiting**: Constraints only

#### Usage Examples
- **API Call Examples**: How to call the API, not how it's implemented
- **Request/Response Examples**: Expected input/output format
- **Integration Examples**: How to use with other APIs (interface level)
- **Error Handling Examples**: What errors to expect and handle

#### Test Instructions
- **Test Scenarios**: What to test, not how to implement tests
- **Expected Behaviors**: What the API should do under different conditions
- **Mock Requirements**: What data/responses are needed for testing
- **Acceptance Criteria Mapping**: How tests verify each acceptance criterion

#### Dependency Information
- **Dependent User Stories**: List all user stories that rely on this API
- **Feature Dependencies**: Cross-feature relationships
- **API Dependencies**: Other APIs this one depends on

## Quality Assurance

### Validation Requirements
- **Acceptance Criteria Coverage**: Every acceptance criterion must be addressable through the designed APIs
- **Dependency Satisfaction**: All referenced dependencies must be properly handled
- **Backward Compatibility**: No breaking changes to existing APIs
- **Package Consistency**: New APIs within a package must follow established patterns

### Consistency Requirements
- **Naming Conventions**: Enforce consistent naming across all APIs
- **REST Principles**: Follow REST architectural constraints
- **Python Guidelines**: Adhere to provided Python coding standards
- **Error Handling**: Consistent error response patterns

## Conflict Resolution

### When Conflicts Arise
1. **Analyze Conflict**: Identify the conflicting requirements
2. **Propose Solution**: Suggest resolution (e.g., optional fields, conditional responses)
3. **Document Assumptions**: Record any assumptions made in resolution
4. **If Unsolvable**: Halt processing and alert user with specific conflict details

### Deprecation Alerts
When existing APIs need changes that would break backward compatibility:
- **Alert**: Highlight the problem clearly
- **Recommendation**: Suggest creating new API version
- **Impact**: Document which features/stories would be affected

## Output Structure

### Package Documentation Files
Each `[package_name]_api_documentation.md` file should contain:

#### 1. Package Overview
- **Purpose**: What this package handles
- **Key Components**: Main modules and classes
- **Dependencies**: Other packages this depends on
- **User Stories Served**: List of user stories implemented in this package

#### 2. HTTP APIs (if applicable)
- **Endpoints**: REST endpoint documentation
- **Request/Response Schemas**: Complete with examples
- **Error Handling**: Package-specific error patterns

#### 3. Python Class Interfaces
- **Public Classes**: Class signatures and public methods only
- **Method Signatures**: Parameters, return types, no implementation
- **Properties**: Public properties with types
- **Usage Patterns**: How to instantiate and use classes

#### 4. Event/Message Interfaces (if applicable)
- **Event Types**: Event names and payload structures
- **Message Schemas**: Data structures only
- **Publisher/Consumer Contracts**: Interface definitions

#### 5. Configuration Interfaces (if applicable)
- **Settings Structure**: Configuration schema
- **Environment Variables**: Required variables and types
- **Defaults**: Default values only

#### 6. Internal APIs
- **Module Functions**: Public function signatures only
- **Inter-module Contracts**: Interface definitions between modules
- **Utility Functions**: Function signatures for shared utilities

### API Documentation Examples

#### Package Structure Example
```
## Package: myapp.user
**Package Path**: `myapp/user/`
**Purpose**: User management functionality

**Modules**:
- myapp.user.models (User data models)
- myapp.user.services (User business logic)
- myapp.user.handlers (HTTP request handlers)
- myapp.user.events (User-related events)
```

#### HTTP API Example
```
## POST /api/users
**Module**: myapp.user.handlers
**Purpose**: Create a new user
**Handler Function**: create_user_handler

**Request**: 
- Body: UserCreateRequest
- Headers: Authorization required

**Response**: 
- 201: UserResponse
- 400: ValidationError
- 401: AuthenticationError
```

#### Python Class Example
```
## class UserService
**Module**: myapp.user.services
**Purpose**: Handle user operations

**Methods**:
- create_user(user_data: UserCreateRequest) -> UserResponse
- get_user(user_id: int) -> Optional[UserResponse]
- update_user(user_id: int, updates: UserUpdateRequest) -> UserResponse
- delete_user(user_id: int) -> bool

**Dependencies**: UserRepository (from myapp.user.models)
```

#### Python Function Example
```
## validate_email
**Module**: myapp.user.utils
**Signature**: validate_email(email: str) -> bool
**Purpose**: Validate email format
**Used by**: UserService.create_user
```

#### Event Interface Example
```
## UserCreatedEvent
**Module**: myapp.user.events
**Purpose**: Notify when user is created

**Payload**:
- user_id: int
- user_email: str
- timestamp: datetime

**Publishers**: UserService (myapp.user.services)
**Consumers**: EmailService, AuditService
```

#### 7. Dependencies and Integration
- **Package Dependencies**: Other packages this depends on
- **Integration Points**: How this package integrates with others
- **User Story Cross-References**: Which user stories use which APIs

### File Update Strategy
- **Existing Files**: Read existing package documentation before adding new content
- **Preserve Existing**: Keep all existing API documentation intact
- **Add New Sections**: Append new APIs to appropriate sections
- **Update Cross-References**: Update user story mappings when adding new functionality
- **Maintain Consistency**: Ensure new APIs follow patterns established in the package

### Reference Format for Code Agents
Each API section should include:
```
## API: [API_NAME]
**Serves User Stories**: [STORY_ID_1, STORY_ID_2, ...]
**Depends On**: [DEPENDENCY_APIS]
**Used By**: [DEPENDENT_APIS]
```

## Error Handling

### When to Halt Processing
- Unresolvable conflicts between dependent user stories
- Missing critical dependency information
- Circular dependencies that cannot be resolved
- Acceptance criteria that cannot be satisfied with any API design

### When to Continue with Warnings
- Optional dependencies that are not yet implemented
- Non-critical conflicts that can be resolved with assumptions
- Performance concerns that don't affect functionality

## Final Deliverable

Package-specific API documentation files containing:
- **Complete API specifications** for all user stories within each package
- **Usage examples and test instructions** relevant to the package
- **Dependency mappings** for code agents to understand package relationships
- **Documented assumptions** and design decisions made for the package
- **Alerts** for any deprecation or compatibility issues

The documentation should be structured for easy consumption by AI coding agents and serve as the definitive contract for package implementation. Each package file should be self-contained while clearly documenting integration points with other packages.
