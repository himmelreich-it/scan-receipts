"""Duplicate detection adapter implementation."""

import logging
from pathlib import Path
from typing import List

from core.domain.receipt import DuplicateDetectionResult, FileHash
from ports.duplicate_detection import DuplicateDetectionPort
from ports.file_system import FileSystemPort

logger = logging.getLogger(__name__)


class DuplicateDetectionAdapter(DuplicateDetectionPort):
    """Implementation of duplicate detection operations."""

    def __init__(self, file_system: FileSystemPort):
        self.file_system = file_system

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
        try:
            # Calculate hash for the incoming file
            file_hash = self.file_system.calculate_file_hash(file_path)
            if not file_hash:
                return DuplicateDetectionResult(
                    file_path=file_path,
                    is_duplicate=False,
                    error_message="Failed to calculate file hash",
                )

            # Check against existing hashes
            for existing_hash in existing_hashes:
                if file_hash.hash_value == existing_hash.hash_value:
                    logger.info(
                        f"Duplicate detected: {file_path.name} matches {existing_hash.file_path}"
                    )
                    return DuplicateDetectionResult(
                        file_path=file_path,
                        is_duplicate=True,
                        duplicate_location=existing_hash.file_path,
                        hash_value=file_hash.hash_value,
                    )

            # No duplicate found
            return DuplicateDetectionResult(
                file_path=file_path,
                is_duplicate=False,
                hash_value=file_hash.hash_value,
            )

        except Exception as e:
            logger.error(f"Error during duplicate detection for {file_path}: {e}")
            return DuplicateDetectionResult(
                file_path=file_path,
                is_duplicate=False,
                error_message=f"Duplicate detection failed: {str(e)}",
            )
