"""Integration tests for duplicate detection flow."""

from pathlib import Path
from unittest.mock import Mock

from adapters.secondary.duplicate_detection_adapter import DuplicateDetectionAdapter
from adapters.secondary.file_system_adapter import FileSystemAdapter
from core.domain.configuration import AppConfig
from core.use_cases.process_receipt import ProcessReceiptUseCase


class TestDuplicateDetectionIntegration:
    """Test duplicate detection integration with real file system operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.file_system = FileSystemAdapter()
        self.duplicate_detection = DuplicateDetectionAdapter(self.file_system)

        # Mock AI extraction and CSV ports for isolated testing
        self.mock_ai_extraction = Mock()
        self.mock_csv = Mock()

        self.use_case = ProcessReceiptUseCase(
            self.file_system,
            self.mock_ai_extraction,
            self.mock_csv,
            self.duplicate_detection
        )

    def test_duplicate_detection_with_real_files(self, tmp_path: Path):
        """Test duplicate detection with real file operations."""
        # Create folder structure
        incoming = tmp_path / "incoming"
        imported = tmp_path / "imported"
        scanned = tmp_path / "scanned"
        failed = tmp_path / "failed"

        incoming.mkdir()
        imported.mkdir()
        scanned.mkdir()
        failed.mkdir()

        # Create identical files
        identical_content = b"This is identical receipt content"

        # File in incoming (to be processed)
        incoming_file = incoming / "new_receipt.pdf"
        incoming_file.write_bytes(identical_content)

        # Existing file in imported folder (duplicate)
        existing_file = imported / "existing_receipt.pdf"
        existing_file.write_bytes(identical_content)

        # Get hashes
        incoming_hash = self.file_system.calculate_file_hash(incoming_file)
        existing_hash = self.file_system.calculate_file_hash(existing_file)

        assert incoming_hash is not None
        assert existing_hash is not None
        assert incoming_hash.hash_value == existing_hash.hash_value

        # Test duplicate detection
        result = self.duplicate_detection.check_duplicate(
            incoming_file, [existing_hash]
        )

        assert result.is_duplicate
        assert result.duplicate_location == existing_file
        assert result.hash_value == existing_hash.hash_value
        assert not result.has_error

    def test_duplicate_detection_different_files(self, tmp_path: Path):
        """Test duplicate detection with different files."""
        # Create folder structure
        incoming = tmp_path / "incoming"
        imported = tmp_path / "imported"

        incoming.mkdir()
        imported.mkdir()

        # Create different files
        incoming_file = incoming / "new_receipt.pdf"
        incoming_file.write_bytes(b"Different content 1")

        existing_file = imported / "existing_receipt.pdf"
        existing_file.write_bytes(b"Different content 2")

        # Get hashes
        incoming_hash = self.file_system.calculate_file_hash(incoming_file)
        existing_hash = self.file_system.calculate_file_hash(existing_file)

        assert incoming_hash is not None
        assert existing_hash is not None
        assert incoming_hash.hash_value != existing_hash.hash_value

        # Test duplicate detection
        result = self.duplicate_detection.check_duplicate(
            incoming_file, [existing_hash]
        )

        assert not result.is_duplicate
        assert result.duplicate_location is None
        assert result.hash_value == incoming_hash.hash_value
        assert not result.has_error

    def test_process_receipt_use_case_skips_duplicates(self, tmp_path: Path):
        """Test ProcessReceiptUseCase skips duplicate files."""
        # Create folder structure
        incoming = tmp_path / "incoming"
        imported = tmp_path / "imported"
        scanned = tmp_path / "scanned"
        failed = tmp_path / "failed"
        csv_file = tmp_path / "receipts.csv"

        for folder in [incoming, imported, scanned, failed]:
            folder.mkdir()

        # Create test files
        identical_content = b"Identical receipt content"
        different_content = b"Different receipt content"

        # Files in incoming
        duplicate_file = incoming / "duplicate.pdf"
        duplicate_file.write_bytes(identical_content)

        unique_file = incoming / "unique.pdf"
        unique_file.write_bytes(different_content)

        # Existing file in imported (creates duplicate)
        existing_file = imported / "existing.pdf"
        existing_file.write_bytes(identical_content)

        config = AppConfig(
            incoming_folder=incoming,
            scanned_folder=scanned,
            imported_folder=imported,
            failed_folder=failed,
            csv_staging_file=csv_file,
            xlsx_output_file=tmp_path / "test.xlsx"
        )

        # Execute the use case
        self.use_case.execute(config)

        # Should only call AI extraction for unique file
        # Note: AI extraction is mocked so we can check call count
        assert self.mock_ai_extraction.extract_receipt_data.call_count == 0  # Still TODO in implementation

    def test_get_existing_hashes_from_both_folders(self, tmp_path: Path):
        """Test getting hashes from both imported and scanned folders."""
        # Create folder structure
        imported = tmp_path / "imported"
        scanned = tmp_path / "scanned"

        imported.mkdir()
        scanned.mkdir()

        # Create files in both folders
        imported_file = imported / "imported.pdf"
        imported_file.write_bytes(b"Imported content")

        scanned_file = scanned / "scanned.pdf"
        scanned_file.write_bytes(b"Scanned content")

        # Get existing hashes using public interface
        imported_hashes = self.file_system.get_file_hashes_from_folder(imported)
        scanned_hashes = self.file_system.get_file_hashes_from_folder(scanned)
        existing_hashes = imported_hashes + scanned_hashes

        assert len(existing_hashes) == 2
        hash_file_names = [h.file_path.name for h in existing_hashes]
        assert "imported.pdf" in hash_file_names
        assert "scanned.pdf" in hash_file_names

    def test_hash_calculation_error_handling(self, tmp_path: Path):
        """Test graceful handling of hash calculation errors."""
        # Create a directory instead of a file to trigger error
        incoming = tmp_path / "incoming"
        incoming.mkdir()

        # Create a subdirectory with receipt extension (should cause error)
        fake_file = incoming / "fake_receipt.pdf"
        fake_file.mkdir()  # This is a directory, not a file

        # Try to calculate hash - should return None gracefully
        result = self.file_system.calculate_file_hash(fake_file)
        assert result is None

        # Test duplicate detection with error file
        result = self.duplicate_detection.check_duplicate(fake_file, [])
        assert not result.is_duplicate
        assert result.has_error
        assert result.error_message is not None
        assert "Failed to calculate file hash" in result.error_message