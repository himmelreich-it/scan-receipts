"""File system operations port."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from core.domain.configuration import AppConfig
from core.domain.receipt import FileHash, StagingInfo


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

    @abstractmethod
    def get_supported_files(self, folder: Path) -> List[Path]:
        """Get list of supported receipt files from a folder.

        Args:
            folder: Path to the folder to scan.

        Returns:
            List of paths to supported files (PDF, JPG, PNG).
        """
        pass

    @abstractmethod
    def remove_file_if_exists(self, file_path: Path) -> bool:
        """Remove a file if it exists.

        Args:
            file_path: Path to the file to remove.

        Returns:
            True if file was removed, False if it didn't exist.
        """
        pass

    @abstractmethod
    def clear_folder(self, folder: Path) -> None:
        """Clear all files from a folder.

        Args:
            folder: Path to the folder to clear.
        """
        pass

    @abstractmethod
    def calculate_file_hash(self, file_path: Path) -> Optional[FileHash]:
        """Calculate hash for a file.

        Args:
            file_path: Path to the file to hash.

        Returns:
            FileHash if successful, None if calculation failed.
        """
        pass

    @abstractmethod
    def get_file_hashes_from_folder(self, folder: Path) -> List[FileHash]:
        """Get hashes for all supported files in a folder.

        Args:
            folder: Path to the folder to scan.

        Returns:
            List of FileHash objects for files that could be hashed.
        """
        pass

    @abstractmethod
    def copy_file_to_folder(self, source_file: Path, destination_folder: Path) -> Path:
        """Copy a file to a destination folder.

        Args:
            source_file: Path to the source file.
            destination_folder: Path to the destination folder.

        Returns:
            Path to the copied file.

        Raises:
            OSError: If copy operation fails.
        """
        pass

    @abstractmethod
    def write_error_log(self, failed_folder: Path, filename: str, error_message: str) -> None:
        """Write error log for failed file processing.

        Args:
            failed_folder: Path to the failed folder.
            filename: Name of the failed file.
            error_message: Error message to log.
        """
        pass
