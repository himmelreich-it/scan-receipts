"""Domain models and result objects for file operations."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from enum import Enum


class FileErrorCode(Enum):
    """Error codes for file system operations."""
    # Folder errors
    FOLDER_PERMISSION_DENIED = "FOLDER_PERMISSION_DENIED"
    FOLDER_NOT_WRITABLE = "FOLDER_NOT_WRITABLE"
    FOLDER_CREATION_FAILED = "FOLDER_CREATION_FAILED"
    
    # File errors
    FILE_LOCKED = "FILE_LOCKED"
    FILE_EXISTS = "FILE_EXISTS"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_UNREADABLE = "FILE_UNREADABLE"
    FILE_CORRUPTED = "FILE_CORRUPTED"
    FILE_PERMISSION_DENIED = "FILE_PERMISSION_DENIED"
    
    # System errors
    DISK_SPACE_FULL = "DISK_SPACE_FULL"
    DISK_IO_ERROR = "DISK_IO_ERROR"
    INVALID_PATH = "INVALID_PATH"
    MEMORY_INSUFFICIENT = "MEMORY_INSUFFICIENT"


@dataclass(frozen=True)
class FileOperationResult:
    """Result of a file system operation."""
    success: bool
    error_code: Optional[FileErrorCode] = None
    error_message: Optional[str] = None
    file_path: Optional[Path] = None


@dataclass(frozen=True)
class HashResult:
    """Result of file hash generation."""
    success: bool
    hash_value: Optional[str] = None
    error_code: Optional[FileErrorCode] = None
    error_message: Optional[str] = None
    file_path: Optional[Path] = None


@dataclass(frozen=True)
class FolderValidationResult:
    """Result of folder validation and creation."""
    success: bool
    folder_path: Path
    exists: bool = False
    is_writable: bool = False
    error_code: Optional[FileErrorCode] = None
    error_message: Optional[str] = None