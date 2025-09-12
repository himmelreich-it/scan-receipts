"""CSV port definition."""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Optional

from core.domain import Receipt


class StagingInfo:
    """Information about staging CSV file."""
    
    def __init__(self, file_path: Path, modified_time: datetime, entry_count: int):
        self.file_path = file_path
        self.modified_time = modified_time
        self.entry_count = entry_count
    
    def __str__(self) -> str:
        """Format staging info for display."""
        time_str = self.modified_time.strftime("%Y-%m-%d %H:%M")
        return f"{self.file_path.name} (modified: {time_str}, {self.entry_count} entries)"


class CSVPort(ABC):
    """Port for CSV file operations."""

    @abstractmethod
    def get_staging_info(self, csv_path: Path) -> Optional[StagingInfo]:
        """Get information about staging CSV file.
        
        Args:
            csv_path: Path to CSV file.
            
        Returns:
            StagingInfo if file exists, None otherwise.
        """
        pass

    @abstractmethod
    def save_receipt_data(self, receipts: list[Receipt], csv_path: Path) -> None:
        """Save receipt data to CSV file.
        
        Args:
            receipts: List of receipts to save.
            csv_path: Path to CSV file.
        """
        pass