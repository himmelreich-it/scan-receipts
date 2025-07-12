"""End-to-end integration tests for AI extraction."""

from unittest.mock import patch, Mock
from pathlib import Path
import json
from decimal import Decimal

from ai_extraction import ExtractionFacade, ImageExtractionRequest


class TestEndToEndExtraction:
    """Test complete extraction workflow."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_request = ImageExtractionRequest(
            file_path=Path("test_receipt.jpg"),
            image_data=b"\xff\xd8fake_jpeg_data",
            mime_type="image/jpeg"
        )
    
    @patch('ai_extraction.infrastructure.api.claude_client.Anthropic')
    def test_complete_successful_extraction_workflow(self, mock_anthropic_class):
        """Test: Complete workflow from image request through successful data extraction."""
        # Arrange
        with patch('ai_extraction.infrastructure.config.settings') as mock_settings:
            mock_settings.anthropic_api_key = 'test_key'
            mock_settings.model_name = 'claude-sonnet-4-20250514'
            mock_settings.max_tokens = 2000
            mock_settings.enable_thinking = True
            
            mock_response_content = Mock()
            mock_response_content.text = json.dumps({
                "amount": 45.67,
                "tax": 5.67,
                "tax_percentage": 21,
                "description": "Test Store",
                "currency": "EUR",
                "date": "15-03-2024",
                "confidence": 85
            })
            
            mock_response = Mock()
            mock_response.content = [mock_response_content]
            
            mock_anthropic = Mock()
            mock_anthropic.messages.create.return_value = mock_response
            mock_anthropic_class.return_value = mock_anthropic
            
            facade = ExtractionFacade()
            
            # Act
            result = facade.extract_from_image(self.test_request)
            
            # Assert - Verify acceptance criteria for successful extraction
            assert result.success is True
            assert result.data.amount == Decimal('45.67')
            assert result.data.tax == Decimal('5.67')
            assert result.data.description == "Test Store"
            assert result.data.currency == "EUR"
            assert result.data.date == "15-03-2024"
            assert result.data.confidence == 85
            assert result.filename == "test_receipt.jpg"
    
    @patch('ai_extraction.infrastructure.api.claude_client.Anthropic')
    def test_complete_error_handling_workflow(self, mock_anthropic_class):
        """Test: Complete workflow with API error through error categorization."""
        from anthropic import RateLimitError
        
        # Arrange
        with patch('ai_extraction.infrastructure.config.settings') as mock_settings:
            mock_settings.anthropic_api_key = 'test_key'
            mock_settings.max_retries = 1
            
            # Create mock response and body for Anthropic exceptions
            mock_response = Mock()
            mock_response.status_code = 429
            mock_body = {"error": {"message": "Rate limit exceeded"}}
            
            mock_anthropic = Mock()
            mock_anthropic.messages.create.side_effect = RateLimitError("Rate limit exceeded", response=mock_response, body=mock_body)
            mock_anthropic_class.return_value = mock_anthropic
            
            facade = ExtractionFacade()
            
            # Act
            result = facade.extract_from_image(self.test_request)
            
            # Assert - Verify acceptance criteria for error handling
            assert result.success is False
            assert result.error_data.description == "ERROR-API"
            assert result.error_data.confidence == 0
            assert result.error_data.amount == 0
            assert result.error_data.tax == 0
            assert result.error_data.currency == ""
            assert result.error_data.date == ""
            assert result.filename == "test_receipt.jpg"
    
    @patch('ai_extraction.infrastructure.api.claude_client.Anthropic')
    def test_batch_processing_workflow(self, mock_anthropic_class):
        """Test: Extract receipt data from multiple images sequentially."""
        # Arrange
        with patch('ai_extraction.infrastructure.config.settings') as mock_settings:
            mock_settings.anthropic_api_key = 'test_key'
            mock_settings.model_name = 'claude-sonnet-4-20250514'
            mock_settings.max_tokens = 2000
            mock_settings.enable_thinking = True
            
            mock_response_content = Mock()
            mock_response_content.text = json.dumps({
                "amount": 45.67,
                "tax": 5.67,
                "tax_percentage": 21,
                "description": "Test Store",
                "currency": "EUR",
                "date": "15-03-2024",
                "confidence": 85
            })
            
            mock_response = Mock()
            mock_response.content = [mock_response_content]
            
            mock_anthropic = Mock()
            mock_anthropic.messages.create.return_value = mock_response
            mock_anthropic_class.return_value = mock_anthropic
            
            requests = [
                self.test_request,
                ImageExtractionRequest(
                    file_path=Path("test_receipt2.jpg"),
                    image_data=b"\xff\xd8fake_jpeg_data2",
                    mime_type="image/jpeg"
                )
            ]
            
            facade = ExtractionFacade()
            
            # Act
            results = facade.extract_from_images(requests)
            
            # Assert
            assert len(results) == 2
            assert all(result.success for result in results)
            assert results[0].filename == "test_receipt.jpg"
            assert results[1].filename == "test_receipt2.jpg"
    
    def test_file_validation_workflow(self):
        """Test: When image file is corrupted, complete error handling workflow."""
        # Arrange
        corrupted_request = ImageExtractionRequest(
            file_path=Path("corrupted.jpg"),
            image_data=b"",  # Empty image data
            mime_type="image/jpeg"
        )
        
        facade = ExtractionFacade()
        
        # Act
        result = facade.extract_from_image(corrupted_request)
        
        # Assert
        assert result.success is False
        assert result.error_data.description == "ERROR-FILE"
        assert result.filename == "corrupted.jpg"