"""Interface definitions for external dependencies."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Set


class AIExtractionPort(ABC):
    """Port for AI-powered data extraction services."""

    @abstractmethod
    async def extract_receipt_data(self, file_path: str) -> Dict[str, Any]:
        """Extract structured data from receipt file.

        Args:
            file_path: Path to receipt file

        Returns:
            Dictionary containing extracted data fields

        Raises:
            Exception: When extraction fails
        """
        pass


class FileSystemPort(ABC):
    """Port for file system operations."""

    @abstractmethod
    def validate_file_format(self, file_path: str) -> bool:
        """Validate if file format is supported.

        Args:
            file_path: Path to file to validate

        Returns:
            True if format is supported, False otherwise
        """
        pass

    @abstractmethod
    def read_file_content(self, file_path: str) -> bytes:
        """Read file content as bytes.

        Args:
            file_path: Path to file to read

        Returns:
            File content as bytes

        Raises:
            FileNotFoundError: When file doesn't exist
            PermissionError: When file cannot be read
        """
        pass


class DuplicateDetectionPort(ABC):
    """Port for duplicate detection services."""

    @abstractmethod
    def generate_file_hash(self, file_path: str) -> str:
        """Generate hash for file duplicate detection.

        Args:
            file_path: Path to file

        Returns:
            Hash string for the file
        """
        pass

    @abstractmethod
    def is_duplicate(self, file_hash: str, known_hashes: Set[str]) -> bool:
        """Check if file hash is a duplicate.

        Args:
            file_hash: Hash to check
            known_hashes: Set of known hashes

        Returns:
            True if duplicate, False otherwise
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
