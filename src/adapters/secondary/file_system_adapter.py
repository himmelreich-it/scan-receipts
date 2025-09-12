"""File system adapter implementation."""

import logging
from pathlib import Path
from typing import List

from core.domain import is_valid_receipt_file
from ports import FileSystemPort
from scan_receipts.folders import count_receipt_files

logger = logging.getLogger(__name__)


class FileSystemAdapter(FileSystemPort):
    """File system adapter implementation."""

    def get_receipt_files(self, folder: Path) -> List[Path]:
        """Get all receipt files from a folder.
        
        Args:
            folder: Folder to scan for receipt files.
            
        Returns:
            List of receipt file paths.
        """
        if not folder.exists():
            logger.warning(f"Folder does not exist: {folder}")
            return []

        receipt_files: List[Path] = []
        
        try:
            for file_path in folder.iterdir():
                if file_path.is_file() and is_valid_receipt_file(file_path):
                    receipt_files.append(file_path)
            
            logger.info(f"Found {len(receipt_files)} receipt files in {folder}")
            return sorted(receipt_files)
            
        except Exception as e:
            logger.error(f"Error scanning folder {folder}: {e}")
            return []

    def move_file(self, source: Path, destination: Path) -> None:
        """Move a file from source to destination.
        
        Args:
            source: Source file path.
            destination: Destination file path.
        """
        try:
            # Ensure destination directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Move the file
            source.rename(destination)
            logger.info(f"Moved file: {source.name} -> {destination}")
            
        except Exception as e:
            logger.error(f"Failed to move file {source} to {destination}: {e}")
            raise

    def create_folders(self, folders: List[Path]) -> None:
        """Create folders if they don't exist.
        
        Args:
            folders: List of folder paths to create.
        """
        for folder in folders:
            try:
                folder.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Created folder: {folder}")
            except Exception as e:
                logger.error(f"Failed to create folder {folder}: {e}")
                raise

    def count_receipt_files(self, folder: Path) -> int:
        """Count receipt files in a folder.
        
        Args:
            folder: Folder to count files in.
            
        Returns:
            Number of receipt files.
        """
        return count_receipt_files(folder)