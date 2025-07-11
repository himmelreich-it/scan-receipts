"""Tests for FileFilteringService."""

import pytest
from unittest.mock import patch
from src.receipt_processing.domain.services.file_filtering_service import FileFilteringService
from src.receipt_processing.domain.specifications.supported_file_spec import SupportedFileExtensionSpecification
from src.receipt_processing.domain.models.file_path import FilePath
from src.receipt_processing.domain.models.file_extension import FileExtension


class TestFileFilteringService:
    """Test cases for FileFilteringService."""
    
    def test_filter_supported_files_includes_supported_extensions(self):
        """Test that supported file extensions are included in results."""
        spec = SupportedFileExtensionSpecification(['.pdf', '.jpg'])
        service = FileFilteringService(spec)
        
        file_paths = [
            FilePath("/path/to/file1.pdf"),
            FilePath("/path/to/file2.jpg"),
            FilePath("/path/to/file3.txt")  # unsupported
        ]
        
        with patch('os.path.splitext') as mock_splitext:
            mock_splitext.side_effect = [
                ("/path/to/file1", ".pdf"),
                ("/path/to/file2", ".jpg"),
                ("/path/to/file3", ".txt")
            ]
            
            result = service.filter_supported_files(file_paths)
        
        assert len(result) == 2
        assert result[0].file_path == file_paths[0]
        assert result[0].extension.extension == ".pdf"
        assert result[1].file_path == file_paths[1]
        assert result[1].extension.extension == ".jpg"
    
    def test_filter_supported_files_excludes_unsupported_extensions(self):
        """Test that unsupported file extensions are excluded from results."""
        spec = SupportedFileExtensionSpecification(['.pdf'])
        service = FileFilteringService(spec)
        
        file_paths = [
            FilePath("/path/to/file1.txt"),
            FilePath("/path/to/file2.doc")
        ]
        
        with patch('os.path.splitext') as mock_splitext:
            mock_splitext.side_effect = [
                ("/path/to/file1", ".txt"),
                ("/path/to/file2", ".doc")
            ]
            
            result = service.filter_supported_files(file_paths)
        
        assert len(result) == 0
    
    def test_filter_supported_files_handles_files_without_extensions(self):
        """Test that files without extensions are excluded."""
        spec = SupportedFileExtensionSpecification(['.pdf'])
        service = FileFilteringService(spec)
        
        file_paths = [
            FilePath("/path/to/file_without_extension")
        ]
        
        with patch('os.path.splitext') as mock_splitext:
            mock_splitext.return_value = ("/path/to/file_without_extension", "")
            
            result = service.filter_supported_files(file_paths)
        
        assert len(result) == 0
    
    def test_filter_supported_files_handles_invalid_extensions(self):
        """Test that invalid file extensions are skipped silently."""
        spec = SupportedFileExtensionSpecification(['.pdf'])
        service = FileFilteringService(spec)
        
        file_paths = [
            FilePath("/path/to/file.pdf")
        ]
        
        with patch('os.path.splitext') as mock_splitext:
            mock_splitext.return_value = ("/path/to/file", ".pdf")
            
            with patch('src.receipt_processing.domain.models.file_extension.FileExtension') as mock_ext:
                mock_ext.side_effect = ValueError("Invalid extension")
                
                result = service.filter_supported_files(file_paths)
        
        assert len(result) == 0
    
    def test_filter_supported_files_case_insensitive(self):
        """Test that filtering is case insensitive."""
        spec = SupportedFileExtensionSpecification(['.pdf'])
        service = FileFilteringService(spec)
        
        file_paths = [
            FilePath("/path/to/file.PDF")
        ]
        
        with patch('os.path.splitext') as mock_splitext:
            mock_splitext.return_value = ("/path/to/file", ".PDF")
            
            result = service.filter_supported_files(file_paths)
        
        assert len(result) == 1
        assert result[0].extension.extension == ".pdf"  # normalized to lowercase