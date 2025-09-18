"""Anthropic AI extraction adapter implementation."""

import base64
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict

import anthropic

from ports.ai_extraction import AIExtractionPort


# Claude prompt template for receipt analysis - accessible for easy modification
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
"""

logger = logging.getLogger(__name__)


class AnthropicAdapter(AIExtractionPort):
    """Anthropic AI extraction implementation using Claude."""

    def __init__(self) -> None:
        """Initialize Anthropic client."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")

        self.client = anthropic.Anthropic(api_key=api_key)

    def extract_receipt_data(self, receipt_path: str) -> Dict[str, Any]:
        """Extract data from receipt image using Claude.

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
            logger.info(f"Extracting data from {file_path.name}")

            if file_path.suffix.lower() == ".pdf":
                return self._extract_from_pdf(file_path)
            else:
                return self._extract_from_image(file_path)

        except Exception as e:
            logger.error(f"Error extracting from {file_path.name}: {e}")
            raise ValueError(f"Failed to extract receipt data: {e}")

    def _extract_from_image(self, file_path: Path) -> Dict[str, Any]:
        """Extract data from image file (JPG/PNG).

        Args:
            file_path: Path to image file.

        Returns:
            Extracted receipt data.
        """
        # Read and encode image
        with open(file_path, "rb") as f:
            image_data = f.read()

        image_base64 = base64.b64encode(image_data).decode("utf-8")

        # Determine media type
        media_type = "image/jpeg" if file_path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"

        # Call Claude API with the base64 image
        return self._call_claude_api(image_base64, media_type, file_path)

    def _extract_from_pdf(self, file_path: Path) -> Dict[str, Any]:
        """Extract data from PDF file by converting to image.

        Args:
            file_path: Path to PDF file.

        Returns:
            Extracted receipt data.
        """
        try:
            from pdf2image import convert_from_path  # type: ignore
        except ImportError:
            raise ValueError("pdf2image library required for PDF processing")

        # Convert PDF to image (first page only)
        images = convert_from_path(file_path, first_page=1, last_page=1)

        if not images:
            raise ValueError("No pages found in PDF")

        # Convert PIL image to base64
        import io

        image = images[0]
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_data = buffer.getvalue()
        image_base64 = base64.b64encode(image_data).decode("utf-8")

        # Call Claude API with the converted image
        return self._call_claude_api(image_base64, "image/png", file_path)

    def _call_claude_api(self, image_base64: str, media_type: str, file_path: Path) -> Dict[str, Any]:
        """Call Claude API to analyze receipt image.

        Args:
            image_base64: Base64 encoded image data.
            media_type: MIME type of the image.
            file_path: Original file path for context.

        Returns:
            Extracted receipt data.
        """
        # Call Claude API
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",  # type: ignore
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_base64,
                            },
                        },
                        {"type": "text", "text": CLAUDE_RECEIPT_PROMPT},
                    ],
                }
            ],
        )

        return self._parse_response(response, file_path)

    def _parse_response(self, response: Any, file_path: Path) -> Dict[str, Any]:
        """Parse Claude API response and validate required fields.

        Args:
            response: Claude API response.
            file_path: Original file path for fallback description.

        Returns:
            Validated receipt data dictionary.

        Raises:
            ValueError: If response parsing fails or required fields missing.
        """
        try:
            # Extract text content from response
            content = response.content[0].text

            # Try to parse JSON from response
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON from text if it's embedded in other text
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                else:
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