"""Domain-specific exceptions for file organization operations."""

from typing import Optional


class FileOrganizationError(Exception):
    """Base exception for file organization operations.

    This exception is the base class for all file organization related errors.
    It provides context about the operation that failed and detailed error messages.
    """

    def __init__(self, message: str, operation: Optional[str] = None) -> None:
        """Initialize file organization error.

        Args:
            message: Detailed error message describing what went wrong
            operation: Optional operation name that failed
        """
        super().__init__(message)
        self.message = message
        self.operation = operation

    def __str__(self) -> str:
        """Return formatted error message."""
        if self.operation:
            return f"{self.operation}: {self.message}"
        return self.message


class FolderCreationError(FileOrganizationError):
    """Raised when folder creation fails.

    This exception indicates that the system could not create a required folder
    due to permissions, disk space, or other file system issues.
    """

    def __init__(self, folder_path: str, reason: str) -> None:
        """Initialize folder creation error.

        Args:
            folder_path: Path to the folder that could not be created
            reason: Specific reason for the failure
        """
        message = f"Cannot create {folder_path} folder: {reason}"
        super().__init__(message, "Folder Creation")
        self.folder_path = folder_path
        self.reason = reason


class FileCopyError(FileOrganizationError):
    """Raised when file copy operation fails.

    This exception indicates that a file could not be copied from source to
    destination due to permissions, disk space, or other file system issues.
    """

    def __init__(self, source_path: str, target_path: str, reason: str) -> None:
        """Initialize file copy error.

        Args:
            source_path: Path to the source file
            target_path: Path to the target location
            reason: Specific reason for the failure
        """
        message = f"Cannot copy file {source_path}: {reason}"
        super().__init__(message, "File Copy")
        self.source_path = source_path
        self.target_path = target_path
        self.reason = reason


class FileAccessError(FileOrganizationError):
    """Raised when file access validation fails.

    This exception indicates that a file could not be accessed for reading
    or that required permissions are not available.
    """

    def __init__(self, file_path: str, operation: str, reason: str) -> None:
        """Initialize file access error.

        Args:
            file_path: Path to the file that could not be accessed
            operation: Operation that was attempted
            reason: Specific reason for the failure
        """
        message = f"Cannot {operation} file {file_path}: {reason}"
        super().__init__(message, "File Access")
        self.file_path = file_path
        self.access_operation = operation
        self.reason = reason
