"""Unit tests for file organization domain models."""

from datetime import datetime

from file_organization.domain.models import ArchiveResult


class TestArchiveResult:
    """Test ArchiveResult value object."""

    def test_archive_result_creation(self):
        """Test: ArchiveResult can be created with all required fields"""
        timestamp = datetime(2024, 3, 15, 14, 30, 52, 123456)
        
        result = ArchiveResult(
            source_filename="receipt.jpg",
            archived_filename="1-20240315-143052123456-receipt.jpg",
            archive_timestamp=timestamp,
            file_id=1
        )
        
        assert result.source_filename == "receipt.jpg"
        assert result.archived_filename == "1-20240315-143052123456-receipt.jpg"
        assert result.archive_timestamp == timestamp
        assert result.file_id == 1

    def test_archive_result_immutable(self):
        """Test: ArchiveResult is immutable (frozen dataclass)"""
        timestamp = datetime.now()
        result = ArchiveResult(
            source_filename="test.pdf",
            archived_filename="2-timestamp-test.pdf",
            archive_timestamp=timestamp,
            file_id=2
        )
        
        # Attempting to modify should raise AttributeError
        try:
            result.file_id = 999
            assert False, "Should not be able to modify frozen dataclass"
        except AttributeError:
            pass  # Expected behavior

    def test_get_done_filename(self):
        """Test: get_done_filename returns archived filename without path"""
        timestamp = datetime(2024, 1, 1, 12, 0, 0, 0)
        
        result = ArchiveResult(
            source_filename="invoice.png",
            archived_filename="5-20240101-120000000000-invoice.png",
            archive_timestamp=timestamp,
            file_id=5
        )
        
        done_filename = result.get_done_filename()
        assert done_filename == "5-20240101-120000000000-invoice.png"
        assert done_filename == result.archived_filename

    def test_archive_result_equality(self):
        """Test: ArchiveResult instances are equal if all fields match"""
        timestamp = datetime(2024, 3, 15, 14, 30, 52, 123456)
        
        result1 = ArchiveResult(
            source_filename="receipt.jpg",
            archived_filename="1-20240315-143052123456-receipt.jpg",
            archive_timestamp=timestamp,
            file_id=1
        )
        
        result2 = ArchiveResult(
            source_filename="receipt.jpg",
            archived_filename="1-20240315-143052123456-receipt.jpg",
            archive_timestamp=timestamp,
            file_id=1
        )
        
        assert result1 == result2

    def test_archive_result_string_representation(self):
        """Test: ArchiveResult has meaningful string representation"""
        timestamp = datetime(2024, 3, 15, 14, 30, 52, 123456)
        
        result = ArchiveResult(
            source_filename="receipt.jpg",
            archived_filename="1-20240315-143052123456-receipt.jpg",
            archive_timestamp=timestamp,
            file_id=1
        )
        
        str_repr = str(result)
        assert "receipt.jpg" in str_repr
        assert "1-20240315-143052123456-receipt.jpg" in str_repr
        assert "file_id=1" in str_repr