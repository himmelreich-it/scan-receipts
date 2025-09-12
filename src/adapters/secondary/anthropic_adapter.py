"""Anthropic AI extraction adapter implementation."""

import logging
from typing import Any, Dict

from ports.ai_extraction import AIExtractionPort

logger = logging.getLogger(__name__)


class AnthropicAdapter(AIExtractionPort):
    """PLACEHOLDER: Anthropic AI extraction implementation."""
    
    def extract_receipt_data(self, receipt_path: str) -> Dict[str, Any]:
        """Extract data from receipt image.
        
        Args:
            receipt_path: Path to receipt image file.
            
        Returns:
            Extracted receipt data.
        """
        logger.warning("PLACEHOLDER: Anthropic extract_receipt_data not yet implemented")
        return {}