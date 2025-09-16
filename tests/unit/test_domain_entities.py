"""Unit tests for domain entities."""

from pathlib import Path
import pytest

from core.domain.receipt import FileHash, DuplicateDetectionResult


class TestFileHash:
    """Test FileHash domain entity."""

    def test_file_hash_creation(self, tmp_path: Path):
        """Test creating a FileHash."""
        test_file = tmp_path / "test.pdf"
        hash_value = "abc123"

        file_hash = FileHash(file_path=test_file, hash_value=hash_value)

        assert file_hash.file_path == test_file
        assert file_hash.hash_value == hash_value

    def test_file_hash_empty_hash_raises_error(self, tmp_path: Path):
        """Test FileHash raises error for empty hash value."""
        test_file = tmp_path / "test.pdf"

        with pytest.raises(ValueError, match="Hash value cannot be empty"):
            FileHash(file_path=test_file, hash_value="")

    def test_file_hash_whitespace_hash_raises_error(self, tmp_path: Path):
        """Test FileHash raises error for whitespace-only hash value."""
        test_file = tmp_path / "test.pdf"

        with pytest.raises(ValueError, match="Hash value cannot be empty"):
            FileHash(file_path=test_file, hash_value="   ")

    def test_file_hash_immutable(self, tmp_path: Path):
        """Test FileHash is immutable (frozen dataclass)."""
        test_file = tmp_path / "test.pdf"
        file_hash = FileHash(file_path=test_file, hash_value="abc123")

        with pytest.raises(AttributeError):
            file_hash.hash_value = "modified"  # type: ignore


class TestDuplicateDetectionResult:
    """Test DuplicateDetectionResult domain entity."""

    def test_duplicate_detection_result_no_duplicate(self, tmp_path: Path):
        """Test creating result for non-duplicate file."""
        test_file = tmp_path / "test.pdf"

        result = DuplicateDetectionResult(
            file_path=test_file, is_duplicate=False, hash_value="abc123"
        )

        assert result.file_path == test_file
        assert result.is_duplicate is False
        assert result.hash_value == "abc123"
        assert result.duplicate_location is None
        assert result.error_message is None
        assert result.has_error is False

    def test_duplicate_detection_result_with_duplicate(self, tmp_path: Path):
        """Test creating result for duplicate file."""
        test_file = tmp_path / "test.pdf"
        duplicate_file = tmp_path / "imported" / "original.pdf"

        result = DuplicateDetectionResult(
            file_path=test_file,
            is_duplicate=True,
            duplicate_location=duplicate_file,
            hash_value="abc123",
        )

        assert result.file_path == test_file
        assert result.is_duplicate is True
        assert result.duplicate_location == duplicate_file
        assert result.hash_value == "abc123"
        assert result.error_message is None
        assert result.has_error is False

    def test_duplicate_detection_result_with_error(self, tmp_path: Path):
        """Test creating result with error."""
        test_file = tmp_path / "test.pdf"
        error_msg = "Failed to calculate hash"

        result = DuplicateDetectionResult(
            file_path=test_file, is_duplicate=False, error_message=error_msg
        )

        assert result.file_path == test_file
        assert result.is_duplicate is False
        assert result.error_message == error_msg
        assert result.has_error is True
        assert result.duplicate_location is None
        assert result.hash_value is None

    def test_location_name_with_duplicate_location(self, tmp_path: Path):
        """Test location_name property with duplicate location."""
        test_file = tmp_path / "test.pdf"
        duplicate_file = tmp_path / "imported" / "original.pdf"

        result = DuplicateDetectionResult(
            file_path=test_file, is_duplicate=True, duplicate_location=duplicate_file
        )

        assert result.location_name == "imported"

    def test_location_name_without_duplicate_location(self, tmp_path: Path):
        """Test location_name property without duplicate location."""
        test_file = tmp_path / "test.pdf"

        result = DuplicateDetectionResult(file_path=test_file, is_duplicate=False)

        assert result.location_name == "unknown"

    def test_duplicate_detection_result_immutable(self, tmp_path: Path):
        """Test DuplicateDetectionResult is immutable (frozen dataclass)."""
        test_file = tmp_path / "test.pdf"
        result = DuplicateDetectionResult(file_path=test_file, is_duplicate=False)

        with pytest.raises(AttributeError):
            result.is_duplicate = True  # type: ignore
