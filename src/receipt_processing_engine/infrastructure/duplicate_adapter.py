"""Hash-based duplicate detection adapter."""

import hashlib
import logging
from typing import Dict, Set
from pathlib import Path
from ..application.ports import DuplicateDetectionPort


logger = logging.getLogger(__name__)


class DuplicateDetectionAdapter(DuplicateDetectionPort):
    """Adapter for SHA-256 hash-based duplicate detection."""

    def __init__(self):
        """Initialize with empty hash databases."""
        self.imported_folder_hashes: Set[str] = set()
        self.session_hashes: Dict[str, str] = {}  # hash -> original filename

    def initialize_imported_folder_hashes(self, imported_folder: Path) -> None:
        """Scan imported folder and build hash database.

        Process:
        1. Scan all files in imported folder
        2. Generate SHA-256 hash for each file
        3. Store in hash database for duplicate checking
        """
        try:
            if not imported_folder.exists():
                logger.info(f"Imported folder does not exist: {imported_folder}")
                return

            hash_count = 0
            for file_path in imported_folder.iterdir():
                if file_path.is_file():
                    try:
                        file_hash = self._generate_file_hash(file_path)
                        self.imported_folder_hashes.add(file_hash)
                        hash_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to hash file {file_path}: {e}")
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
        """Generate SHA-256 hash for file."""
        return self._generate_file_hash(file_path)

    def _generate_file_hash(self, file_path: Path) -> str:
        """Generate SHA-256 hash for file."""
        try:
            hash_sha256 = hashlib.sha256()

            with open(file_path, "rb") as f:
                # Read file in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)

            file_hash = hash_sha256.hexdigest()
            logger.debug(f"Generated hash for {file_path}: {file_hash}")
            return file_hash

        except Exception as e:
            logger.error(f"Failed to generate hash for {file_path}: {e}")
            raise
