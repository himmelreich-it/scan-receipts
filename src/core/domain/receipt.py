"""Receipt domain entities and constants."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Final, List, Set


RECEIPT_EXTENSIONS: Final[Set[str]] = {".pdf", ".jpg", ".png", ".jpeg"}


@dataclass(frozen=True)
class ReceiptData:
    """Receipt data from CSV staging file."""

    amount: str
    tax: str
    tax_percentage: str
    description: str
    currency: str
    date: str
    confidence: str
    hash: str
    done_filename: str


@dataclass(frozen=True)
class StagingTableData:
    """Complete staging table data."""

    file_path: Path
    headers: List[str]
    receipts: List[ReceiptData]

    @property
    def exists(self) -> bool:
        """Check if staging file exists."""
        return self.file_path.exists()

    @property
    def is_empty(self) -> bool:
        """Check if staging table is empty."""
        return len(self.receipts) == 0


@dataclass(frozen=True)
class StagingInfo:
    """Information about the staging CSV file."""

    file_path: Path
    modified_time: datetime
    entry_count: int

    def __str__(self) -> str:
        """Format staging info for display."""
        time_str = self.modified_time.strftime("%Y-%m-%d %H:%M")
        return (
            f"{self.file_path.name} (modified: {time_str}, {self.entry_count} entries)"
        )
