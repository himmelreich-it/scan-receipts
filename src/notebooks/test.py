






import asyncio
import datetime
from pathlib import Path
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeSDKClient,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    ThinkingBlock,
    UserMessage,
    Message,
    ContentBlock,
)
import logging

import yaml


# Logger instance
logger = logging.getLogger(__name__)

prompt = """
You are an AI assistant that extracts structured data from receipt images. Analyze the provided image and return the extracted data in JSON format with the following fields: vendor_name, date, total_amount, tax_amount, items (list of item names and prices). If any field is missing, set its value to null.
The image to analyze is `receipt.jpg`.
"""


async def handle_response(client: ClaudeSDKClient) -> str:
    """Handle and display messages from Claude SDK client."""

    responses: list[str] = []
    try:
        async for msg in client.receive_response():
            responses.append(handle_message(msg))
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Response handling error: {error_msg}")

        return f"Error: {error_msg}"

    return "\n".join(responses)

def handle_message(msg: Message) -> str:
    """Standardized message display function with user-friendly formatting."""

    def concat_text(blocks: str | list[ContentBlock], prefix: str = "") -> str:
        texts: list[str] = []
        for block in blocks:
            if isinstance(block, TextBlock):
                logger.info(f"Claude: {block.text}")
                texts.append(f"{prefix}{block.text}")
            elif isinstance(block, ToolUseBlock):
                # Register this tool use for later reference
                logger.info(f"    Tool Use Initiated: {block.name} (ID: {block.id})")
                
            elif isinstance(block, ToolResultBlock):
                logger.info(f"    Tool Result Received: (Tool Use ID: {block.tool_use_id})")
                
                

                # Track failed tools
                if block.is_error:
                    logger.error(f"    Tool Result - Error (Tool Use ID: {block.tool_use_id})\nContent:\n{block.content}")
            elif isinstance(block, ThinkingBlock):
                logger.info(f"    Thinking: {block.thinking}")

        return " ".join(texts)

    def handle_system_message(block: SystemMessage) -> str:
        data_yaml = (
            yaml.dump(block.data, default_flow_style=False).strip()
            if block.data
            else "N/A"
        )
        message = f"System Message - {block.subtype}\nData:\n{data_yaml}"
        logger.info(message)
        return message

    if isinstance(msg, UserMessage):
        return concat_text(msg.content)

    elif isinstance(msg, AssistantMessage):
        return concat_text(msg.content, prefix="Claude: ")

    elif isinstance(msg, SystemMessage):
        return handle_system_message(msg)

    elif isinstance(msg, ResultMessage):  # type: ignore
        logger.info("Session ended")
        logger.info(
            f"Duration: {msg.duration_ms}ms, API Duration: {msg.duration_api_ms}ms"
        )
        logger.info(f"Turns: {msg.num_turns}, Error: {msg.is_error}")
        logger.info(
            f"Total Cost: ${msg.total_cost_usd:.5f}"
            if msg.total_cost_usd
            else "Total Cost: N/A"
        )
        if msg.usage:
            usage_yaml = yaml.dump(msg.usage, default_flow_style=False).strip()
            logger.debug(f"Usage:\n{usage_yaml}")
        else:
            logger.debug("Usage: N/A")
        logger.debug(f"Result: {msg.result}" if msg.result else "Result: N/A")

        return msg.result if msg.result else ""

    else:
        logger.warning(f"Unknown message type: {type(msg)}")
        return ""
    
def configure_logging() -> None:
    """Configure logging with user-friendly formatters."""
    # Create logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Clear any existing handlers
    root_logger.handlers.clear()

    # Console handler with user-friendly formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    # console_formatter = UserFriendlyFormatter()
    # console_handler.setFormatter(console_formatter)

    # File handler with detailed formatting
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    log_dir = Path("coder/out")
    log_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    log_file = log_dir / f"{timestamp}.log"
    file_handler = logging.FileHandler(log_file, mode="w")
    file_handler.setLevel(logging.DEBUG)
    # file_formatter = UserFriendlyFormatter()  # Use same friendly format for file too
    # file_handler.setFormatter(file_formatter)

    # Add handlers to logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    logger.info(f"Logging configured. Writing to {log_file}")

async def main():
    """Main workflow."""
   
    # Call Claude SDK
    configure_logging()
    logger.info("Starting Claude SDK client, analyzing receipt image...")
    try:
        async with ClaudeSDKClient() as client:
            await client.query(prompt=prompt)

            await handle_response(client)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Client error: {error_msg}")


if __name__ == "__main__":
    asyncio.run(main())