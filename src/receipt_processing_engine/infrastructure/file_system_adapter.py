"""File operations and format validation."""

import logging
import mimetypes
from typing import List
from pathlib import Path
from ..application.ports import FileSystemPort
from file_management.adapters import FileSystemAdapter as FileManagerAdapter


logger = logging.getLogger(__name__)


class FileSystemAdapter(FileSystemPort):
    """Adapter for file system operations."""

    SUPPORTED_FORMATS = {".pdf", ".jpg", ".jpeg", ".png"}

    def __init__(self):
        """Initialize with file management service."""
        self.file_manager = FileManagerAdapter()

    def validate_file_format(self, file_path: str) -> bool:
        """Validate if file format is supported.

        Args:
            file_path: Path to file to validate

        Returns:
            True if format is supported, False otherwise
        """
        try:
            path = Path(file_path)
            extension = path.suffix.lower()

            if extension in self.SUPPORTED_FORMATS:
                return True

            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type:
                if mime_type.startswith("image/") and extension in {
                    ".jpg",
                    ".jpeg",
                    ".png",
                }:
                    return True
                if mime_type == "application/pdf":
                    return True

            logger.warning(
                f"Unsupported file format: {file_path} (extension: {extension})"
            )
            return False

        except Exception as e:
            logger.error(f"Error validating file format for {file_path}: {e}")
            return False

    def read_file_content(self, file_path: str) -> bytes:
        """Read file content as bytes using file management service.

        Args:
            file_path: Path to file to read

        Returns:
            File content as bytes

        Raises:
            FileNotFoundError: When file doesn't exist
            PermissionError: When file cannot be read
        """
        try:
            path = Path(file_path)

            # Check file size to prevent memory issues using direct stat (this is validation logic, not file ops)
            try:
                file_size_mb = path.stat().st_size / (1024 * 1024)
                if file_size_mb > 10:  # 10MB limit
                    raise ValueError(f"File too large: {file_size_mb:.1f}MB > 10MB limit")
            except (FileNotFoundError, OSError):
                # File doesn't exist or can't stat - let the file read operation handle the error
                pass

            with open(path, "rb") as file:
                content = file.read()

            logger.debug(f"Successfully read {len(content)} bytes from {file_path}")
            return content

        except (FileNotFoundError, PermissionError):
            raise
        except Exception as e:
            self._handle_file_access_error(e)
            raise

    def _detect_file_type(self, file_path: str) -> str:
        """Detect file type using multiple methods.

        Args:
            file_path: Path to file

        Returns:
            Detected file type
        """
        path = Path(file_path)
        extension = path.suffix.lower()

        mime_type, _ = mimetypes.guess_type(file_path)

        return f"extension: {extension}, mime: {mime_type}"

    def _handle_file_access_error(self, error: Exception) -> None:
        """Handle file access errors with appropriate logging.

        Args:
            error: Exception that occurred
        """
        logger.error(f"File access error: {type(error).__name__}: {error}")

    def get_input_files(self, input_folder: Path) -> List[Path]:
        """Get list of supported files in input folder using file management service."""
        try:
            # Use file management service to list all files
            all_files = self.file_manager.list_files(input_folder)
            
            # Filter for supported formats
            files: List[Path] = []
            for file_path in all_files:
                if self.validate_file_format(str(file_path)):
                    files.append(file_path)
            return files
        except Exception as e:
            logger.error(f"Failed to get input files from {input_folder}: {e}")
            return []

    def ensure_folders_exist(self, folders: List[Path]) -> None:
        """Create folder structure if it doesn't exist using file management service."""
        for folder in folders:
            folder_result = self.file_manager.ensure_folder_exists(folder)
            if folder_result.success:
                logger.debug(f"Ensured folder exists: {folder}")
            else:
                logger.error(f"Failed to create folder {folder}: {folder_result.error_message}")
                raise Exception(f"Failed to create folder {folder}: {folder_result.error_message}")

    def move_file_to_failed(self, file_path: Path, error_message: str) -> None:
        """Move file to failed folder with error log (stub implementation)."""
        logger.info(f"Would move {file_path} to failed folder: {error_message}")
