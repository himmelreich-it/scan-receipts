"""Tests for Claude API client."""

import pytest
import json
from unittest.mock import Mock, patch
from pathlib import Path

from ai_extraction.infrastructure.api.claude_client import ClaudeApiClient
from ai_extraction.domain.models import ImageExtractionRequest
from ai_extraction.domain.exceptions import (
    ApiExtractionError, ParseExtractionError
)


class TestClaudeApiClient:
    """Test ClaudeApiClient wrapper."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with patch('ai_extraction.infrastructure.api.claude_client.settings') as mock_settings:
            mock_settings.anthropic_api_key = "test_key"
            mock_settings.model_name = "claude-sonnet-4-20250514"
            mock_settings.max_tokens = 2000
            mock_settings.enable_thinking = True
            mock_settings.max_retries = 3
            mock_settings.base_backoff_delay = 1.0
            mock_settings.max_backoff_delay = 60.0
            
            with patch('ai_extraction.infrastructure.api.claude_client.Anthropic'):
                self.client = ClaudeApiClient()
        
        self.test_request = ImageExtractionRequest(
            file_path=Path("test_receipt.jpg"),
            image_data=b"fake_jpeg_data",
            mime_type="image/jpeg"
        )
    
    @patch('ai_extraction.infrastructure.api.claude_client.Anthropic')
    @patch('ai_extraction.infrastructure.api.claude_client.settings')
    def test_successful_api_call(self, mock_settings, mock_anthropic_class):
        """Test: When Claude API returns successful response, extract receipt data successfully."""
        # Arrange
        mock_settings.anthropic_api_key = "test_key"
        mock_settings.model_name = "claude-sonnet-4-20250514"
        mock_settings.max_tokens = 2000
        mock_settings.enable_thinking = True
        
        mock_response_content = Mock()
        mock_response_content.text = json.dumps({
            "amount": 45.67,
            "tax": 5.67,
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
        
        client = ClaudeApiClient()
        
        # Act
        result = client.extract_receipt_data(self.test_request)
        
        # Assert
        assert result["amount"] == 45.67
        assert result["currency"] == "EUR"
        assert result["confidence"] == 85
        mock_anthropic.messages.create.assert_called_once()
    
    @patch('ai_extraction.infrastructure.api.claude_client.Anthropic')
    @patch('ai_extraction.infrastructure.api.claude_client.settings')
    def test_malformed_json_response(self, mock_settings, mock_anthropic_class):
        """Test: When Claude API returns malformed JSON response, raise ParseExtractionError."""
        # Arrange
        mock_settings.anthropic_api_key = "test_key"
        mock_settings.max_retries = 3
        
        mock_response_content = Mock()
        mock_response_content.text = "invalid json response"
        
        mock_response = Mock()
        mock_response.content = [mock_response_content]
        
        mock_anthropic = Mock()
        mock_anthropic.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_anthropic
        
        client = ClaudeApiClient()
        
        # Act & Assert
        with pytest.raises(ParseExtractionError, match="Malformed JSON response"):
            client.extract_receipt_data(self.test_request)
    
    @patch('ai_extraction.infrastructure.api.claude_client.Anthropic')
    @patch('ai_extraction.infrastructure.api.claude_client.settings')
    @patch('ai_extraction.infrastructure.api.claude_client.time.sleep')
    def test_retry_logic_with_rate_limit(self, mock_sleep, mock_settings, mock_anthropic_class):
        """Test: When Claude API returns rate limit error, implement retry logic with exponential backoff."""
        from anthropic import RateLimitError
        
        # Arrange
        mock_settings.anthropic_api_key = "test_key"
        mock_settings.max_retries = 3
        mock_settings.base_backoff_delay = 1.0
        mock_settings.max_backoff_delay = 60.0
        
        mock_anthropic = Mock()
        mock_anthropic.messages.create.side_effect = [
            RateLimitError("Rate limit exceeded"),
            RateLimitError("Rate limit exceeded"), 
            RateLimitError("Rate limit exceeded")
        ]
        mock_anthropic_class.return_value = mock_anthropic
        
        client = ClaudeApiClient()
        
        # Act & Assert
        with pytest.raises(ApiExtractionError, match="API call failed after retries"):
            client.extract_receipt_data(self.test_request)
        
        # Verify retry delays: 1s, 2s for exponential backoff
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(1.0)  # First retry: base_delay * 2^0
        mock_sleep.assert_any_call(2.0)  # Second retry: base_delay * 2^1
    
    @patch('ai_extraction.infrastructure.api.claude_client.Anthropic')
    @patch('ai_extraction.infrastructure.api.claude_client.settings')
    def test_authentication_error(self, mock_settings, mock_anthropic_class):
        """Test: When Claude API returns authentication error, raise ApiExtractionError."""
        from anthropic import AuthenticationError
        
        # Arrange
        mock_settings.anthropic_api_key = "test_key"
        mock_settings.max_retries = 3
        
        mock_anthropic = Mock()
        mock_anthropic.messages.create.side_effect = AuthenticationError("Authentication failed")
        mock_anthropic_class.return_value = mock_anthropic
        
        client = ClaudeApiClient()
        
        # Act & Assert
        with pytest.raises(ApiExtractionError, match="Authentication failed"):
            client.extract_receipt_data(self.test_request)
    
    @patch('ai_extraction.infrastructure.api.claude_client.base64.b64encode')
    def test_image_encoding(self, mock_b64encode):
        """Test: When processing image, encode image data as base64 for API submission."""
        # Arrange
        mock_b64encode.return_value = b"encoded_image_data"
        
        with patch.object(self.client, '_make_api_call') as mock_make_call:
            mock_make_call.return_value = {"test": "data"}
            
            # Act
            self.client.extract_receipt_data(self.test_request)
            
            # Assert
            mock_b64encode.assert_called_once_with(b"fake_jpeg_data")
    
    def test_extraction_prompt_structure(self):
        """Test: When building extraction prompt, request specific JSON schema with exact field names."""
        # Act
        prompt = self.client._build_extraction_prompt()
        
        # Assert
        assert "amount" in prompt
        assert "tax" in prompt
        assert "description" in prompt
        assert "currency" in prompt
        assert "date" in prompt
        assert "confidence" in prompt
        assert "dd-MM-YYYY" in prompt
        assert "0-100" in prompt
    
    @patch('ai_extraction.infrastructure.api.claude_client.Anthropic')
    @patch('ai_extraction.infrastructure.api.claude_client.settings')
    def test_markdown_json_response_parsing(self, mock_settings, mock_anthropic_class):
        """Test: When Claude API returns JSON wrapped in markdown code blocks, extract JSON successfully."""
        # Arrange
        mock_settings.anthropic_api_key = "test_key"
        mock_settings.model_name = "claude-sonnet-4-20250514"
        mock_settings.max_tokens = 2000
        mock_settings.enable_thinking = True
        
        json_data = {
            "amount": 8.50,
            "tax": 0.70,
            "description": "Coffeecompany De Dijk Amsterdam",
            "currency": "EUR",
            "date": "16-03-2025",
            "confidence": 95
        }
        
        mock_response_content = Mock()
        mock_response_content.text = f"```json\n{json.dumps(json_data)}\n```"
        
        mock_response = Mock()
        mock_response.content = [mock_response_content]
        
        mock_anthropic = Mock()
        mock_anthropic.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_anthropic
        
        client = ClaudeApiClient()
        
        # Act
        result = client.extract_receipt_data(self.test_request)
        
        # Assert
        assert result["amount"] == 8.50
        assert result["tax"] == 0.70
        assert result["description"] == "Coffeecompany De Dijk Amsterdam"
        assert result["currency"] == "EUR"
        assert result["date"] == "16-03-2025"
        assert result["confidence"] == 95