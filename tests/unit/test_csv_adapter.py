"""Unit tests for CSVAdapter."""

import csv
import tempfile
from pathlib import Path


from adapters.secondary.csv_adapter import CSVAdapter


class TestCSVAdapter:
    """Test CSV adapter functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = CSVAdapter()
    
    def test_read_staging_table_file_not_exists(self):
        """Test reading when CSV file doesn't exist."""
        non_existent_path = Path("/tmp/does_not_exist.csv")
        result = self.adapter.read_staging_table(non_existent_path)
        
        assert result is not None
        assert result.file_path == non_existent_path
        assert result.headers == []
        assert result.receipts == []
        assert not result.exists
        assert result.is_empty
    
    def test_read_staging_table_empty_file(self):
        """Test reading an empty CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            result = self.adapter.read_staging_table(temp_path)
            
            assert result is not None
            assert result.file_path == temp_path
            assert result.headers == []
            assert result.receipts == []
            assert result.exists
            assert result.is_empty
        finally:
            temp_path.unlink()
    
    def test_read_staging_table_with_headers_only(self):
        """Test reading CSV with headers but no data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = Path(f.name)
            writer = csv.writer(f)
            writer.writerow(['Amount', 'Tax', 'TaxPercentage', 'Description', 
                           'Currency', 'Date', 'Confidence', 'Hash', 'DoneFilename'])
        
        try:
            result = self.adapter.read_staging_table(temp_path)
            
            assert result is not None
            assert result.file_path == temp_path
            assert len(result.headers) == 9
            assert 'Amount' in result.headers
            assert result.receipts == []
            assert result.exists
            assert result.is_empty
        finally:
            temp_path.unlink()
    
    def test_read_staging_table_with_data(self):
        """Test reading CSV with data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = Path(f.name)
            writer = csv.DictWriter(f, fieldnames=['Amount', 'Tax', 'TaxPercentage', 
                                                   'Description', 'Currency', 'Date', 
                                                   'Confidence', 'Hash', 'DoneFilename'])
            writer.writeheader()
            writer.writerow({
                'Amount': '100.00',
                'Tax': '10.00',
                'TaxPercentage': '10',
                'Description': 'Test Receipt',
                'Currency': 'USD',
                'Date': '2024-01-01',
                'Confidence': '0.95',
                'Hash': 'abc123',
                'DoneFilename': 'receipt_001.pdf'
            })
            writer.writerow({
                'Amount': '200.00',
                'Tax': '20.00',
                'TaxPercentage': '10',
                'Description': 'Another Receipt',
                'Currency': 'EUR',
                'Date': '2024-01-02',
                'Confidence': '0.90',
                'Hash': 'def456',
                'DoneFilename': 'receipt_002.pdf'
            })
        
        try:
            result = self.adapter.read_staging_table(temp_path)
            
            assert result is not None
            assert result.file_path == temp_path
            assert len(result.headers) == 9
            assert len(result.receipts) == 2
            assert result.exists
            assert not result.is_empty
            
            # Check first receipt
            first_receipt = result.receipts[0]
            assert first_receipt.amount == '100.00'
            assert first_receipt.tax == '10.00'
            assert first_receipt.tax_percentage == '10'
            assert first_receipt.description == 'Test Receipt'
            assert first_receipt.currency == 'USD'
            assert first_receipt.date == '2024-01-01'
            assert first_receipt.confidence == '0.95'
            assert first_receipt.hash == 'abc123'
            assert first_receipt.done_filename == 'receipt_001.pdf'
            
            # Check second receipt
            second_receipt = result.receipts[1]
            assert second_receipt.amount == '200.00'
            assert second_receipt.description == 'Another Receipt'
        finally:
            temp_path.unlink()
    
    def test_read_staging_table_with_missing_columns(self):
        """Test reading CSV with some missing columns."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = Path(f.name)
            writer = csv.DictWriter(f, fieldnames=['Amount', 'Description'])
            writer.writeheader()
            writer.writerow({
                'Amount': '50.00',
                'Description': 'Partial Receipt'
            })
        
        try:
            result = self.adapter.read_staging_table(temp_path)
            
            assert result is not None
            assert len(result.receipts) == 1
            
            receipt = result.receipts[0]
            assert receipt.amount == '50.00'
            assert receipt.description == 'Partial Receipt'
            # Missing fields should be empty strings
            assert receipt.tax == ''
            assert receipt.tax_percentage == ''
            assert receipt.currency == ''
            assert receipt.date == ''
            assert receipt.confidence == ''
            assert receipt.hash == ''
            assert receipt.done_filename == ''
        finally:
            temp_path.unlink()