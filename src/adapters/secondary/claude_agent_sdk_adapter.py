"""Claude Agent SDK extraction adapter implementation."""

import asyncio
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, ToolPermissionContext, PermissionResultAllow, PermissionResultDeny
from claude_agent_sdk.types import ResultMessage

from ports.ai_extraction import AIExtractionPort


# Claude prompt template for receipt analysis - shared with AnthropicAdapter
CLAUDE_RECEIPT_PROMPT = """
Analyze this receipt image and extract the following information in JSON format:

{
  "amount": "required - total amount as number string, e.g. '25.99'",
  "tax": "optional - tax amount as number string, e.g. '2.08' or empty string if not found",
  "tax_percentage": "optional - tax percentage as string, e.g. '8.25' or empty string if not found",
  "description": "required - vendor name or main description from receipt",
  "currency": "required - currency code, e.g. 'USD', 'EUR', 'GBP'",
  "date": "required - date in YYYY-MM-DD format, e.g. '2024-03-15'",
  "confidence": "required - confidence score 0-100 as string, e.g. '85'"
}

Rules:
- Always return valid JSON
* Extract the total amount including tax
* If tax is separately listed, extract it; otherwise use 0
* Use standard 3-letter currency codes
* Format date as dd-MM-YYYY (e.g., 15-03-2024 for the 15th of March 2024)
* Provide confidence score based on image quality and text clarity
* For description, prefer business name over generic terms, otherwise use filename
* When multiple dates exist on receipt, purchase date takes priority over printed date

Important Notes:
* Most receipts are dutch, they will often use comma as decimal separator (e.g. 12,34) and terms like 'BTW' for tax.
"""

logger = logging.getLogger(__name__)


async def my_permission_callback(
    tool_name: str,
    input_data: Dict[str, Any],
    context: ToolPermissionContext
) -> PermissionResultAllow | PermissionResultDeny:
    """Control tool permissions based on tool type and input."""

    # Log the tool request
    logger.info("Tool Permission Request", extra={
        "tool": tool_name,
        "input": input_data,
        "suggestions": context.suggestions
    })

    # Always allow read operations
    if tool_name in ["Read", "Glob", "Grep"]:
        logger.info(f"   ✅ Automatically allowing {tool_name} (read-only operation)")
        return PermissionResultAllow()

    # Deny write operations to system directories
    if tool_name in ["Write", "Edit", "MultiEdit"]:
        file_path = input_data.get("file_path", "")
        if file_path.startswith("/etc/") or file_path.startswith("/usr/"):
            logger.info(f"   ❌ Denying write to system directory: {file_path}")
            return PermissionResultDeny(
                message=f"Cannot write to system directory: {file_path}"
            )

        # Redirect writes to a safe directory
        if not file_path.startswith("/tmp/") and not file_path.startswith("./"):
            safe_path = f"./safe_output/{file_path.split('/')[-1]}"
            logger.info(f"   ⚠️  Redirecting write from {file_path} to {safe_path}")
            modified_input = input_data.copy()
            modified_input["file_path"] = safe_path
            return PermissionResultAllow(
                updated_input=modified_input
            )

    # Check dangerous bash commands
    if tool_name == "Bash":
        command = input_data.get("command", "")
        dangerous_commands = ["rm -rf", "sudo", "chmod 777", "dd if=", "mkfs"]

        for dangerous in dangerous_commands:
            if dangerous in command:
                logger.info(f"   ❌ Denying dangerous command: {command}")
                return PermissionResultDeny(
                    message=f"Dangerous command pattern detected: {dangerous}"
                )

        # Allow but log the command
        logger.info(f"   ✅ Allowing bash command: {command}")
        return PermissionResultAllow()

    # For all other tools, ask the user
    logger.info(f"   ❓ Unknown tool: {tool_name}")
    logger.info(f"      Input: {json.dumps(input_data, indent=6)}")
    user_input = input("   Allow this tool? (y/N): ").strip().lower()

    if user_input in ("y", "yes"):
        return PermissionResultAllow()
    else:
        return PermissionResultDeny(
            message="User denied permission"
        )


class ClaudeAgentSdkAdapter(AIExtractionPort):
    """Claude Agent SDK extraction implementation using ClaudeSDKClient.

    This adapter leverages the existing Claude authentication via the Agent SDK,
    eliminating the need for separate API key management.
    """

    def __init__(self) -> None:
        """Initialize Claude Agent SDK adapter.

        No API key configuration needed - uses existing Claude authentication.
        """
        pass

    def extract_receipt_data(self, receipt_path: str) -> Dict[str, Any]:
        """Extract data from receipt image using Claude Agent SDK.

        Args:
            receipt_path: Path to receipt image file.

        Returns:
            Extracted receipt data with keys: amount, tax, tax_percentage,
            description, currency, date, confidence.

        Raises:
            ValueError: If file is not supported or extraction fails.
            FileNotFoundError: If file doesn't exist.
        """
        file_path = Path(receipt_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Receipt file not found: {receipt_path}")

        # Check file extension
        if file_path.suffix.lower() not in {".pdf", ".jpg", ".jpeg", ".png"}:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")

        try:
            logger.info(f"Extracting data from {file_path.name} using Agent SDK")

            # Run async extraction in sync context
            # Handle both regular Python and Jupyter notebook environments
            try:
                # Check if there's a running event loop (like in Jupyter)
                asyncio.get_running_loop()
                # We're in a running loop, need to run async code in a new thread
                import threading

                # We need to run the async function in a new thread with its own event loop
                # because we can't use asyncio.run() in a running loop
                result_container: list[Dict[str, Any]] = []
                exception_container: list[Exception] = []

                def run_in_new_loop() -> None:
                    new_loop = asyncio.new_event_loop()
                    try:
                        asyncio.set_event_loop(new_loop)
                        result = new_loop.run_until_complete(self._extract_async(file_path))
                        result_container.append(result)
                    except Exception as e:
                        exception_container.append(e)
                    finally:
                        new_loop.close()

                thread = threading.Thread(target=run_in_new_loop)
                thread.start()
                thread.join()

                if exception_container:
                    raise exception_container[0]

                return result_container[0]

            except RuntimeError:
                # No running loop, we can use asyncio.run() directly
                return asyncio.run(self._extract_async(file_path))

        except Exception as e:
            logger.error(f"Error extracting from {file_path.name}: {e}")
            raise ValueError(f"Failed to extract receipt data: {e}")

    async def _extract_async(self, file_path: Path) -> Dict[str, Any]:
        """Async extraction implementation.

        Args:
            file_path: Path to receipt file.

        Returns:
            Extracted receipt data.
        """
        if file_path.suffix.lower() == ".pdf":
            return await self._extract_from_pdf(file_path)
        else:
            return await self._extract_from_image(file_path)

    async def _extract_from_image(self, file_path: Path) -> Dict[str, Any]:
        """Extract data from image file (JPG/PNG).

        Args:
            file_path: Path to image file.

        Returns:
            Extracted receipt data.
        """
        # Use the agent approach: point to file and let it read with tools
        return await self._call_claude_agent_sdk(file_path)

    async def _extract_from_pdf(self, file_path: Path) -> Dict[str, Any]:
        """Extract data from PDF file.

        Args:
            file_path: Path to PDF file.

        Returns:
            Extracted receipt data.
        """
        # Agent SDK can read PDFs directly with the Read tool
        return await self._call_claude_agent_sdk(file_path)

    async def _call_claude_agent_sdk(self, file_path: Path) -> Dict[str, Any]:
        """Call Claude Agent SDK to analyze receipt file.

        Uses the agentic approach: provides the file path and lets Claude
        use its Read tool to access and analyze the image.

        Args:
            file_path: Path to receipt file.

        Returns:
            Extracted receipt data.
        """
        # Use absolute path for the file
        absolute_path = file_path.resolve()

        # Create prompt that references the image file
        prompt = f"""Analyze the receipt image at: {absolute_path}

{CLAUDE_RECEIPT_PROMPT}"""

        # Configure options to auto-accept file read permissions
        options = ClaudeAgentOptions(
            can_use_tool=my_permission_callback,
            # Use default permission mode to ensure callbacks are invoked
            permission_mode="default",
        )

        # Use ClaudeSDKClient with context manager
        response_text = ""
        async with ClaudeSDKClient(options=options) as client:
            # Send query
            await client.query(prompt=prompt)

            # Collect ONLY the final result from ResultMessage, not intermediate messages
            async for message in client.receive_response():
                if isinstance(message, ResultMessage):
                    # The final result is in ResultMessage.result
                    if message.result:
                        response_text = message.result  # Use assignment, not +=
                        logger.debug(f"Got final result from ResultMessage: {message.result[:200]}...")
                        break  # We have the final result, stop processing

            if not response_text:
                logger.warning("No response text collected from Agent SDK")
            else:
                logger.debug(f"Final response: {response_text[:200]}...")

        return self._parse_response_text(response_text, file_path)

    def _parse_response_text(self, response_text: str, file_path: Path) -> Dict[str, Any]:
        """Parse response text and extract JSON data.

        Args:
            response_text: Raw text response from Claude.
            file_path: Original file path for fallback description.

        Returns:
            Validated receipt data dictionary.

        Raises:
            ValueError: If response parsing fails or required fields missing.
        """
        try:
            # Log the actual response for debugging
            if not response_text:
                logger.error("Empty response text received from Agent SDK")
                raise ValueError("Empty response from Agent SDK")

            # Try to parse JSON from response
            try:
                data = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON from text if it's embedded in other text
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                else:
                    logger.error(f"No JSON found in response. Response text: {response_text[:500]}")
                    raise ValueError("No valid JSON found in response")

            # Validate and clean data
            validated_data = self._validate_extracted_data(data, file_path)

            logger.info(f"Successfully extracted data from {file_path.name}")
            return validated_data

        except Exception as e:
            logger.error(f"Error parsing response for {file_path.name}: {e}")
            raise ValueError(f"Failed to parse extraction response: {e}")

    def _validate_extracted_data(self, data: Dict[str, Any], file_path: Path) -> Dict[str, Any]:
        """Validate and clean extracted data.

        Args:
            data: Raw extracted data.
            file_path: Original file path for fallback description.

        Returns:
            Validated data dictionary.

        Raises:
            ValueError: If required fields are missing or invalid.
        """
        # Required fields
        required_fields = {"amount", "currency", "date", "confidence"}
        missing_fields = required_fields - set(data.keys())

        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        # Validate amount (must be non-empty)
        if not str(data.get("amount", "")).strip():
            raise ValueError("Amount field cannot be empty")

        # Validate currency (must be non-empty)
        if not str(data.get("currency", "")).strip():
            raise ValueError("Currency field cannot be empty")

        # Validate date (must be non-empty)
        if not str(data.get("date", "")).strip():
            raise ValueError("Date field cannot be empty")

        # Validate confidence (must be non-empty)
        if not str(data.get("confidence", "")).strip():
            raise ValueError("Confidence field cannot be empty")

        # Use filename as fallback description if empty
        description = str(data.get("description", "")).strip()
        if not description:
            description = file_path.stem  # filename without extension

        # Return validated data with all required fields
        return {
            "amount": str(data["amount"]).strip(),
            "tax": str(data.get("tax", "")).strip(),
            "tax_percentage": str(data.get("tax_percentage", "")).strip(),
            "description": description,
            "currency": str(data["currency"]).strip(),
            "date": str(data["date"]).strip(),
            "confidence": str(data["confidence"]).strip(),
        }
