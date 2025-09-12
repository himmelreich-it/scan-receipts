"""XLSX port definition."""

from abc import ABC, abstractmethod
from pathlib import Path

from core.domain import Receipt


class XLSXPort(ABC):
    """Port for Excel file operations."""

    @abstractmethod
    def append_receipts(self, receipts: list[Receipt], xlsx_path: Path) -> None:
        """Append receipts to Excel file.
        
        Args:
            receipts: List of receipts to append.
            xlsx_path: Path to Excel file.
        """
        pass

    @abstractmethod
    def read_existing_data(self, xlsx_path: Path) -> list[Receipt]:
        """Read existing receipt data from Excel file.
        
        Args:
            xlsx_path: Path to Excel file.
            
        Returns:
            List of existing receipts.
        """
        pass