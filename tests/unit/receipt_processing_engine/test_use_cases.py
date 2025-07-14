"""Unit tests for application use cases."""

import pytest
from unittest.mock import Mock, AsyncMock
from decimal import Decimal
from datetime import datetime
from receipt_processing_engine.application.use_cases import (
    ProcessReceiptUseCase, ExtractDataUseCase
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
        ai_port.extract_data = AsyncMock()
        ai_port.supports_file_format = Mock(return_value=True)
        
        file_port = Mock()
        file_port.get_input_files = Mock(return_value=[])
        file_port.move_file_to_failed = Mock()
        
        dup_port = Mock()
        dup_port.generate_file_hash = Mock(return_value="abc123")
        dup_port.is_duplicate = Mock(return_value=False)
        dup_port.initialize_done_folder_hashes = Mock()
        dup_port.add_to_session = Mock()
        
        return ai_port, file_port, dup_port
    
    @pytest.fixture
    def use_case(self, mock_ports):
        """Create ProcessReceiptUseCase with mocked dependencies."""
        ai_port, file_port, dup_port = mock_ports
        return ProcessReceiptUseCase(ai_port, file_port, dup_port)
    
    @pytest.mark.asyncio
    async def test_successful_processing(self, use_case, mock_ports):
        """Test: Successful receipt processing workflow."""
        from pathlib import Path
        ai_port, file_port, dup_port = mock_ports
        
        # Setup mocks
        test_file = Path("/test/receipt.jpg")
        file_port.get_input_files.return_value = [test_file]
        ai_port.extract_data.return_value = {
            "amount": 45.67,
            "tax": None,
            "tax_percentage": None,
            "description": "Test Store",
            "currency": "EUR",
            "date": "15-01-2025",
            "confidence": 85
        }
        
        # Execute
        results = await use_case.process_receipts(Path("/test/input"), Path("/test/done"))
        
        # Verify
        assert len(results) == 1
        result = results[0]
        assert result.processing_status == ProcessingStatus.COMPLETED
        assert result.file_path == str(test_file)
        assert result.file_hash == "abc123"
        assert result.extraction_data is not None
        assert result.extraction_data.amount.value == Decimal('45.67')
        
        # Verify mocks called
        dup_port.initialize_done_folder_hashes.assert_called_once()
        ai_port.extract_data.assert_called_once_with(test_file)
        dup_port.add_to_session.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_duplicate_file_skipped(self, use_case, mock_ports):
        """Test: Duplicate file is skipped without processing."""
        from pathlib import Path
        ai_port, file_port, dup_port = mock_ports
        
        # Setup duplicate detection
        test_file = Path("/test/receipt.jpg")
        file_port.get_input_files.return_value = [test_file]
        dup_port.is_duplicate.return_value = True
        
        # Execute
        results = await use_case.process_receipts(Path("/test/input"), Path("/test/done"))
        
        # Verify
        assert len(results) == 1
        result = results[0]
        assert result.processing_status == ProcessingStatus.DUPLICATE
        assert result.file_path == str(test_file)
        assert result.extraction_data is None
        
        # Verify AI not called for duplicates
        ai_port.extract_data.assert_not_called()
        dup_port.add_to_session.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_unsupported_file_format(self, use_case, mock_ports):
        """Test: Unsupported file format handled as error."""
        from pathlib import Path
        ai_port, file_port, dup_port = mock_ports
        
        # Setup invalid format
        test_file = Path("/test/receipt.txt")
        file_port.get_input_files.return_value = [test_file]
        ai_port.supports_file_format.return_value = False
        
        # Execute
        results = await use_case.process_receipts(Path("/test/input"), Path("/test/done"))
        
        # Verify
        assert len(results) == 1
        result = results[0]
        assert result.processing_status == ProcessingStatus.FAILED
        assert result.error_message == "Unsupported file format"
        
        # Verify AI not called for invalid formats
        ai_port.extract_data.assert_not_called()
        # Verify file moved to failed folder
        file_port.move_file_to_failed.assert_called_once_with(test_file, "Unsupported file format")
    
    @pytest.mark.asyncio
    async def test_api_extraction_failure(self, use_case, mock_ports):
        """Test: API extraction failure handled as error."""
        from pathlib import Path
        ai_port, file_port, dup_port = mock_ports
        
        # Setup valid format but API failure
        test_file = Path("/test/receipt.jpg")
        file_port.get_input_files.return_value = [test_file]
        ai_port.extract_data.side_effect = Exception("API Error")
        
        # Execute
        results = await use_case.process_receipts(Path("/test/input"), Path("/test/done"))
        
        # Verify
        assert len(results) == 1
        result = results[0]
        assert result.processing_status == ProcessingStatus.FAILED
        assert "API failure: API Error" in result.error_message
        
        # Verify file moved to failed folder
        file_port.move_file_to_failed.assert_called_once()
        assert "API failure: API Error" in file_port.move_file_to_failed.call_args[0][1]


class TestExtractDataUseCase:
    """Test ExtractDataUseCase."""
    
    @pytest.fixture
    def ai_port(self):
        """Create mock AI port."""
        port = Mock()
        port.extract_data = AsyncMock()
        return port
    
    @pytest.fixture
    def use_case(self, ai_port):
        """Create ExtractDataUseCase with mocked AI port."""
        return ExtractDataUseCase(ai_port)
    
    @pytest.mark.asyncio
    async def test_successful_extraction(self, use_case, ai_port):
        """Test: Successful data extraction from API."""
        from pathlib import Path
        # Setup mock response
        ai_port.extract_data.return_value = {
            "amount": 45.67,
            "tax": 5.67,
            "tax_percentage": None,
            "description": "Test Store",
            "currency": "EUR",
            "date": "15-01-2025",
            "confidence": 85
        }
        
        # Execute
        result = await use_case.extract_and_validate(Path("/test/receipt.jpg"))
        
        # Verify
        assert isinstance(result, ExtractionData)
        assert result.amount.value == Decimal('45.67')
        assert result.description.text == "Test Store"
        assert result.confidence.score == 85
    
    @pytest.mark.asyncio
    async def test_missing_required_fields(self, use_case, ai_port):
        """Test: Missing required fields in API response."""
        from pathlib import Path
        # Setup incomplete response
        ai_port.extract_data.return_value = {
            "amount": 45.67,
            # Missing required fields
        }
        
        # Execute and verify exception
        with pytest.raises(Exception, match="Missing required fields"):
            await use_case.extract_and_validate(Path("/test/receipt.jpg"))
    
    @pytest.mark.asyncio
    async def test_invalid_confidence_score(self, use_case, ai_port):
        """Test: Invalid confidence score in API response."""
        from pathlib import Path
        # Setup invalid confidence
        ai_port.extract_data.return_value = {
            "amount": 45.67,
            "description": "Test Store",
            "currency": "EUR",
            "date": "15-01-2025",
            "confidence": 150  # Invalid - over 100
        }
        
        # Execute and verify exception
        with pytest.raises(Exception, match="Invalid confidence score"):
            await use_case.extract_and_validate(Path("/test/receipt.jpg"))

