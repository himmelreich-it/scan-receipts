"""Unit tests for Anthropic adapter."""

import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

import pytest

from adapters.secondary.anthropic_adapter import AnthropicAdapter


class TestAnthropicAdapter:
    """Test cases for AnthropicAdapter."""

    def test_init_with_api_key(self):
        """Test adapter initialization with API key."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("adapters.secondary.anthropic_adapter.anthropic.Anthropic") as mock_anthropic:
                AnthropicAdapter()
                mock_anthropic.assert_called_once_with(api_key="test-key")

    def test_init_without_api_key(self):
        """Test adapter initialization fails without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY environment variable is required"):
                AnthropicAdapter()

    def test_extract_receipt_data_file_not_found(self):
        """Test extraction fails when file doesn't exist."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("adapters.secondary.anthropic_adapter.anthropic.Anthropic"):
                adapter = AnthropicAdapter()

                with pytest.raises(FileNotFoundError, match="Receipt file not found"):
                    adapter.extract_receipt_data("/nonexistent/file.jpg")

    def test_extract_receipt_data_unsupported_file_type(self):
        """Test extraction fails with unsupported file type."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("adapters.secondary.anthropic_adapter.anthropic.Anthropic"):
                adapter = AnthropicAdapter()

                with patch("pathlib.Path.exists", return_value=True):
                    with pytest.raises(ValueError, match="Unsupported file type: .txt"):
                        adapter.extract_receipt_data("/test/file.txt")

    def test_extract_from_image_success(self):
        """Test successful extraction from image file."""
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = json.dumps({
            "amount": "25.99",
            "tax": "2.08",
            "tax_percentage": "8.25",
            "description": "Coffee Shop",
            "currency": "USD",
            "date": "2024-03-15",
            "confidence": "85"
        })

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("adapters.secondary.anthropic_adapter.anthropic.Anthropic") as mock_anthropic:
                mock_client = Mock()
                mock_anthropic.return_value = mock_client
                mock_client.messages.create.return_value = mock_response

                adapter = AnthropicAdapter()

                with patch("pathlib.Path.exists", return_value=True):
                    with patch("pathlib.Path.suffix", new_callable=lambda: property(lambda self: ".jpg")):
                        with patch("builtins.open", mock_open(read_data=b"fake_image_data")):
                            with patch("base64.b64encode", return_value=b"encoded_data"):
                                result = adapter.extract_receipt_data("/test/receipt.jpg")

                assert result["amount"] == "25.99"
                assert result["currency"] == "USD"
                assert result["description"] == "Coffee Shop"
                assert result["confidence"] == "85"

    def test_extract_from_pdf_success(self):
        """Test successful extraction from PDF file."""
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = json.dumps({
            "amount": "45.67",
            "tax": "3.65",
            "tax_percentage": "8.0",
            "description": "Restaurant",
            "currency": "USD",
            "date": "2024-03-16",
            "confidence": "90"
        })

        mock_image = Mock()
        mock_buffer = Mock()

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("adapters.secondary.anthropic_adapter.anthropic.Anthropic") as mock_anthropic:
                mock_client = Mock()
                mock_anthropic.return_value = mock_client
                mock_client.messages.create.return_value = mock_response

                adapter = AnthropicAdapter()

                with patch("pathlib.Path.exists", return_value=True):
                    with patch("pathlib.Path.suffix", new_callable=lambda: property(lambda self: ".pdf")):
                        with patch("pdf2image.convert_from_path", return_value=[mock_image]):
                            with patch("io.BytesIO", return_value=mock_buffer):
                                with patch("base64.b64encode", return_value=b"encoded_data"):
                                    mock_buffer.getvalue.return_value = b"image_data"

                                    result = adapter.extract_receipt_data("/test/receipt.pdf")

                assert result["amount"] == "45.67"
                assert result["currency"] == "USD"
                assert result["description"] == "Restaurant"

    def test_extract_from_pdf_no_images(self):
        """Test PDF extraction fails when no images found."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("adapters.secondary.anthropic_adapter.anthropic.Anthropic"):
                adapter = AnthropicAdapter()

                with patch("pathlib.Path.exists", return_value=True):
                    with patch("pathlib.Path.suffix", new_callable=lambda: property(lambda self: ".pdf")):
                        with patch("pdf2image.convert_from_path", return_value=[]):
                            with pytest.raises(ValueError, match="No pages found in PDF"):
                                adapter.extract_receipt_data("/test/receipt.pdf")

    def test_validate_extracted_data_missing_required_fields(self):
        """Test validation fails when required fields are missing."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("adapters.secondary.anthropic_adapter.anthropic.Anthropic"):
                adapter = AnthropicAdapter()

                data = {"amount": "25.99"}  # Missing required fields
                file_path = Path("/test/receipt.jpg")

                with pytest.raises(ValueError, match="Missing required fields"):
                    adapter._validate_extracted_data(data, file_path)  # type: ignore

    def test_validate_extracted_data_empty_required_fields(self):
        """Test validation fails when required fields are empty."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("adapters.secondary.anthropic_adapter.anthropic.Anthropic"):
                adapter = AnthropicAdapter()

                data = {
                    "amount": "",  # Empty required field
                    "currency": "USD",
                    "date": "2024-03-15",
                    "confidence": "85"
                }
                file_path = Path("/test/receipt.jpg")

                with pytest.raises(ValueError, match="Amount field cannot be empty"):
                    adapter._validate_extracted_data(data, file_path)  # type: ignore

    def test_validate_extracted_data_uses_filename_fallback(self):
        """Test validation uses filename as fallback for empty description."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("adapters.secondary.anthropic_adapter.anthropic.Anthropic"):
                adapter = AnthropicAdapter()

                data = {
                    "amount": "25.99",
                    "currency": "USD",
                    "date": "2024-03-15",
                    "confidence": "85",
                    "description": ""  # Empty description
                }
                file_path = Path("/test/coffee_receipt.jpg")

                result = adapter._validate_extracted_data(data, file_path)  # type: ignore

                assert result["description"] == "coffee_receipt"

    def test_parse_response_invalid_json(self):
        """Test parsing fails with invalid JSON response."""
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "Not a JSON response"

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("adapters.secondary.anthropic_adapter.anthropic.Anthropic"):
                adapter = AnthropicAdapter()

                file_path = Path("/test/receipt.jpg")

                with pytest.raises(ValueError, match="No valid JSON found in response"):
                    adapter._parse_response(mock_response, file_path)  # type: ignore

    def test_parse_response_json_in_text(self):
        """Test parsing extracts JSON from mixed text response."""
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = 'Here is the extracted data: {"amount": "25.99", "currency": "USD", "date": "2024-03-15", "confidence": "85", "description": "Test"}'

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("adapters.secondary.anthropic_adapter.anthropic.Anthropic"):
                adapter = AnthropicAdapter()

                file_path = Path("/test/receipt.jpg")

                result = adapter._parse_response(mock_response, file_path)  # type: ignore

                assert result["amount"] == "25.99"
                assert result["currency"] == "USD"