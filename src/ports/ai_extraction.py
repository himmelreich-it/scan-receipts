"""AI extraction port for receipt data extraction."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class AIExtractionPort(ABC):
    """Interface for AI-powered receipt data extraction."""

    @abstractmethod
    def extract_receipt_data(self, receipt_path: str) -> Dict[str, Any]:
        """Extract data from receipt image.

        Args:
            receipt_path: Path to receipt image file.

        Returns:
            Extracted receipt data.
        """
        pass
