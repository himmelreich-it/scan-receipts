"""Duplicate detection operations port."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from core.domain.receipt import DuplicateDetectionResult, FileHash


class DuplicateDetectionPort(ABC):
    """Interface for duplicate detection operations."""

    @abstractmethod
    def check_duplicate(
        self, file_path: Path, existing_hashes: List[FileHash]
    ) -> DuplicateDetectionResult:
        """Check if a file is a duplicate of existing files.

        Args:
            file_path: Path to the file to check.
            existing_hashes: List of existing file hashes to compare against.

        Returns:
            DuplicateDetectionResult with detection status and details.
        """
        pass