"""FileContent value object for receipt processing."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FileContent:
    """Value object representing file content for Claude API."""
    
    data: str  # base64 encoded content
    mime_type: str
    size_bytes: int
    
    def __post_init__(self) -> None:
        if not self.data:
            raise ValueError("File content cannot be empty")
        if self.size_bytes < 0:
            raise ValueError("File size cannot be negative")