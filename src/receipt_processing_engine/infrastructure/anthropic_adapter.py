"""Claude API integration for receipt data extraction with PDF conversion."""

import json
import logging
import base64
import tempfile
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


class AnthropicAIAdapter(AIExtractionPort):
    """Adapter for Anthropic Claude API with PDF conversion support."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        """Initialize adapter with API credentials.

        Args:
            api_key: Anthropic API key
            model: Claude model to use
        """
        self.api_key = api_key
        self.model = model
        self._client = None
        self.supported_formats = {".pdf", ".jpg", ".jpeg", ".png"}

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

    def supports_file_format(self, file_path: Path) -> bool:
        """Check if file format is supported (PDF, JPG, PNG)."""
        return file_path.suffix.lower() in self.supported_formats

    async def extract_data(self, file_path: Path) -> Dict[str, Any]:
        """Extract structured data from receipt file.

        Process:
        1. Check file format (PDF, JPG, PNG)
        2. Convert PDF to image if needed
        3. Send image to Claude API
        4. Parse JSON response
        5. Return extracted data
        """
        try:
            logger.info(f"Starting Claude API extraction for {file_path}")

            # Check if file format is supported
            if not self.supports_file_format(file_path):
                raise ValueError(f"Unsupported file format: {file_path.suffix}")

            # Convert PDF to image if needed
            image_path = (
                self._convert_pdf_to_image(file_path)
                if file_path.suffix.lower() == ".pdf"
                else file_path
            )

            # Send image to Claude API
            response_data = await self._send_to_claude_api(image_path)

            # Clean up temporary image file if it was created
            if image_path != file_path:
                image_path.unlink()

            logger.info(
                f"Successfully extracted data from {file_path} with confidence {response_data.get('confidence', 'unknown')}"
            )
            return response_data

        except Exception as e:
            logger.error(f"Claude API extraction failed for {file_path}: {e}")
            raise e

    def _convert_pdf_to_image(self, pdf_path: Path) -> Path:
        """Convert PDF first page to PNG image.

        Uses pdf2image library to convert PDF to image format
        that can be sent to Anthropic API.
        """
        try:
            from pdf2image import convert_from_path

            # Convert first page of PDF to image
            images = convert_from_path(pdf_path, first_page=1, last_page=1)

            if not images:
                raise ValueError("No pages found in PDF")

            # Save to temporary PNG file
            temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            temp_path = Path(temp_file.name)
            temp_file.close()

            images[0].save(temp_path, "PNG")

            return temp_path

        except ImportError:
            raise ImportError(
                "pdf2image library required for PDF conversion. Install with: uv add pdf2image"
            )
        except Exception as e:
            raise Exception(f"PDF conversion failed: {e}")

    async def _send_to_claude_api(self, image_path: Path) -> Dict[str, Any]:
        """Send image to Claude API and get structured response."""
        try:
            # Read and encode image content
            with open(image_path, "rb") as f:
                image_content = f.read()

            # Build prompt for extraction
            prompt = self._build_extraction_prompt()

            # Determine media type
            file_extension = image_path.suffix.lower()
            if file_extension in [".jpg", ".jpeg"]:
                media_type = "image/jpeg"
            elif file_extension == ".png":
                media_type = "image/png"
            else:
                raise ValueError(f"Unsupported image type: {file_extension}")

            # Encode image content to base64
            encoded_content = base64.b64encode(image_content).decode("utf-8")

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
            response_text = (
                message.content[0].text
                if hasattr(message.content[0], "text")
                else str(message.content[0])
            )
            response_data = self._parse_extraction_response(response_text)

            return response_data

        except Exception as e:
            raise Exception(f"Claude API call failed: {e}")

    def _parse_extraction_response(self, response: str) -> Dict[str, Any]:
        """Parse Claude API response into structured data."""
        try:
            # Try to find JSON in response
            response = response.strip()

            # Handle case where response is wrapped in markdown
            if response.startswith("```json"):
                response = response[7:]
            elif response.startswith("```"):
                response = response[3:]
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

    def _build_extraction_prompt(self) -> str:
        """Build extraction prompt for Claude API."""
        return """You are to analyze receipts and extract the appropriate information. Most often they are dutch receipts, so it will have wording like BTW instead of VAT and Totaal instead of Total. The receipt might be in other languages, but mainly Dutch.

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
* For description, prefer business name over generic terms
* When multiple dates exist on receipt, purchase date takes priority over printed date"""

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
