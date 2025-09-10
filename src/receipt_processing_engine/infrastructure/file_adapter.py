"""File system operations and folder management adapter."""

import logging
from typing import List
from pathlib import Path
from ..application.ports import FileSystemPort
from file_management.adapters import FileSystemAdapter as FileManagerAdapter
from file_management.models import FileMovementRequest


logger = logging.getLogger(__name__)


class FileSystemAdapter(FileSystemPort):
    """Adapter for file system operations."""

    def __init__(self, imported_folder: Path, failed_folder: Path):
        """Initialize with folder paths."""
        self.imported_folder = Path(imported_folder)
        self.failed_folder = Path(failed_folder)
        self.supported_formats = {".pdf", ".jpg", ".jpeg", ".png"}
        self.file_manager = FileManagerAdapter()

    def ensure_folders_exist(self, folders: List[Path]) -> None:
        """Create folder structure if it doesn't exist."""
        for folder in folders:
            folder_result = self.file_manager.ensure_folder_exists(folder)
            if folder_result.success:
                logger.debug(f"Ensured folder exists: {folder}")
            else:
                logger.error(f"Failed to create folder {folder}: {folder_result.error_message}")
                raise Exception(f"Failed to create folder {folder}: {folder_result.error_message}")

    def move_file_to_failed(self, file_path: Path, error_message: str) -> None:
        """Move file to failed folder with error log.

        Process:
        1. Copy file to failed folder using file management service
        2. Create text error log with same name + .error extension
        3. Log error details to console
        """
        try:
            # Ensure failed folder exists
            self.ensure_folders_exist([self.failed_folder])

            # Create movement request
            movement_request = FileMovementRequest(
                source_path=file_path,
                target_folder=self.failed_folder,
                description="failed",  # Not used for this operation
                date="",  # Not used for this operation
                sequence_number=None  # Not used for this operation
            )

            # Copy file to failed folder using file management service
            result = self.file_manager.copy_to_failed(movement_request)
            
            if result.success and result.target_path:
                # Create error log
                self._create_error_log(result.target_path, error_message)
                
                logger.info(f"Moved file to failed folder: {file_path} -> {result.target_path}")
                logger.error(f"File processing failed: {file_path} - {error_message}")
            else:
                logger.error(f"Failed to move file to failed folder: {result.error_message}")
                raise Exception(f"Failed to move file: {result.error_message}")

        except Exception as e:
            logger.error(f"Failed to move file to failed folder: {file_path} - {e}")
            raise

    def get_input_files(self, input_folder: Path) -> List[Path]:
        """Get list of receipt files from input folder.

        Filters for supported formats: PDF, JPG, PNG using file management service
        """
        try:
            # Use file management service to list all files
            all_files = self.file_manager.list_files(input_folder)
            
            if not all_files:
                logger.warning(f"Input folder is empty or does not exist: {input_folder}")
                return []

            # Filter for supported formats
            files: List[Path] = []
            for file_path in all_files:
                if file_path.suffix.lower() in self.supported_formats:
                    files.append(file_path)

            logger.info(f"Found {len(files)} receipt files in {input_folder}")
            return sorted(files)  # Sort for consistent processing order

        except Exception as e:
            logger.error(f"Failed to get input files from {input_folder}: {e}")
            raise

    def _create_error_log(self, failed_file_path: Path, error_message: str) -> None:
        """Create simple text error log file."""
        try:
            from datetime import datetime
            
            error_log_path = failed_file_path.with_suffix(
                failed_file_path.suffix + ".error"
            )

            with open(error_log_path, "w") as f:
                f.write(f"Error processing file: {failed_file_path.name}\n")
                f.write(f"Error message: {error_message}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")

            logger.debug(f"Created error log: {error_log_path}")

        except Exception as e:
            logger.error(f"Failed to create error log for {failed_file_path}: {e}")
            # Don't raise here - we don't want to fail the whole process if we can't create the log
