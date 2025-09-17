The user would like the agent to implement github ticket given in $ARGUMENTS:
- Use subagent git-project-navigator to retrieve ticket information for ticket_number $1.
- Use subagent advanced-software-engineer to analyse the requirements using instructions in `coder/prompts/analyze-ticket.md`
- Use subagent git-project-navigator to prepare git before implementation, use the instructions in `coder/prompts/prepare-git.md`
- Use subagent advanced-software-engineer to implement the ticket, use the instructions in `coder/prompts/implement.md`
- Use subagent advanced-software-engineer to check and finalize your implementation, use instructions in `coder/prompts/verify-implementation.md`
- Use subagent git-project-navigator to wrap-up the ticket for review using instruction in `coder/prompts/finalize-ticket.md`



- Use `design/prompts/ai_code_agent_instructions_ticket.md` as the main implementation guide
- Follow Python coding standards from `design/rules/python_agent_instructions.md`
- Follow the exact workflow outlined in the AI code agent instructions
- Run Code Quality Checks and Testing Commands

Once done:
- Update Github ticket with label "implemented"
- Create PR to main using Github CLI
