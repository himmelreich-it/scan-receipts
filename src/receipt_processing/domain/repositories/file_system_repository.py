"""File system repository interface."""

from abc import ABC, abstractmethod
from typing import List

from receipt_processing.domain.models.file_path import FilePath


class FileSystemRepository(ABC):
    """Abstract repository for file system operations."""
    
    @abstractmethod
    def list_files_in_directory(self, directory_path: str) -> List[FilePath]:
        """List all files in the given directory."""
        pass
    
    @abstractmethod
    def ensure_directory_exists(self, directory_path: str) -> None:
        """Ensure the given directory exists, creating it if necessary."""
        pass
    
    @abstractmethod
    def directory_exists(self, directory_path: str) -> bool:
        """Check if the given directory exists."""
        pass