"""Tests for SupportedFileExtensionSpecification."""

import pytest
from src.receipt_processing.domain.specifications.supported_file_spec import SupportedFileExtensionSpecification
from src.receipt_processing.domain.models.file_extension import FileExtension


class TestSupportedFileExtensionSpecification:
    """Test cases for SupportedFileExtensionSpecification."""
    
    def test_is_satisfied_by_supported_extension(self):
        """Test that supported extensions satisfy the specification."""
        spec = SupportedFileExtensionSpecification(['.pdf', '.jpg'])
        extension = FileExtension('.pdf')
        
        assert spec.is_satisfied_by(extension) is True
    
    def test_is_satisfied_by_unsupported_extension(self):
        """Test that unsupported extensions do not satisfy the specification."""
        spec = SupportedFileExtensionSpecification(['.pdf', '.jpg'])
        extension = FileExtension('.txt')
        
        assert spec.is_satisfied_by(extension) is False
    
    def test_is_satisfied_by_case_insensitive(self):
        """Test that specification is case insensitive."""
        spec = SupportedFileExtensionSpecification(['.pdf'])
        extension = FileExtension('.PDF')
        
        assert spec.is_satisfied_by(extension) is True
    
    def test_multiple_supported_extensions(self):
        """Test specification with multiple supported extensions."""
        spec = SupportedFileExtensionSpecification(['.pdf', '.jpg', '.jpeg', '.png'])
        
        assert spec.is_satisfied_by(FileExtension('.pdf')) is True
        assert spec.is_satisfied_by(FileExtension('.jpg')) is True
        assert spec.is_satisfied_by(FileExtension('.jpeg')) is True
        assert spec.is_satisfied_by(FileExtension('.png')) is True
        assert spec.is_satisfied_by(FileExtension('.txt')) is False
    
    def test_empty_supported_extensions(self):
        """Test specification with no supported extensions."""
        spec = SupportedFileExtensionSpecification([])
        extension = FileExtension('.pdf')
        
        assert spec.is_satisfied_by(extension) is False