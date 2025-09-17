"""Integration tests for complete receipt analysis workflow."""

import tempfile
from pathlib import Path
from unittest.mock import Mock


from adapters.secondary.anthropic_adapter import AnthropicAdapter
from adapters.secondary.csv_adapter import CSVAdapter
from adapters.secondary.duplicate_detection_adapter import DuplicateDetectionAdapter
from adapters.secondary.file_system_adapter import FileSystemAdapter
from core.domain.configuration import AppConfig
from core.use_cases.process_receipt import ProcessReceiptUseCase


class TestReceiptAnalysisIntegration:
    """Integration tests for receipt analysis workflow."""

    def setup_method(self):
        """Set up test environment with temporary directories."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

        # Create test directories
        self.incoming_dir = self.temp_path / "incoming"
        self.scanned_dir = self.temp_path / "scanned"
        self.imported_dir = self.temp_path / "imported"
        self.failed_dir = self.temp_path / "failed"
        self.csv_file = self.temp_path / "receipts.csv"

        for directory in [self.incoming_dir, self.scanned_dir, self.imported_dir, self.failed_dir]:
            directory.mkdir(parents=True)

        # Create configuration
        self.config = AppConfig(
            incoming_folder=self.incoming_dir,
            scanned_folder=self.scanned_dir,
            imported_folder=self.imported_dir,
            failed_folder=self.failed_dir,
            csv_staging_file=self.csv_file,
            xlsx_output_file=self.temp_path / "output.xlsx"
        )

        # Create real adapters
        self.file_system = FileSystemAdapter()
        self.csv = CSVAdapter()
        self.duplicate_detection = DuplicateDetectionAdapter(self.file_system)

    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_successful_receipt_processing_workflow(self):
        """Test complete workflow for successful receipt processing."""
        # Create a test receipt file
        test_receipt = self.incoming_dir / "receipt.jpg"
        test_receipt.write_bytes(b"fake image data")

        # Mock Anthropic adapter with successful response
        mock_ai = Mock(spec=AnthropicAdapter)
        mock_ai.extract_receipt_data.return_value = {
            "amount": "25.99",
            "tax": "2.08",
            "tax_percentage": "8.25",
            "description": "Coffee Shop",
            "currency": "USD",
            "date": "2024-03-15",
            "confidence": "85"
        }

        # Create use case with mocked AI
        use_case = ProcessReceiptUseCase(
            self.file_system, mock_ai, self.csv, self.duplicate_detection
        )

        # Execute workflow
        use_case.execute(self.config)

        # Verify file was copied to scanned folder
        scanned_file = self.scanned_dir / "receipt.jpg"
        assert scanned_file.exists()
        assert scanned_file.read_bytes() == b"fake image data"

        # Verify CSV was created with correct data
        assert self.csv_file.exists()
        csv_content = self.csv_file.read_text()
        assert "Amount,Tax,TaxPercentage,Description,Currency,Date,Confidence,Hash,DoneFilename" in csv_content
        assert "25.99,2.08,8.25,Coffee Shop,USD,2024-03-15,85" in csv_content
        assert "receipt.jpg" in csv_content

        # Verify no files in failed folder
        assert len(list(self.failed_dir.iterdir())) == 0

        # Verify AI extraction was called with correct path
        mock_ai.extract_receipt_data.assert_called_once_with(str(test_receipt))

    def test_failed_receipt_processing_workflow(self):
        """Test complete workflow for failed receipt processing."""
        # Create a test receipt file
        test_receipt = self.incoming_dir / "bad_receipt.pdf"
        test_receipt.write_bytes(b"fake pdf data")

        # Mock Anthropic adapter with failure
        mock_ai = Mock(spec=AnthropicAdapter)
        mock_ai.extract_receipt_data.side_effect = ValueError("API error: Invalid image")

        # Create use case with mocked AI
        use_case = ProcessReceiptUseCase(
            self.file_system, mock_ai, self.csv, self.duplicate_detection
        )

        # Execute workflow
        use_case.execute(self.config)

        # Verify file was copied to failed folder
        failed_file = self.failed_dir / "bad_receipt.pdf"
        assert failed_file.exists()
        assert failed_file.read_bytes() == b"fake pdf data"

        # Verify error log was created
        error_log = self.failed_dir / "bad_receipt_error.txt"
        assert error_log.exists()
        error_content = error_log.read_text()
        assert "Error processing file: bad_receipt.pdf" in error_content
        assert "API error: Invalid image" in error_content

        # Verify CSV was not created (no successful extractions)
        assert not self.csv_file.exists()

        # Verify no files in scanned folder
        assert len(list(self.scanned_dir.iterdir())) == 0

    def test_duplicate_detection_workflow(self):
        """Test workflow with duplicate file detection."""
        # Create test files in incoming and imported folders with same content
        # Note: We use imported folder because scanned folder gets cleared by the use case
        test_receipt_incoming = self.incoming_dir / "receipt.jpg"
        test_receipt_imported = self.imported_dir / "existing_receipt.jpg"
        file_content = b"same image data"

        test_receipt_incoming.write_bytes(file_content)
        test_receipt_imported.write_bytes(file_content)

        # Mock Anthropic adapter (should not be called for duplicates)
        mock_ai = Mock(spec=AnthropicAdapter)

        # Create use case
        use_case = ProcessReceiptUseCase(
            self.file_system, mock_ai, self.csv, self.duplicate_detection
        )

        # Execute workflow
        use_case.execute(self.config)

        # Verify AI extraction was NOT called
        mock_ai.extract_receipt_data.assert_not_called()

        # Verify CSV was not created (or if created, it's empty)
        if self.csv_file.exists():
            csv_content = self.csv_file.read_text()
            lines = csv_content.strip().split('\n')
            # Should only have header or be empty
            assert len(lines) <= 1 or (len(lines) == 2 and not lines[1].strip())

        # Verify original file still in incoming folder
        assert test_receipt_incoming.exists()

        # Verify scanned folder is empty (was cleared and nothing was added)
        scanned_files = list(self.scanned_dir.iterdir())
        assert len(scanned_files) == 0

    def test_mixed_results_workflow(self):
        """Test workflow with mix of successful, failed, and duplicate files."""
        # Create multiple test files
        successful_receipt = self.incoming_dir / "good_receipt.jpg"
        failed_receipt = self.incoming_dir / "bad_receipt.png"
        duplicate_receipt = self.incoming_dir / "duplicate.pdf"
        existing_duplicate = self.imported_dir / "existing.pdf"

        successful_receipt.write_bytes(b"good image")
        failed_receipt.write_bytes(b"bad image")
        duplicate_receipt.write_bytes(b"duplicate content")
        existing_duplicate.write_bytes(b"duplicate content")

        # Mock Anthropic adapter with mixed responses
        def mock_extract_side_effect(file_path: str) -> dict[str, str]:
            if "good_receipt" in file_path:
                return {
                    "amount": "15.50",
                    "tax": "1.24",
                    "tax_percentage": "8.0",
                    "description": "Lunch",
                    "currency": "USD",
                    "date": "2024-03-16",
                    "confidence": "92"
                }
            else:
                raise ValueError("Extraction failed")

        mock_ai = Mock(spec=AnthropicAdapter)
        mock_ai.extract_receipt_data.side_effect = mock_extract_side_effect

        # Create use case
        use_case = ProcessReceiptUseCase(
            self.file_system, mock_ai, self.csv, self.duplicate_detection
        )

        # Execute workflow
        use_case.execute(self.config)

        # Verify successful file was processed
        assert (self.scanned_dir / "good_receipt.jpg").exists()
        assert self.csv_file.exists()
        csv_content = self.csv_file.read_text()
        assert "15.50,1.24,8.0,Lunch,USD,2024-03-16,92" in csv_content

        # Verify failed file was handled
        assert (self.failed_dir / "bad_receipt.png").exists()
        assert (self.failed_dir / "bad_receipt_error.txt").exists()

        # Verify duplicate was skipped (still in incoming, not processed to other folders)
        assert duplicate_receipt.exists()  # Still in incoming
        assert not (self.scanned_dir / "duplicate.pdf").exists()
        # Note: duplicate files should NOT be copied to failed folder

        # Verify AI was called only for non-duplicate files
        assert mock_ai.extract_receipt_data.call_count == 2

    def test_csv_append_multiple_receipts(self):
        """Test CSV appending with multiple successful receipts."""
        # Create multiple test receipt files
        receipt1 = self.incoming_dir / "receipt1.jpg"
        receipt2 = self.incoming_dir / "receipt2.png"
        receipt1.write_bytes(b"image1 data")
        receipt2.write_bytes(b"image2 data")

        # Mock Anthropic adapter with different responses
        def mock_extract_side_effect(file_path: str) -> dict[str, str]:
            if "receipt1" in file_path:
                return {
                    "amount": "10.00",
                    "tax": "0.80",
                    "tax_percentage": "8.0",
                    "description": "Store A",
                    "currency": "USD",
                    "date": "2024-03-15",
                    "confidence": "95"
                }
            else:
                return {
                    "amount": "20.50",
                    "tax": "",
                    "tax_percentage": "",
                    "description": "Store B",
                    "currency": "EUR",
                    "date": "2024-03-16",
                    "confidence": "88"
                }

        mock_ai = Mock(spec=AnthropicAdapter)
        mock_ai.extract_receipt_data.side_effect = mock_extract_side_effect

        # Create use case
        use_case = ProcessReceiptUseCase(
            self.file_system, mock_ai, self.csv, self.duplicate_detection
        )

        # Execute workflow
        use_case.execute(self.config)

        # Verify both files were processed
        assert (self.scanned_dir / "receipt1.jpg").exists()
        assert (self.scanned_dir / "receipt2.png").exists()

        # Verify CSV contains both entries
        csv_content = self.csv_file.read_text()
        lines = csv_content.strip().split('\n')
        assert len(lines) == 3  # Header + 2 data lines

        assert "10.00,0.80,8.0,Store A,USD,2024-03-15,95" in csv_content
        assert "20.50,,,Store B,EUR,2024-03-16,88" in csv_content

        # Verify both filenames are in CSV
        assert "receipt1.jpg" in csv_content
        assert "receipt2.png" in csv_content