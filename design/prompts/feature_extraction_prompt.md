# Feature Extraction Prompt

## Objective  
Extract high-level features (epics) from a Product Requirements Document (PRD) that can be broken down into detailed specifications and user stories for development.

## Instructions  

You are analyzing a Product Requirements Document to identify the core features that need to be built. **ONLY extract features explicitly described in the PRD** - do not infer, assume, or add features not directly mentioned. Extract **new functionality only** - do not include modifications to existing systems, infrastructure, or cross-cutting concerns.

### Feature Identification Guidelines  

1. **Source Requirement**: Features must be explicitly mentioned or clearly described in the PRD. Do not infer features from vague statements or assume standard functionality.  

2. **Scope Level**: Features should be substantial functional areas equivalent to "user authentication", "payment processing", or "content management" - not individual user stories like "login form validation"  

3. **Maximum Count**: Extract no more than **12 features** total. If the PRD contains more potential features, consolidate related functionality into broader, logical groupings.  

4. **Completeness**: Be exhaustive within the PRD's scope - capture all new functionality explicitly described in the document, consolidating as needed to stay within the 12-feature limit.  

5. **Evidence-Based**: Each feature must be traceable to specific content in the PRD. If you cannot point to where a feature is described, do not include it.  

### Output Format  

For each feature, provide:

## Feature: Clear, descriptive name  
**Code**: DESCRIPTIVE_NAME_HASH4  
**Description**: 2-3 sentence functional description of what this feature accomplishes  
**Dependencies**: List any hard dependencies (must be completed first) and soft dependencies (would benefit from being completed first) on other features from your extracted list  

### Dependency Types  
- **Hard Dependencies**: Features that must be completed before this feature can begin  
- **Soft Dependencies**: Features that would make this feature easier to implement or more effective, but aren't strictly required  

### Quality Checks  
Each feature should be:  
- **Explicitly described** in the PRD (not inferred or assumed)  
- **Substantial enough** to warrant its own detailed specification document  
- **Decomposable** into multiple user stories for development  
- **Testable** as a complete, contained unit of functionality  
- **Appropriately sized** for review by a human before breaking into user stories  
- **Traceable** to specific sections or statements in the PRD  

### Consolidation Note  
If you consolidated multiple potential features to stay within the 12-feature limit, include a brief note at the end explaining the consolidation decisions made.

## Example Output Structure  

## Feature: User Authentication  
**Code**: USER_AUTH_A7B3  
**Description**: Comprehensive user authentication system allowing users to register, login, logout, and manage their account credentials. Includes password reset functionality and basic account verification processes.  
**Dependencies**: None  

## Feature: User Profile Management  
**Code**: PROFILE_MGMT_K9M2  
**Description**: Enables users to create, view, edit, and manage their personal profiles including personal information, preferences, and account settings. Provides the foundation for personalized user experiences.  
**Dependencies**: Hard - User Authentication [USER_AUTH_A7B3]  

---

**CRITICAL**: Only extract features that are explicitly described in the PRD. Do not add features based on assumptions about what "should" be included in a typical system. If the PRD doesn't mention it, don't extract it.

Now analyze the provided PRD and extract the features following these guidelines.