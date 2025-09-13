"""CSV operations port."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, List

from core.domain.receipt import ReceiptData


class CSVPort(ABC):
    """Interface for CSV operations."""

    @abstractmethod
    def read_staging_data(self, csv_path: str) -> List[Any]:
        """Read staging data from CSV.

        Args:
            csv_path: Path to CSV file.

        Returns:
            List of staging data records.
        """
        pass

    @abstractmethod
    def write_staging_data(self, csv_path: str, data: List[Any]) -> None:
        """Write staging data to CSV.

        Args:
            csv_path: Path to CSV file.
            data: Data to write.
        """
        pass

    @abstractmethod
    def append_receipt(self, csv_path: Path, receipt_data: ReceiptData) -> None:
        """Append receipt data to CSV file.

        Args:
            csv_path: Path to CSV file.
            receipt_data: Receipt data to append.
        """
        pass
