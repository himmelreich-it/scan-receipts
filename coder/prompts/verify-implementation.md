# Completion Check

Please verify that all implementation tasks are complete:

## Checklist:
1. **Feature Implementation:**
   - [ ] All required functionality is implemented
   - [ ] Code follows project architecture and patterns
   - [ ] Error handling follows fail-fast principles (see `coder/rules/python_agent_instructions.md`)

2. **Testing:**
   - [ ] Unit tests are written and passing
   - [ ] Integration tests are written and passing (if applicable)
   - [ ] BDD tests are written and passing (if applicable)
   - [ ] Test coverage meets requirements
   - [ ] Run all test commands from CLAUDE.md

3. **Code Quality:**
   - [ ] Linting passes (see CLAUDE.md for commands)
   - [ ] Type checking passes (see CLAUDE.md for commands)
   - [ ] Code is properly formatted

4. **Documentation:**
   - [ ] All new code has docstrings per `coder/rules/python_agent_instructions.md`
   - [ ] Complex logic has inline comments
   - [ ] API documentation in `__init__.py` if applicable

## Complete Remaining Tasks

Based on the previous check, there are still tasks to complete. Please finish all remaining items:

1. Fix any failing tests (use agent retry protocol - up to 3 attempts)
2. Resolve any linting or type checking errors (use commands from CLAUDE.md)
3. Complete any missing functionality per acceptance criteria
4. Add any missing documentation per `coder/rules/python_agent_instructions.md`

Focus on completing everything so the feature is fully ready for review.