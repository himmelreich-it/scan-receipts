"""Unit tests for CSV adapter append functionality."""

from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from adapters.secondary.csv_adapter import CSVAdapter


class TestCSVAdapterAppend:
    """Test cases for CSV adapter append functionality."""

    def test_append_receipt_data_new_file(self):
        """Test appending data to a new CSV file creates headers and data."""
        adapter = CSVAdapter()
        csv_path = Path("/test/receipts.csv")
        receipt_data = {
            "amount": "25.99",
            "tax": "2.08",
            "tax_percentage": "8.25",
            "description": "Coffee Shop",
            "currency": "USD",
            "date": "2024-03-15",
            "confidence": "85"
        }
        file_hash = "abc123"
        filename = "receipt.jpg"

        mock_file = mock_open()
        with patch("pathlib.Path.exists", return_value=False):
            with patch("pathlib.Path.mkdir"):
                with patch("builtins.open", mock_file):
                    adapter.append_receipt_data(csv_path, receipt_data, file_hash, filename)

        # Verify file was opened for append
        mock_file.assert_called_once_with(csv_path, "a", newline="", encoding="utf-8")

        # Get the written content
        written_content = "".join(call.args[0] for call in mock_file().write.call_args_list)

        # Check headers and data were written
        assert "Amount,Tax,TaxPercentage,Description,Currency,Date,Confidence,Hash,DoneFilename" in written_content
        assert "25.99,2.08,8.25,Coffee Shop,USD,2024-03-15,85,abc123,receipt.jpg" in written_content

    def test_append_receipt_data_existing_file(self):
        """Test appending data to existing CSV file doesn't write headers."""
        adapter = CSVAdapter()
        csv_path = Path("/test/receipts.csv")
        receipt_data = {
            "amount": "45.67",
            "tax": "3.65",
            "tax_percentage": "8.0",
            "description": "Restaurant",
            "currency": "USD",
            "date": "2024-03-16",
            "confidence": "90"
        }
        file_hash = "def456"
        filename = "receipt2.pdf"

        mock_file = mock_open()
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.mkdir"):
                with patch("builtins.open", mock_file):
                    adapter.append_receipt_data(csv_path, receipt_data, file_hash, filename)

        # Get the written content
        written_content = "".join(call.args[0] for call in mock_file().write.call_args_list)

        # Check only data was written, no headers
        assert "Amount,Tax,TaxPercentage" not in written_content
        assert "45.67,3.65,8.0,Restaurant,USD,2024-03-16,90,def456,receipt2.pdf" in written_content

    def test_append_receipt_data_with_missing_optional_fields(self):
        """Test appending data with missing optional fields."""
        adapter = CSVAdapter()
        csv_path = Path("/test/receipts.csv")
        receipt_data = {
            "amount": "15.00",
            "description": "Store",
            "currency": "EUR",
            "date": "2024-03-17",
            "confidence": "75"
            # Missing tax and tax_percentage
        }
        file_hash = "ghi789"
        filename = "receipt3.png"

        mock_file = mock_open()
        with patch("pathlib.Path.exists", return_value=False):
            with patch("pathlib.Path.mkdir"):
                with patch("builtins.open", mock_file):
                    adapter.append_receipt_data(csv_path, receipt_data, file_hash, filename)

        # Get the written content
        written_content = "".join(call.args[0] for call in mock_file().write.call_args_list)

        # Check empty values for missing optional fields
        assert "15.00,,,Store,EUR,2024-03-17,75,ghi789,receipt3.png" in written_content

    def test_append_receipt_data_creates_parent_directory(self):
        """Test appending data creates parent directory if it doesn't exist."""
        adapter = CSVAdapter()
        csv_path = Path("/test/subdir/receipts.csv")
        receipt_data = {
            "amount": "10.50",
            "currency": "USD",
            "date": "2024-03-18",
            "confidence": "95",
            "description": "Test"
        }

        mock_file = mock_open()
        with patch("pathlib.Path.exists", return_value=False):
            with patch("pathlib.Path.mkdir") as mock_mkdir:
                with patch("builtins.open", mock_file):
                    adapter.append_receipt_data(csv_path, receipt_data, "hash", "file.jpg")

        # Verify parent directory creation was called
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_append_receipt_data_handles_write_error(self):
        """Test appending data handles file write errors gracefully."""
        adapter = CSVAdapter()
        csv_path = Path("/test/receipts.csv")
        receipt_data = {
            "amount": "20.00",
            "currency": "USD",
            "date": "2024-03-19",
            "confidence": "80",
            "description": "Test"
        }

        with patch("pathlib.Path.exists", return_value=False):
            with patch("pathlib.Path.mkdir"):
                with patch("builtins.open", side_effect=IOError("Write failed")):
                    with pytest.raises(ValueError, match="Failed to write to CSV"):
                        adapter.append_receipt_data(csv_path, receipt_data, "hash", "file.jpg")

    def test_append_receipt_data_handles_special_characters(self):
        """Test appending data handles special characters in fields."""
        adapter = CSVAdapter()
        csv_path = Path("/test/receipts.csv")
        receipt_data = {
            "amount": "33.50",
            "description": 'Café "Bistro", Main St.',  # Contains quotes and comma
            "currency": "USD",
            "date": "2024-03-20",
            "confidence": "88"
        }
        file_hash = "special123"
        filename = "café_receipt.jpg"

        mock_file = mock_open()
        with patch("pathlib.Path.exists", return_value=False):
            with patch("pathlib.Path.mkdir"):
                with patch("builtins.open", mock_file):
                    adapter.append_receipt_data(csv_path, receipt_data, file_hash, filename)

        # Get the written content
        written_content = "".join(call.args[0] for call in mock_file().write.call_args_list)

        # Check special characters are handled properly (CSV should quote fields with special chars)
        assert "café_receipt.jpg" in written_content
        assert file_hash in written_content