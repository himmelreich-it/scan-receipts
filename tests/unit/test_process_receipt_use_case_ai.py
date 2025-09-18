"""Unit tests for process receipt use case with AI integration."""

from pathlib import Path
from unittest.mock import Mock


from core.domain.configuration import AppConfig
from core.domain.receipt import DuplicateDetectionResult, FileHash
from core.use_cases.process_receipt import ProcessReceiptUseCase


class TestProcessReceiptUseCaseAI:
    """Test cases for ProcessReceiptUseCase with AI integration."""

    def setup_method(self):
        """Set up test dependencies."""
        self.file_system = Mock()
        self.ai_extraction = Mock()
        self.csv = Mock()
        self.duplicate_detection = Mock()
        self.use_case = ProcessReceiptUseCase(
            self.file_system, self.ai_extraction, self.csv, self.duplicate_detection
        )
        self.config = AppConfig(
            incoming_folder=Path("/test/incoming"),
            scanned_folder=Path("/test/scanned"),
            imported_folder=Path("/test/imported"),
            failed_folder=Path("/test/failed"),
            csv_staging_file=Path("/test/receipts.csv"),
            xlsx_output_file=Path("/test/output.xlsx")
        )

    def test_execute_successful_ai_extraction(self):
        """Test successful AI extraction and CSV writing."""
        # Setup mocks
        file_path = Path("/test/incoming/receipt.jpg")
        self.file_system.get_supported_files.return_value = [file_path]
        self.file_system.remove_file_if_exists.return_value = True
        self.file_system.get_file_hashes_from_folder.return_value = []

        # Mock duplicate detection - not a duplicate
        duplicate_result = DuplicateDetectionResult(
            file_path=file_path,
            is_duplicate=False,
            hash_value="abc123"
        )
        self.duplicate_detection.check_duplicate.return_value = duplicate_result

        # Mock AI extraction success
        receipt_data = {
            "amount": "25.99",
            "tax": "2.08",
            "tax_percentage": "8.25",
            "description": "Coffee Shop",
            "currency": "USD",
            "date": "2024-03-15",
            "confidence": "85"
        }
        self.ai_extraction.extract_receipt_data.return_value = receipt_data

        # Mock file hash calculation
        file_hash = FileHash(file_path=file_path, hash_value="abc123")
        self.file_system.calculate_file_hash.return_value = file_hash

        # Execute
        self.use_case.execute(self.config)

        # Verify AI extraction was called
        self.ai_extraction.extract_receipt_data.assert_called_once_with(str(file_path))

        # Verify CSV append was called
        self.csv.append_receipt_data.assert_called_once_with(
            self.config.csv_staging_file,
            receipt_data,
            "abc123",
            "receipt.jpg"
        )

        # Verify file was copied to scanned folder
        self.file_system.copy_file_to_folder.assert_called_once_with(
            file_path, self.config.scanned_folder
        )

    def test_execute_ai_extraction_failure(self):
        """Test handling of AI extraction failure."""
        # Setup mocks
        file_path = Path("/test/incoming/receipt.jpg")
        self.file_system.get_supported_files.return_value = [file_path]
        self.file_system.remove_file_if_exists.return_value = True
        self.file_system.get_file_hashes_from_folder.return_value = []

        # Mock duplicate detection - not a duplicate
        duplicate_result = DuplicateDetectionResult(
            file_path=file_path,
            is_duplicate=False,
            hash_value="abc123"
        )
        self.duplicate_detection.check_duplicate.return_value = duplicate_result

        # Mock AI extraction failure
        self.ai_extraction.extract_receipt_data.side_effect = ValueError("API error")

        # Execute
        self.use_case.execute(self.config)

        # Verify AI extraction was called
        self.ai_extraction.extract_receipt_data.assert_called_once_with(str(file_path))

        # Verify CSV append was NOT called
        self.csv.append_receipt_data.assert_not_called()

        # Verify file was copied to failed folder
        self.file_system.copy_file_to_folder.assert_called_once_with(
            file_path, self.config.failed_folder
        )

        # Verify error log was written
        self.file_system.write_error_log.assert_called_once_with(
            self.config.failed_folder, "receipt.jpg", "API error"
        )

    def test_execute_hash_calculation_failure(self):
        """Test handling of hash calculation failure."""
        # Setup mocks
        file_path = Path("/test/incoming/receipt.jpg")
        self.file_system.get_supported_files.return_value = [file_path]
        self.file_system.remove_file_if_exists.return_value = True
        self.file_system.get_file_hashes_from_folder.return_value = []

        # Mock duplicate detection - not a duplicate
        duplicate_result = DuplicateDetectionResult(
            file_path=file_path,
            is_duplicate=False,
            hash_value="abc123"
        )
        self.duplicate_detection.check_duplicate.return_value = duplicate_result

        # Mock AI extraction success
        receipt_data = {
            "amount": "25.99",
            "currency": "USD",
            "date": "2024-03-15",
            "confidence": "85",
            "description": "Test"
        }
        self.ai_extraction.extract_receipt_data.return_value = receipt_data

        # Mock hash calculation failure
        self.file_system.calculate_file_hash.return_value = None

        # Execute
        self.use_case.execute(self.config)

        # Verify file was copied to failed folder due to hash failure
        self.file_system.copy_file_to_folder.assert_called_once_with(
            file_path, self.config.failed_folder
        )

        # Verify error log was written
        self.file_system.write_error_log.assert_called_once_with(
            self.config.failed_folder, "receipt.jpg", "Failed to calculate file hash"
        )

    def test_execute_duplicate_detected(self):
        """Test skipping duplicate files."""
        # Setup mocks
        file_path = Path("/test/incoming/receipt.jpg")
        self.file_system.get_supported_files.return_value = [file_path]
        self.file_system.remove_file_if_exists.return_value = True
        self.file_system.get_file_hashes_from_folder.return_value = []

        # Mock duplicate detection - is a duplicate
        duplicate_result = DuplicateDetectionResult(
            file_path=file_path,
            is_duplicate=True,
            duplicate_location=Path("/test/scanned"),
            hash_value="abc123"
        )
        self.duplicate_detection.check_duplicate.return_value = duplicate_result

        # Execute
        self.use_case.execute(self.config)

        # Verify AI extraction was NOT called
        self.ai_extraction.extract_receipt_data.assert_not_called()

        # Verify CSV append was NOT called
        self.csv.append_receipt_data.assert_not_called()

        # Verify no files were copied
        self.file_system.copy_file_to_folder.assert_not_called()

    def test_execute_shows_csv_contents_when_processed(self):
        """Test CSV contents are displayed when files are processed."""
        # Setup mocks
        file_path = Path("/test/incoming/receipt.jpg")
        self.file_system.get_supported_files.return_value = [file_path]
        self.file_system.remove_file_if_exists.return_value = True
        self.file_system.get_file_hashes_from_folder.return_value = []

        # Mock duplicate detection - not a duplicate
        duplicate_result = DuplicateDetectionResult(
            file_path=file_path,
            is_duplicate=False,
            hash_value="abc123"
        )
        self.duplicate_detection.check_duplicate.return_value = duplicate_result

        # Mock AI extraction success
        receipt_data = {
            "amount": "25.99",
            "currency": "USD",
            "date": "2024-03-15",
            "confidence": "85",
            "description": "Test"
        }
        self.ai_extraction.extract_receipt_data.return_value = receipt_data

        # Mock file hash calculation
        file_hash = FileHash(file_path=file_path, hash_value="abc123")
        self.file_system.calculate_file_hash.return_value = file_hash

        # Mock CSV reading for summary
        from core.domain.receipt import ReceiptData, StagingTableData
        staging_data = StagingTableData(
            file_path=self.config.csv_staging_file,
            headers=["Amount", "Currency", "Description"],
            receipts=[ReceiptData(
                amount="25.99",
                tax="2.08",
                tax_percentage="8.25",
                description="Coffee Shop",
                currency="USD",
                date="2024-03-15",
                confidence="85",
                hash="abc123",
                done_filename="receipt.jpg"
            )]
        )
        self.csv.read_staging_table.return_value = staging_data

        # Mock failed files check
        self.file_system.get_supported_files.side_effect = [
            [file_path],  # For incoming files
            []  # For failed files check
        ]

        # Execute
        self.use_case.execute(self.config)

        # Verify CSV staging table was read for summary
        self.csv.read_staging_table.assert_called_once_with(self.config.csv_staging_file)

    def test_execute_copy_error_handling(self):
        """Test handling of file copy errors."""
        # Setup mocks
        file_path = Path("/test/incoming/receipt.jpg")
        self.file_system.get_supported_files.return_value = [file_path]
        self.file_system.remove_file_if_exists.return_value = True
        self.file_system.get_file_hashes_from_folder.return_value = []

        # Mock duplicate detection - not a duplicate
        duplicate_result = DuplicateDetectionResult(
            file_path=file_path,
            is_duplicate=False,
            hash_value="abc123"
        )
        self.duplicate_detection.check_duplicate.return_value = duplicate_result

        # Mock AI extraction failure
        self.ai_extraction.extract_receipt_data.side_effect = ValueError("API error")

        # Mock copy operation failure
        self.file_system.copy_file_to_folder.side_effect = OSError("Copy failed")

        # Execute (should not raise exception)
        self.use_case.execute(self.config)

        # Verify error handling continued execution