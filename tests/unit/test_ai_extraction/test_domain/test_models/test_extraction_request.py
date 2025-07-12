"""Tests for extraction request value objects."""

import pytest
from pathlib import Path

from ai_extraction.domain.models.extraction_request import ImageExtractionRequest


class TestImageExtractionRequest:
    """Test ImageExtractionRequest value object."""
    
    def test_valid_jpeg_request_creation(self):
        """Test: When valid JPEG image request is provided, create request successfully."""
        request = ImageExtractionRequest(
            file_path=Path("test_receipt.jpg"),
            image_data=b"fake_jpeg_data",
            mime_type="image/jpeg"
        )
        
        assert request.file_path == Path("test_receipt.jpg")
        assert request.image_data == b"fake_jpeg_data"
        assert request.mime_type == "image/jpeg"
        assert request.filename == "test_receipt.jpg"
    
    def test_valid_png_request_creation(self):
        """Test: When valid PNG image request is provided, create request successfully."""
        request = ImageExtractionRequest(
            file_path=Path("test_receipt.png"),
            image_data=b"fake_png_data",
            mime_type="image/png"
        )
        
        assert request.mime_type == "image/png"
        assert request.filename == "test_receipt.png"
    
    def test_valid_gif_request_creation(self):
        """Test: When valid GIF image request is provided, create request successfully."""
        request = ImageExtractionRequest(
            file_path=Path("test_receipt.gif"),
            image_data=b"fake_gif_data",
            mime_type="image/gif"
        )
        
        assert request.mime_type == "image/gif"
        assert request.filename == "test_receipt.gif"
    
    def test_valid_pdf_request_creation(self):
        """Test: When valid PDF request is provided, create request successfully."""
        request = ImageExtractionRequest(
            file_path=Path("test_receipt.pdf"),
            image_data=b"fake_pdf_data",
            mime_type="application/pdf"
        )
        
        assert request.mime_type == "application/pdf"
        assert request.filename == "test_receipt.pdf"
    
    def test_unsupported_mime_type(self):
        """Test: When unsupported MIME type is provided, raise validation error."""
        with pytest.raises(ValueError, match="Unsupported MIME type"):
            ImageExtractionRequest(
                file_path=Path("test_receipt.doc"),
                image_data=b"fake_doc_data",
                mime_type="application/msword"
            )
    
    def test_filename_property(self):
        """Test: When file path is provided, filename property returns correct name."""
        request = ImageExtractionRequest(
            file_path=Path("/path/to/test_receipt.jpg"),
            image_data=b"fake_data",
            mime_type="image/jpeg"
        )
        
        assert request.filename == "test_receipt.jpg"