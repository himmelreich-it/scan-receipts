"""AI extraction port definition."""

from abc import ABC, abstractmethod
from pathlib import Path

from core.domain import Receipt


class AIExtractionPort(ABC):
    """Port for AI-powered receipt data extraction."""

    @abstractmethod
    def extract_receipt_data(self, file_path: Path) -> Receipt:
        """Extract receipt data from a file.
        
        Args:
            file_path: Path to receipt file.
            
        Returns:
            Receipt with extracted data.
            
        Raises:
            ProcessingError: If extraction fails.
        """
        pass