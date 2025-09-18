# AI Code Agent Instructions - PR Comment Resolution

## System Overview
Analyze and address unresolved GitHub PR comments. Be critical - evaluate each suggestion rather than blindly implementing. Provide reasoned technical responses.

**Input Documents**: Python Code Guidelines, PR Context via GitHub CLI

## Core Workflow

### 1. Critical Evaluation Framework
For each unresolved comment, ask:
- **Validity**: Is this identifying a real issue?
- **Best Solution**: Is the suggested fix optimal?
- **Project Alignment**: Does this support project goals/constraints?
- **Trade-offs**: What are we gaining/losing?

### 2. Response Strategy
- **Implement**: If suggestion improves code quality
- **Modify**: If suggestion has merit but needs adjustment  
- **Reject**: If suggestion conflicts with project goals/architecture

### 3. Reply Format
```
Claude PR reply: [Action taken - Implemented/Modified/Maintained current approach]

[Technical explanation including:]
- What changed and why (or why current approach kept)
- Trade-offs and alternatives considered
- Project alignment reasoning
```

## Implementation Patterns

### Reply Templates

**Implemented:**
```
Claude PR reply: Implemented with modifications

Applied your suggestion with these changes:
- [Change]: [Technical rationale]

This improves [benefits] while maintaining [qualities].
Files modified: [list]
```

**Rejected:**
```
Claude PR reply: Maintaining current approach

Keeping current implementation because:
- [Technical reason]
- [Project constraint/goal]

Current approach achieves [goals] while [advantages].
Considered alternatives: [brief summary]
```

### Testing & Quality
- Check quality after work is done
- Execute all relevant tests
- Validate no regressions introduced
- Do not attempt to fix issues not related to the code you are working on unless a comment indicates to do so
- **HALT** if tests fail after 3 attempts

## Guidelines

**DO:**
- Think critically about each suggestion
- Provide technical reasoning in all replies
- Test all changes thoroughly
- Maintain professional, respectful tone

**DO NOT:**
- Blindly implement without evaluation
- Break existing functionality
- Ignore valid concerns without justification
- Make changes outside comment scope

**Success Criteria:**
- All unresolved comments addressed appropriately
- Technical replies explaining all decisions
- Code quality maintained/improved
- All tests pass, all clean-up of scenarios are good
- All linting checks pass for source and tests