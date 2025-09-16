import logging
import asyncio
import datetime
import argparse
from typing import Any
import yaml

from pathlib import Path
from  claude_code_sdk  import (
    AssistantMessage,
    ClaudeCodeOptions,
    ClaudeSDKClient,
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


# Logger instance
logger = logging.getLogger(__name__)


class UserFriendlyFormatter(logging.Formatter):
    """Custom formatter that only shows ERROR prefix for errors, and formats objects nicely."""

    def format(self, record: logging.LogRecord) -> str:
        # Format objects/dicts as YAML
        if hasattr(record, 'args') and record.args:
            formatted_args: list[Any]   = []
            for arg in record.args:
                if isinstance(arg, (dict, list)):
                    formatted_args.append(f"\n{yaml.dump(arg, default_flow_style=False).strip()}")
                else:
                    formatted_args.append(str(arg))
            record.args = tuple(formatted_args)

        # Only show ERROR and WARNING prefixes
        if record.levelno >= logging.ERROR:
            return f"ERROR - {record.getMessage()}"
        elif record.levelno >= logging.WARNING:
            return f"WARNING - {record.getMessage()}"
        else:
            return record.getMessage()


def configure_logging(ticket_number: str, mode: str) -> None:
    """Configure logging with user-friendly formatters."""
    # Create logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Clear any existing handlers
    root_logger.handlers.clear()

    # Console handler with user-friendly formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = UserFriendlyFormatter()
    console_handler.setFormatter(console_formatter)

    # File handler with detailed formatting
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    log_dir = Path("coder/out")
    log_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    log_file = log_dir / f"{mode}-{ticket_number}-{timestamp}.log"
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = UserFriendlyFormatter()  # Use same friendly format for file too
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
    """Standardized message display function with user-friendly formatting."""
    def concat_text(blocks: str | list[ContentBlock], prefix: str = "") -> str:
        texts: list[str] = []
        for block in blocks:
            if isinstance(block, TextBlock):
                logger.info(f"Claude: {block.text}")
                texts.append(f"{prefix}{block.text}")
            elif isinstance(block, ToolUseBlock):
                tool_input = yaml.dump(block.input, default_flow_style=False).strip() if block.input else 'N/A'
                logger.info(f"    Tool Use - {block.name} (ID: {block.id})\nInput:\n{tool_input}")
            elif isinstance(block, ToolResultBlock):
                tool_content = yaml.dump(block.content, default_flow_style=False).strip() if block.content else 'N/A'
                error_status = "Error" if block.is_error else "Success"
                logger.info(f"    Tool Result - {error_status} (Tool Use ID: {block.tool_use_id})\nContent:\n{tool_content}")
            elif isinstance(block, ThinkingBlock):
                logger.info(f"    Thinking: {block.thinking}")

        return " ".join(texts)

    def handle_system_message(block: SystemMessage) -> str:
        data_yaml = yaml.dump(block.data, default_flow_style=False).strip() if block.data else 'N/A'
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
        logger.info(f"Duration: {msg.duration_ms}ms, API Duration: {msg.duration_api_ms}ms")
        logger.info(f"Turns: {msg.num_turns}, Error: {msg.is_error}")
        logger.info(f"Total Cost: ${msg.total_cost_usd:.5f}" if msg.total_cost_usd else "Total Cost: N/A")
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


async def main():
    """Main workflow."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Claude Coder - AI-powered ticket implementation')
    parser.add_argument('mode', help='implementation mode', choices=['implement-ticket', 'resolve-pr-comments'])
    parser.add_argument('ticket_number', help='Ticket number to implement')
    
    # Parse known arguments and capture unknown ones
    args, []= parser.parse_known_args()

    
    print(f"Ticket number: {args.ticket_number}")
    print(f"Mode: {args.mode}")

    # Configure logging for this ticket
    configure_logging(args.ticket_number, args.mode)

    # claude_options = ClaudeCodeOptions(
    #     cwd=str(Path("../").resolve())
    # )

    # Call Claude SDK
    async with ClaudeSDKClient() as client:
        prompt = f"/{args.mode} {args.ticket_number}"
        await client.query(prompt=prompt)

        await handle_response(client)


if __name__ == "__main__":
    asyncio.run(main())