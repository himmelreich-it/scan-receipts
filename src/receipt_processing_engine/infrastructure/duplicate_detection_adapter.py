"""SHA-256 file hashing for duplicate detection."""

import hashlib
import logging
from pathlib import Path
from typing import Set
from ..application.ports import DuplicateDetectionPort


logger = logging.getLogger(__name__)


class DuplicateDetectionAdapter(DuplicateDetectionPort):
    """Adapter for file duplicate detection using SHA-256 hashing."""

    def generate_file_hash(self, file_path: str) -> str:
        """Generate SHA-256 hash for file.

        Args:
            file_path: Path to file

        Returns:
            SHA-256 hash string for the file

        Raises:
            FileNotFoundError: When file doesn't exist
            PermissionError: When file cannot be read
        """
        try:
            path = Path(file_path)

            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            if not path.is_file():
                raise ValueError(f"Path is not a file: {file_path}")

            with open(path, "rb") as file:
                file_content = file.read()

            file_hash = self._calculate_sha256(file_content)
            logger.debug(f"Generated hash for {file_path}: {file_hash[:16]}...")

            return file_hash

        except Exception as e:
            logger.error(f"Failed to generate hash for {file_path}: {e}")
            raise

    def is_duplicate(self, file_hash: str, known_hashes: Set[str]) -> bool:
        """Check if file hash is a duplicate.

        Args:
            file_hash: Hash to check
            known_hashes: Set of known hashes

        Returns:
            True if duplicate, False otherwise
        """
        is_dup = file_hash in known_hashes
        if is_dup:
            logger.info(f"Duplicate detected: {file_hash[:16]}...")
        return is_dup

    def _calculate_sha256(self, file_content: bytes) -> str:
        """Calculate SHA-256 hash of file content.

        Args:
            file_content: Binary file content

        Returns:
            SHA-256 hash as hexadecimal string
        """
        sha256_hash = hashlib.sha256()
        sha256_hash.update(file_content)
        return sha256_hash.hexdigest()
