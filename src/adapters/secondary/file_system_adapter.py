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

    def copy_file_to_folder(
        self, source_file: Path, destination_folder: Path, target_filename: Optional[str] = None
    ) -> Path:
        """Copy a file to a destination folder.

        Args:
            source_file: Path to the source file.
            destination_folder: Path to the destination folder.
            target_filename: Optional target filename. If not provided, uses original filename.

        Returns:
            Path to the copied file.

        Raises:
            OSError: If copy operation fails.
        """
        import shutil

        if not source_file.exists():
            raise OSError(f"Source file does not exist: {source_file}")

        # Ensure destination folder exists
        destination_folder.mkdir(parents=True, exist_ok=True)

        # Determine destination file path
        filename = target_filename if target_filename else source_file.name
        destination_file = destination_folder / filename

        try:
            # Copy the file
            shutil.copy2(source_file, destination_file)
            logger.info(f"Copied {source_file.name} to {destination_folder.name}/{filename}")
            return destination_file
        except Exception as e:
            logger.error(f"Failed to copy {source_file.name}: {e}")
            raise OSError(f"Failed to copy file: {e}")

    def write_error_log(self, failed_folder: Path, filename: str, error_message: str) -> None:
        """Write error log for failed file processing.

        Args:
            failed_folder: Path to the failed folder.
            filename: Name of the failed file.
            error_message: Error message to log.
        """
        try:
            # Ensure failed folder exists
            failed_folder.mkdir(parents=True, exist_ok=True)

            # Create error log file path
            log_filename = f"{Path(filename).stem}_error.txt"
            log_file_path = failed_folder / log_filename

            # Write error message to log file
            with open(log_file_path, "w", encoding="utf-8") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"Error processing file: {filename}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Error: {error_message}\n")

            logger.info(f"Created error log: {log_filename}")

        except Exception as e:
            logger.error(f"Failed to write error log for {filename}: {e}")

    def create_backup_file(self, file_path: Path) -> Optional[Path]:
        """Create a numbered backup of a file.

        Creates backup with incremental numbering: file.1.ext, file.2.ext, etc.
        Finds the next available number if backups already exist.

        Args:
            file_path: Path to the file to backup.

        Returns:
            Path to the backup file if successful, None if file doesn't exist.

        Raises:
            OSError: If backup creation fails.
        """
        import shutil

        if not file_path.exists():
            return None

        # Get file parts
        parent = file_path.parent
        stem = file_path.stem
        suffix = file_path.suffix

        # Find next available backup number
        backup_number = 1
        while True:
            backup_path = parent / f"{stem}.{backup_number}{suffix}"
            if not backup_path.exists():
                break
            backup_number += 1

        try:
            # Create backup
            shutil.copy2(file_path, backup_path)
            logger.info(f"Created backup: {backup_path.name}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup of {file_path.name}: {e}")
            raise OSError(f"Failed to create backup: {e}")

    def move_file_to_folder(
        self, source_file: Path, destination_folder: Path, target_filename: str
    ) -> Path:
        """Move a file to a destination folder with a new name.

        Args:
            source_file: Path to the source file.
            destination_folder: Path to the destination folder.
            target_filename: Target filename for the moved file.

        Returns:
            Path to the moved file.

        Raises:
            OSError: If move operation fails.
        """
        import shutil

        if not source_file.exists():
            raise OSError(f"Source file does not exist: {source_file}")

        # Ensure destination folder exists
        destination_folder.mkdir(parents=True, exist_ok=True)

        # Determine destination file path
        destination_file = destination_folder / target_filename

        try:
            # Move the file
            shutil.move(str(source_file), str(destination_file))
            logger.info(f"Moved {source_file.name} to {destination_folder.name}/{target_filename}")
            return destination_file
        except Exception as e:
            logger.error(f"Failed to move {source_file.name}: {e}")
            raise OSError(f"Failed to move file: {e}")
