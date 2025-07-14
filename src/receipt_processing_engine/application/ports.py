"""Interface definitions for external dependencies."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Set, List
from pathlib import Path


class AIExtractionPort(ABC):
    """Port for AI-powered data extraction services."""

    @abstractmethod
    async def extract_data(self, file_path: Path) -> Dict[str, Any]:
        """Extract structured data from receipt file.

        Args:
            file_path: Path to receipt file

        Returns:
            Dictionary containing extracted data fields

        Raises:
            Exception: When extraction fails
        """
        pass

    @abstractmethod
    def supports_file_format(self, file_path: Path) -> bool:
        """Check if file format is supported for extraction.

        Args:
            file_path: Path to file to check

        Returns:
            True if format is supported, False otherwise
        """
        pass


class FileSystemPort(ABC):
    """Port for file system operations."""

    @abstractmethod
    def ensure_folders_exist(self, folders: List[Path]) -> None:
        """Create folder structure if it doesn't exist.

        Args:
            folders: List of folder paths to create
        """
        pass

    @abstractmethod
    def move_file_to_failed(self, file_path: Path, error_message: str) -> None:
        """Move file to failed folder with error log.

        Args:
            file_path: Path to file to move
            error_message: Error message to log
        """
        pass

    @abstractmethod
    def get_input_files(self, input_folder: Path) -> List[Path]:
        """Get list of receipt files from input folder.

        Args:
            input_folder: Path to input folder

        Returns:
            List of file paths in input folder
        """
        pass


class DuplicateDetectionPort(ABC):
    """Port for duplicate detection services."""

    @abstractmethod
    def initialize_done_folder_hashes(self, done_folder: Path) -> None:
        """Scan done folder and build hash database.

        Args:
            done_folder: Path to done folder to scan
        """
        pass

    @abstractmethod
    def is_duplicate(self, file_hash: str) -> bool:
        """Check if file hash is a duplicate.

        Args:
            file_hash: Hash to check

        Returns:
            True if duplicate, False otherwise
        """
        pass

    @abstractmethod
    def add_to_session(self, file_hash: str, filename: str) -> None:
        """Add file hash to current session tracking.

        Args:
            file_hash: Hash to add
            filename: Original filename
        """
        pass

    @abstractmethod
    def generate_file_hash(self, file_path: Path) -> str:
        """Generate hash for file duplicate detection.

        Args:
            file_path: Path to file

        Returns:
            Hash string for the file
        """
        pass


class ReceiptRepositoryPort(ABC):
    """Port for receipt data persistence operations."""

    @abstractmethod
    def save_receipt(self, receipt) -> None:
        """Save receipt to repository.

        Args:
            receipt: Receipt entity to save
        """
        pass

    @abstractmethod
    def get_processed_hashes(self) -> Set[str]:
        """Get set of all processed file hashes.

        Returns:
            Set of file hashes that have been processed
        """
        pass
