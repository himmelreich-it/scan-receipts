# Implementation Design Instructions for AI Coding Agents

## Objective
Generate detailed implementation specifications for Python applications from user stories. Create comprehensive coding instructions that AI agents can follow to build actual code.

**CRITICAL CONSTRAINT**: Only implement what is explicitly required by the user stories and their acceptance criteria. Do not add features, libraries, or design decisions not directly needed to satisfy the acceptance criteria.

## Input Processing
1. **Analyze user stories** in dependency order (dependencies first)
2. **Extract acceptance criteria** and map to implementation requirements
3. **Identify Python packages** that need creation or modification
4. **Create one specification file per package**: `[package_name]_implementation_spec.md`

## Output Format: Implementation Specifications

### Package Structure
```
## Package: [package_name]
**Path**: `[path/to/package]/`  
**Purpose**: [Brief description]  
**User Stories**: [List of user story IDs this package implements]  
**Dependencies**: [List required packages/libraries]
```

### For Each Component, Include:

#### Module Details
- **Module location**: Exact file path  
- **Libraries used**: Specific imports with versions/reasons  
- **Module-level functions**: Signatures with implementation guidance  
- **Module-level properties**: Configuration, constants, globals

#### Class Specifications
- **Class definition**: Inheritance, mixins, decorators  
- **Methods**: Signatures, parameters, return types, implementation notes  
- **Properties**: Getters/setters, validation, caching  
- **Internal methods**: Private methods needed for functionality

#### Implementation Guidance
- **Code samples**: Key methods with pseudocode/real code (only if complexity requires it)  
- **Design patterns**: Which patterns to use and why (only if needed for acceptance criteria)  
- **Error handling**: Exception types, validation strategies (only as specified in user stories)  
- **Data structures**: Internal data handling approaches (minimal viable solution)

#### Technical Details
- **Performance considerations**: Only include if performance requirements are specified in user stories  
- **Security considerations**: Only include if security requirements are specified in user stories  
- **Configuration**: Settings structure, environment variables, defaults (only as needed by acceptance criteria)  
- **Database integration**: Models, queries, migrations (only if data persistence is required)

#### Usage Examples
- **Instantiation**: How to create and configure objects  
- **Common operations**: Typical usage patterns  
- **Integration**: How components work together  
- **API usage**: Request/response examples (if applicable)

#### Testing Requirements
- **Test scenarios**: Specific test cases for acceptance criteria (only test what's specified)  
- **Mock requirements**: What to mock and how (minimal necessary mocking)  
- **Test data**: Required fixtures or data structures (only as needed for acceptance criteria)  
- **Edge cases**: Important boundary conditions to test (only if mentioned in user stories)

#### User Story References
- **Implements**: [List of user story IDs this component implements]  
- **Depends on**: [List of user story IDs this component depends on]  
- **Used by**: [List of user story IDs that use this component]

## Quality Requirements
- **Acceptance criteria coverage**: Every criterion must be implementable  
- **Dependency satisfaction**: All referenced dependencies handled  
- **Code consistency**: Follow Python standards and existing patterns  
- **Package coherence**: Related functionality grouped logically  
- **No feature creep**: Only implement what's explicitly stated in user stories  
- **Justification required**: Every technical decision must trace back to acceptance criteria  
- **Minimal viable implementation**: Choose simplest solution that meets requirements

## Validation Rules
Before including any implementation detail, verify:
1. **Is this required by a user story acceptance criterion?**  
2. **Is this needed to satisfy a stated dependency?**  
3. **Is this the minimal implementation that meets the requirement?**  
4. **Can I trace this decision back to specific user story language?**  
5. **Does this change break any existing dependent user stories?**  
6. **Are all interfaces used by dependent user stories preserved?**

If any answer is "no", do not include the implementation detail.

## Processing Rules
1. **One file per package** - don't mix package specifications  
2. **Update existing files** when adding to existing packages  
3. **Preserve existing content** when updating specifications  
4. **Backward compatibility**: Ensure no breaking changes to interfaces used by existing user stories  
5. **Dependency validation**: Check that all dependent user stories remain satisfiable  
6. **Resolve conflicts** or halt with specific error details  
7. **Document assumptions** made during design decisions

## Backward Compatibility Requirements
When modifying existing packages or interfaces:
- **Preserve existing method signatures** used by dependent user stories  
- **Maintain existing data structures** that dependent user stories rely on  
- **Keep existing configuration options** that dependent user stories require  
- **Preserve existing error handling** that dependent user stories expect  
- **If breaking changes are unavoidable**: Create new versions/methods instead of modifying existing ones

## File Structure
Each `[package_name]_implementation_spec.md` contains:
- Package overview and dependencies  
- Module-by-module implementation details  
- Class-by-class specifications with code samples  
- Configuration and deployment guidance  
- Testing implementation requirements  
- Integration points with other packages

## Example Structure
```
## Package: myapp.user
**Path**: `myapp/user/`  
**Purpose**: User management functionality  
**User Stories**: US001, US002, US003  
**Dependencies**: SQLAlchemy 2.0+, Pydantic, bcrypt

### Module: myapp.user.models
**File**: `myapp/user/models.py`  
**Libraries**: from sqlalchemy import Column, Integer, String  
**Purpose**: User data models and database schema  
**Implements**: US001 (User Registration), US002 (User Authentication)

#### Class: User
**Inherits**: SQLAlchemy Base  
**Table**: users  
**Properties**:
- id: Integer, primary_key  
- email: String(255), unique, not null  
- password_hash: String(255), not null  
**Methods**:
- set_password(password: str) -> None  
- verify_password(password: str) -> bool  
**Implementation Notes**: Use bcrypt for password hashing

### Module: myapp.user.services
**File**: `myapp/user/services.py`  
**Purpose**: User business logic  
**Dependencies**: UserRepository, EmailValidator  
**Implements**: US001, US002, US003

#### Class: UserService
**Methods**:
- create_user(email: str, password: str) -> User  
- authenticate_user(email: str, password: str) -> Optional[User]  
**Error Handling**: Raise UserExistsError, InvalidCredentialsError  
**Performance**: Cache user lookups for 5 minutes  
**Security**: Validate email format, enforce password complexity

### Configuration
**File**: `myapp/user/config.py`  
**Settings**:
- PASSWORD_MIN_LENGTH: int = 8  
- SESSION_TIMEOUT: int = 3600  
- BCRYPT_ROUNDS: int = 12

### Testing Requirements
- Test password hashing/verification  
- Test email validation  
- Test duplicate user creation  
- Mock database operations
```

The specification should provide enough detail for an AI coding agent to implement the complete functionality without additional design decisions.