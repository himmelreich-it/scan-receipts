"""Integration tests for complete receipt processing feature."""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import AsyncMock, Mock
from decimal import Decimal
from datetime import datetime

from receipt_processing_engine.application.use_cases import ProcessReceiptUseCase
from receipt_processing_engine.infrastructure.file_system_adapter import FileSystemAdapter
from receipt_processing_engine.infrastructure.duplicate_detection_adapter import DuplicateDetectionAdapter
from receipt_processing_engine.infrastructure.csv_repository_adapter import CsvRepositoryAdapter
from receipt_processing_engine.domain.entities import ProcessingStatus


class TestReceiptProcessingComplete:
    """Test complete receipt processing feature across all user stories."""
    
    @pytest.fixture
    def temp_directory(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def test_files(self, temp_directory):
        """Create test receipt files."""
        # Create valid test files
        jpg_file = Path(temp_directory) / "receipt1.jpg"
        png_file = Path(temp_directory) / "receipt2.png"
        pdf_file = Path(temp_directory) / "receipt3.pdf"
        invalid_file = Path(temp_directory) / "receipt4.txt"
        
        # Create actual files with some content
        jpg_file.write_bytes(b"JPEG fake content")
        png_file.write_bytes(b"PNG fake content")
        pdf_file.write_bytes(b"PDF fake content")
        invalid_file.write_text("Invalid format")
        
        return {
            'jpg': str(jpg_file),
            'png': str(png_file),
            'pdf': str(pdf_file),
            'invalid': str(invalid_file)
        }
    
    @pytest.fixture
    def csv_file(self, temp_directory):
        """Create temporary CSV file for testing."""
        return str(Path(temp_directory) / "test_receipts.csv")
    
    @pytest.fixture
    def mock_ai_adapter(self):
        """Create mock AI adapter that returns valid responses."""
        adapter = Mock()
        adapter.extract_receipt_data = AsyncMock()
        
        # Default successful response
        adapter.extract_receipt_data.return_value = {
            "amount": 45.67,
            "tax": 5.67,
            "tax_percentage": 12.5,
            "description": "Test Store",
            "currency": "EUR",
            "date": "15-01-2023",
            "confidence": 85
        }
        
        return adapter
    
    @pytest.fixture
    def processing_system(self, mock_ai_adapter, csv_file):
        """Create complete processing system with real adapters."""
        file_adapter = FileSystemAdapter()
        duplicate_adapter = DuplicateDetectionAdapter()
        csv_adapter = CsvRepositoryAdapter(csv_file)
        
        # Reset CSV for fresh testing
        csv_adapter.reset()
        
        use_case = ProcessReceiptUseCase(
            ai_extraction_port=mock_ai_adapter,
            file_system_port=file_adapter,
            receipt_repository_port=csv_adapter,
            duplicate_detector_port=duplicate_adapter
        )
        
        return use_case, csv_adapter
    
    @pytest.mark.asyncio
    async def test_complete_workflow_story_1_to_3(self, processing_system, test_files):
        """Test: Complete workflow from file validation through duplicate detection."""
        use_case, csv_adapter = processing_system
        
        # Process valid JPG file - RECEIPT_ANALYSIS_A1B2
        result_jpg = await use_case.execute(test_files['jpg'])
        assert result_jpg.processing_status == ProcessingStatus.COMPLETED
        assert result_jpg.extraction_data is not None
        assert result_jpg.extraction_data.amount.value == Decimal('45.67')
        
        # Process valid PNG file - FILE_VALIDATION_C3D4
        result_png = await use_case.execute(test_files['png'])
        assert result_png.processing_status == ProcessingStatus.COMPLETED
        
        # Process valid PDF file
        result_pdf = await use_case.execute(test_files['pdf'])
        assert result_pdf.processing_status == ProcessingStatus.COMPLETED
        
        # Process invalid format file - FILE_VALIDATION_C3D4
        result_invalid = await use_case.execute(test_files['invalid'])
        assert result_invalid.processing_status == ProcessingStatus.FAILED
        assert result_invalid.error_type == "UNSUPPORTED_FORMAT"
        
        # Process duplicate file - DUPLICATE_DETECTION_E5F6
        result_duplicate = await use_case.execute(test_files['jpg'])  # Same file again
        assert result_duplicate.processing_status == ProcessingStatus.DUPLICATE
    
    @pytest.mark.asyncio
    async def test_user_story_acceptance_criteria(self, processing_system, test_files, mock_ai_adapter):
        """Test: Copy exact acceptance criteria for each story."""
        use_case, csv_adapter = processing_system
        
        # RECEIPT_ANALYSIS_A1B2 acceptance criteria
        # "When valid receipt file (PDF, JPG, PNG) is processed, Claude API extracts required fields"
        result = await use_case.execute(test_files['jpg'])
        assert result.processing_status == ProcessingStatus.COMPLETED
        assert result.extraction_data.amount.value == Decimal('45.67')
        assert result.extraction_data.description.text == "Test Store"
        assert result.extraction_data.currency.code == "EUR"
        assert result.extraction_data.confidence.score == 85
        
        # "When processing succeeds, console displays progress message with filename and confidence"
        # (This would be tested in end-to-end tests with real console logger)
        
        # FILE_VALIDATION_C3D4 acceptance criteria
        # "When file format is unsupported, system logs message and continues with next file"
        result_invalid = await use_case.execute(test_files['invalid'])
        assert result_invalid.processing_status == ProcessingStatus.FAILED
        assert result_invalid.error_type == "UNSUPPORTED_FORMAT"
        
        # "When file is corrupted or unreadable, system creates CSV entry with confidence 0"
        csv_row = result_invalid.to_csv_row()
        assert csv_row['Confidence'] == '0'
        assert csv_row['Description'] == 'UNSUPPORTED_FORMAT'
        
        # DUPLICATE_DETECTION_E5F6 acceptance criteria
        # "When file hash matches existing hash, system skips file and logs duplicate message"
        result_original = await use_case.execute(test_files['png'])
        result_duplicate = await use_case.execute(test_files['png'])
        
        assert result_original.processing_status == ProcessingStatus.COMPLETED
        assert result_duplicate.processing_status == ProcessingStatus.DUPLICATE
        
        # "When duplicate is detected, system does not send file to API or create CSV entry"
        initial_call_count = mock_ai_adapter.extract_receipt_data.call_count
        await use_case.execute(test_files['png'])  # Another duplicate
        assert mock_ai_adapter.extract_receipt_data.call_count == initial_call_count  # No additional API call
    
    @pytest.mark.asyncio
    async def test_csv_output_integration(self, processing_system, test_files, csv_file):
        """Test: CSV output matches expected format across all stories."""
        use_case, csv_adapter = processing_system
        
        # Process files
        await use_case.execute(test_files['jpg'])
        await use_case.execute(test_files['invalid'])
        
        # Verify CSV file exists and has correct structure
        assert os.path.exists(csv_file)
        
        with open(csv_file, 'r') as f:
            content = f.read()
            
        # Check headers exist
        assert 'ID,Amount,Tax,TaxPercentage,Description,Currency,Date,Confidence,Hash,DoneFilename' in content
        
        # Check successful entry format
        assert '45.67' in content
        assert 'Test Store' in content
        assert 'EUR' in content
        assert '85' in content
        
        # Check error entry format
        assert 'UNSUPPORTED_FORMAT' in content
        assert '0' in content  # Confidence 0 for error
    
    @pytest.mark.asyncio
    async def test_error_handling_across_stories(self, processing_system, test_files, mock_ai_adapter):
        """Test: Error handling workflow across story boundaries."""
        use_case, csv_adapter = processing_system
        
        # Test API failure handling
        mock_ai_adapter.extract_receipt_data.side_effect = Exception("Network timeout")
        
        result = await use_case.execute(test_files['jpg'])
        assert result.processing_status == ProcessingStatus.FAILED
        assert result.error_type == "API_FAILURE"  # Network timeout is classified as API failure
        
        # Verify processing continues after error
        mock_ai_adapter.extract_receipt_data.side_effect = None  # Reset
        mock_ai_adapter.extract_receipt_data.return_value = {
            "amount": 25.50,
            "tax": None,
            "tax_percentage": None,
            "description": "Another Store",
            "currency": "USD",
            "date": "20-01-2023",
            "confidence": 75
        }
        
        result2 = await use_case.execute(test_files['png'])
        assert result2.processing_status == ProcessingStatus.COMPLETED
        assert result2.extraction_data.amount.value == Decimal('25.50')
    
    @pytest.mark.asyncio
    async def test_hash_generation_consistency(self, processing_system, test_files):
        """Test: File hash generation is consistent for duplicate detection."""
        use_case, csv_adapter = processing_system
        
        # Process same file multiple times
        result1 = await use_case.execute(test_files['jpg'])
        result2 = await use_case.execute(test_files['jpg'])
        result3 = await use_case.execute(test_files['jpg'])
        
        # First should succeed, others should be duplicates
        assert result1.processing_status == ProcessingStatus.COMPLETED
        assert result2.processing_status == ProcessingStatus.DUPLICATE
        assert result3.processing_status == ProcessingStatus.DUPLICATE
        
        # All should have same hash
        assert result1.file_hash == result2.file_hash == result3.file_hash
    
    def test_feature_boundaries_and_integration(self, processing_system):
        """Test: Feature boundaries and integration points work correctly."""
        use_case, csv_adapter = processing_system
        
        # Verify all components are properly integrated
        assert use_case.ai_extraction_port is not None
        assert use_case.file_system_port is not None
        assert use_case.receipt_repository_port is not None
        assert use_case.duplicate_detector_port is not None
        
        # Verify repository starts with no processed hashes
        initial_hashes = csv_adapter.get_processed_hashes()
        assert len(initial_hashes) == 0
        
        # Verify duplicate detector can generate hashes
        hash1 = use_case.duplicate_detector_port.generate_file_hash(__file__)
        hash2 = use_case.duplicate_detector_port.generate_file_hash(__file__)
        assert hash1 == hash2  # Same file should generate same hash
        assert len(hash1) == 64  # SHA-256 hash length