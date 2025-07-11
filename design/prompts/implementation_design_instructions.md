# Interactive Implementation Design Instructions

## Objective
Generate detailed implementation specifications for Python applications from user stories through interactive technical validation. Only implement what is explicitly required by user stories.

## Process Flow

### Phase 1: Analysis
- Read user stories and extract implementation requirements
- Identify Python packages needing creation/modification
- Map acceptance criteria to technical needs

### Phase 2: Interactive Technical Planning
Ask focused questions about missing technical context:

**Architecture & Libraries**
- Preferred architectural pattern (MVC, layered, etc.)?
- Required/prohibited libraries or frameworks?
- Database technology and ORM preference?
- Target Python version and constraints?

**Performance & Integration**
- Performance requirements not in user stories?
- External APIs or services to integrate?
- Caching, async processing, or message queue needs?
- Authentication/authorization framework preference?

**Implementation Approach**
- Error handling strategy preference?
- Testing framework and approach?
- Configuration management approach?
- Existing patterns or utilities to follow?

### Phase 3: Design Validation
1. Propose implementation approach with key design decisions
2. Present technical trade-offs and rationale
3. Get confirmation before generating detailed specs
4. Adjust based on feedback

### Phase 4: Specification Generation
Create implementation specs based on validated approach.

## Interactive Guidelines
- Ask 1-2 focused questions at a time
- Provide context for why questions matter
- Offer specific options when possible
- Confirm understanding before proceeding
- Balance thoroughness with avoiding over-engineering

## Output Format

### Package Structure
```
## Package: [package_name]
**Path**: `[path/to/package]/`
**Purpose**: [Brief description]
**User Stories**: [List of story IDs]
**Dependencies**: [Required packages/libraries]
**Design Decisions**: [Key technical choices from interactive planning]
```

### Component Details
For each module/class include:
- **File location** and purpose
- **Libraries used** with rationale
- **Design patterns** applied
- **Methods/properties** with implementation notes
- **Error handling** approach
- **Testing requirements** specific to acceptance criteria
- **User story references** implemented

### Technical Specifications
- **Code samples** for complex implementations only
- **Configuration** structure and defaults
- **Database integration** if data persistence required
- **External integrations** confirmed in planning
- **Performance considerations** if discussed
- **Security measures** if specified

### Integration Specifications
- **Main application entry point** integration requirements
- **Configuration changes** needed for the feature
- **CLI argument** or user interface integration points
- **Initialization sequence** and dependency injection setup

## Quality Requirements
- Every design decision must trace back to user story requirements or confirmed preferences
- No feature creep beyond acceptance criteria
- Backward compatibility with existing dependent user stories
- All technical choices validated through interactive process

## File Management
- Create `[package_name]_implementation_spec.md` per package
- Update user stories file with implementation references
- Document design decisions and rationale
- Maintain implementation tracking index

## Validation Rules
Before including any implementation detail:
1. Is this required by user story acceptance criteria?
2. Was this approach confirmed in interactive planning?
3. Is this the minimal viable implementation?
4. Does this preserve interfaces used by dependent stories?

## Example Interactive Flow
```
> "Looking at your authentication user stories, I need to clarify:
> 
> **Authentication**: JWT tokens or session-based auth?
> **Database**: SQLAlchemy ORM or direct SQL queries?
> **API Framework**: FastAPI, Flask, or Django REST?
> 
> This affects how I structure the auth package and user management."

> "Based on your preferences, I propose:
> - JWT tokens for stateless auth
> - SQLAlchemy with repository pattern
> - FastAPI with Pydantic validation
> 
> This approach satisfies your user stories while maintaining scalability. Confirm?"
```

The interactive process ensures technically sound, validated implementation specifications that avoid over-engineering while meeting all user story requirements.