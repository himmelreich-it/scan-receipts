"""Tests for FileExtension value object."""

import pytest
from src.receipt_processing.domain.models.file_extension import FileExtension


class TestFileExtension:
    """Test cases for FileExtension value object."""
    
    def test_creation_with_valid_extension(self):
        """Test creating FileExtension with valid extension."""
        ext = FileExtension(".pdf")
        assert ext.extension == ".pdf"
    
    def test_creation_with_extension_without_dot(self):
        """Test creating FileExtension automatically adds dot."""
        ext = FileExtension("pdf")
        assert ext.extension == ".pdf"
    
    def test_creation_normalizes_to_lowercase(self):
        """Test creating FileExtension normalizes to lowercase."""
        ext = FileExtension(".PDF")
        assert ext.extension == ".pdf"
    
    def test_creation_with_empty_extension_raises_error(self):
        """Test creating FileExtension with empty extension raises ValueError."""
        with pytest.raises(ValueError, match="File extension cannot be empty"):
            FileExtension("")
    
    def test_matches_with_same_extension(self):
        """Test matches method returns True for same extension."""
        ext1 = FileExtension(".pdf")
        ext2 = FileExtension(".pdf")
        assert ext1.matches(ext2) is True
    
    def test_matches_with_different_extension(self):
        """Test matches method returns False for different extension."""
        ext1 = FileExtension(".pdf")
        ext2 = FileExtension(".jpg")
        assert ext1.matches(ext2) is False
    
    def test_matches_case_insensitive(self):
        """Test matches method is case insensitive."""
        ext1 = FileExtension(".PDF")
        ext2 = FileExtension(".pdf")
        assert ext1.matches(ext2) is True
    
    def test_immutability(self):
        """Test FileExtension is immutable."""
        ext = FileExtension(".pdf")
        with pytest.raises(AttributeError):
            ext.extension = ".jpg"