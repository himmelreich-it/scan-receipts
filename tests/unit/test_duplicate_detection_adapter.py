"""Unit tests for DuplicateDetectionAdapter."""

from pathlib import Path
from unittest.mock import Mock

from adapters.secondary.duplicate_detection_adapter import DuplicateDetectionAdapter
from core.domain.receipt import FileHash


class TestDuplicateDetectionAdapter:
    """Test DuplicateDetectionAdapter functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_file_system = Mock()
        self.adapter = DuplicateDetectionAdapter(self.mock_file_system)

    def test_check_duplicate_no_existing_hashes(self, tmp_path: Path):
        """Test check_duplicate with no existing hashes."""
        test_file = tmp_path / "test.pdf"
        test_hash = FileHash(file_path=test_file, hash_value="abc123")
        self.mock_file_system.calculate_file_hash.return_value = test_hash

        result = self.adapter.check_duplicate(test_file, [])

        assert not result.is_duplicate
        assert result.file_path == test_file
        assert result.hash_value == "abc123"
        assert result.duplicate_location is None
        assert not result.has_error

    def test_check_duplicate_no_match(self, tmp_path: Path):
        """Test check_duplicate with existing hashes but no match."""
        test_file = tmp_path / "test.pdf"
        other_file = tmp_path / "other.pdf"

        test_hash = FileHash(file_path=test_file, hash_value="abc123")
        existing_hash = FileHash(file_path=other_file, hash_value="xyz789")

        self.mock_file_system.calculate_file_hash.return_value = test_hash

        result = self.adapter.check_duplicate(test_file, [existing_hash])

        assert not result.is_duplicate
        assert result.file_path == test_file
        assert result.hash_value == "abc123"
        assert result.duplicate_location is None
        assert not result.has_error

    def test_check_duplicate_with_match(self, tmp_path: Path):
        """Test check_duplicate with matching hash."""
        test_file = tmp_path / "test.pdf"
        existing_file = tmp_path / "imported" / "existing.pdf"

        test_hash = FileHash(file_path=test_file, hash_value="abc123")
        existing_hash = FileHash(file_path=existing_file, hash_value="abc123")

        self.mock_file_system.calculate_file_hash.return_value = test_hash

        result = self.adapter.check_duplicate(test_file, [existing_hash])

        assert result.is_duplicate
        assert result.file_path == test_file
        assert result.hash_value == "abc123"
        assert result.duplicate_location == existing_file
        assert not result.has_error

    def test_check_duplicate_hash_calculation_fails(self, tmp_path: Path):
        """Test check_duplicate when hash calculation fails."""
        test_file = tmp_path / "test.pdf"
        self.mock_file_system.calculate_file_hash.return_value = None

        result = self.adapter.check_duplicate(test_file, [])

        assert not result.is_duplicate
        assert result.file_path == test_file
        assert result.has_error
        assert result.error_message is not None
        assert "Failed to calculate file hash" in result.error_message
        assert result.hash_value is None
        assert result.duplicate_location is None

    def test_check_duplicate_exception_handling(self, tmp_path: Path):
        """Test check_duplicate handles exceptions gracefully."""
        test_file = tmp_path / "test.pdf"
        self.mock_file_system.calculate_file_hash.side_effect = Exception("IO Error")

        result = self.adapter.check_duplicate(test_file, [])

        assert not result.is_duplicate
        assert result.file_path == test_file
        assert result.has_error
        assert result.error_message is not None
        assert "Duplicate detection failed: IO Error" in result.error_message

    def test_check_duplicate_first_match_wins(self, tmp_path: Path):
        """Test check_duplicate returns first matching hash."""
        test_file = tmp_path / "test.pdf"
        existing_file1 = tmp_path / "imported" / "existing1.pdf"
        existing_file2 = tmp_path / "scanned" / "existing2.pdf"

        test_hash = FileHash(file_path=test_file, hash_value="abc123")
        existing_hash1 = FileHash(file_path=existing_file1, hash_value="abc123")
        existing_hash2 = FileHash(file_path=existing_file2, hash_value="abc123")

        self.mock_file_system.calculate_file_hash.return_value = test_hash

        result = self.adapter.check_duplicate(
            test_file, [existing_hash1, existing_hash2]
        )

        assert result.is_duplicate
        assert result.duplicate_location == existing_file1  # First match

    def test_check_duplicate_multiple_hashes_no_match(self, tmp_path: Path):
        """Test check_duplicate with multiple existing hashes but no match."""
        test_file = tmp_path / "test.pdf"
        existing_file1 = tmp_path / "imported" / "existing1.pdf"
        existing_file2 = tmp_path / "scanned" / "existing2.pdf"

        test_hash = FileHash(file_path=test_file, hash_value="abc123")
        existing_hash1 = FileHash(file_path=existing_file1, hash_value="def456")
        existing_hash2 = FileHash(file_path=existing_file2, hash_value="ghi789")

        self.mock_file_system.calculate_file_hash.return_value = test_hash

        result = self.adapter.check_duplicate(
            test_file, [existing_hash1, existing_hash2]
        )

        assert not result.is_duplicate
        assert result.hash_value == "abc123"
        assert result.duplicate_location is None
