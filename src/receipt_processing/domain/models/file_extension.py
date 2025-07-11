"""FileExtension value object for receipt processing."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FileExtension:
    """Value object representing a file extension."""
    
    extension: str
    
    def __post_init__(self) -> None:
        if not self.extension:
            raise ValueError("File extension cannot be empty")
        # Normalize to lowercase with leading dot
        normalized = self.extension.lower()
        if not normalized.startswith('.'):
            normalized = f'.{normalized}'
        object.__setattr__(self, 'extension', normalized)
    
    def matches(self, other: 'FileExtension') -> bool:
        """Check if this extension matches another."""
        return self.extension == other.extension