"""Abstract interface for file system operations following hexagonal architecture."""

from abc import ABC, abstractmethod
from pathlib import Path
from file_management.models import FileOperationResult, HashResult, FolderValidationResult


class FileSystemPort(ABC):
    """Abstract port for file system operations."""
    
    @abstractmethod
    def ensure_folder_exists(self, folder_path: Path) -> FolderValidationResult:
        """Create folder if missing, validate permissions.
        
        Args:
            folder_path: Path to the folder to validate/create
            
        Returns:
            FolderValidationResult with success status and details
        """
        
    @abstractmethod
    def clear_folder(self, folder_path: Path) -> FileOperationResult:
        """Remove all contents from folder.
        
        Args:
            folder_path: Path to the folder to clear
            
        Returns:
            FileOperationResult with operation status
        """
        
    @abstractmethod
    def copy_file(self, source_path: Path, target_path: Path) -> FileOperationResult:
        """Copy file from source to target location.
        
        Args:
            source_path: Source file path
            target_path: Target file path
            
        Returns:
            FileOperationResult with operation status
        """
        
    @abstractmethod
    def move_file(self, source_path: Path, target_path: Path) -> FileOperationResult:
        """Move file from source to target location.
        
        Args:
            source_path: Source file path
            target_path: Target file path
            
        Returns:
            FileOperationResult with operation status
        """
        
    @abstractmethod
    def generate_file_hash(self, file_path: Path) -> HashResult:
        """Generate SHA-256 hash for file content.
        
        Args:
            file_path: Path to the file to hash
            
        Returns:
            HashResult with hash value or error details
        """
        
    @abstractmethod
    def list_files(self, folder_path: Path, pattern: str = "*") -> list[Path]:
        """List files in folder matching optional pattern.
        
        Args:
            folder_path: Path to the folder to search
            pattern: Glob pattern for file matching (default: "*")
            
        Returns:
            List of matching file paths
        """