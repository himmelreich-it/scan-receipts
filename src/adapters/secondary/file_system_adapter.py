"""File system adapter implementation."""

import csv
from datetime import datetime
from pathlib import Path
from typing import Optional

from core.domain.configuration import AppConfig
from core.domain.receipt import RECEIPT_EXTENSIONS, StagingInfo
from ports.file_system import FileSystemPort


class FileSystemAdapter(FileSystemPort):
    """Implementation of file system operations."""
    
    def create_folders(self, config: AppConfig) -> None:
        """Create all required folders if they don't exist.
        
        Args:
            config: AppConfig instance with folder paths.
            
        Raises:
            OSError: If folder creation fails.
        """
        folders = [
            config.incoming_folder,
            config.scanned_folder, 
            config.imported_folder,
            config.failed_folder,
        ]
        
        for folder in folders:
            try:
                folder.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise OSError(f"Failed to create folder {folder}: {e}")
    
    def count_receipt_files(self, folder: Path) -> int:
        """Count receipt files in a folder (non-recursive).
        
        Args:
            folder: Path to the folder to count files in.
            
        Returns:
            Number of receipt files found.
        """
        if not folder.exists():
            return 0
        
        count = 0
        for file_path in folder.iterdir():
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in RECEIPT_EXTENSIONS:
                    count += 1
        
        return count
    
    def get_staging_info(self, csv_path: Path) -> Optional[StagingInfo]:
        """Get information about the staging CSV file.
        
        Args:
            csv_path: Path to the CSV staging file.
            
        Returns:
            StagingInfo if file exists, None otherwise.
        """
        if not csv_path.exists():
            return None
        
        try:
            modified_time = datetime.fromtimestamp(csv_path.stat().st_mtime)
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                lines = list(reader)
                entry_count = len(lines) - 1 if lines else 0
            
            return StagingInfo(
                file_path=csv_path,
                modified_time=modified_time,
                entry_count=entry_count
            )
        except Exception:
            return None