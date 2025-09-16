The user wants to refine a ticket with number $ARGUMENTS. If no number is given, ask which ticket number should be refined.

- Use subagent ticket-refiner to refine the ticket with the given ticket number
- The ticket-refiner agent will handle all aspects of ticket refinement including:
  - Retrieving ticket information via GitHub CLI
  - Reading `design/product_requirements.md` for context
  - Considering architectural principles from `design/architecture/hexagonal_design.md`
  - Using `coder/prompts/refine_ticket_prompt.md` for guidance
  - Interactive refinement process, ask questions, confirm choices with user before updates