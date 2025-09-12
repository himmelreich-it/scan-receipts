"""Receipt domain entities and constants."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Final, Set


RECEIPT_EXTENSIONS: Final[Set[str]] = {".pdf", ".jpg", ".png", ".jpeg"}


@dataclass(frozen=True)
class StagingInfo:
    """Information about the staging CSV file."""
    
    file_path: Path
    modified_time: datetime
    entry_count: int
    
    def __str__(self) -> str:
        """Format staging info for display."""
        time_str = self.modified_time.strftime("%Y-%m-%d %H:%M")
        return f"{self.file_path.name} (modified: {time_str}, {self.entry_count} entries)"