"""Anthropic API client wrapper with retry logic."""

import base64
import time
import logging
import json
import re
from typing import Dict, Any

from anthropic import Anthropic, APIError, APIConnectionError, RateLimitError, AuthenticationError

from ...domain.exceptions import (
    ApiExtractionError, ParseExtractionError, UnknownExtractionError
)
from ...domain.models import ImageExtractionRequest
from ..config import settings

logger = logging.getLogger(__name__)


class ClaudeApiClient:
    """Wrapper for Anthropic Claude API with retry logic and error handling."""
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self._extraction_prompt = self._build_extraction_prompt()
    
    def extract_receipt_data(self, request: ImageExtractionRequest) -> Dict[str, Any]:
        """
        Extract receipt data using Claude API with retry logic.
        
        Args:
            request: Image extraction request with file data
            
        Returns:
            Parsed JSON response from Claude API
            
        Raises:
            ApiExtractionError: For API-related failures
            ParseExtractionError: For response parsing failures
            UnknownExtractionError: For unexpected errors
        """
        for attempt in range(settings.max_retries):
            try:
                return self._make_api_call(request)
            except (RateLimitError, APIConnectionError) as e:
                if attempt == settings.max_retries - 1:
                    logger.error(f"API call failed after {settings.max_retries} attempts for {request.filename}: {e}")
                    raise ApiExtractionError(
                        f"API call failed after retries: {str(e)}", 
                        request.filename, 
                        e
                    )
                
                backoff_delay = min(
                    settings.base_backoff_delay * (2 ** attempt),
                    settings.max_backoff_delay
                )
                logger.warning(f"API call failed for {request.filename}, retrying in {backoff_delay}s: {e}")
                time.sleep(backoff_delay)
            except AuthenticationError as e:
                logger.error(f"Authentication failed for {request.filename}: {e}")
                raise ApiExtractionError(f"Authentication failed: {str(e)}", request.filename, e)
            except APIError as e:
                logger.error(f"API error for {request.filename}: {e}")
                raise ApiExtractionError(f"API error: {str(e)}", request.filename, e)
            except Exception as e:
                logger.error(f"Unexpected error during API call for {request.filename}: {e}")
                raise UnknownExtractionError(f"Unexpected API error: {str(e)}", request.filename, e)
    
    def _make_api_call(self, request: ImageExtractionRequest) -> Dict[str, Any]:
        """Make actual API call to Claude."""
        try:
            # Encode image as base64
            image_b64 = base64.b64encode(request.image_data).decode('utf-8')
            
            response = self.client.messages.create(
                model=settings.model_name,
                max_tokens=settings.max_tokens,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": request.mime_type,
                                "data": image_b64
                            }
                        },
                        {
                            "type": "text",
                            "text": self._extraction_prompt
                        }
                    ]
                }],
                extra_headers={"anthropic-enable-thinking": "true"} if settings.enable_thinking else {}
            )
            
            # Parse JSON response
            response_text = response.content[0].text
            try:
                # Extract JSON from markdown code blocks if present
                cleaned_text = self._extract_json_from_response(response_text)
                return json.loads(cleaned_text)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response for {request.filename}: {response_text}")
                raise ParseExtractionError(f"Malformed JSON response: {str(e)}", request.filename, e)
                
        except Exception as e:
            if isinstance(e, (ApiExtractionError, ParseExtractionError)):
                raise
            logger.error(f"Unexpected error in API call for {request.filename}: {e}")
            raise UnknownExtractionError(f"Unexpected error: {str(e)}", request.filename, e)
    
    def _extract_json_from_response(self, response_text: str) -> str:
        """Extract JSON from response text, handling markdown code blocks."""
        # Remove markdown code blocks if present
        json_pattern = r'```(?:json\s*)?\n?(.*?)\n?```'
        match = re.search(json_pattern, response_text, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # If no code blocks, return original text stripped
        return response_text.strip()
    
    def _build_extraction_prompt(self) -> str:
        """Build the extraction prompt for Claude API."""
        return """
You are to anlyze receipts and extract the appropriate information. Most often they are dutch receipts, so it will have wording like BTW instead of VAT and Totaal instead of Total. The receipt might be in other languages, but mainly Dutch.

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
"""