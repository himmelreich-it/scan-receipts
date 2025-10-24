"""XLSX operations port."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List


class XLSXPort(ABC):
    """Interface for Excel operations."""

    @abstractmethod
    def get_last_sequential_number(self, xlsx_path: Path) -> int:
        """Get the last sequential number from XLSX file.

        Reads from column A starting at row 11 to find the highest number.
        Returns 0 if file is empty or doesn't exist.

        Args:
            xlsx_path: Path to XLSX file.

        Returns:
            Last sequential number, or 0 if none found.
        """
        pass

    @abstractmethod
    def append_entries(
        self, xlsx_path: Path, entries: List[Dict[str, str]]
    ) -> List[int]:
        """Append receipt entries to XLSX file.

        Appends entries starting from first empty row (found by checking Column B).
        Reads sequential numbers from Column A (already filled in spreadsheet).
        Writes to: B=Date, F=Description, J=Amount, K=VAT, S=Notes (NOT Column A).

        Args:
            xlsx_path: Path to XLSX file.
            entries: List of receipt entries with keys: date, description, amount, tax, currency

        Returns:
            List of sequential numbers used for each entry (read from Column A).

        Raises:
            OSError: If file operations fail.
            ValueError: If no sequential number found in Column A.
        """
        pass

    @abstractmethod
    def xlsx_file_exists(self, xlsx_path: Path) -> bool:
        """Check if XLSX file exists.

        Args:
            xlsx_path: Path to XLSX file.

        Returns:
            True if file exists, False otherwise.
        """
        pass
