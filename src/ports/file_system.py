"""File system operations port."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from core.domain.configuration import AppConfig
from core.domain.receipt import StagingInfo


class FileSystemPort(ABC):
    """Interface for file system operations."""
    
    @abstractmethod
    def create_folders(self, config: AppConfig) -> None:
        """Create all required folders if they don't exist.
        
        Args:
            config: AppConfig instance with folder paths.
            
        Raises:
            OSError: If folder creation fails.
        """
        pass
    
    @abstractmethod
    def count_receipt_files(self, folder: Path) -> int:
        """Count receipt files in a folder (non-recursive).
        
        Args:
            folder: Path to the folder to count files in.
            
        Returns:
            Number of receipt files found.
        """
        pass
    
    @abstractmethod
    def get_staging_info(self, csv_path: Path) -> Optional[StagingInfo]:
        """Get information about the staging CSV file.
        
        Args:
            csv_path: Path to the CSV staging file.
            
        Returns:
            StagingInfo if file exists, None otherwise.
        """
        pass