"""Integration tests for CSV output feature."""

import csv
import os
import tempfile
import pytest
from decimal import Decimal
from src.csv_output.csv_service import CsvService
from src.csv_output.config import CSV_HEADERS, ERROR_FILE
from src.ai_extraction.domain.models.extraction_result import ReceiptData, ErrorReceiptData


class TestCsvOutputIntegration:
    """Integration tests for CSV output with AI extraction models."""
    
    def setup_method(self):
        """Set up test environment for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_csv_path = os.path.join(self.temp_dir, "integration_test.csv")
        self.csv_service = CsvService(self.test_csv_path)
    
    def teardown_method(self):
        """Clean up after each test."""
        if os.path.exists(self.test_csv_path):
            os.remove(self.test_csv_path)
        os.rmdir(self.temp_dir)
    
    def test_complete_workflow_successful_extraction(self):
        """Test complete workflow from ReceiptData to CSV record."""
        # Create CSV file
        self.csv_service.ensure_csv_exists()
        
        # Create AI extraction result
        receipt_data = ReceiptData(
            amount=Decimal('25.75'),
            tax=Decimal('4.12'),
            description="Grocery Store XYZ",
            currency="EUR",
            date="20-03-2024",
            confidence=92
        )
        
        # Calculate tax percentage (simulating integration logic)
        tax_percentage = float(receipt_data.tax / receipt_data.amount * 100) if receipt_data.amount > 0 else 0.0
        
        # Append to CSV
        record_id = self.csv_service.append_record(
            amount=float(receipt_data.amount),
            tax=float(receipt_data.tax),
            tax_percentage=tax_percentage,
            description=receipt_data.description,
            currency=receipt_data.currency,
            date=receipt_data.date,
            confidence=receipt_data.confidence,
            hash_value="sha256hash123456",
            done_filename="1-20240320-143522123456-grocery_receipt.pdf"
        )
        
        assert record_id == 1
        
        # Verify the complete record in CSV
        with open(self.test_csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            record = next(reader)
            
            assert record['ID'] == '1'
            assert record['Amount'] == '25.75'
            assert record['Tax'] == '4.12'
            assert record['TaxPercentage'] == '16.00'  # 4.12/25.75*100 = 16.00
            assert record['Description'] == 'Grocery Store XYZ'
            assert record['Currency'] == 'EUR'
            assert record['Date'] == '20-03-2024'
            assert record['Confidence'] == '92'
            assert record['Hash'] == 'sha256hash123456'
            assert record['DoneFilename'] == '1-20240320-143522123456-grocery_receipt.pdf'
    
    def test_complete_workflow_error_extraction(self):
        """Test complete workflow from ErrorReceiptData to CSV error record."""
        # Create CSV file
        self.csv_service.ensure_csv_exists()
        
        # Create AI extraction error result
        error_data = ErrorReceiptData(
            description=ERROR_FILE,
            amount=Decimal('0'),
            tax=Decimal('0'),
            currency="",
            date="",
            confidence=0
        )
        
        # Append error to CSV
        record_id = self.csv_service.append_error_record(
            error_type=error_data.description,
            hash_value="errorhash789",
            done_filename="2-20240320-143600789012-corrupted_file.jpg"
        )
        
        assert record_id == 1
        
        # Verify the complete error record in CSV
        with open(self.test_csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            record = next(reader)
            
            assert record['ID'] == '1'
            assert record['Amount'] == '0.00'
            assert record['Tax'] == '0.00'
            assert record['TaxPercentage'] == '0.00'
            assert record['Description'] == ERROR_FILE
            assert record['Currency'] == ''
            assert record['Date'] == ''
            assert record['Confidence'] == '0'
            assert record['Hash'] == 'errorhash789'
            assert record['DoneFilename'] == '2-20240320-143600789012-corrupted_file.jpg'
    
    def test_mixed_successful_and_error_records(self):
        """Test CSV with mix of successful and error records."""
        # Create CSV file
        self.csv_service.ensure_csv_exists()
        
        # Add successful record
        receipt_data = ReceiptData(
            amount=Decimal('15.50'),
            tax=Decimal('2.50'),
            description="Coffee Shop",
            currency="USD",
            date="18-03-2024",
            confidence=95
        )
        
        tax_percentage = float(receipt_data.tax / receipt_data.amount * 100)
        
        record_id_1 = self.csv_service.append_record(
            amount=float(receipt_data.amount),
            tax=float(receipt_data.tax),
            tax_percentage=tax_percentage,
            description=receipt_data.description,
            currency=receipt_data.currency,
            date=receipt_data.date,
            confidence=receipt_data.confidence,
            hash_value="hash1",
            done_filename="1-20240318-120000111111-coffee.pdf"
        )
        
        # Add error record
        record_id_2 = self.csv_service.append_error_record(
            error_type="ERROR-API",
            hash_value="hash2",
            done_filename="2-20240318-120100222222-failed.jpg"
        )
        
        # Add another successful record
        receipt_data_2 = ReceiptData(
            amount=Decimal('45.99'),
            tax=Decimal('0.00'),  # No tax
            description="Online Purchase",
            currency="GBP",
            date="19-03-2024",
            confidence=88
        )
        
        tax_percentage_2 = 0.0  # No tax
        
        record_id_3 = self.csv_service.append_record(
            amount=float(receipt_data_2.amount),
            tax=float(receipt_data_2.tax),
            tax_percentage=tax_percentage_2,
            description=receipt_data_2.description,
            currency=receipt_data_2.currency,
            date=receipt_data_2.date,
            confidence=receipt_data_2.confidence,
            hash_value="hash3",
            done_filename="3-20240319-150000333333-online.pdf"
        )
        
        assert record_id_1 == 1
        assert record_id_2 == 2
        assert record_id_3 == 3
        
        # Verify all records in CSV
        with open(self.test_csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            records = list(reader)
            
            assert len(records) == 3
            
            # Check first record (successful)
            assert records[0]['ID'] == '1'
            assert records[0]['Amount'] == '15.50'
            assert records[0]['Description'] == 'Coffee Shop'
            assert records[0]['Currency'] == 'USD'
            
            # Check second record (error)
            assert records[1]['ID'] == '2'
            assert records[1]['Amount'] == '0.00'
            assert records[1]['Description'] == 'ERROR-API'
            assert records[1]['Currency'] == ''
            
            # Check third record (successful, no tax)
            assert records[2]['ID'] == '3'
            assert records[2]['Amount'] == '45.99'
            assert records[2]['Tax'] == '0.00'
            assert records[2]['TaxPercentage'] == '0.00'
            assert records[2]['Description'] == 'Online Purchase'
            assert records[2]['Currency'] == 'GBP'
    
    def test_csv_creation_and_multiple_records_sequence(self):
        """Test complete sequence: create CSV, add multiple records, verify IDs."""
        # Ensure CSV exists
        self.csv_service.ensure_csv_exists()
        
        # Verify file exists with headers
        assert os.path.exists(self.test_csv_path)
        
        with open(self.test_csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)
            assert headers == CSV_HEADERS
        
        # Add 5 records and verify sequential IDs
        for i in range(1, 6):
            record_id = self.csv_service.append_record(
                amount=10.0 + i,
                tax=1.5,
                tax_percentage=15.0,
                description=f"Test Receipt {i}",
                currency="EUR",
                date="15-03-2024",
                confidence=90 + i,
                hash_value=f"hash{i}",
                done_filename=f"{i}-20240315-120000000000-test{i}.pdf"
            )
            assert record_id == i
        
        # Verify all records exist with correct IDs
        with open(self.test_csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            records = list(reader)
            
            assert len(records) == 5
            for i, record in enumerate(records, 1):
                assert record['ID'] == str(i)
                assert record['Description'] == f"Test Receipt {i}"
                assert record['Confidence'] == str(90 + i)
    
    def test_integration_with_decimal_precision(self):
        """Test integration handling Decimal types from AI extraction."""
        self.csv_service.ensure_csv_exists()
        
        # Test with various Decimal precisions
        test_cases = [
            (Decimal('123.456'), Decimal('19.74'), "3 decimal places"),
            (Decimal('99.1'), Decimal('15.856'), "Mixed precision"),
            (Decimal('1000'), Decimal('0'), "Whole numbers"),
            (Decimal('0.01'), Decimal('0.001'), "Very small amounts")
        ]
        
        for i, (amount, tax, description) in enumerate(test_cases, 1):
            tax_percentage = float(tax / amount * 100) if amount > 0 else 0.0
            
            record_id = self.csv_service.append_record(
                amount=float(amount),
                tax=float(tax),
                tax_percentage=tax_percentage,
                description=description,
                currency="EUR",
                date="15-03-2024",
                confidence=85,
                hash_value=f"hash{i}",
                done_filename=f"{i}-20240315-120000000000-test.pdf"
            )
            
            assert record_id == i
        
        # Verify proper formatting in CSV
        with open(self.test_csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            records = list(reader)
            
            # Check formatting
            assert records[0]['Amount'] == '123.46'  # Rounded to 2 decimal places
            assert records[0]['Tax'] == '19.74'
            assert records[1]['Amount'] == '99.10'   # Padded to 2 decimal places
            assert records[2]['Amount'] == '1000.00' # Whole number with decimals
            assert records[3]['Amount'] == '0.01'    # Small amount preserved