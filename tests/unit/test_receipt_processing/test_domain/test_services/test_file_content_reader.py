"""Tests for FileContentReader."""

import pytest
from unittest.mock import patch, mock_open
from src.receipt_processing.domain.services.file_content_reader import FileContentReader
from src.receipt_processing.domain.models.processable_file import ProcessableFile
from src.receipt_processing.domain.models.file_path import FilePath
from src.receipt_processing.domain.models.file_extension import FileExtension


class TestFileContentReader:
    """Test cases for FileContentReader."""
    
    def test_read_file_content_success(self):
        """Test successful file content reading."""
        reader = FileContentReader()
        file_path = FilePath("/path/to/file.pdf")
        extension = FileExtension(".pdf")
        processable_file = ProcessableFile(file_path, extension)
        
        file_data = b"test file content"
        
        with patch('builtins.open', mock_open(read_data=file_data)):
            with patch('base64.b64encode') as mock_b64encode:
                mock_b64encode.return_value = b"dGVzdCBmaWxlIGNvbnRlbnQ="
                
                reader.read_file_content(processable_file)
        
        assert processable_file.content is not None
        assert processable_file.content.data == "dGVzdCBmaWxlIGNvbnRlbnQ="
        assert processable_file.content.mime_type == "application/pdf"
        assert processable_file.content.size_bytes == len(file_data)
        assert processable_file.processing_status == "pending"
    
    def test_read_file_content_file_not_found(self):
        """Test handling of file not found error."""
        reader = FileContentReader()
        file_path = FilePath("/path/to/nonexistent.pdf")
        extension = FileExtension(".pdf")
        processable_file = ProcessableFile(file_path, extension)
        
        with patch('builtins.open', side_effect=FileNotFoundError()):
            reader.read_file_content(processable_file)
        
        assert processable_file.content is None
        assert processable_file.processing_status == "error"
        assert "File no longer accessible" in processable_file.error_message
    
    def test_read_file_content_permission_denied(self):
        """Test handling of permission denied error."""
        reader = FileContentReader()
        file_path = FilePath("/path/to/file.pdf")
        extension = FileExtension(".pdf")
        processable_file = ProcessableFile(file_path, extension)
        
        with patch('builtins.open', side_effect=PermissionError()):
            reader.read_file_content(processable_file)
        
        assert processable_file.content is None
        assert processable_file.processing_status == "error"
        assert "Permission denied" in processable_file.error_message
    
    def test_read_file_content_io_error(self):
        """Test handling of IO error."""
        reader = FileContentReader()
        file_path = FilePath("/path/to/file.pdf")
        extension = FileExtension(".pdf")
        processable_file = ProcessableFile(file_path, extension)
        
        with patch('builtins.open', side_effect=IOError()):
            reader.read_file_content(processable_file)
        
        assert processable_file.content is None
        assert processable_file.processing_status == "error"
        assert "Failed to read file" in processable_file.error_message
    
    def test_read_file_content_memory_error(self):
        """Test handling of memory error."""
        reader = FileContentReader()
        file_path = FilePath("/path/to/file.pdf")
        extension = FileExtension(".pdf")
        processable_file = ProcessableFile(file_path, extension)
        
        with patch('builtins.open', side_effect=MemoryError()):
            reader.read_file_content(processable_file)
        
        assert processable_file.content is None
        assert processable_file.processing_status == "error"
        assert "File too large" in processable_file.error_message
    
    def test_read_file_content_unexpected_error(self):
        """Test handling of unexpected error."""
        reader = FileContentReader()
        file_path = FilePath("/path/to/file.pdf")
        extension = FileExtension(".pdf")
        processable_file = ProcessableFile(file_path, extension)
        
        with patch('builtins.open', side_effect=Exception("Unexpected error")):
            reader.read_file_content(processable_file)
        
        assert processable_file.content is None
        assert processable_file.processing_status == "error"
        assert "Unexpected error" in processable_file.error_message
    
    def test_determine_mime_type_pdf(self):
        """Test MIME type determination for PDF files."""
        reader = FileContentReader()
        extension = FileExtension(".pdf")
        
        mime_type = reader._determine_mime_type(extension)
        
        assert mime_type == "application/pdf"
    
    def test_determine_mime_type_jpg(self):
        """Test MIME type determination for JPG files."""
        reader = FileContentReader()
        extension = FileExtension(".jpg")
        
        mime_type = reader._determine_mime_type(extension)
        
        assert mime_type == "image/jpeg"
    
    def test_determine_mime_type_jpeg(self):
        """Test MIME type determination for JPEG files."""
        reader = FileContentReader()
        extension = FileExtension(".jpeg")
        
        mime_type = reader._determine_mime_type(extension)
        
        assert mime_type == "image/jpeg"
    
    def test_determine_mime_type_png(self):
        """Test MIME type determination for PNG files."""
        reader = FileContentReader()
        extension = FileExtension(".png")
        
        mime_type = reader._determine_mime_type(extension)
        
        assert mime_type == "image/png"
    
    def test_determine_mime_type_unknown(self):
        """Test MIME type determination for unknown extensions."""
        reader = FileContentReader()
        extension = FileExtension(".unknown")
        
        mime_type = reader._determine_mime_type(extension)
        
        assert mime_type == "application/octet-stream"