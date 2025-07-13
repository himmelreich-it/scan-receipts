"""Claude API integration for receipt data extraction."""

import json
import logging
import base64
from typing import Dict, Any
from pathlib import Path
from ..application.ports import AIExtractionPort


logger = logging.getLogger(__name__)


# JSON Schema for validating API responses
EXTRACTION_SCHEMA = {
    "type": "object",
    "required": ["amount", "description", "currency", "date", "confidence"],
    "properties": {
        "amount": {"type": "number"},
        "tax": {"type": ["number", "null"]},
        "tax_percentage": {"type": ["number", "null"]},
        "description": {"type": "string"},
        "currency": {"type": "string"},
        "date": {"type": "string"},
        "confidence": {"type": "integer", "minimum": 0, "maximum": 100},
    },
}


class AnthropicAdapter(AIExtractionPort):
    """Adapter for Anthropic Claude API integration."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        """Initialize adapter with API credentials.

        Args:
            api_key: Anthropic API key
            model: Claude model to use
        """
        self.api_key = api_key
        self.model = model
        self._client = None

    @property
    def client(self):
        """Lazy initialization of Anthropic client."""
        if self._client is None:
            try:
                import anthropic

                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                logger.error(
                    "anthropic library not installed. Install with: uv add anthropic"
                )
                raise ImportError("anthropic library required")
        return self._client

    async def extract_receipt_data(self, file_path: str) -> Dict[str, Any]:
        """Extract structured data from receipt file using Claude API.

        Args:
            file_path: Path to receipt file

        Returns:
            Dictionary containing extracted data fields

        Raises:
            Exception: When extraction fails
        """
        try:
            logger.info(f"Starting Claude API extraction for {file_path}")

            # Read and encode file content
            file_content = self._read_file_content(file_path)

            # Build prompt for extraction
            prompt = self._build_extraction_prompt()

            # Prepare image data for API
            file_extension = Path(file_path).suffix.lower()
            if file_extension == ".pdf":
                media_type = "application/pdf"
            elif file_extension in [".jpg", ".jpeg"]:
                media_type = "image/jpeg"
            elif file_extension == ".png":
                media_type = "image/png"
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")

            # Encode file content to base64
            encoded_content = base64.b64encode(file_content).decode("utf-8")

            # Make API call
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": encoded_content,
                                },
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
            )

            # Parse response
            response_text = message.content[0].text
            response_data = self._parse_response(response_text)

            logger.info(
                f"Successfully extracted data from {file_path} with confidence {response_data.get('confidence', 'unknown')}"
            )
            return response_data

        except Exception as e:
            logger.error(f"Claude API extraction failed for {file_path}: {e}")
            return self._handle_api_error(e)

    def _read_file_content(self, file_path: str) -> bytes:
        """Read file content for API submission."""
        try:
            with open(file_path, "rb") as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Failed to read file {file_path}: {e}")

    def _build_extraction_prompt(self) -> str:
        """Build extraction prompt for Claude API."""
        return """You are to anlyze receipts and extract the appropriate information. Most often they are dutch receipts, so it will have wording like BTW instead of VAT and Totaal instead of Total. The receipt might be in other languages, but mainly Dutch.

Analyze this receipt image and extract the following financial information:  

```
{
    "amount": <total purchase amount as number>,
    "tax": <tax amount as number, or 0 if not separately listed>,
    "tax_percentage": <tax percentage as number, or 0 if not separately listed>,
    "description": "<business name or transaction description>",
    "currency": "<3-letter currency code like EUR, USD, GBP>",
    "date": "<transaction date in dd-MM-YYYY format>",
    "confidence": <integer from 0-100 indicating extraction confidence>
}
```

Guidelines: 
* Extract the total amount including tax
* If tax is separately listed, extract it; otherwise use 0
* Use standard 3-letter currency codes
* Format date as dd-MM-YYYY (e.g., 15-03-2024)
* Provide confidence score based on image quality and text clarity
* For description, prefer business name over generic terms"""

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse Claude API response to extract JSON data.

        Args:
            response: Raw API response text

        Returns:
            Parsed JSON data

        Raises:
            Exception: When parsing fails
        """
        try:
            # Try to find JSON in response
            response = response.strip()

            # Handle case where response is wrapped in markdown
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]

            # Parse JSON
            data = json.loads(response)

            # Validate required fields
            self._validate_response_data(data)

            return data

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}. Response: {response[:200]}...")
            raise Exception(f"Invalid JSON response from API: {e}")
        except Exception as e:
            logger.error(f"Response parsing failed: {e}")
            raise

    def _validate_response_data(self, data: Dict[str, Any]) -> None:
        """Validate API response data against schema."""
        required_fields = EXTRACTION_SCHEMA["required"]

        for field in required_fields:
            if field not in data:
                raise Exception(f"Missing required field: {field}")

        # Validate confidence score
        confidence = data.get("confidence")
        if not isinstance(confidence, int) or not 0 <= confidence <= 100:
            raise Exception(f"Invalid confidence score: {confidence}")

        # Validate amount
        amount = data.get("amount")
        if not isinstance(amount, (int, float)) or amount < 0:
            raise Exception(f"Invalid amount: {amount}")

    def _handle_api_error(self, error: Exception) -> Dict[str, Any]:
        """Handle API errors and return error response.

        Args:
            error: Exception that occurred

        Returns:
            Error response dictionary
        """
        error_msg = str(error)
        logger.error(f"API error: {error_msg}")

        return {
            "amount": 0,
            "tax": None,
            "tax_percentage": None,
            "description": "API_FAILURE",
            "currency": "EUR",
            "date": "01-01-1970",
            "confidence": 0,
        }
