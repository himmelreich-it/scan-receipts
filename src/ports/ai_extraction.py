"""AI extraction port for receipt data extraction."""

from abc import ABC, abstractmethod
from pathlib import Path

from core.domain.receipt import ReceiptData


class AIExtractionPort(ABC):
    """Interface for AI-powered receipt data extraction."""

    @abstractmethod
    def extract_receipt_data(self, receipt_path: Path) -> ReceiptData:
        """Extract data from receipt image.

        Args:
            receipt_path: Path to receipt image file.

        Returns:
            Extracted receipt data.
        """
        pass
