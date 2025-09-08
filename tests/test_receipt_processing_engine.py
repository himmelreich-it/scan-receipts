"""Simple unit tests for Receipt Processing Engine."""

import pytest
import tempfile
from decimal import Decimal
from datetime import datetime
from pathlib import Path
from receipt_processing_engine.domain.entities import Receipt, ProcessingStatus
from receipt_processing_engine.domain.value_objects import (
    ExtractionData, Amount, Currency, Confidence, Description, ReceiptDate
)
from receipt_processing_engine.infrastructure.file_system_adapter import FileSystemAdapter
from receipt_processing_engine.infrastructure.duplicate_adapter import DuplicateDetectionAdapter


class TestReceiptDomain:
    """Test Receipt domain functionality."""
    
    def test_receipt_creation_and_status_transitions(self):
        """Test receipt creation and status changes."""
        receipt = Receipt("/test/receipt.jpg", "abc123")
        
        # Test initial state
        assert receipt.file_path == "/test/receipt.jpg"
        assert receipt.file_hash == "abc123"
        assert receipt.processing_status == ProcessingStatus.PENDING
        assert receipt.extraction_data is None
        assert receipt.error_type is None
        
        # Test marking as failed
        receipt.mark_as_failed("API call failed", "API_FAILURE")
        assert receipt.processing_status == ProcessingStatus.FAILED
        assert receipt.error_type == "API_FAILURE"
        assert receipt.extraction_data is None
        
        # Test CSV output for failed receipt
        csv_row = receipt.to_csv_row()
        assert csv_row['Description'] == 'API call failed'
        assert csv_row['Confidence'] == '0'
        assert csv_row['Amount'] == '0'


class TestValueObjects:
    """Test domain value objects."""
    
    def test_amount_validation(self):
        """Test Amount value object validation."""
        # Valid amount
        amount = Amount(Decimal('45.67'))
        assert amount.value == Decimal('45.67')
        
        # Invalid negative amount
        with pytest.raises(ValueError, match="Amount must be non-negative"):
            Amount(Decimal('-10.50'))
    
    def test_currency_validation(self):
        """Test Currency value object validation."""
        # Valid currency codes
        eur = Currency("EUR")
        usd = Currency("USD")
        assert eur.code == "EUR"
        assert usd.code == "USD"
        
        # Invalid currency codes
        with pytest.raises(ValueError, match="Currency code must be 3 uppercase letters"):
            Currency("eur")  # lowercase
        
        with pytest.raises(ValueError, match="Currency code must be 3 uppercase letters"):
            Currency("EURO")  # too long
    
    def test_confidence_validation(self):
        """Test Confidence value object validation."""
        # Valid confidence scores
        conf_0 = Confidence(0)
        conf_100 = Confidence(100)
        assert conf_0.score == 0
        assert conf_100.score == 100
        
        # Invalid confidence scores
        with pytest.raises(ValueError, match="Confidence score must be between 0 and 100"):
            Confidence(-1)
        
        with pytest.raises(ValueError, match="Confidence score must be between 0 and 100"):
            Confidence(101)
    
    def test_extraction_data_from_api_response(self):
        """Test ExtractionData creation from API response."""
        api_response = {
            "amount": 45.67,
            "tax": 5.67,
            "tax_percentage": None,
            "description": "Test Store",
            "currency": "EUR",
            "date": "15-01-2025",
            "confidence": 85
        }
        
        extraction_data = ExtractionData.from_api_response(api_response)
        
        assert extraction_data.amount.value == Decimal('45.67')
        assert extraction_data.tax is not None and extraction_data.tax.value == Decimal('5.67')
        assert extraction_data.tax_percentage is None
        assert extraction_data.description.text == "Test Store"
        assert extraction_data.currency.code == "EUR"
        assert extraction_data.confidence.score == 85
        assert extraction_data.date.to_string() == "15-01-2025"


class TestInfrastructure:
    """Test infrastructure adapters."""
    
    def test_file_system_adapter_format_validation(self):
        """Test file format validation."""
        adapter = FileSystemAdapter()
        
        # Supported formats
        assert adapter.validate_file_format("test.pdf") is True
        assert adapter.validate_file_format("test.jpg") is True
        assert adapter.validate_file_format("test.jpeg") is True
        assert adapter.validate_file_format("test.png") is True
        
        # Unsupported formats
        assert adapter.validate_file_format("test.txt") is False
        assert adapter.validate_file_format("test.doc") is False
    
    def test_duplicate_detection_adapter(self):
        """Test duplicate detection functionality."""
        adapter = DuplicateDetectionAdapter()
        
        # Create test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('test content')
            test_file = f.name
        
        # Test hash generation consistency
        hash1 = adapter.generate_file_hash(Path(test_file))
        hash2 = adapter.generate_file_hash(Path(test_file))
        
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hash length
        assert isinstance(hash1, str)
        
        # Test duplicate detection
        # Initially no duplicates
        assert adapter.is_duplicate(hash1) is False
        assert adapter.is_duplicate("different_hash") is False
        
        # Add to session and test
        adapter.add_to_session(hash1, "test_file.txt")
        assert adapter.is_duplicate(hash1) is True
        assert adapter.is_duplicate("different_hash") is False


class TestCompleteWorkflow:
    """Test complete processing workflow integration."""
    
    def test_receipt_processing_workflow_integration(self):
        """Test integration between domain and infrastructure components."""
        # Create receipt
        receipt = Receipt("/test/receipt.jpg", "abc123")
        
        # Create extraction data
        extraction_data = ExtractionData(
            amount=Amount(Decimal('45.67')),
            tax=None,
            tax_percentage=None,
            description=Description("Test Store"),
            currency=Currency("EUR"),
            date=ReceiptDate(datetime(2025, 1, 15)),
            confidence=Confidence(85)
        )
        
        # Process receipt
        receipt.mark_as_processed(extraction_data)
        
        # Verify integration
        assert receipt.processing_status == ProcessingStatus.COMPLETED
        assert receipt.extraction_data == extraction_data
        
        # Test CSV output
        csv_row = receipt.to_csv_row()
        assert csv_row['Amount'] == '45.67'
        assert csv_row['Description'] == 'Test Store'
        assert csv_row['Currency'] == 'EUR'
        assert csv_row['Date'] == '15-01-2025'
        assert csv_row['Confidence'] == '85'
        assert csv_row['Hash'] == 'abc123'
    
    def test_error_handling_integration(self):
        """Test error handling across components."""
        receipt = Receipt("/test/corrupt.jpg", "def456")
        
        # Test different error types
        receipt.mark_as_failed("File is corrupted", "FILE_CORRUPT")
        assert receipt.processing_status == ProcessingStatus.FAILED
        assert receipt.error_type == "FILE_CORRUPT"
        
        csv_row = receipt.to_csv_row()
        assert csv_row['Description'] == 'File is corrupted'
        assert csv_row['Confidence'] == '0'
        
        # Test duplicate handling
        receipt.mark_as_duplicate()
        assert receipt.processing_status == ProcessingStatus.DUPLICATE
        assert receipt.error_type is None