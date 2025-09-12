"""Receipt domain entity."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class Receipt:
    """Receipt entity representing a processed receipt document."""
    
    file_path: Path
    total: Optional[float] = None
    vendor: Optional[str] = None
    date: Optional[datetime] = None
    confidence: Optional[float] = None
    
    @property
    def filename(self) -> str:
        """Get the filename of the receipt."""
        return self.file_path.name
    
    @property
    def is_valid(self) -> bool:
        """Check if receipt has minimum required data."""
        return self.total is not None and self.vendor is not None