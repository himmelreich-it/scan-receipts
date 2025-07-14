"""File system operations and folder management adapter."""

import logging
import shutil
from typing import List
from pathlib import Path
from ..application.ports import FileSystemPort


logger = logging.getLogger(__name__)


class FileSystemAdapter(FileSystemPort):
    """Adapter for file system operations."""

    def __init__(self, done_folder: Path, failed_folder: Path):
        """Initialize with folder paths."""
        self.done_folder = Path(done_folder)
        self.failed_folder = Path(failed_folder)
        self.supported_formats = {".pdf", ".jpg", ".jpeg", ".png"}

    def ensure_folders_exist(self, folders: List[Path]) -> None:
        """Create folder structure if it doesn't exist."""
        for folder in folders:
            try:
                folder.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Ensured folder exists: {folder}")
            except Exception as e:
                logger.error(f"Failed to create folder {folder}: {e}")
                raise

    def move_file_to_failed(self, file_path: Path, error_message: str) -> None:
        """Move file to failed folder with error log.

        Process:
        1. Copy file to failed folder
        2. Create text error log with same name + .error extension
        3. Log error details to console
        """
        try:
            # Ensure failed folder exists
            self.ensure_folders_exist([self.failed_folder])

            # Copy file to failed folder
            failed_file_path = self.failed_folder / file_path.name
            shutil.copy2(file_path, failed_file_path)

            # Create error log
            self._create_error_log(failed_file_path, error_message)

            logger.info(
                f"Moved file to failed folder: {file_path} -> {failed_file_path}"
            )
            logger.error(f"File processing failed: {file_path} - {error_message}")

        except Exception as e:
            logger.error(f"Failed to move file to failed folder: {file_path} - {e}")
            raise

    def get_input_files(self, input_folder: Path) -> List[Path]:
        """Get list of receipt files from input folder.

        Filters for supported formats: PDF, JPG, PNG
        """
        try:
            if not input_folder.exists():
                logger.warning(f"Input folder does not exist: {input_folder}")
                return []

            files = []
            for file_path in input_folder.iterdir():
                if (
                    file_path.is_file()
                    and file_path.suffix.lower() in self.supported_formats
                ):
                    files.append(file_path)

            logger.info(f"Found {len(files)} receipt files in {input_folder}")
            return sorted(files)  # Sort for consistent processing order

        except Exception as e:
            logger.error(f"Failed to get input files from {input_folder}: {e}")
            raise

    def _create_error_log(self, failed_file_path: Path, error_message: str) -> None:
        """Create simple text error log file."""
        try:
            error_log_path = failed_file_path.with_suffix(
                failed_file_path.suffix + ".error"
            )

            with open(error_log_path, "w") as f:
                f.write(f"Error processing file: {failed_file_path.name}\n")
                f.write(f"Error message: {error_message}\n")
                f.write(
                    f"Timestamp: {logger.handlers[0].format(logger.makeRecord(logger.name, logging.ERROR, __file__, 0, error_message, (), None)).split(']')[0][1:]}\n"
                )

            logger.debug(f"Created error log: {error_log_path}")

        except Exception as e:
            logger.error(f"Failed to create error log for {failed_file_path}: {e}")
            # Don't raise here - we don't want to fail the whole process if we can't create the log
