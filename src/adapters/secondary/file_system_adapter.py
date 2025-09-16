"""File system adapter implementation."""

import csv
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from core.domain.configuration import AppConfig
from core.domain.receipt import RECEIPT_EXTENSIONS, FileHash, StagingInfo
from ports.file_system import FileSystemPort

logger = logging.getLogger(__name__)


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

            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                lines = list(reader)
                entry_count = len(lines) - 1 if lines else 0

            return StagingInfo(
                file_path=csv_path, modified_time=modified_time, entry_count=entry_count
            )
        except Exception:
            return None

    def get_supported_files(self, folder: Path) -> List[Path]:
        """Get list of supported receipt files from a folder.

        Args:
            folder: Path to the folder to scan.

        Returns:
            List of paths to supported files (PDF, JPG, PNG).
        """
        if not folder.exists():
            return []

        supported_files: List[Path] = []
        for file_path in folder.iterdir():
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in RECEIPT_EXTENSIONS:
                    supported_files.append(file_path)

        return sorted(supported_files)

    def remove_file_if_exists(self, file_path: Path) -> bool:
        """Remove a file if it exists.

        Args:
            file_path: Path to the file to remove.

        Returns:
            True if file was removed, False if it didn't exist.
        """
        if file_path.exists():
            try:
                file_path.unlink()
                return True
            except Exception:
                return False
        return False

    def clear_folder(self, folder: Path) -> None:
        """Clear all files from a folder.

        Args:
            folder: Path to the folder to clear.
        """
        if not folder.exists():
            return

        for file_path in folder.iterdir():
            if file_path.is_file():
                try:
                    file_path.unlink()
                except Exception:
                    pass

    def calculate_file_hash(self, file_path: Path) -> Optional[FileHash]:
        """Calculate hash for a file.

        Args:
            file_path: Path to the file to hash.

        Returns:
            FileHash if successful, None if calculation failed.
        """
        if not file_path.exists() or not file_path.is_file():
            return None

        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)

            hash_value = hash_md5.hexdigest()
            return FileHash(file_path=file_path, hash_value=hash_value)
        except Exception as e:
            logger.warning(f"Failed to calculate hash for {file_path}: {e}")
            return None

    def get_file_hashes_from_folder(self, folder: Path) -> List[FileHash]:
        """Get hashes for all supported files in a folder.

        Args:
            folder: Path to the folder to scan.

        Returns:
            List of FileHash objects for files that could be hashed.
        """
        if not folder.exists():
            return []

        file_hashes: List[FileHash] = []
        for file_path in folder.iterdir():
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in RECEIPT_EXTENSIONS:
                    file_hash = self.calculate_file_hash(file_path)
                    if file_hash:
                        file_hashes.append(file_hash)

        return file_hashes
