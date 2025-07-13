"""Unit tests for application use cases."""

import pytest
from unittest.mock import Mock, AsyncMock
from decimal import Decimal
from datetime import datetime
from receipt_processing_engine.application.use_cases import (
    ProcessReceiptUseCase, ExtractDataUseCase, ValidateResultsUseCase
)
from receipt_processing_engine.domain.entities import Receipt, ProcessingStatus
from receipt_processing_engine.domain.value_objects import ExtractionData, Amount, Currency, Confidence, Description, ReceiptDate
from receipt_processing_engine.domain.policies import ProcessingPolicies
from receipt_processing_engine.domain.exceptions import InvalidFileFormatError


class TestProcessReceiptUseCase:
    """Test ProcessReceiptUseCase."""
    
    @pytest.fixture
    def mock_ports(self):
        """Create mock ports for testing."""
        ai_port = Mock()
        ai_port.extract_receipt_data = AsyncMock()
        
        file_port = Mock()
        file_port.validate_file_format = Mock()
        
        repo_port = Mock()
        repo_port.get_processed_hashes = Mock(return_value=set())
        repo_port.save_receipt = Mock()
        
        dup_port = Mock()
        dup_port.generate_file_hash = Mock(return_value="abc123")
        dup_port.is_duplicate = Mock(return_value=False)
        
        return ai_port, file_port, repo_port, dup_port
    
    @pytest.fixture
    def use_case(self, mock_ports):
        """Create ProcessReceiptUseCase with mocked dependencies."""
        ai_port, file_port, repo_port, dup_port = mock_ports
        return ProcessReceiptUseCase(ai_port, file_port, repo_port, dup_port)
    
    @pytest.mark.asyncio
    async def test_successful_processing(self, use_case, mock_ports):
        """Test: Successful receipt processing workflow."""
        ai_port, file_port, repo_port, dup_port = mock_ports
        
        # Setup mocks
        file_port.validate_file_format.return_value = True
        ai_port.extract_receipt_data.return_value = {
            "amount": 45.67,
            "tax": None,
            "tax_percentage": None,
            "description": "Test Store",
            "currency": "EUR",
            "date": "15-01-2023",
            "confidence": 85
        }
        
        # Execute
        result = await use_case.execute("/test/receipt.jpg")
        
        # Verify
        assert result.processing_status == ProcessingStatus.COMPLETED
        assert result.file_path == "/test/receipt.jpg"
        assert result.file_hash == "abc123"
        assert result.extraction_data is not None
        assert result.extraction_data.amount.value == Decimal('45.67')
        
        # Verify mocks called
        file_port.validate_file_format.assert_called_once_with("/test/receipt.jpg")
        ai_port.extract_receipt_data.assert_called_once_with("/test/receipt.jpg")
        repo_port.save_receipt.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_duplicate_file_skipped(self, use_case, mock_ports):
        """Test: Duplicate file is skipped without processing."""
        ai_port, file_port, repo_port, dup_port = mock_ports
        
        # Setup duplicate detection
        dup_port.is_duplicate.return_value = True
        
        # Execute
        result = await use_case.execute("/test/receipt.jpg")
        
        # Verify
        assert result.processing_status == ProcessingStatus.DUPLICATE
        assert result.file_path == "/test/receipt.jpg"
        assert result.extraction_data is None
        
        # Verify AI not called for duplicates
        ai_port.extract_receipt_data.assert_not_called()
        file_port.validate_file_format.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_unsupported_file_format(self, use_case, mock_ports):
        """Test: Unsupported file format handled as error."""
        ai_port, file_port, repo_port, dup_port = mock_ports
        
        # Setup invalid format
        file_port.validate_file_format.return_value = False
        
        # Execute
        result = await use_case.execute("/test/receipt.txt")
        
        # Verify
        assert result.processing_status == ProcessingStatus.FAILED
        assert result.error_type == "UNSUPPORTED_FORMAT"
        
        # Verify AI not called for invalid formats
        ai_port.extract_receipt_data.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_api_extraction_failure(self, use_case, mock_ports):
        """Test: API extraction failure handled as error."""
        ai_port, file_port, repo_port, dup_port = mock_ports
        
        # Setup valid format but API failure
        file_port.validate_file_format.return_value = True
        ai_port.extract_receipt_data.side_effect = Exception("API Error")
        
        # Execute
        result = await use_case.execute("/test/receipt.jpg")
        
        # Verify
        assert result.processing_status == ProcessingStatus.FAILED
        assert result.error_type == "FILE_CORRUPT"  # Default classification
        repo_port.save_receipt.assert_called()


class TestExtractDataUseCase:
    """Test ExtractDataUseCase."""
    
    @pytest.fixture
    def ai_port(self):
        """Create mock AI port."""
        port = Mock()
        port.extract_receipt_data = AsyncMock()
        return port
    
    @pytest.fixture
    def use_case(self, ai_port):
        """Create ExtractDataUseCase with mocked AI port."""
        return ExtractDataUseCase(ai_port)
    
    @pytest.mark.asyncio
    async def test_successful_extraction(self, use_case, ai_port):
        """Test: Successful data extraction from API."""
        # Setup mock response
        ai_port.extract_receipt_data.return_value = {
            "amount": 45.67,
            "tax": 5.67,
            "tax_percentage": None,
            "description": "Test Store",
            "currency": "EUR",
            "date": "15-01-2023",
            "confidence": 85
        }
        
        # Execute
        result = await use_case.execute("/test/receipt.jpg")
        
        # Verify
        assert isinstance(result, ExtractionData)
        assert result.amount.value == Decimal('45.67')
        assert result.description.text == "Test Store"
        assert result.confidence.score == 85
    
    @pytest.mark.asyncio
    async def test_missing_required_fields(self, use_case, ai_port):
        """Test: Missing required fields in API response."""
        # Setup incomplete response
        ai_port.extract_receipt_data.return_value = {
            "amount": 45.67,
            # Missing required fields
        }
        
        # Execute and verify exception
        with pytest.raises(Exception, match="Missing required fields"):
            await use_case.execute("/test/receipt.jpg")
    
    @pytest.mark.asyncio
    async def test_invalid_confidence_score(self, use_case, ai_port):
        """Test: Invalid confidence score in API response."""
        # Setup invalid confidence
        ai_port.extract_receipt_data.return_value = {
            "amount": 45.67,
            "description": "Test Store",
            "currency": "EUR",
            "date": "15-01-2023",
            "confidence": 150  # Invalid - over 100
        }
        
        # Execute and verify exception
        with pytest.raises(Exception, match="Invalid confidence score"):
            await use_case.execute("/test/receipt.jpg")


class TestValidateResultsUseCase:
    """Test ValidateResultsUseCase."""
    
    @pytest.fixture
    def use_case(self):
        """Create ValidateResultsUseCase."""
        return ValidateResultsUseCase(ProcessingPolicies())
    
    def test_valid_extraction_data(self, use_case):
        """Test: Valid extraction data passes validation."""
        extraction_data = ExtractionData(
            amount=Amount(Decimal('45.67')),
            tax=None,
            tax_percentage=None,
            description=Description("Test Store"),
            currency=Currency("EUR"),
            date=ReceiptDate(datetime(2023, 1, 15)),
            confidence=Confidence(85)
        )
        
        result = use_case.execute(extraction_data)
        
        assert result.is_valid is True
        assert len(result.issues) == 0
    
    def test_zero_amount_validation(self, use_case):
        """Test: Zero amount fails validation."""
        extraction_data = ExtractionData(
            amount=Amount(Decimal('0')),  # Zero amount
            tax=None,
            tax_percentage=None,
            description=Description("Test Store"),
            currency=Currency("EUR"),
            date=ReceiptDate(datetime(2023, 1, 15)),
            confidence=Confidence(85)
        )
        
        result = use_case.execute(extraction_data)
        
        assert result.is_valid is False
        assert "Amount must be positive" in result.issues