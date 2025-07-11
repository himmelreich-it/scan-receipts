"""Tests for FileContent value object."""

import pytest
from src.receipt_processing.domain.models.file_content import FileContent


class TestFileContent:
    """Test cases for FileContent value object."""
    
    def test_creation_with_valid_content(self):
        """Test creating FileContent with valid content."""
        content = FileContent(
            data="base64encodeddata",
            mime_type="application/pdf",
            size_bytes=1024
        )
        assert content.data == "base64encodeddata"
        assert content.mime_type == "application/pdf"
        assert content.size_bytes == 1024
    
    def test_creation_with_empty_data_raises_error(self):
        """Test creating FileContent with empty data raises ValueError."""
        with pytest.raises(ValueError, match="File content cannot be empty"):
            FileContent(
                data="",
                mime_type="application/pdf",
                size_bytes=1024
            )
    
    def test_creation_with_negative_size_raises_error(self):
        """Test creating FileContent with negative size raises ValueError."""
        with pytest.raises(ValueError, match="File size cannot be negative"):
            FileContent(
                data="base64encodeddata",
                mime_type="application/pdf",
                size_bytes=-1
            )
    
    def test_immutability(self):
        """Test FileContent is immutable."""
        content = FileContent(
            data="base64encodeddata",
            mime_type="application/pdf",
            size_bytes=1024
        )
        with pytest.raises(AttributeError):
            content.data = "newdata"