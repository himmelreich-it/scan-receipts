"""Tests for extraction service."""

from unittest.mock import Mock, patch
from decimal import Decimal
from pathlib import Path

from ai_extraction.domain.services.extraction_service import ExtractionService
from ai_extraction.domain.models import ImageExtractionRequest
from ai_extraction.domain.exceptions import (
    ApiExtractionError
)


class TestExtractionService:
    """Test ExtractionService domain service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_api_client = Mock()
        self.service = ExtractionService(self.mock_api_client)
        self.test_request = ImageExtractionRequest(
            file_path=Path("test_receipt.jpg"),
            image_data=b"\xff\xd8fake_jpeg_data",  # Valid JPEG header
            mime_type="image/jpeg"
        )
    
    def test_successful_extraction(self):
        """Test: When API returns valid response, extract receipt data successfully."""
        # Arrange
        api_response = {
            "amount": 45.67,
            "tax": 5.67,
            "description": "Test Store",
            "currency": "EUR",
            "date": "15-03-2024",
            "confidence": 85
        }
        self.mock_api_client.extract_receipt_data.return_value = api_response
        
        # Act
        with patch('ai_extraction.domain.services.extraction_service.logger') as mock_logger:
            result = self.service.extract_receipt_data(self.test_request)
        
        # Assert
        assert result.success is True
        assert result.data.amount == Decimal('45.67')
        assert result.data.currency == "EUR"
        assert result.data.confidence == 85
        assert result.filename == "test_receipt.jpg"
        mock_logger.info.assert_called_once()
    
    def test_empty_image_data_error(self):
        """Test: When image file is empty, create error entry with description 'ERROR-FILE'."""
        # Arrange
        empty_request = ImageExtractionRequest(
            file_path=Path("empty_receipt.jpg"),
            image_data=b"",
            mime_type="image/jpeg"
        )
        
        # Act
        with patch('ai_extraction.domain.services.extraction_service.logger') as mock_logger:
            result = self.service.extract_receipt_data(empty_request)
        
        # Assert
        assert result.success is False
        assert result.error_data.description == "ERROR-FILE"
        assert result.error_data.confidence == 0
        assert result.filename == "empty_receipt.jpg"
        mock_logger.error.assert_called_once()
    
    def test_corrupted_jpeg_file_error(self):
        """Test: When image file is corrupted, create error entry with description 'ERROR-FILE'."""
        # Arrange
        corrupted_request = ImageExtractionRequest(
            file_path=Path("corrupted_receipt.jpg"),
            image_data=b"not_jpeg_data",  # Invalid JPEG header
            mime_type="image/jpeg"
        )
        
        # Act
        with patch('ai_extraction.domain.services.extraction_service.logger') as mock_logger:
            result = self.service.extract_receipt_data(corrupted_request)
        
        # Assert
        assert result.success is False
        assert result.error_data.description == "ERROR-FILE"
        mock_logger.error.assert_called_once_with("Corrupted file: corrupted_receipt.jpg")
    
    def test_api_error_handling(self):
        """Test: When Claude API returns rate limit error, create error entry with description 'ERROR-API'."""
        # Arrange
        self.mock_api_client.extract_receipt_data.side_effect = ApiExtractionError(
            "Rate limit exceeded", "test_receipt.jpg"
        )
        
        # Act
        with patch('ai_extraction.domain.services.extraction_service.logger') as mock_logger:
            result = self.service.extract_receipt_data(self.test_request)
        
        # Assert
        assert result.success is False
        assert result.error_data.description == "ERROR-API"
        assert result.error_data.confidence == 0
        mock_logger.error.assert_called_once_with("Rate limit exceeded for file test_receipt.jpg")
    
    def test_missing_required_fields_error(self):
        """Test: When Claude API response missing required fields, create error entry with description 'ERROR-PARSE'."""
        # Arrange
        incomplete_response = {
            "amount": 45.67,
            "description": "Test Store",
            # Missing tax, currency, date, confidence
        }
        self.mock_api_client.extract_receipt_data.return_value = incomplete_response
        
        # Act
        with patch('ai_extraction.domain.services.extraction_service.logger') as mock_logger:
            result = self.service.extract_receipt_data(self.test_request)
        
        # Assert
        assert result.success is False
        assert result.error_data.description == "ERROR-PARSE"
        mock_logger.error.assert_called_once_with("Incomplete extraction data for file test_receipt.jpg")
    
    def test_unexpected_error_handling(self):
        """Test: When unexpected error occurs, create error entry with description 'ERROR-UNKNOWN'."""
        # Arrange
        self.mock_api_client.extract_receipt_data.side_effect = RuntimeError("Unexpected error")
        
        # Act
        with patch('ai_extraction.domain.services.extraction_service.logger') as mock_logger:
            result = self.service.extract_receipt_data(self.test_request)
        
        # Assert
        assert result.success is False
        assert result.error_data.description == "ERROR-UNKNOWN"
        mock_logger.error.assert_called_with("Unexpected error for file test_receipt.jpg: Unexpected error")
    
    def test_error_result_structure_consistency(self):
        """Test: When error entry is created, populate amount=0, tax=0, currency='', date='' for consistency."""
        # Arrange
        self.mock_api_client.extract_receipt_data.side_effect = ApiExtractionError(
            "API error", "test_receipt.jpg"
        )
        
        # Act
        result = self.service.extract_receipt_data(self.test_request)
        
        # Assert
        assert result.error_data.amount == Decimal('0')
        assert result.error_data.tax == Decimal('0')
        assert result.error_data.currency == ""
        assert result.error_data.date == ""
        assert result.error_data.confidence == 0