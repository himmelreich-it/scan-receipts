"""Hash-based duplicate detection adapter."""

import logging
from typing import Dict, Set
from pathlib import Path
from ..application.ports import DuplicateDetectionPort
from file_management.adapters import FileSystemAdapter as FileManagerAdapter


logger = logging.getLogger(__name__)


class DuplicateDetectionAdapter(DuplicateDetectionPort):
    """Adapter for SHA-256 hash-based duplicate detection."""

    def __init__(self):
        """Initialize with empty hash databases."""
        self.imported_folder_hashes: Set[str] = set()
        self.session_hashes: Dict[str, str] = {}  # hash -> original filename
        self.file_manager = FileManagerAdapter()

    def initialize_imported_folder_hashes(self, imported_folder: Path) -> None:
        """Scan imported folder and build hash database.

        Process:
        1. Scan all files in imported folder using file management service
        2. Generate SHA-256 hash for each file
        3. Store in hash database for duplicate checking
        """
        try:
            # Use file management service to list files (returns empty list if folder doesn't exist)
            file_paths = self.file_manager.list_files(imported_folder)
            
            if not file_paths:
                logger.info(f"Imported folder is empty or does not exist: {imported_folder}")
                return

            hash_count = 0
            for file_path in file_paths:
                hash_result = self.file_manager.generate_file_hash(file_path)
                if hash_result.success and hash_result.hash_value:
                    self.imported_folder_hashes.add(hash_result.hash_value)
                    hash_count += 1
                else:
                    logger.warning(f"Failed to hash file {file_path}: {hash_result.error_message}")
                    continue

            logger.info(
                f"Loaded {hash_count} file hashes from imported folder: {imported_folder}"
            )

        except Exception as e:
            logger.error(f"Failed to initialize imported folder hashes: {e}")
            raise

    def initialize_done_folder_hashes(self, done_folder: Path) -> None:
        """Legacy method: Scan done folder and build hash database.
        
        This method is deprecated. Use initialize_imported_folder_hashes instead.
        For backward compatibility, this calls the new method.
        """
        return self.initialize_imported_folder_hashes(done_folder)

    def is_duplicate(self, file_hash: str) -> bool:
        """Check if file hash is a duplicate.

        Checks against:
        1. Imported folder hash database
        2. Current session hash database
        """
        # Check against imported folder hashes
        if file_hash in self.imported_folder_hashes:
            logger.debug(f"Duplicate found in imported folder: {file_hash}")
            return True

        # Check against current session hashes
        if file_hash in self.session_hashes:
            original_filename = self.session_hashes[file_hash]
            logger.debug(
                f"Duplicate found in current session: {file_hash} (matches {original_filename})"
            )
            return True

        return False

    def add_to_session(self, file_hash: str, filename: str) -> None:
        """Add file hash to current session tracking."""
        self.session_hashes[file_hash] = filename
        logger.debug(f"Added to session tracking: {filename} -> {file_hash}")

    def generate_file_hash(self, file_path: Path) -> str:
        """Generate SHA-256 hash for file using file management service."""
        hash_result = self.file_manager.generate_file_hash(file_path)
        if hash_result.success and hash_result.hash_value:
            logger.debug(f"Generated hash for {file_path}: {hash_result.hash_value}")
            return hash_result.hash_value
        else:
            error_msg = hash_result.error_message or "Unknown error"
            logger.error(f"Failed to generate hash for {file_path}: {error_msg}")
            raise Exception(f"Hash generation failed: {error_msg}")
