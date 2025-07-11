"""FilePath value object for receipt processing."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class FilePath:
    """Value object representing a file path."""
    
    path: str
    
    def __post_init__(self) -> None:
        if not self.path:
            raise ValueError("File path cannot be empty")
        if not isinstance(self.path, str):
            raise TypeError("File path must be a string")
    
    @property
    def name(self) -> str:
        """Get the filename from the path."""
        return os.path.basename(self.path)
    
    @property
    def directory(self) -> str:
        """Get the directory from the path."""
        return os.path.dirname(self.path)
    
    def exists(self) -> bool:
        """Check if the file exists."""
        return os.path.exists(self.path)