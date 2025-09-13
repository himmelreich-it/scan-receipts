"""Anthropic AI extraction adapter implementation."""

import hashlib
import logging
from datetime import datetime
from pathlib import Path

from core.domain.receipt import ReceiptData
from ports.ai_extraction import AIExtractionPort

logger = logging.getLogger(__name__)


class AnthropicAdapter(AIExtractionPort):
    """PLACEHOLDER: Anthropic AI extraction implementation."""

    def extract_receipt_data(self, receipt_path: Path) -> ReceiptData:
        """Extract data from receipt image.

        Args:
            receipt_path: Path to receipt image file.

        Returns:
            Extracted receipt data.
        """
        logger.warning(f"PLACEHOLDER: Processing {receipt_path.name} with mock data")

        # Generate a simple hash for the file
        file_hash = hashlib.md5(str(receipt_path).encode()).hexdigest()

        # Return mock data for now - in real implementation this would call Anthropic API
        return ReceiptData(
            amount="100.00",
            tax="19.00",
            tax_percentage="19.0",
            description=f"Mock receipt from {receipt_path.name}",
            currency="EUR",
            date=datetime.now().strftime("%Y-%m-%d"),
            confidence="0.95",
            hash=file_hash,
            done_filename=receipt_path.name,
        )
