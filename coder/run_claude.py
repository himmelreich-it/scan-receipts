import logging
import asyncio
import datetime
import argparse
from typing import Any, List, Dict
import yaml

from pathlib import Path
from claude_code_sdk import (
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


# Logger instance
logger = logging.getLogger(__name__)

# Global tracking for tools
failed_tools: List[Dict[str, str]] = []
permission_errors: List[Dict[str, str]] = []
tool_use_registry: Dict[str, Dict[str, Any]] = {}


def register_tool_use(tool_id: str, tool_name: str, tool_input: Dict[str, Any]):
    """Register a tool use for later reference."""
    tool_use_registry[tool_id] = {"tool_name": tool_name, "input": tool_input}


def track_tool_failure(tool_name: str, tool_id: str, reason: str):
    """Track a tool failure for any reason."""
    # Try to get more details from registry
    if tool_id in tool_use_registry:
        registry_entry = tool_use_registry[tool_id]
        tool_name = registry_entry["tool_name"]
        tool_input = registry_entry["input"]

        # For Bash commands, include the actual command
        if tool_name == "Bash" and "command" in tool_input:
            command = tool_input["command"]
            tool_display = f"Bash({command})"
        else:
            tool_display = tool_name
    else:
        tool_display = tool_name

    # Categorize the failure
    is_permission_error = any(
        keyword in reason.lower()
        for keyword in ["requires approval", "rejected", "permission", "blocked", "not allowed"]
    )

    failure_entry = {
        "tool_name": tool_display,
        "tool_use_id": tool_id,
        "error": reason[:200] + "..." if len(reason) > 200 else reason,
    }

    if is_permission_error:
        permission_errors.append(failure_entry)
    else:
        failed_tools.append(failure_entry)


class UserFriendlyFormatter(logging.Formatter):
    """Custom formatter that only shows ERROR prefix for errors, and formats objects nicely."""

    def format(self, record: logging.LogRecord) -> str:
        message = record.getMessage()

        # Context-aware cleanup based on message type
        message = self.clean_message_by_context(message)

        # Format objects/dicts as YAML with proper indentation
        if hasattr(record, "args") and record.args:
            formatted_args: list[Any] = []
            for arg in record.args:
                if isinstance(arg, (dict, list)):
                    yaml_str = yaml.dump(arg, default_flow_style=False).strip()
                    # Add proper indentation for nested content
                    indented_yaml = "\n".join(
                        "    " + line for line in yaml_str.split("\n")
                    )
                    formatted_args.append(f"\n{indented_yaml}")
                else:
                    formatted_args.append(str(arg))
            record.args = tuple(formatted_args)
            message = record.getMessage()
            # Clean the final message again after formatting
            message = self.clean_message_by_context(message)

        # Add proper indentation for tool-related messages
        if message.startswith("    Tool"):
            # Already properly indented
            pass
        elif "Input:" in message or "Content:" in message:
            # Ensure these are properly indented under tool messages
            lines = message.split("\n")
            formatted_lines = []
            for line in lines:
                if line.strip():
                    formatted_lines.append("    " + line.strip())  # pyright: ignore[reportUnknownMemberType]
                else:
                    formatted_lines.append("")  # pyright: ignore[reportUnknownMemberType]
            message = "\n".join(formatted_lines)  # pyright: ignore[reportUnknownArgumentType]

        # Only show ERROR and WARNING prefixes
        if record.levelno >= logging.ERROR:
            return f"ERROR - {message}"
        elif record.levelno >= logging.WARNING:
            return f"WARNING - {message}"
        else:
            return message

    def clean_message_by_context(self, message: str) -> str:
        """Context-aware message cleaning based on content type."""

        # Always remove these unicode artifacts
        message = message.replace("\u2192", "").replace("\\u21", "")

        # For Tool Results - aggressive cleanup since these often contain escaped content
        if "Tool Result -" in message:
            message = self.unescape_tool_content(message)

        # For Tool Use Input - moderate cleanup, preserve intentional structure
        elif "Tool Use -" in message or "Input:" in message:
            message = self.clean_tool_input(message)

        # For Claude responses - minimal cleanup to preserve formatting
        elif message.startswith("Claude:"):
            message = self.clean_claude_response(message)

        # For system/data messages - preserve structure but clean display
        elif "System Message" in message or "Data:" in message:
            message = self.clean_system_message(message)

        return message

    def unescape_tool_content(self, message: str) -> str:
        """Aggressively clean tool result content for readability."""
        # Remove line continuation backslashes
        message = message.replace("\\\n", "\n")
        message = message.replace("\\n", "\n")
        message = message.replace("\\t", "    ")
        message = message.replace('\\"', '"')
        message = message.replace("\\'", "'")
        message = message.replace("\\\\", "\\")

        # Clean up numbered line prefixes like "     1→"
        import re

        message = re.sub(r"\s+\d+\u2192", "", message)
        message = re.sub(r"\s+\d+→", "", message)
        # Also handle escaped versions
        message = re.sub(r"\s+\d+\\u2192", "", message)

        return message

    def clean_tool_input(self, message: str) -> str:
        """Moderate cleanup for tool inputs, preserve YAML/JSON structure."""
        # Only clean obvious display artifacts
        message = message.replace("\\\n", "\n")
        message = message.replace("\\n", "\n")
        message = message.replace("\\t", "    ")
        return message

    def clean_claude_response(self, message: str) -> str:
        """Minimal cleanup for Claude responses to preserve intended formatting."""
        # Only remove clear artifacts, preserve intentional escapes
        message = message.replace("\\\n", "")  # Remove line continuations
        return message

    def clean_system_message(self, message: str) -> str:
        """Clean system messages while preserving data structure."""
        # Basic cleanup only
        message = message.replace("\\n", "\n")
        message = message.replace("\\t", "    ")
        return message


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
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    log_dir = Path("coder/out")
    log_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    log_file = log_dir / f"{mode}-{ticket_number}-{timestamp}.log"
    file_handler = logging.FileHandler(log_file, mode="w")
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
    try:
        async for msg in client.receive_response():
            responses.append(handle_message(msg))
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Response handling error: {error_msg}")

        # Track approval failures specifically
        if "rejected" in error_msg.lower() or "approval" in error_msg.lower():
            track_tool_failure("SDK", "unknown", f"Tool approval rejected: {error_msg}")

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
                register_tool_use(block.id, block.name, block.input or {})

                tool_input = (
                    yaml.dump(block.input, default_flow_style=False).strip()
                    if block.input
                    else "N/A"
                )
                logger.info(
                    f"    Tool Use - {block.name} (ID: {block.id})\nInput:\n{tool_input}"
                )
            elif isinstance(block, ToolResultBlock):
                tool_content = (
                    yaml.dump(block.content, default_flow_style=False).strip()
                    if block.content
                    else "N/A"
                )
                error_status = "Error" if block.is_error else "Success"
                logger.info(
                    f"    Tool Result - {error_status} (Tool Use ID: {block.tool_use_id})\nContent:\n{tool_content}"
                )

                # Track failed tools
                if block.is_error:
                    track_tool_failure("Unknown", block.tool_use_id, str(block.content))
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

        # Log failed tools summary
        if failed_tools or permission_errors:
            logger.info("=" * 80)
            logger.info("TOOL EXECUTION SUMMARY")
            logger.info("=" * 80)

        # Show actual failures (bugs, errors, etc.)
        if failed_tools:
            logger.info(f"FAILED TOOLS SUMMARY ({len(failed_tools)} failures)")
            logger.info("-" * 40)
            for i, failure in enumerate(failed_tools, 1):
                tool_name = failure.get("tool_name", "Unknown")
                logger.info(f"{i}. Tool: {tool_name} (ID: {failure['tool_use_id']})")
                logger.info(f"   Error: {failure['error']}")
                logger.info("")

        # Show permission/approval errors separately
        if permission_errors:
            logger.info(f"TOOL PERMISSION ERRORS ({len(permission_errors)} blocked)")
            logger.info("-" * 40)
            logger.info("These tools need to be added to your allowlist:")
            logger.info("")
            for i, failure in enumerate(permission_errors, 1):
                tool_name = failure.get("tool_name", "Unknown")
                logger.info(f"{i}. Tool: {tool_name} (ID: {failure['tool_use_id']})")
                logger.info(f"   Reason: {failure['error']}")
                logger.info("")

            # Generate suggested allowlist entries
            suggested_allowances = []
            for failure in permission_errors:
                tool_name = failure.get("tool_name", "Unknown")
                if tool_name.startswith("Bash(") and tool_name.endswith(")"):
                    # Extract command from Bash(command)
                    command = tool_name[5:-1]  # Remove "Bash(" and ")"
                    # Create allowance pattern
                    suggested_allowances.append(f"Bash({command}:*)") # pyright: ignore[reportUnknownMemberType]
                elif tool_name != "Unknown":
                    suggested_allowances.append(f"{tool_name}(*)") # pyright: ignore[reportUnknownMemberType]

            if suggested_allowances:
                logger.info("SUGGESTED ALLOWLIST ADDITIONS:")
                logger.info("-" * 40)
                for allowance in sorted(set(suggested_allowances)): # pyright: ignore[reportUnknownVariableType, reportUnknownArgumentType]
                    logger.info(f"  - {allowance}")
                logger.info("")

        return msg.result if msg.result else ""

    else:
        logger.warning(f"Unknown message type: {type(msg)}")
        return ""


async def main():
    """Main workflow."""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Claude Coder - AI-powered ticket implementation"
    )
    parser.add_argument(
        "mode",
        help="implementation mode",
        choices=["implement-ticket", "resolve-pr-comments"],
    )
    parser.add_argument("ticket_number", help="Ticket number to implement")

    # Parse known arguments and capture unknown ones
    args, [] = parser.parse_known_args()

    print(f"Ticket number: {args.ticket_number}")
    print(f"Mode: {args.mode}")

    # Configure logging for this ticket
    configure_logging(args.ticket_number, args.mode)

    # Call Claude SDK
    try:
        async with ClaudeSDKClient() as client:
            prompt = f"/{args.mode} {args.ticket_number}"
            await client.query(prompt=prompt)

            await handle_response(client)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Client error: {error_msg}")

        # Track permission/approval failures
        if any(
            keyword in error_msg.lower()
            for keyword in ["rejected", "approval", "permission", "blocked"]
        ):
            track_tool_failure(
                "Client", "N/A", f"Permission/approval error: {error_msg}"
            )

        raise


if __name__ == "__main__":
    asyncio.run(main())
