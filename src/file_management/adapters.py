"""Concrete implementation of File System Port using pathlib and system APIs."""

import hashlib
import logging
import shutil
from pathlib import Path

from file_management.models import (
    FileErrorCode,
    FileOperationResult,
    FolderValidationResult,
    HashResult
)
from file_management.ports import FileSystemPort


logger = logging.getLogger(__name__)


class FileSystemAdapter(FileSystemPort):
    """Concrete implementation of file system operations using pathlib and system APIs."""
    
    def ensure_folder_exists(self, folder_path: Path) -> FolderValidationResult:
        """Create folder if missing, validate permissions."""
        try:
            # Check if folder exists
            if folder_path.exists():
                if not folder_path.is_dir():
                    return FolderValidationResult(
                        success=False,
                        folder_path=folder_path,
                        exists=True,
                        is_writable=False,
                        error_code=FileErrorCode.INVALID_PATH,
                        error_message=f"Path exists but is not a directory: {folder_path}"
                    )
                
                # Check if writable
                try:
                    # Test write permission by creating a temporary file
                    test_file = folder_path / ".tmp_write_test"
                    test_file.touch()
                    test_file.unlink()
                    is_writable = True
                except (PermissionError, OSError):
                    is_writable = False
                    return FolderValidationResult(
                        success=False,
                        folder_path=folder_path,
                        exists=True,
                        is_writable=False,
                        error_code=FileErrorCode.FOLDER_NOT_WRITABLE,
                        error_message=f"Folder is not writable: {folder_path}"
                    )
                
                return FolderValidationResult(
                    success=True,
                    folder_path=folder_path,
                    exists=True,
                    is_writable=is_writable
                )
            
            # Try to create the folder
            folder_path.mkdir(parents=True, exist_ok=True)
            
            # Verify creation and writability
            if not folder_path.exists():
                return FolderValidationResult(
                    success=False,
                    folder_path=folder_path,
                    exists=False,
                    is_writable=False,
                    error_code=FileErrorCode.FOLDER_CREATION_FAILED,
                    error_message=f"Failed to create folder: {folder_path}"
                )
            
            # Test write permission
            try:
                test_file = folder_path / ".tmp_write_test"
                test_file.touch()
                test_file.unlink()
                is_writable = True
            except (PermissionError, OSError):
                is_writable = False
                return FolderValidationResult(
                    success=False,
                    folder_path=folder_path,
                    exists=True,
                    is_writable=False,
                    error_code=FileErrorCode.FOLDER_NOT_WRITABLE,
                    error_message=f"Created folder is not writable: {folder_path}"
                )
            
            return FolderValidationResult(
                success=True,
                folder_path=folder_path,
                exists=True,
                is_writable=is_writable
            )
            
        except PermissionError as e:
            return FolderValidationResult(
                success=False,
                folder_path=folder_path,
                exists=False,
                is_writable=False,
                error_code=FileErrorCode.FOLDER_PERMISSION_DENIED,
                error_message=f"Permission denied creating folder {folder_path}: {e}"
            )
        except OSError as e:
            if e.errno == 28:  # No space left on device
                error_code = FileErrorCode.DISK_SPACE_FULL
                message = f"Insufficient disk space to create folder {folder_path}: {e}"
            else:
                error_code = FileErrorCode.FOLDER_CREATION_FAILED
                message = f"OS error creating folder {folder_path}: {e}"
                
            return FolderValidationResult(
                success=False,
                folder_path=folder_path,
                exists=False,
                is_writable=False,
                error_code=error_code,
                error_message=message
            )
        except Exception as e:
            return FolderValidationResult(
                success=False,
                folder_path=folder_path,
                exists=False,
                is_writable=False,
                error_code=FileErrorCode.FOLDER_CREATION_FAILED,
                error_message=f"Unexpected error creating folder {folder_path}: {e}"
            )
    
    def clear_folder(self, folder_path: Path) -> FileOperationResult:
        """Remove all contents from folder."""
        try:
            if not folder_path.exists():
                return FileOperationResult(
                    success=False,
                    error_code=FileErrorCode.FILE_NOT_FOUND,
                    error_message=f"Folder does not exist: {folder_path}",
                    file_path=folder_path
                )
            
            if not folder_path.is_dir():
                return FileOperationResult(
                    success=False,
                    error_code=FileErrorCode.INVALID_PATH,
                    error_message=f"Path is not a directory: {folder_path}",
                    file_path=folder_path
                )
            
            # Remove all contents
            for item in folder_path.iterdir():
                try:
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                except (PermissionError, OSError) as e:
                    return FileOperationResult(
                        success=False,
                        error_code=FileErrorCode.FILE_PERMISSION_DENIED,
                        error_message=f"Permission denied removing {item}: {e}",
                        file_path=item
                    )
            
            return FileOperationResult(success=True, file_path=folder_path)
            
        except PermissionError as e:
            return FileOperationResult(
                success=False,
                error_code=FileErrorCode.FILE_PERMISSION_DENIED,
                error_message=f"Permission denied clearing folder {folder_path}: {e}",
                file_path=folder_path
            )
        except OSError as e:
            return FileOperationResult(
                success=False,
                error_code=FileErrorCode.DISK_IO_ERROR,
                error_message=f"OS error clearing folder {folder_path}: {e}",
                file_path=folder_path
            )
        except Exception as e:
            return FileOperationResult(
                success=False,
                error_code=FileErrorCode.DISK_IO_ERROR,
                error_message=f"Unexpected error clearing folder {folder_path}: {e}",
                file_path=folder_path
            )
    
    def copy_file(self, source_path: Path, target_path: Path) -> FileOperationResult:
        """Copy file from source to target location."""
        try:
            if not source_path.exists():
                return FileOperationResult(
                    success=False,
                    error_code=FileErrorCode.FILE_NOT_FOUND,
                    error_message=f"Source file does not exist: {source_path}",
                    file_path=source_path
                )
            
            if target_path.exists():
                return FileOperationResult(
                    success=False,
                    error_code=FileErrorCode.FILE_EXISTS,
                    error_message=f"Target file already exists: {target_path}",
                    file_path=target_path
                )
            
            # Ensure target directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy the file
            shutil.copy2(source_path, target_path)
            
            return FileOperationResult(success=True, file_path=target_path)
            
        except PermissionError as e:
            return FileOperationResult(
                success=False,
                error_code=FileErrorCode.FILE_PERMISSION_DENIED,
                error_message=f"Permission denied copying {source_path} to {target_path}: {e}",
                file_path=source_path
            )
        except OSError as e:
            if e.errno == 28:  # No space left on device
                error_code = FileErrorCode.DISK_SPACE_FULL
                message = f"Insufficient disk space copying {source_path} to {target_path}: {e}"
            elif e.errno == 16:  # Device or resource busy (file locked)
                error_code = FileErrorCode.FILE_LOCKED
                message = f"File is locked: {source_path}: {e}"
            else:
                error_code = FileErrorCode.DISK_IO_ERROR
                message = f"OS error copying {source_path} to {target_path}: {e}"
                
            return FileOperationResult(
                success=False,
                error_code=error_code,
                error_message=message,
                file_path=source_path
            )
        except Exception as e:
            return FileOperationResult(
                success=False,
                error_code=FileErrorCode.DISK_IO_ERROR,
                error_message=f"Unexpected error copying {source_path} to {target_path}: {e}",
                file_path=source_path
            )
    
    def move_file(self, source_path: Path, target_path: Path) -> FileOperationResult:
        """Move file from source to target location."""
        try:
            if not source_path.exists():
                return FileOperationResult(
                    success=False,
                    error_code=FileErrorCode.FILE_NOT_FOUND,
                    error_message=f"Source file does not exist: {source_path}",
                    file_path=source_path
                )
            
            if target_path.exists():
                return FileOperationResult(
                    success=False,
                    error_code=FileErrorCode.FILE_EXISTS,
                    error_message=f"Target file already exists: {target_path}",
                    file_path=target_path
                )
            
            # Ensure target directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move the file
            shutil.move(str(source_path), str(target_path))
            
            return FileOperationResult(success=True, file_path=target_path)
            
        except PermissionError as e:
            return FileOperationResult(
                success=False,
                error_code=FileErrorCode.FILE_PERMISSION_DENIED,
                error_message=f"Permission denied moving {source_path} to {target_path}: {e}",
                file_path=source_path
            )
        except OSError as e:
            if e.errno == 28:  # No space left on device
                error_code = FileErrorCode.DISK_SPACE_FULL
                message = f"Insufficient disk space moving {source_path} to {target_path}: {e}"
            elif e.errno == 16:  # Device or resource busy (file locked)
                error_code = FileErrorCode.FILE_LOCKED
                message = f"File is locked: {source_path}: {e}"
            else:
                error_code = FileErrorCode.DISK_IO_ERROR
                message = f"OS error moving {source_path} to {target_path}: {e}"
                
            return FileOperationResult(
                success=False,
                error_code=error_code,
                error_message=message,
                file_path=source_path
            )
        except Exception as e:
            return FileOperationResult(
                success=False,
                error_code=FileErrorCode.DISK_IO_ERROR,
                error_message=f"Unexpected error moving {source_path} to {target_path}: {e}",
                file_path=source_path
            )
    
    def generate_file_hash(self, file_path: Path) -> HashResult:
        """Generate SHA-256 hash for file content."""
        try:
            if not file_path.exists():
                return HashResult(
                    success=False,
                    error_code=FileErrorCode.FILE_NOT_FOUND,
                    error_message=f"File does not exist: {file_path}",
                    file_path=file_path
                )
            
            # Process file in chunks to handle large files
            hash_sha256 = hashlib.sha256()
            chunk_size = 64 * 1024  # 64KB chunks
            
            with open(file_path, "rb") as f:
                while chunk := f.read(chunk_size):
                    hash_sha256.update(chunk)
            
            hash_value = hash_sha256.hexdigest()
            return HashResult(
                success=True,
                hash_value=hash_value,
                file_path=file_path
            )
            
        except PermissionError as e:
            return HashResult(
                success=False,
                error_code=FileErrorCode.FILE_PERMISSION_DENIED,
                error_message=f"Permission denied reading file {file_path}: {e}",
                file_path=file_path
            )
        except OSError as e:
            if e.errno == 5:  # Input/output error (file corruption)
                error_code = FileErrorCode.FILE_CORRUPTED
                message = f"File appears to be corrupted: {file_path}: {e}"
            else:
                error_code = FileErrorCode.FILE_UNREADABLE
                message = f"Cannot read file {file_path}: {e}"
                
            return HashResult(
                success=False,
                error_code=error_code,
                error_message=message,
                file_path=file_path
            )
        except MemoryError as e:
            return HashResult(
                success=False,
                error_code=FileErrorCode.MEMORY_INSUFFICIENT,
                error_message=f"Insufficient memory to hash file {file_path}: {e}",
                file_path=file_path
            )
        except Exception as e:
            return HashResult(
                success=False,
                error_code=FileErrorCode.FILE_UNREADABLE,
                error_message=f"Unexpected error reading file {file_path}: {e}",
                file_path=file_path
            )
    
    def list_files(self, folder_path: Path, pattern: str = "*") -> list[Path]:
        """List files in folder matching optional pattern."""
        try:
            if not folder_path.exists() or not folder_path.is_dir():
                return []
            
            # Use glob to find matching files
            return list(folder_path.glob(pattern))
            
        except (PermissionError, OSError):
            # If we can't access the folder, return empty list
            return []