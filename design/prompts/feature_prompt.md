# Feature Extraction and Update Instructions

## Objective  
Extract high-level features (epics) from a Product Requirements Document (PRD) or update existing features based on an updated PRD. Features must be substantial functional areas that can be broken down into detailed specifications and user stories for development.

## Input Requirements
- Product Requirements Document (PRD) with feature descriptions
- Existing feature file (if updating existing features)

## Instructions  

You are analyzing a Product Requirements Document to identify core features that need to be built or to update existing features against PRD changes. **ONLY extract or update features explicitly described in the PRD** - do not infer, assume, or add features not directly mentioned. Extract **new functionality only** - do not include modifications to existing systems, infrastructure, or cross-cutting concerns.

## Feature Identification Guidelines  

1. **Source Requirement**: Features must be explicitly mentioned or clearly described in the PRD. Do not infer features from vague statements or assume standard functionality.  

2. **Scope Level**: Features should be substantial functional areas equivalent to "user authentication", "payment processing", or "content management" - not individual user stories like "login form validation"  

3. **Maximum Count**: Extract no more than **12 features** total. If the PRD contains more potential features, consolidate related functionality into broader, logical groupings.  

4. **Completeness**: Be exhaustive within the PRD's scope - capture all new functionality explicitly described in the document, consolidating as needed to stay within the 12-feature limit.  

5. **Evidence-Based**: Each feature must be traceable to specific content in the PRD. If you cannot point to where a feature is described, do not include it.  

## Status Management Rules
- **Features with Status: IMPLEMENTED**: Change status to `OUTDATED` if the PRD indicates changes need to be made to that feature
- **Features without Status**: These are not yet implemented and have no status field
- **New Features**: Do not include status field unless specifically required
- **Extraction Mode**: New features do not include status field

## Mode-Specific Processes

### Extraction Mode (New PRD Analysis)
1. Analyze PRD comprehensively for all explicitly described features
2. Identify substantial functional areas that warrant separate development
3. Group related functionality into coherent features
4. Create new feature codes for all features
5. Focus on complete PRD coverage within 12-feature limit

### Update Mode (Existing Feature Analysis)
1. **Compare Each Existing Feature**
   - Check if the PRD requires changes to this feature
   - If feature has `Status: IMPLEMENTED` and PRD indicates changes needed → Change status to `OUTDATED`
   - Update feature description if PRD shows different requirements
   - Update dependencies if needed based on PRD changes
   - Keep original feature codes for existing features

2. **Add New Features**
   - Identify any new features described in the PRD that don't exist in the current feature file
   - Create new feature codes for new features

3. **Remove Obsolete Features**
   - Identify features that may no longer be relevant to the updated PRD requirements

## Output Format  

For each feature, provide:

## Feature: Clear, descriptive name  
**Code**: DESCRIPTIVE_NAME_HASH4  
**Status**: [OUTDATED if was IMPLEMENTED and PRD requires changes, otherwise keep original status or omit if none]
**Description**: 2-3 sentence functional description of what this feature accomplishes  
**Dependencies**: List any hard dependencies (must be completed first) and soft dependencies (would benefit from being completed first) on other features from your extracted list  

### Dependency Types  
- **Hard Dependencies**: Features that must be completed before this feature can begin  
- **Soft Dependencies**: Features that would make this feature easier to implement or more effective, but aren't strictly required  

## Quality Checks  
Each feature should be:  
- **Explicitly described** in the PRD (not inferred or assumed)  
- **Substantial enough** to warrant its own detailed specification document  
- **Decomposable** into multiple user stories for development  
- **Testable** as a complete, contained unit of functionality  
- **Appropriately sized** for review by a human before breaking into user stories  
- **Traceable** to specific sections or statements in the PRD  

## Example Output Structure  

### Extraction Mode Example
## Feature: User Authentication  
**Code**: USER_AUTH_A7B3  
**Description**: Comprehensive user authentication system allowing users to register, login, logout, and manage their account credentials. Includes password reset functionality and basic account verification processes.  
**Dependencies**: None  

## Feature: User Profile Management  
**Code**: PROFILE_MGMT_K9M2  
**Description**: Enables users to create, view, edit, and manage their personal profiles including personal information, preferences, and account settings. Provides the foundation for personalized user experiences.  
**Dependencies**: Hard - User Authentication [USER_AUTH_A7B3]  

### Update Mode Example
## Feature: User Authentication  
**Code**: USER_AUTH_A7B3  
**Status**: OUTDATED
**Description**: Comprehensive user authentication system allowing users to register, login, logout, and manage their account credentials. Now includes social media login integration and multi-factor authentication as described in the updated PRD.  
**Dependencies**: Soft - Social Media Integration [SOCIAL_AUTH_X4Y9] (new dependency)

## Mode Detection
**The agent will automatically detect the mode based on input:**
- **Extraction Mode**: When no existing feature file is provided
- **Update Mode**: When existing feature file is provided for comparison

## Change Management Notes (Update Mode Only)
- Clearly identify which features were updated vs newly created
- Provide rationale for status changes (IMPLEMENTED → OUTDATED)
- Note any features removed due to changed requirements
- Document new dependencies introduced by PRD changes

## Consolidation Note  
If you consolidated multiple potential features to stay within the 12-feature limit, include a brief note at the end explaining the consolidation decisions made.

## Output Requirements
- **Extraction Mode**: Create markdown document with extracted features
- **Update Mode**: Update existing feature file and include change summary noting updated, new, and removed features

---

## Critical Requirements
- Only extract or update features that are explicitly described in the PRD
- **Update Mode**: Only change `Status: IMPLEMENTED` to `Status: OUTDATED` when PRD explicitly indicates changes needed
- Features without status remain without status unless updated
- **Update Mode**: Keep original feature codes for existing features
- Do not add features based on assumptions about what "should" be included in a typical system
- **Update Mode**: Clearly distinguish between updated existing features and newly created features
- If the PRD doesn't mention it, don't extract it

Your goal: Extract features from PRD or update existing features based on PRD changes. **Base all feature work strictly on what is explicitly described in the PRD - do not add functionality not directly mentioned in the document.**