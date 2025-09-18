# Feature Extraction and Update Instructions

## Objective  
Extract high-level features (epics) from a Product Requirements Document (PRD) or update existing features based on an updated PRD. Features must be substantial, self-contained functional areas that can be implemented independently without accidentally including functionality from other features.

## Feature Identification Guidelines  

1. **Source Requirement**: Features must be explicitly mentioned in the PRD. Do not infer or assume functionality.

2. **Independence Test**: Each feature should be implementable without accidentally building core functionality of other features. If implementing Feature A naturally leads to building Feature B, consolidate them.

3. **Size Guidelines**: 
   - **Too Small**: Individual forms, single endpoints, specific UI components
   - **Just Right**: Complete user workflows, data management systems, integration modules
   - **Too Large**: Entire applications, multiple unrelated functional areas

4. **Functional Completeness**: Each feature should represent a complete user-facing capability. Users should accomplish meaningful tasks with just that feature implemented.

5. **Maximum Count**: Extract no more than **12 features** total. Consolidate related functionality into broader, logical groupings if needed.

## Well-Sized Feature Examples
- **User Account Management**: Complete registration, authentication, profile management, account settings
- **Payment Processing**: Full payment flow, multiple methods, transaction history, refunds
- **Content Publishing System**: Create, edit, publish, manage content with full workflow
- **Admin Dashboard**: Complete administrative interface for managing users, content, system settings

## Status Management Rules
- **New Features**: Always get `Status: NEW`
- **Existing IMPLEMENTED Features**: Change to `Status: OUTDATED` if PRD requires changes
- **Status Values**: `NEW` (not implemented), `IMPLEMENTED` (built), `OUTDATED` (needs updates)

## Output Format  

## Feature: Clear, descriptive name  
**Code**: DESCRIPTIVE_NAME_HASH4  
**Status**: [NEW for new features, OUTDATED if was IMPLEMENTED and PRD requires changes, otherwise keep original status]
**Description**: 2-3 sentence functional description including clear boundaries. Be specific about what is included and NOT included to avoid overlap.
**Implementation Scope**: Brief bullet points of main components/capabilities included
**Dependencies**: Hard dependencies (must be completed first) and soft dependencies (would benefit from being completed first)

## Quality Checks  
Each feature should be:  
- **Explicitly described** in the PRD
- **Self-contained** - implementable without building other features  
- **Functionally complete** - users can accomplish meaningful tasks
- **Substantial** - requires 3-10 user stories to implement fully
- **Boundary-clear** - obvious what is included vs excluded

## Pre-Implementation Validation
Ask before finalizing each feature:
1. Could a developer implement this without building core functionality of other features?
2. Does this represent a complete, valuable capability for users?
3. Are boundaries clear enough to avoid conflicts between developers?

## Example Output

### Extraction Mode Example
## Feature: User Account Management  
**Code**: USER_ACCOUNT_A7B3  
**Status**: NEW  
**Description**: Complete user lifecycle management including registration, authentication, profile management, password reset, and account settings. Provides the foundation for all user-specific functionality in the system.
**Implementation Scope**: 
- User registration and email verification
- Login/logout functionality  
- Password reset and change capabilities
- Profile editing and management
- Account settings and preferences
- Session management

**Dependencies**: None  

### Update Mode Example
## Feature: User Account Management  
**Code**: USER_ACCOUNT_A7B3  
**Status**: OUTDATED  
**Description**: Complete user lifecycle management including registration, authentication, profile management, password reset, and account settings. Now includes social media login integration and multi-factor authentication as described in the updated PRD.
**Implementation Scope**: 
- User registration and email verification
- Login/logout functionality (expanded with social media)
- Multi-factor authentication (NEW)
- Password reset and change capabilities
- Profile editing and management
- Account settings and preferences
- Session management

**Dependencies**: Soft - Social Media Integration [SOCIAL_AUTH_X4Y9] (new dependency)

## Mode Detection
- **Extraction Mode**: When no existing feature file is provided
- **Update Mode**: When existing feature file is provided for comparison

## Critical Requirements
- Only extract features explicitly described in the PRD
- Ensure implementation independence - each feature implementable without building other features
- Define clear boundaries - be explicit about what is included and excluded
- All new features get `Status: NEW`
- Keep original feature codes for existing features in update mode
- Base all work strictly on what is explicitly described in the PRD

Your goal: Extract features from PRD or update existing features based on PRD changes. **Base all feature work strictly on what is explicitly described in the PRD - do not add functionality not directly mentioned in the document.**