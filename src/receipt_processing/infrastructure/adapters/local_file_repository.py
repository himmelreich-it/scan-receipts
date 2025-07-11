"""Local file system repository implementation."""

import os
from typing import List

from receipt_processing.domain.models.file_path import FilePath
from receipt_processing.domain.repositories.file_system_repository import FileSystemRepository


class LocalFileRepository(FileSystemRepository):
    """Concrete implementation of file system repository using local file system."""
    
    def list_files_in_directory(self, directory_path: str) -> List[FilePath]:
        """List all files in the given directory."""
        if not self.directory_exists(directory_path):
            return []
        
        file_paths = []
        try:
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                if os.path.isfile(item_path):
                    file_paths.append(FilePath(item_path))
        except PermissionError:
            raise PermissionError(f"Permission denied: cannot access {directory_path}")
        
        return file_paths
    
    def ensure_directory_exists(self, directory_path: str) -> None:
        """Ensure the given directory exists, creating it if necessary."""
        if not self.directory_exists(directory_path):
            try:
                os.makedirs(directory_path, exist_ok=True)
                print("Created input folder")
            except PermissionError:
                raise PermissionError(f"Permission denied: cannot create {directory_path}")
    
    def directory_exists(self, directory_path: str) -> bool:
        """Check if the given directory exists."""
        return os.path.exists(directory_path) and os.path.isdir(directory_path)