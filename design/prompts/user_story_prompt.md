# User Story Creation and Update Agent Instructions

## Objective  
Create detailed user stories for a specific feature or update existing user stories based on updated feature documentation. Stories must contain sufficient information for developer-AI agent collaboration on implementation specifications. **ONLY create or update user stories based on functionality explicitly described in the feature documentation** - do not infer, assume, or add functionality not directly mentioned.

## Input Requirements  
- High-level feature document with descriptions and dependencies  
- Target feature name to analyze  
- Existing user stories file (if updating existing stories)  
- Content of any dependency features  

## Process Flow

### Phase 1: Analysis  
- Read feature document and identify target feature and its explicit requirements  
- **If updating existing stories**: Compare against existing user stories to identify changes, additions, and obsolete functionality
- **If creating new stories**: Focus on comprehensive coverage of documented functionality
- Understand dependency features and their documented interfaces  
- Identify **complete user outcomes** rather than technical boundaries
- Group functionality by user goals and workflows to avoid fragmentation
- Do not assume standard features or functionality not explicitly mentioned  

### Phase 2: Story Comparison and Status Update (Update Mode Only)
For each existing user story when updating:
- Check if the updated feature document requires changes to this story's functionality
- If story has `Status: IMPLEMENTED` and feature update indicates changes needed → Change status to `OUTDATED`
- Update story description, acceptance criteria, and technical notes if feature shows different requirements
- Update dependencies if needed based on feature changes
- Identify stories that may no longer be relevant to the updated feature
- Keep original story codes for existing stories

### Phase 3: Information Gathering  
Ask focused questions about:

**Technical Constraints**  
- Technologies, frameworks, architectural patterns  
- Performance, scalability, security requirements  
- Existing systems or API integrations  

**User Experience & Business Rules**  
- User journeys and different user types  
- Core business logic and validation rules  
- Edge cases and exception scenarios  

**Data & Integration**  
- Data operations (CRUD) and validation requirements  
- Interactions with dependency features  
- External integrations or third-party services  

**Error Handling**  
- Failure scenarios and system responses  
- Recovery mechanisms and user feedback  

### Phase 4: Story Creation or Update  
1. **Creation Mode**: Propose user story breakdown covering **only the functionality described in the feature**
2. **Update Mode**: Propose user story updates and new story breakdown covering **only the functionality described in the updated feature**
3. Get user confirmation  
4. Create detailed user stories or update existing stories **based strictly on documented requirements**  

## Story Sizing Principles
- Each user story should represent a **complete, valuable user outcome**
- Stories should encompass entire user workflows or complete feature capabilities
- Prefer fewer, comprehensive stories over many fragmented ones
- Only separate stories when they serve distinctly different user needs or have different dependencies
- If a story feels too small to stand alone, merge it with related functionality

## Status Management Rules
- **Stories with Status: IMPLEMENTED**: Change status to `OUTDATED` if the updated feature indicates changes need to be made to that story's functionality
- **Stories without Status**: These are not yet implemented and have no status field
- **New Stories**: Do not include status field unless specifically required
- **Creation Mode**: New stories do not include status field

## Acceptance Criteria Requirements
- Must be **testable** with clear pass/fail outcomes
- Must be **specific** - avoid vague terms like "gracefully", "properly", "correctly"
- Must be **measurable** - define exact behaviors, error messages, UI states
- Use format: "When [condition], then [specific observable result]"
- Bad: "Handle missing input folder gracefully"
- Good: "When input folder is missing, display error message 'Input folder not found at [path]' and exit with code 1"

## User Story Format

### Story Title: [Clear, descriptive name]  
**Code**: STORY_NAME_HASH4  
**Status**: [OUTDATED if was IMPLEMENTED and feature update requires changes, otherwise keep original status or omit if none]
**Functional Description**: What this story accomplishes for implementation understanding  
**Acceptance Criteria**: Specific, testable conditions for completion (must be verifiable with clear pass/fail outcomes)  
**Technical Notes**: Implementation hints and constraints  
**Dependencies**: Other user stories that must be completed first  
**Data Requirements**: Data operations and field specifications  
**Error Scenarios**: Failure handling and edge cases  

## Story Consolidation Rules  
- Keep total stories manageable to avoid overwhelming complexity
- Combine related functionality that serves the same user goal
- Flag combined stories: "⚠️ **Combined Story**: Requires sub-division before development"  

## Story Quality Validation
Before finalizing, ensure each story:
- Delivers complete user value (not just technical tasks)
- Can be demonstrated independently
- Has clear entry/exit points for the user workflow
- Minimizes handoffs between stories for related functionality

## Mode-Specific Processes

### Creation Mode (New Feature)
1. Analyze feature document comprehensively
2. Identify all user workflows and outcomes
3. Group related functionality into coherent stories
4. Create new story codes for all stories
5. Focus on complete feature coverage

### Update Mode (Existing Feature)
1. **Compare Each Existing Story**
   - Check if the updated feature document requires changes to this story's functionality
   - If story has `Status: IMPLEMENTED` and feature update indicates changes needed → Change status to `OUTDATED`
   - Update story description, acceptance criteria, and technical notes if feature shows different requirements
   - Update dependencies if needed based on feature changes
   - Keep original story codes for existing stories

2. **Add New Stories**
   - Identify any new functionality described in the updated feature that doesn't exist in the current user stories
   - Create new story codes for new stories

3. **Remove Obsolete Stories**
   - Identify stories that may no longer be relevant to the updated feature requirements

## Example Output

### Story Title: Complete User Registration and Setup Flow
**Code**: USER_REG_SETUP_B4K9  
**Status**: OUTDATED *(Update Mode only, when applicable)*
**Functional Description**: End-to-end user registration including form submission, validation, account creation, email verification, and initial profile setup
**Acceptance Criteria**: 
- When user submits valid registration form, account is created and confirmation email sent
- When user enters invalid email format, display "Please enter a valid email address" 
- When user enters mismatched passwords, display "Passwords do not match"
- When user clicks verification link, account status changes to verified and user redirected to dashboard
- When user tries to register with existing email, display "Account already exists with this email"  
**Technical Notes**: Use React Hook Form, integrate validation utilities, server-side password hashing, rate limiting, email service integration
**Dependencies**: None  
**Data Requirements**: Creates user record with verification tracking, handles profile data, manages verification tokens
**Error Scenarios**: Network failures, server errors, validation failures, duplicate emails, verification timeouts

## Output Requirements  
- Create or update markdown document with feature name, user stories list, dependencies, implementation notes  
- Update high-level feature document with: `**User Stories**: [filename.md]`  
- **Update Mode Only**: Include change summary noting updated, new, and removed stories

## Quality Checks  
- All feature functionality covered  
- **Update Mode**: Existing stories properly updated with status changes
- **Update Mode**: New stories align with updated requirements
- Sufficient context for implementation specs  
- Dependencies properly mapped including new dependencies
- Technical constraints documented  
- Error scenarios identified  

## Interactive Guidelines  
- Ask focused questions one at a time  
- Confirm understanding by restating requirements and changes  
- Probe for missing information, especially edge cases  
- Validate assumptions about flows and business rules  
- Confirm final breakdown before creating or updating detailed stories  

## Change Management Notes (Update Mode Only)
- Clearly identify which stories were updated vs newly created
- Provide rationale for status changes (IMPLEMENTED → OUTDATED)
- Note any stories removed due to changed requirements
- Document new dependencies introduced by feature changes

---

## Mode Detection
**The agent will automatically detect the mode based on input:**
- **Creation Mode**: When no existing user stories file is provided
- **Update Mode**: When existing user stories file is provided for comparison

## Critical Requirements
- Only create or update stories based on functionality explicitly described in the feature documentation
- **Update Mode**: Only change `Status: IMPLEMENTED` to `Status: OUTDATED` when feature update explicitly indicates changes needed
- Stories without status remain without status unless updated
- **Update Mode**: Keep original story codes for existing stories
- Do not add stories based on assumptions about what "should" be included
- **Update Mode**: Clearly distinguish between updated existing stories and newly created stories

Your goal: Create or update user stories with sufficient information for developer-AI agent collaboration on detailed implementation specifications. **Base all user story work strictly on the documented feature requirements - do not add functionality not explicitly described in the feature documentation.**