# Feature Update Prompt

## Objective  
Compare an existing feature file against a Product Requirements Document (PRD) to update features and manage status changes.

## Instructions  

You are analyzing a PRD against an existing feature file. **ONLY extract features explicitly described in the PRD** - do not infer, assume, or add features not directly mentioned. Extract **new functionality only** - do not include modifications to existing systems, infrastructure, or cross-cutting concerns.

### Feature Identification Guidelines  

1. **Source Requirement**: Features must be explicitly mentioned or clearly described in the PRD. Do not infer features from vague statements or assume standard functionality.  

2. **Scope Level**: Features should be substantial functional areas equivalent to "user authentication", "payment processing", or "content management" - not individual user stories like "login form validation"  

3. **Maximum Count**: Extract no more than **12 features** total. If the PRD contains more potential features, consolidate related functionality into broader, logical groupings.  

4. **Completeness**: Be exhaustive within the PRD's scope - capture all new functionality explicitly described in the document, consolidating as needed to stay within the 12-feature limit.  

5. **Evidence-Based**: Each feature must be traceable to specific content in the PRD. If you cannot point to where a feature is described, do not include it.  

### Status Update Rules
- **Features with Status: IMPLEMENTED**: Change status to `OUTDATED` if the PRD indicates changes need to be made to that feature
- **Features without Status**: These are not yet implemented and have no status field

### Update Process

#### 1. Compare Each Existing Feature
For each feature in the feature file:
- Check if the PRD requires changes to this feature
- If feature has `Status: IMPLEMENTED` and PRD indicates changes needed → Change status to `OUTDATED`
- Update feature description if PRD shows different requirements
- Update dependencies if needed based on PRD changes

#### 2. Add New Features
Identify any new features described in the PRD that don't exist in the current feature file.

### Output Format  

For each feature, provide:

## Feature: Clear, descriptive name  
**Code**: DESCRIPTIVE_NAME_HASH4  
**Status**: [OUTDATED if was IMPLEMENTED and PRD requires changes, otherwise keep original status or omit if none]
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

---

**CRITICAL**: 
- Only extract features that are explicitly described in the PRD
- Only change `Status: IMPLEMENTED` to `Status: OUTDATED` when PRD explicitly indicates changes needed
- Features without status remain without status
- Keep original feature codes for existing features
- Do not add features based on assumptions about what "should" be included

Now analyze the provided PRD against the existing feature file and provide the updated feature set following these guidelines.