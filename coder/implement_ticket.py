
import sys
import logging
import asyncio
import json
import uuid
from pathlib import Path
from  claude_code_sdk  import (
    AssistantMessage,
    ClaudeCodeOptions,
    ClaudeSDKClient,
    CLIConnectionError,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    ThinkingBlock,
    UserMessage,
    Message,
    ContentBlock
) 



# Configuration - Edit these paths to point to your prompt files
PROMPT_FILES = {
    "system": "coder/prompts/system.md",
    "prepare": "coder/prompts/prepare.md",
    "code": "coder/prompts/code.md",
    "check": "coder/prompts/check.md",
    "complete_remaining": "coder/prompts/complete_remaining.md",
    "finish": "coder/prompts/finish.md"
}

SESSION_FILE = Path("coder/session_id.txt")
MAX_RETRIES = 3
ANTHROPIC_MODEL = "claude-sonnet-4-20250514"

ALLOWED_DIRS = ["src", "data", "tests"]

# Logger instance
logger = logging.getLogger(__name__)

def configure_logging(ticket_number: str) -> None:
    """Configure logging with both console and file handlers."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Create logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Clear any existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    # File handler
    log_file = f"{ticket_number}-implementation.log"
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(log_format)
    file_handler.setFormatter(file_formatter)

    # Add handlers to logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    logger.info(f"Logging configured. Writing to {log_file}")

async def handle_response(client: ClaudeSDKClient) -> str:
    """Handle and display messages from Claude SDK client."""

    responses: list[str] = []
    async for msg in client.receive_response():
        responses.append(handle_message(msg))

    return "\n".join(responses)



def handle_message(msg: Message) -> str:
    """Standardized message display function.

    - UserMessage: "User: <content>"
    - AssistantMessage: "Claude: <content>"
    - SystemMessage: ignored
    - ResultMessage: "Result ended" + cost if available
    """
    def concat_text(blocks: str | list[ContentBlock], prefix: str = "") -> str:
        texts: list[str] = []
        for block in blocks:
            if isinstance(block, TextBlock):
                texts.append(f"{prefix}{block.text}")
            
        return " ".join(texts)
    
    if isinstance(msg, UserMessage):
        return concat_text(msg.content)
    
    elif isinstance(msg, AssistantMessage):
        return concat_text(msg.content, prefix="Claude: ")
    
    elif isinstance(msg, SystemMessage):
        return ""
    
    elif isinstance(msg, ResultMessage):  # type: ignore
        logger.info("Session ended")
        logger.info(f"Duration: {msg.duration_ms}ms, API Duration: {msg.duration_api_ms}ms")
        logger.info(f"Turns: {msg.num_turns}, Error: {msg.is_error}")
        logger.info(f"Total Cost: ${msg.total_cost_usd:.5f}" if msg.total_cost_usd else "Total Cost: N/A")
        logger.debug(f"Usage: {json.dumps(msg.usage, indent=2)}" if msg.usage else "Usage: N/A")
        logger.debug(f"Result: {msg.result}" if msg.result else "Result: N/A")
        return msg.result if msg.result else ""
    
    else:
        logger.warning(f"Unknown message type: {type(msg)}")
        return ""


async def prepare_github(client: ClaudeSDKClient, session_id: str, retry: int = 0) -> bool:
    """Prepare GitHub repository."""
    logger.info("Preparing GitHub repository...")

    prompt = load_prompt("prepare")

    await client.query(prompt=prompt, session_id=session_id)

    response = await handle_response(client)

    if "GITHUB PREPARED" not in response.upper():
        if retry >= MAX_RETRIES:
            logger.error("Max retries reached. Exiting preparation.")
            return False

        logger.warning(f"Preparation incomplete, retrying... (attempt {retry + 1})")
        return await prepare_github(client, session_id=session_id, retry=retry + 1)

    return True


async def implement_ticket_code(client: ClaudeSDKClient, session_id: str) -> str:
    """Implement the ticket code."""
    logger.info("Implementing ticket code...")

    prompt = load_prompt("code")

    await client.query(prompt=prompt, session_id=session_id)

    response = await handle_response(client)

    return response


async def check_completion(client: ClaudeSDKClient, session_id: str) -> tuple[bool, str]:
    """Check if all tasks are complete."""
    logger.info("Checking task completion...")

    prompt = load_prompt("check")

    await client.query(prompt=prompt, session_id=session_id)

    response = await handle_response(client)

    is_complete = "COMPLETE" in response.upper() or "ALL DONE" in response.upper()
    return is_complete, response


async def complete_implementation(client: ClaudeSDKClient, session_id: str, retry: int = 0) -> bool:
    """Finalize the implementation."""
    logger.info("Finalizing implementation...")

    prompt = load_prompt("check")

    await client.query(prompt=prompt, session_id=session_id)

    response = await handle_response(client)

    if "IMPLEMENTATION COMPLETED" not in response.upper():
        if retry >= MAX_RETRIES:
            logger.error("Max retries reached. Exiting completion.")
            return False

        logger.warning(f"Completion incomplete, completing implementation (attempt {retry + 1})")
        prompt = load_prompt("complete_remaining")
        await client.query(prompt=prompt, session_id=session_id)
        response = await handle_response(client)

        return await complete_implementation(client, session_id=session_id, retry=retry + 1)

    return True

async def finish_implementation(client: ClaudeSDKClient, session_id: str, retry: int = 0) -> bool:
    """Finish the implementation."""
    logger.info("Finishing implementation...")

    prompt = load_prompt("finish")

    await client.query(prompt=prompt, session_id=session_id)

    response = await handle_response(client)

    if "IMPLEMENTATION FINALIZED" not in response.upper():
        if retry >= MAX_RETRIES:
            logger.error("Max retries reached. Exiting finishing.")
            return False

        logger.warning(f"Finishing incomplete, retrying... (attempt {retry + 1})")
        return await finish_implementation(client, session_id=session_id, retry=retry + 1)

    return True


async def implement_ticket(ticket_number: str):
    """Main function to implement ticket using Claude Code SDK."""
    # Configure logging for this ticket
    configure_logging(ticket_number)
    logger.info(f"Starting ticket implementation for ticket #{ticket_number}")

    session_id = str(uuid.uuid4())
    logger.debug(f"Session ID: {session_id}")
    
    # async def create_message_stream():
    #     """Generate a stream of messages."""
    #     print("User: Hello! I have multiple questions.")
    #     yield {
    #         "type": "user",
    #         "message": {"role": "user", "content": "Hello! I have multiple questions."},
    #         "parent_tool_use_id": None,
    #         "session_id": session_id,
    #     }

    async with ClaudeSDKClient(options=define_options()) as client:
        try:
            github_result = await prepare_github(client, session_id)

            if not github_result:
                logger.error("GitHub preparation failed. Exiting.")
                return

            logger.info("GitHub prepared successfully. Proceeding with ticket implementation...")

            implementation_result = await implement_ticket_code(client, session_id)

            logger.info("Ticket implementation completed.")
            logger.debug(f"Implementation result: {implementation_result}")

            complete_implementation_result = await complete_implementation(client, session_id)

            if complete_implementation_result:
                logger.info("✓ Implementation finalized successfully")
            else:
                logger.error("✗ Implementation finalization failed")
                return

            finish_implementation_result = await finish_implementation(client, session_id)

            if finish_implementation_result:
                logger.info("✓ Ticket implementation finished successfully")
            else:
                logger.error("✗ Ticket implementation finishing failed")
                return
            
        except CLIConnectionError as e:
            logger.error(f"Connection error: {e}", exc_info=True)
    

def load_prompt(step_name: str):
    """Load prompt from file."""
    prompt_file = Path(PROMPT_FILES.get(step_name, f"coder/prompts/{step_name}.md"))
    if not prompt_file.exists():
        return f"# {step_name.upper()}\n\nPrompt file not found: {prompt_file}"
    return prompt_file.read_text()


def define_options() -> ClaudeCodeOptions:
    """Define Claude Code SDK options."""

    return ClaudeCodeOptions(
        allowed_tools=["Read", "Write"],  # Allow file operations
        system_prompt=load_prompt("system"),
        env={
            "ANTHROPIC_MODEL": ANTHROPIC_MODEL,
        },
    )


async def main():
    """Main workflow."""
    # get ticket number from input
    if len(sys.argv) < 2:
        print("Usage: python implement_ticket.py <ticket_number>")
        sys.exit(1)
    ticket_number = sys.argv[1]

    # Call the implement_ticket function which handles everything
    await implement_ticket(ticket_number)


if __name__ == "__main__":
    asyncio.run(main())