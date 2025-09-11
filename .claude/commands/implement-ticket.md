The user would like the agent to implement github ticket given in $ARGUMENTS :
- After analysis, before implementation, use Github CLI to create a feature branch `feature/$ticket_number`

- If no feature is given in $ARGUMENTS, ask the user which ticket should be implemented
- Use `design/prompts/ai_code_agent_instructions_ticket.md` as the main implementation guide
- Follow Python coding standards from `design/rules/python_agent_instructions.md`
- Follow the exact workflow outlined in the AI code agent instructions
- Run Code Quality Checks and Testing Commands

Once done:
- Update Github ticket with label "IMPLEMENTED"
- Create PR to main using Github CLI
