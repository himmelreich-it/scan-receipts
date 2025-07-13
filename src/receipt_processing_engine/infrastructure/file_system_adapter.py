"""File operations and format validation."""

import logging
import mimetypes
from pathlib import Path
from ..application.ports import FileSystemPort


logger = logging.getLogger(__name__)


class FileSystemAdapter(FileSystemPort):
    """Adapter for file system operations."""

    SUPPORTED_FORMATS = {".pdf", ".jpg", ".jpeg", ".png"}

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
        """Read file content as bytes.

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

            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            if not path.is_file():
                raise ValueError(f"Path is not a file: {file_path}")

            # Check file size to prevent memory issues
            file_size_mb = path.stat().st_size / (1024 * 1024)
            if file_size_mb > 10:  # 10MB limit
                raise ValueError(f"File too large: {file_size_mb:.1f}MB > 10MB limit")

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
