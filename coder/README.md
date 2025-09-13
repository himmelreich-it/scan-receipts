# Claude SDK Coding Agent

An automated coding agent that uses the Claude SDK to implement tickets through a structured workflow.

## Features

- **Session Management**: Persistent conversation sessions with ID tracking
- **Multi-step Workflow**: Prepare → Code → Check → Finish
- **Permission Control**: Restricted file modifications to `src/`, `data/`, and `tests/` directories
- **Full Read Access**: Can read all files in the repository
- **Automated Quality Checks**: Includes linting, formatting, and type checking
- **Git Integration**: Handles branching, commits, and pull requests

## Setup

1. **Install Dependencies**:
   ```bash
   pip install anthropic
   ```

2. **Configure Credentials**:
   ```bash
   cp coder/credentials.json.example coder/credentials.json
   # Edit credentials.json with your API keys
   ```

3. **Set Up Ticket Information** (optional):
   ```bash
   cp coder/ticket_info.json.example coder/ticket_info.json
   # Edit ticket_info.json with ticket details
   ```

## Usage

Run the script to implement a ticket:

```bash
python coder/implement_ticket.py
```

The agent will:
1. **Prepare**: Pull latest changes, create feature branch
2. **Code**: Implement the feature with tests
3. **Check**: Verify all quality checks pass (retries up to 3 times)
4. **Finish**: Commit changes and create pull request

## File Structure

```
coder/
├── implement_ticket.py      # Main script
├── session_id.txt          # Current session ID (auto-generated)
├── credentials.json        # API keys and tokens (create from .example)
├── ticket_info.json        # Ticket details (optional)
└── prompts/               # Step-specific prompts
    ├── prepare.md         # Preparation instructions
    ├── code.md           # Implementation instructions
    ├── check.md          # Completion verification
    ├── complete_remaining.md  # Retry instructions
    └── finish.md         # Finalization instructions
```

## Configuration

### Session Configuration
- `session_id`: Unique identifier for conversation continuity
- `api_key`: Anthropic API key
- `allowed_paths`: Directories where files can be modified (default: src, data, tests)
- `max_retries`: Maximum attempts for completion checks (default: 3)

### Environment Variables
- `ANTHROPIC_API_KEY`: Can be used instead of credentials.json

## Security Notes

- **Never commit** `credentials.json` or `session_id.txt`
- The `.gitignore` file is configured to exclude sensitive files
- API keys should be kept secure and rotated regularly

## Customization

### Custom Prompts
Edit the files in `coder/prompts/` to customize the agent's behavior for each step.

### Workflow Modification
Extend the `ClaudeCodeAgent` class to add new steps or modify the workflow:

```python
class CustomAgent(ClaudeCodeAgent):
    def custom_step(self):
        return self.execute_step("custom", "Your custom prompt here")
```

## Troubleshooting

- **Session Issues**: Delete `session_id.txt` to start a fresh session
- **API Errors**: Verify API key in credentials.json or environment
- **Permission Errors**: Ensure the agent only modifies allowed directories