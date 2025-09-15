"""Unit tests for ProcessReceiptUseCase."""

from pathlib import Path
from unittest.mock import Mock

from core.use_cases.process_receipt import ProcessReceiptUseCase


class TestProcessReceiptUseCase:
    """Test ProcessReceiptUseCase functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.file_system_mock = Mock()
        self.ai_extraction_mock = Mock()
        self.csv_mock = Mock()
        self.use_case = ProcessReceiptUseCase(
            self.file_system_mock,
            self.ai_extraction_mock,
            self.csv_mock
        )

    def test_execute_no_files(self, tmp_path: Path):
        """Test execute when no files are found."""
        config_mock = Mock()
        config_mock.incoming_folder = tmp_path / "incoming"
        config_mock.scanned_folder = tmp_path / "scanned"

        # Mock empty file list
        self.file_system_mock.get_supported_files.return_value = []

        self.use_case.execute(config_mock)

        # Verify file system calls
        self.file_system_mock.get_supported_files.assert_called_once_with(
            config_mock.incoming_folder
        )
        # Should not call other methods when no files
        self.file_system_mock.remove_file_if_exists.assert_not_called()
        self.file_system_mock.clear_folder.assert_not_called()

    def test_execute_with_files(self, tmp_path: Path):
        """Test execute with files present."""
        config_mock = Mock()
        config_mock.incoming_folder = tmp_path / "incoming"
        config_mock.scanned_folder = tmp_path / "scanned"

        # Mock file list
        test_files = [
            tmp_path / "receipt1.pdf",
            tmp_path / "receipt2.jpg"
        ]
        self.file_system_mock.get_supported_files.return_value = test_files
        self.file_system_mock.remove_file_if_exists.return_value = True

        self.use_case.execute(config_mock)

        # Verify file system calls
        self.file_system_mock.get_supported_files.assert_called_once_with(
            config_mock.incoming_folder
        )

        # Should clear receipts.csv
        self.file_system_mock.remove_file_if_exists.assert_called_once_with(
            config_mock.csv_staging_file
        )

        # Should clear scanned folder
        self.file_system_mock.clear_folder.assert_called_once_with(
            config_mock.scanned_folder
        )

    def test_execute_handles_missing_receipts_csv(self, tmp_path: Path):
        """Test execute when receipts.csv doesn't exist."""
        config_mock = Mock()
        config_mock.incoming_folder = tmp_path / "incoming"
        config_mock.scanned_folder = tmp_path / "scanned"

        # Mock file list
        test_files = [tmp_path / "receipt1.pdf"]
        self.file_system_mock.get_supported_files.return_value = test_files
        self.file_system_mock.remove_file_if_exists.return_value = False

        self.use_case.execute(config_mock)

        # Should still attempt to remove receipts.csv
        self.file_system_mock.remove_file_if_exists.assert_called_once_with(
            config_mock.csv_staging_file
        )