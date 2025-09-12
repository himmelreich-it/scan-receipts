"""Anthropic AI extraction adapter - placeholder implementation."""

import logging
from pathlib import Path

from core.domain import ProcessingError, Receipt
from ports import AIExtractionPort

logger = logging.getLogger(__name__)


class AnthropicAdapter(AIExtractionPort):
    """PLACEHOLDER: Anthropic AI extraction adapter."""

    def extract_receipt_data(self, file_path: Path) -> Receipt:
        """PLACEHOLDER: Extract receipt data using Anthropic AI.
        
        Args:
            file_path: Path to receipt file.
            
        Returns:
            Receipt with placeholder extracted data.
            
        Raises:
            ProcessingError: If extraction fails.
        """
        logger.warning(f"PLACEHOLDER: AI extraction for {file_path.name}")
        
        if not file_path.exists():
            raise ProcessingError(f"File not found: {file_path}")
        
        # Return placeholder receipt with dummy data
        # This simulates AI extraction results
        return Receipt(
            file_path=file_path,
            total=25.99,  # Placeholder amount
            vendor="Sample Vendor",  # Placeholder vendor
            confidence=0.85,  # Placeholder confidence
        )