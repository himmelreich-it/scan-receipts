"""File system port definition."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

# Receipt import not needed for interface


class FileSystemPort(ABC):
    """Port for file system operations."""

    @abstractmethod
    def get_receipt_files(self, folder: Path) -> List[Path]:
        """Get all receipt files from a folder.
        
        Args:
            folder: Folder to scan for receipt files.
            
        Returns:
            List of receipt file paths.
        """
        pass

    @abstractmethod
    def move_file(self, source: Path, destination: Path) -> None:
        """Move a file from source to destination.
        
        Args:
            source: Source file path.
            destination: Destination file path.
        """
        pass

    @abstractmethod
    def create_folders(self, folders: List[Path]) -> None:
        """Create folders if they don't exist.
        
        Args:
            folders: List of folder paths to create.
        """
        pass

    @abstractmethod
    def count_receipt_files(self, folder: Path) -> int:
        """Count receipt files in a folder.
        
        Args:
            folder: Folder to count files in.
            
        Returns:
            Number of receipt files.
        """
        pass