"""Unit tests for CsvService class."""

import csv
import os
import tempfile
import pytest
from unittest.mock import patch, mock_open
from src.csv_output.csv_service import CsvService
from src.csv_output.config import CSV_HEADERS, ERROR_API, ERROR_FILE


class TestCsvService:
    """Test cases for CsvService class."""
    
    def setup_method(self):
        """Set up test environment for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_csv_path = os.path.join(self.temp_dir, "test_receipts.csv")
        self.csv_service = CsvService(self.test_csv_path)
    
    def teardown_method(self):
        """Clean up after each test."""
        if os.path.exists(self.test_csv_path):
            os.remove(self.test_csv_path)
        os.rmdir(self.temp_dir)
    
    def test_init_sets_file_path(self):
        """Test that initialization sets the correct file path."""
        service = CsvService("custom_path.csv")
        assert service.csv_file_path == "custom_path.csv"
    
    def test_init_uses_default_path(self):
        """Test that initialization uses default path when none provided."""
        service = CsvService()
        assert service.csv_file_path == "receipts.csv"
    
    def test_ensure_csv_exists_creates_file_with_headers(self):
        """Test that ensure_csv_exists creates file with correct headers."""
        self.csv_service.ensure_csv_exists()
        
        assert os.path.exists(self.test_csv_path)
        
        with open(self.test_csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)
            assert headers == CSV_HEADERS
    
    @patch('src.csv_output.csv_service.logger')
    def test_ensure_csv_exists_logs_creation(self, mock_logger):
        """Test that CSV creation is logged."""
        self.csv_service.ensure_csv_exists()
        mock_logger.info.assert_called_with("Created receipts.csv with headers")
    
    def test_ensure_csv_exists_permission_error_exits(self):
        """Test that permission error causes system exit."""
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            with pytest.raises(SystemExit) as exc_info:
                self.csv_service.ensure_csv_exists()
            assert exc_info.value.code == 1
    
    def test_get_next_id_returns_1_for_new_file(self):
        """Test that get_next_id returns 1 when file doesn't exist."""
        assert self.csv_service.get_next_id() == 1
    
    def test_get_next_id_returns_1_for_empty_file(self):
        """Test that get_next_id returns 1 for file with only headers."""
        self.csv_service.ensure_csv_exists()
        assert self.csv_service.get_next_id() == 1
    
    def test_get_next_id_increments_correctly(self):
        """Test that get_next_id increments correctly with existing records."""
        # Create file with headers and one record
        self.csv_service.ensure_csv_exists()
        with open(self.test_csv_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["1", "15.50", "2.50", "16.00", "Test", "EUR", "15-03-2024", "95", "hash123", "done.pdf"])
        
        assert self.csv_service.get_next_id() == 2
    
    def test_get_next_id_handles_multiple_records(self):
        """Test that get_next_id works with multiple existing records."""
        # Create file with headers and multiple records
        self.csv_service.ensure_csv_exists()
        with open(self.test_csv_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["1", "15.50", "2.50", "16.00", "Test1", "EUR", "15-03-2024", "95", "hash1", "done1.pdf"])
            writer.writerow(["2", "25.00", "4.00", "16.00", "Test2", "EUR", "16-03-2024", "90", "hash2", "done2.pdf"])
            writer.writerow(["3", "35.75", "5.72", "16.00", "Test3", "EUR", "17-03-2024", "85", "hash3", "done3.pdf"])
        
        assert self.csv_service.get_next_id() == 4
    
    def test_append_record_creates_proper_record(self):
        """Test that append_record creates a properly formatted record."""
        self.csv_service.ensure_csv_exists()
        
        record_id = self.csv_service.append_record(
            amount=15.50,
            tax=2.50,
            tax_percentage=16.13,
            description="Coffee Shop ABC",
            currency="EUR",
            date="15-03-2024",
            confidence=95,
            hash_value="abc123def456",
            done_filename="1-20240315-142530123456-receipt.pdf"
        )
        
        assert record_id == 1
        
        # Verify the record was written correctly
        with open(self.test_csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip headers
            record = next(reader)
            
            assert record[0] == "1"  # ID
            assert record[1] == "15.50"  # Amount
            assert record[2] == "2.50"  # Tax
            assert record[3] == "16.13"  # TaxPercentage
            assert record[4] == "Coffee Shop ABC"  # Description
            assert record[5] == "EUR"  # Currency
            assert record[6] == "15-03-2024"  # Date
            assert record[7] == "95"  # Confidence
            assert record[8] == "abc123def456"  # Hash
            assert record[9] == "1-20240315-142530123456-receipt.pdf"  # DoneFilename
    
    def test_append_record_handles_description_with_commas(self):
        """Test that descriptions with commas are properly handled."""
        self.csv_service.ensure_csv_exists()
        
        self.csv_service.append_record(
            amount=15.50,
            tax=2.50,
            tax_percentage=16.13,
            description="Coffee, Tea & More Shop",
            currency="EUR",
            date="15-03-2024",
            confidence=95,
            hash_value="abc123",
            done_filename="test.pdf"
        )
        
        # Verify the record was written correctly
        with open(self.test_csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip headers
            record = next(reader)
            assert record[4] == "Coffee, Tea & More Shop"
    
    def test_append_error_record_creates_error_entry(self):
        """Test that append_error_record creates proper error entry."""
        self.csv_service.ensure_csv_exists()
        
        record_id = self.csv_service.append_error_record(
            error_type=ERROR_FILE,
            hash_value="def789ghi012",
            done_filename="2-20240315-142645789012-corrupted.jpg"
        )
        
        assert record_id == 1
        
        # Verify the error record was written correctly
        with open(self.test_csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip headers
            record = next(reader)
            
            assert record[0] == "1"  # ID
            assert record[1] == "0.00"  # Amount
            assert record[2] == "0.00"  # Tax
            assert record[3] == "0.00"  # TaxPercentage
            assert record[4] == ERROR_FILE  # Description
            assert record[5] == ""  # Currency
            assert record[6] == ""  # Date
            assert record[7] == "0"  # Confidence
            assert record[8] == "def789ghi012"  # Hash
            assert record[9] == "2-20240315-142645789012-corrupted.jpg"  # DoneFilename
    
    @patch('src.csv_output.csv_service.logger')
    def test_append_error_record_validates_error_type(self, mock_logger):
        """Test that invalid error types are handled with warning."""
        self.csv_service.ensure_csv_exists()
        
        self.csv_service.append_error_record(
            error_type="INVALID-ERROR",
            hash_value="test_hash",
            done_filename="test.pdf"
        )
        
        mock_logger.warning.assert_called_with("Invalid error type INVALID-ERROR, using ERROR-UNKNOWN")
    
    def test_format_currency_field_formats_correctly(self):
        """Test that currency fields are formatted to 2 decimal places."""
        assert self.csv_service._format_currency_field(15.5) == "15.50"
        assert self.csv_service._format_currency_field(15.123) == "15.12"
        assert self.csv_service._format_currency_field(15.999) == "16.00"
        assert self.csv_service._format_currency_field(0) == "0.00"
    
    def test_validate_headers_returns_true_for_correct_headers(self):
        """Test that header validation returns True for correct headers."""
        assert self.csv_service._validate_headers(CSV_HEADERS) is True
    
    def test_validate_headers_returns_false_for_incorrect_headers(self):
        """Test that header validation returns False for incorrect headers."""
        wrong_headers = ["ID", "Wrong", "Headers"]
        assert self.csv_service._validate_headers(wrong_headers) is False
    
    def test_extract_original_filename_works_correctly(self):
        """Test that original filename extraction works correctly."""
        done_filename = "1-20240315-142530123456-receipt.pdf"
        original = self.csv_service._extract_original_filename(done_filename)
        assert original == "receipt.pdf"
    
    def test_extract_original_filename_handles_complex_names(self):
        """Test that original filename extraction handles complex names."""
        done_filename = "5-20240315-142530123456-my-receipt-with-dashes.pdf"
        original = self.csv_service._extract_original_filename(done_filename)
        assert original == "my-receipt-with-dashes.pdf"
    
    def test_extract_original_filename_handles_invalid_format(self):
        """Test that original filename extraction handles invalid format gracefully."""
        done_filename = "invalid-format"
        original = self.csv_service._extract_original_filename(done_filename)
        assert original == "invalid-format"
    
    @patch('src.csv_output.csv_service.logger')
    def test_append_record_logs_success(self, mock_logger):
        """Test that successful record appending is logged."""
        self.csv_service.ensure_csv_exists()
        
        self.csv_service.append_record(
            amount=15.50,
            tax=2.50,
            tax_percentage=16.13,
            description="Test",
            currency="EUR",
            date="15-03-2024",
            confidence=95,
            hash_value="test_hash",
            done_filename="1-20240315-142530123456-receipt.pdf"
        )
        
        mock_logger.info.assert_called_with("Added record ID 1 for file receipt.pdf")
    
    @patch('src.csv_output.csv_service.logger')
    def test_append_error_record_logs_success(self, mock_logger):
        """Test that successful error record appending is logged."""
        self.csv_service.ensure_csv_exists()
        
        self.csv_service.append_error_record(
            error_type=ERROR_API,
            hash_value="test_hash",
            done_filename="1-20240315-142530123456-corrupted.jpg"
        )
        
        mock_logger.info.assert_called_with("Added error record ID 1 for file corrupted.jpg: ERROR-API")
    
    @patch('src.csv_output.csv_service.logger')
    def test_append_record_handles_write_failure(self, mock_logger):
        """Test that write failures are logged but processing continues."""
        # Create a CSV file first so get_next_id works
        self.csv_service.ensure_csv_exists()
        
        # Now mock open to fail on the append operation
        with patch('builtins.open', side_effect=Exception("Write failed")):
            record_id = self.csv_service.append_record(
                amount=15.50,
                tax=2.50,
                tax_percentage=16.13,
                description="Test",
                currency="EUR",
                date="15-03-2024",
                confidence=95,
                hash_value="test_hash",
                done_filename="test.pdf"
            )
        
        assert record_id == 1  # Should still return the ID
        mock_logger.error.assert_called_with("Failed to write record: Write failed")