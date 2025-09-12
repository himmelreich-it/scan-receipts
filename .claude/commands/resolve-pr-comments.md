The user would like the agent to resolve GitHub PR comments given in $ARGUMENTS:

- If no PR number given, ask which PR to review
- Use `design/prompts/ai_code_agent_instructions_pr_comments.md` as implementation guide  
- Follow Python coding standards from `design/rules/python_agent_instructions.md`

Workflow:
1. Fetch PR details: `gh pr view $PR_NUMBER --json title,body,author,files`
2. Get unresolved comments: `gh pr view $PR_NUMBER --comments`
3. For each comment: evaluate critically → implement/modify/reject → reply with reasoning
4. Run quality checks: `npx pyright` and `uv run ruff check src`
5. Run tests and validate no regressions
6. Push changes if any were made

Key Requirements:
- Be critical - don't blindly implement suggestions
- Reply to each comment starting with "Claude PR reply: [Action]"
- Provide technical reasoning for all decisions
- Only modify code that genuinely improves quality
- Test all changes thoroughly

Output:
- Summary of comments addressed
- Files modified (if any)  
- Quality check results