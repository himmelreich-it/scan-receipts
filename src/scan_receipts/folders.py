"""Folder management utilities for the receipt scanner application.

DEPRECATED: This module is kept for backward compatibility.
Use adapters.secondary.file_system_adapter instead.
"""

from pathlib import Path
from typing import Any, Optional

# Re-export from new location for backward compatibility
from core.domain.receipt import RECEIPT_EXTENSIONS, StagingInfo
from adapters.secondary.file_system_adapter import FileSystemAdapter

# Create adapter instance for backward compatibility
_file_system_adapter = FileSystemAdapter()


def create_folders(config: Any) -> None:
    """Create all required folders if they don't exist.
    
    Args:
        config: AppConfig instance with folder paths.
        
    Raises:
        OSError: If folder creation fails.
    """
    _file_system_adapter.create_folders(config)


def count_receipt_files(folder: Path) -> int:
    """Count receipt files in a folder (non-recursive).
    
    Args:
        folder: Path to the folder to count files in.
        
    Returns:
        Number of receipt files found.
    """
    return _file_system_adapter.count_receipt_files(folder)


def get_staging_info(csv_path: Path) -> Optional[StagingInfo]:
    """Get information about the staging CSV file.
    
    Args:
        csv_path: Path to the CSV staging file.
        
    Returns:
        StagingInfo if file exists, None otherwise.
    """
    return _file_system_adapter.get_staging_info(csv_path)


__all__ = ["RECEIPT_EXTENSIONS", "StagingInfo", "create_folders", "count_receipt_files", "get_staging_info"]