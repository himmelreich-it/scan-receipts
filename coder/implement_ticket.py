
import sys

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
        print("Session ended")
        print(f"Duration: {msg.duration_ms}ms, API Duration: {msg.duration_api_ms}ms")
        print(f"Turns: {msg.num_turns}, Error: {msg.is_error}")
        print(f"Total Cost: ${msg.total_cost_usd:.5f}" if msg.total_cost_usd else "Total Cost: N/A")
        print(f"Usage: {json.dumps(msg.usage, indent=2)}" if msg.usage else "Usage: N/A")
        print (f"Result: {msg.result}" if msg.result else "Result: N/A")
        return msg.result if msg.result else ""
    
    else:
        print(f"Unknown message type: {type(msg)}")
        return ""


async def prepare_github(client: ClaudeSDKClient, session_id: str, retry: int = 0) -> bool:
    """Prepare GitHub repository."""
    print("Preparing GitHub repository...")

    prompt = load_prompt("prepare")

    await client.query(prompt=prompt, session_id=session_id)

    response = await handle_response(client)

    if "GITHUB PREPARED" not in response.upper():
        if retry >= MAX_RETRIES:
            print("Max retries reached. Exiting preparation.")
            return False
        
        print(f"Preparation incomplete, retrying... (attempt {retry + 1})")
        await prepare_github(client, session_id = session_id, retry=retry + 1)

    return True


async def implement_ticket_code(client: ClaudeSDKClient, session_id: str) -> str:
    """Implement the ticket code."""
    print("Implementing ticket code...")

    prompt = load_prompt("code")

    await client.query(prompt=prompt, session_id=session_id)

    response = await handle_response(client)

    return response


async def check_completion(client: ClaudeSDKClient, session_id: str) -> tuple[bool, str]:
    """Check if all tasks are complete."""
    print("Checking task completion...")

    prompt = load_prompt("check")

    await client.query(prompt=prompt, session_id=session_id)

    response = await handle_response(client)

    is_complete = "COMPLETE" in response.upper() or "ALL DONE" in response.upper()
    return is_complete, response


async def complete_implementation(client: ClaudeSDKClient, session_id: str, retry: int = 0) -> bool:
    """Finalize the implementation."""
    print("Finalizing implementation...")

    prompt = load_prompt("check")

    await client.query(prompt=prompt, session_id=session_id)

    response = await handle_response(client)

    if "IMPLEMENTATION COMPLETED" not in response.upper():
        if retry >= MAX_RETRIES:
            print("Max retries reached. Exiting completion.")
            return False
        
        print(f"Completion incomplete, completing implementation (attempt {retry + 1})")
        prompt = load_prompt("complete_remaining")
        await client.query(prompt=prompt, session_id=session_id)
        response = await handle_response(client)
        
        await complete_implementation(client, session_id=session_id, retry=retry + 1)

    return True

async def finish_implementation(client: ClaudeSDKClient, session_id: str, retry: int = 0) -> bool:
    """Finish the implementation."""
    print("Finishing implementation...")

    prompt = load_prompt("finish")

    await client.query(prompt=prompt, session_id=session_id)

    response = await handle_response(client)

    if "IMPLEMENTATION FINALIZED" not in response.upper():
        if retry >= MAX_RETRIES:
            print("Max retries reached. Exiting finishing.")
            return False
        
        print(f"Finishing incomplete, retrying... (attempt {retry + 1})")
        await finish_implementation(client, session_id=session_id, retry=retry + 1)

    return True


async def implement_ticket(ticket_number: str):    
    """Main function to implement ticket using Claude Code SDK."""

    session_id = str(uuid.uuid4())
    
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
                print("GitHub preparation failed. Exiting.")
                return
            
            print("GitHub prepared successfully. Proceeding with ticket implementation...")

            implementation_result = await implement_ticket_code(client, session_id)

            print("Ticket implementation completed.")
            print(implementation_result)

            complete_implementation_result = await complete_implementation(client, session_id)

            if complete_implementation_result:
                print("✓ Implementation finalized successfully")
            else:
                print("✗ Implementation finalization failed")
                return

            finish_implementation_result = await finish_implementation(client, session_id)

            if finish_implementation_result:
                print("✓ Ticket implementation finished successfully")
            else:
                print("✗ Ticket implementation finishing failed")
                return
            
        except CLIConnectionError as e:
            print(f"Connection error: {e}")
    

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
    print("Starting ticket implementation workflow...")

    # get ticket number from input
    if len(sys.argv) < 2:
        print("Usage: python implement_ticket.py <ticket_number>")
        sys.exit(1)
    ticket_number = sys.argv[1]
    print(f"Implementing ticket number: {ticket_number}")

    
    # Step 1: Prepare
    run_step("prepare")

    # Step 2: Code
    run_step("code")

    # Step 3: Check completion with retries
    for attempt in range(MAX_RETRIES):
        is_complete, _ = check_completion()

        if is_complete:
            print("✓ All tasks complete")
            break
        else:
            print(f"✗ Tasks incomplete (attempt {attempt + 1}/{MAX_RETRIES})")
            if attempt < MAX_RETRIES - 1:
                run_step("complete_remaining")

    # Step 4: Finish
    run_step("finish")

    print("\nWorkflow complete!")


if __name__ == "__main__":
    asyncio.run(main())