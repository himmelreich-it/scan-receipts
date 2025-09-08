"""Unit tests for domain entities."""

from decimal import Decimal
from datetime import datetime
from receipt_processing_engine.domain.entities import Receipt, ProcessingStatus
from receipt_processing_engine.domain.value_objects import ExtractionData, Amount, Tax, Currency, Confidence, Description, ReceiptDate


class TestReceipt:
    """Test Receipt aggregate."""
    
    def test_receipt_creation(self):
        """Test: Receipt can be created with file path and hash."""
        receipt = Receipt(file_path="/test/receipt.jpg", file_hash="abc123")
        
        assert receipt.file_path == "/test/receipt.jpg"
        assert receipt.file_hash == "abc123"
        assert receipt.processing_status == ProcessingStatus.PENDING
        assert receipt.extraction_data is None
        assert receipt.error_type is None
    
    def test_mark_as_processed(self):
        """Test: Receipt can be marked as processed with extraction data."""
        receipt = Receipt(file_path="/test/receipt.jpg", file_hash="abc123")
        
        extraction_data = ExtractionData(
            amount=Amount(Decimal('45.67')),
            tax=None,
            tax_percentage=None,
            description=Description("Test Store"),
            currency=Currency("EUR"),
            date=ReceiptDate(datetime(2025, 1, 15)),
            confidence=Confidence(85)
        )
        
        receipt.mark_as_processed(extraction_data)
        
        assert receipt.processing_status == ProcessingStatus.COMPLETED
        assert receipt.extraction_data == extraction_data
        assert receipt.error_type is None
    
    def test_mark_as_failed(self):
        """Test: Receipt can be marked as failed with error type."""
        receipt = Receipt(file_path="/test/receipt.jpg", file_hash="abc123")
        
        receipt.mark_as_failed("API call failed", "API_FAILURE")
        
        assert receipt.processing_status == ProcessingStatus.FAILED
        assert receipt.error_type == "API_FAILURE"
        assert receipt.extraction_data is None
    
    def test_mark_as_duplicate(self):
        """Test: Receipt can be marked as duplicate."""
        receipt = Receipt(file_path="/test/receipt.jpg", file_hash="abc123")
        
        receipt.mark_as_duplicate()
        
        assert receipt.processing_status == ProcessingStatus.DUPLICATE
        assert receipt.error_type is None
        assert receipt.extraction_data is None
    
    def test_is_duplicate(self):
        """Test: Receipt can check if it's a duplicate of another hash."""
        receipt = Receipt(file_path="/test/receipt.jpg", file_hash="abc123")
        
        assert receipt.is_duplicate("abc123") is True
        assert receipt.is_duplicate("def456") is False
    
    def test_to_csv_row_successful(self):
        """Test: Receipt converts to CSV row format when successful."""
        receipt = Receipt(file_path="/test/receipt.jpg", file_hash="abc123")
        
        extraction_data = ExtractionData(
            amount=Amount(Decimal('45.67')),
            tax=Tax(Decimal('5.67')),
            tax_percentage=None,
            description=Description("Test Store"),
            currency=Currency("EUR"),
            date=ReceiptDate(datetime(2025, 1, 15)),
            confidence=Confidence(85)
        )
        
        receipt.mark_as_processed(extraction_data)
        csv_row = receipt.to_csv_row()
        
        assert csv_row['Amount'] == '45.67'
        assert csv_row['Tax'] == '5.67'
        assert csv_row['Description'] == 'Test Store'
        assert csv_row['Currency'] == 'EUR'
        assert csv_row['Date'] == '15-01-2025'
        assert csv_row['Confidence'] == '85'
        assert csv_row['Hash'] == 'abc123'
        assert csv_row['DoneFilename'] == 'receipt.jpg'
    
    def test_to_csv_row_failed(self):
        """Test: Receipt converts to CSV row format when failed."""
        receipt = Receipt(file_path="/test/receipt.jpg", file_hash="abc123")
        receipt.mark_as_failed("API_FAILURE")
        
        csv_row = receipt.to_csv_row()
        
        assert csv_row['Amount'] == '0'
        assert csv_row['Tax'] == ''
        assert csv_row['Description'] == 'API_FAILURE'
        assert csv_row['Currency'] == ''
        assert csv_row['Date'] == ''
        assert csv_row['Confidence'] == '0'
        assert csv_row['Hash'] == 'abc123'
        assert csv_row['DoneFilename'] == 'receipt.jpg'


class TestProcessingStatus:
    """Test ProcessingStatus enum."""
    
    def test_status_values(self):
        """Test: ProcessingStatus enum has correct values."""
        assert ProcessingStatus.PENDING.value == "pending"
        assert ProcessingStatus.PROCESSING.value == "processing"
        assert ProcessingStatus.COMPLETED.value == "completed"
        assert ProcessingStatus.FAILED.value == "failed"
        assert ProcessingStatus.DUPLICATE.value == "duplicate"