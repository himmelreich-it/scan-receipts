"""Receipt domain entities and constants."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Final, List, Optional, Set


RECEIPT_EXTENSIONS: Final[Set[str]] = {".pdf", ".jpg", ".png", ".jpeg"}


@dataclass(frozen=True)
class FileHash:
    """Represents a file hash for duplicate detection."""

    file_path: Path
    hash_value: str

    def __post_init__(self) -> None:
        """Validate hash value is not empty."""
        if not self.hash_value.strip():
            raise ValueError("Hash value cannot be empty")


@dataclass(frozen=True)
class DuplicateDetectionResult:
    """Result of duplicate detection for a file."""

    file_path: Path
    is_duplicate: bool
    duplicate_location: Optional[Path] = None
    hash_value: Optional[str] = None
    error_message: Optional[str] = None

    @property
    def has_error(self) -> bool:
        """Check if detection encountered an error."""
        return self.error_message is not None

    @property
    def location_name(self) -> str:
        """Get human-readable location name for duplicate."""
        if not self.duplicate_location:
            return "unknown"
        return self.duplicate_location.parent.name


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
