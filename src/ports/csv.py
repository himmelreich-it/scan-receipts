"""CSV operations port."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.domain.receipt import StagingTableData


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
    def read_staging_table(self, csv_path: Path) -> Optional[StagingTableData]:
        """Read complete staging table data from CSV.

        Args:
            csv_path: Path to CSV file.

        Returns:
            StagingTableData if file exists, None otherwise.
        """
        pass

    @abstractmethod
    def append_receipt_data(
        self, csv_path: Path, receipt_data: Dict[str, str], file_hash: str, filename: str
    ) -> None:
        """Append receipt data to CSV file.

        Args:
            csv_path: Path to CSV file.
            receipt_data: Extracted receipt data containing amount, tax, etc.
            file_hash: Hash of the processed file.
            filename: Name of the processed file.
        """
        pass
