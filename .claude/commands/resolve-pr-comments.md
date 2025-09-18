The user would like the agent to resolve GitHub PR comments given in $ARGUMENTS:

- Use subagent git-project-navigator to fetch PR details and comments for PR number $1
- Use subagent advanced-software-engineer to analyze and address comments using instructions in `coder/prompts/handle-pull-request-comments.md`
- Use subagent advanced-software-engineer to verify implementation using instructions in `coder/prompts/verify-implementation.md`
- Use subagent git-project-navigator to commit and push changes if any were made

## Configuration
- Python coding standards: `coder/rules/python_agent_instructions.md`
- Project commands: `CLAUDE.md`
- PR comment handling: `coder/prompts/handle-pull-request-comments.md`

## Workflow
1. Fetch PR details including all comments (regular and inline)
2. Critically evaluate each comment (don't blindly implement)
3. Implement/modify/reject with technical reasoning
4. Run quality checks and tests
5. Commit and push changes if modifications were made
6. Reply to each comment indicating what you have done to address the comment

## Key Requirements
- Be critical - evaluate suggestions thoroughly
- Reply to each comment with "Claude PR reply: [Action]"
- Provide technical reasoning for all decisions
- Test all changes thoroughly
- Only modify code that genuinely improves quality
- Only modify code related to comments, do not rework other parts unless you find critical issues