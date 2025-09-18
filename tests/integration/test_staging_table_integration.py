"""Integration tests for staging table viewing functionality."""

import csv
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from adapters.primary.tui.terminal_ui import TerminalUI
from adapters.secondary.csv_adapter import CSVAdapter
from adapters.secondary.file_system_adapter import FileSystemAdapter
from core.domain.configuration import AppConfig
from core.use_cases.view_staging import ViewStagingUseCase


class TestStagingTableIntegration:
    """Integration tests for the staging table viewing feature."""

    def setup_method(self):
        """Set up test fixtures."""
        self.file_system = FileSystemAdapter()
        self.csv_adapter = CSVAdapter()

        # Mock other use cases that are not under test
        self.mock_process_receipt_use_case = Mock()
        self.mock_import_to_xlsx_use_case = Mock()

        # Create view staging use case with real implementations
        self.view_staging_use_case = ViewStagingUseCase(
            self.file_system, self.csv_adapter
        )

        # Create TUI with real view staging use case
        self.tui = TerminalUI(
            self.file_system,
            self.mock_process_receipt_use_case,
            self.mock_import_to_xlsx_use_case,
            self.view_staging_use_case,
        )

    def test_display_staging_table_file_not_exists(self, capsys: pytest.CaptureFixture[str]):
        """Test displaying staging table when CSV file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "receipts.csv"
            config = Mock(spec=AppConfig)
            config.csv_staging_file = csv_path

            self.tui.display_staging_table(config)

            captured = capsys.readouterr()
            assert "receipts.csv does not exist" in captured.out

    def test_display_staging_table_empty_file(self, capsys: pytest.CaptureFixture[str]):
        """Test displaying staging table with empty CSV file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            csv_path = Path(f.name)
            # Create empty file with just headers
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Amount",
                    "Tax",
                    "TaxPercentage",
                    "Description",
                    "Currency",
                    "Date",
                    "Confidence",
                    "Hash",
                    "DoneFilename",
                ]
            )

        try:
            config = Mock(spec=AppConfig)
            config.csv_staging_file = csv_path

            self.tui.display_staging_table(config)

            captured = capsys.readouterr()
            assert "receipts.csv is empty" in captured.out
        finally:
            csv_path.unlink()

    def test_display_staging_table_with_data(self, capsys: pytest.CaptureFixture[str]):
        """Test displaying staging table with actual data."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            csv_path = Path(f.name)
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "Amount",
                    "Tax",
                    "TaxPercentage",
                    "Description",
                    "Currency",
                    "Date",
                    "Confidence",
                    "Hash",
                    "DoneFilename",
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "Amount": "100.00",
                    "Tax": "10.00",
                    "TaxPercentage": "10",
                    "Description": "Test Receipt",
                    "Currency": "USD",
                    "Date": "2024-01-01",
                    "Confidence": "0.95",
                    "Hash": "abc123def456",
                    "DoneFilename": "receipt_001.pdf",
                }
            )
            writer.writerow(
                {
                    "Amount": "200.00",
                    "Tax": "20.00",
                    "TaxPercentage": "10",
                    "Description": "Another Receipt",
                    "Currency": "EUR",
                    "Date": "2024-01-02",
                    "Confidence": "0.90",
                    "Hash": "def456ghi789",
                    "DoneFilename": "receipt_002.pdf",
                }
            )

        try:
            config = Mock(spec=AppConfig)
            config.csv_staging_file = csv_path

            self.tui.display_staging_table(config)

            captured = capsys.readouterr()
            output = captured.out

            # Check that table is displayed
            assert "Staging Table" in output
            assert "100.00" in output
            assert "200.00" in output
            assert "Test" in output  # Truncated in table display
            assert "Anoth" in output  # Truncated in table display
            assert "USD" in output
            assert "EUR" in output
            assert "Total entries: 2" in output

            # Check that hash is truncated
            assert "abc12" in output
            assert "def45" in output
        finally:
            csv_path.unlink()

    def test_menu_choice_3_triggers_staging_table_display(self, capsys: pytest.CaptureFixture[str]):
        """Test that menu choice 3 triggers staging table display."""
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "nonexistent.csv"

            config = Mock(spec=AppConfig)
            config.csv_staging_file = csv_path

            # Test menu choice 3
            result = self.tui.handle_menu_choice("3", config)

            # Should return True to continue
            assert result is True

            captured = capsys.readouterr()
            assert "receipts.csv does not exist" in captured.out

    def test_end_to_end_flow(self, capsys: pytest.CaptureFixture[str]):
        """Test complete flow from CSV reading to table display."""
        # Create test CSV file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            csv_path = Path(f.name)
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "Amount",
                    "Tax",
                    "TaxPercentage",
                    "Description",
                    "Currency",
                    "Date",
                    "Confidence",
                    "Hash",
                    "DoneFilename",
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "Amount": "50.25",
                    "Tax": "5.25",
                    "TaxPercentage": "10.5",
                    "Description": "Coffee Shop Receipt",
                    "Currency": "USD",
                    "Date": "2024-09-12",
                    "Confidence": "0.98",
                    "Hash": "hash123456789abc",
                    "DoneFilename": "coffee_receipt.pdf",
                }
            )

        try:
            config = Mock(spec=AppConfig)
            config.csv_staging_file = csv_path

            # Test complete flow: get_full_table -> display
            staging_data = self.view_staging_use_case.get_full_table(config)
            assert staging_data is not None
            assert len(staging_data.receipts) == 1
            assert staging_data.receipts[0].amount == "50.25"

            # Test display
            self.tui.display_staging_table(config)

            captured = capsys.readouterr()
            output = captured.out

            assert "50.25" in output
            assert "Coffee" in output  # Truncated in table display
            assert "2024-" in output  # Date might be truncated
            assert "Total entries: 1" in output
        finally:
            csv_path.unlink()
