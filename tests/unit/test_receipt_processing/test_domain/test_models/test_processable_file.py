"""Tests for ProcessableFile entity."""

from datetime import datetime
from unittest.mock import patch
from src.receipt_processing.domain.models.processable_file import ProcessableFile
from src.receipt_processing.domain.models.file_path import FilePath
from src.receipt_processing.domain.models.file_extension import FileExtension
from src.receipt_processing.domain.models.file_content import FileContent


class TestProcessableFile:
    """Test cases for ProcessableFile entity."""
    
    def test_creation_with_required_fields(self):
        """Test creating ProcessableFile with required fields."""
        file_path = FilePath("/path/to/file.pdf")
        extension = FileExtension(".pdf")
        
        processable_file = ProcessableFile(file_path, extension)
        
        assert processable_file.file_path == file_path
        assert processable_file.extension == extension
        assert processable_file.content is None
        assert processable_file.processing_status == "pending"
        assert processable_file.error_message is None
        assert processable_file.processed_at is None
    
    @patch('src.receipt_processing.domain.models.processable_file.datetime')
    def test_mark_as_processed(self, mock_datetime):
        """Test marking file as processed."""
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = mock_now
        
        file_path = FilePath("/path/to/file.pdf")
        extension = FileExtension(".pdf")
        processable_file = ProcessableFile(file_path, extension)
        
        processable_file.mark_as_processed()
        
        assert processable_file.processing_status == "processed"
        assert processable_file.processed_at == mock_now
    
    @patch('src.receipt_processing.domain.models.processable_file.datetime')
    def test_mark_as_error(self, mock_datetime):
        """Test marking file as error."""
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = mock_now
        
        file_path = FilePath("/path/to/file.pdf")
        extension = FileExtension(".pdf")
        processable_file = ProcessableFile(file_path, extension)
        
        error_message = "File corrupted"
        processable_file.mark_as_error(error_message)
        
        assert processable_file.processing_status == "error"
        assert processable_file.error_message == error_message
        assert processable_file.processed_at == mock_now
    
    def test_is_ready_for_processing_with_content(self):
        """Test is_ready_for_processing returns True when content is present."""
        file_path = FilePath("/path/to/file.pdf")
        extension = FileExtension(".pdf")
        content = FileContent("base64data", "application/pdf", 1024)
        
        processable_file = ProcessableFile(file_path, extension, content=content)
        
        assert processable_file.is_ready_for_processing() is True
    
    def test_is_ready_for_processing_without_content(self):
        """Test is_ready_for_processing returns False when content is missing."""
        file_path = FilePath("/path/to/file.pdf")
        extension = FileExtension(".pdf")
        
        processable_file = ProcessableFile(file_path, extension)
        
        assert processable_file.is_ready_for_processing() is False
    
    def test_is_ready_for_processing_with_error_status(self):
        """Test is_ready_for_processing returns False when status is error."""
        file_path = FilePath("/path/to/file.pdf")
        extension = FileExtension(".pdf")
        content = FileContent("base64data", "application/pdf", 1024)
        
        processable_file = ProcessableFile(file_path, extension, content=content)
        processable_file.mark_as_error("Some error")
        
        assert processable_file.is_ready_for_processing() is False