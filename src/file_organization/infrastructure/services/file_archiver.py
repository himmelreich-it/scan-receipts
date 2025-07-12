"""File archiving service for file organization operations."""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from file_organization.domain.exceptions import FileAccessError, FileCopyError
from file_organization.domain.models import ArchiveResult
from file_organization.infrastructure.config import (
    DEFAULT_DONE_FOLDER,
    ARCHIVE_TIMESTAMP_FORMAT,
)


class FileArchiver:
    """Handles file archiving operations with timestamp naming.

    This service manages the copying of processed files to the done/ folder
    with proper timestamp naming convention. It implements atomic operations
    and comprehensive error handling as required by the user stories.
    """

    def __init__(self, done_folder: Optional[Path] = None) -> None:
        """Initialize file archiver.

        Args:
            done_folder: Path to done folder. If None, uses default.
        """
        self.done_folder = done_folder or DEFAULT_DONE_FOLDER

    def archive_file(self, source_path: Path, file_id: int) -> ArchiveResult:
        """Copies file to done folder with timestamp naming.

        This method implements the complete file archiving workflow including
        source validation, filename generation, atomic copy operation, and
        result object creation.

        Args:
            source_path: Path to source file to archive
            file_id: Unique ID for filename generation

        Returns:
            ArchiveResult with archiving details for CSV recording

        Raises:
            FileAccessError: If source file is not readable
            FileCopyError: If copy operation fails
        """
        # Validate source file before attempting copy
        self._validate_source_file(source_path)

        # Generate timestamp and archive filename
        archive_timestamp = datetime.now()
        archive_filename = self._generate_archive_filename(
            source_path.name, file_id, archive_timestamp
        )

        # Construct target path
        target_path = self.done_folder / archive_filename

        # Perform atomic copy operation
        self._perform_copy_operation(source_path, target_path)

        # Return result object
        return ArchiveResult(
            source_filename=source_path.name,
            archived_filename=archive_filename,
            archive_timestamp=archive_timestamp,
            file_id=file_id,
        )

    def _generate_archive_filename(
        self, original_filename: str, file_id: int, timestamp: datetime
    ) -> str:
        """Generates archive filename with format: {ID}-{timestamp}-{original}.

        Args:
            original_filename: Original filename from source
            file_id: Unique ID for the file
            timestamp: Timestamp for the archive operation

        Returns:
            Generated archive filename

        Example:
            >>> archiver = FileArchiver()
            >>> timestamp = datetime(2024, 3, 15, 14, 30, 52, 123456)
            >>> archiver._generate_archive_filename("receipt.jpg", 1, timestamp)
            "1-20240315-143052123456-receipt.jpg"
        """
        timestamp_str = timestamp.strftime(ARCHIVE_TIMESTAMP_FORMAT)
        return f"{file_id}-{timestamp_str}-{original_filename}"

    def _validate_source_file(self, source_path: Path) -> None:
        """Validates source file exists and is readable.

        Args:
            source_path: Path to source file to validate

        Raises:
            FileAccessError: If source file cannot be accessed
        """
        if not source_path.exists():
            raise FileAccessError(
                str(source_path), "read source", "File does not exist"
            )

        if not source_path.is_file():
            raise FileAccessError(str(source_path), "read source", "Path is not a file")

        try:
            # Test file readability
            with source_path.open("rb") as f:
                f.read(1)
        except PermissionError:
            raise FileAccessError(str(source_path), "read source", "Permission denied")
        except OSError as e:
            raise FileAccessError(str(source_path), "read source", str(e))

    def _perform_copy_operation(self, source_path: Path, target_path: Path) -> None:
        """Performs atomic copy operation with error handling.

        This method uses shutil.copy2() to preserve file metadata and implements
        comprehensive error handling for various copy failure scenarios.

        Args:
            source_path: Path to source file
            target_path: Path to target location

        Raises:
            FileCopyError: If copy operation fails for any reason
        """
        try:
            # Use copy2 to preserve metadata (timestamps, permissions)
            shutil.copy2(source_path, target_path)

            # Verify the copy was successful
            if not target_path.exists():
                raise FileCopyError(
                    str(source_path),
                    str(target_path),
                    "Copy operation completed but target file does not exist",
                )

        except PermissionError:
            raise FileCopyError(str(source_path), str(target_path), "Permission denied")
        except OSError as e:
            # Handle various OS-level errors
            error_msg = str(e).lower()
            if "no space left on device" in error_msg:
                raise FileCopyError(
                    str(source_path), str(target_path), "Insufficient disk space"
                )
            elif "permission denied" in error_msg:
                raise FileCopyError(
                    str(source_path), str(target_path), "Permission denied"
                )
            else:
                raise FileCopyError(str(source_path), str(target_path), str(e))
        except Exception as e:
            # Catch any other unexpected errors
            raise FileCopyError(
                str(source_path), str(target_path), f"Unexpected error: {str(e)}"
            )
