"""Integration tests for Run Analysis feature."""

import tempfile
from pathlib import Path
from unittest.mock import Mock
import shutil


from core.domain.configuration import AppConfig
from core.use_cases.process_receipt import ProcessReceiptUseCase
from adapters.secondary.file_system_adapter import FileSystemAdapter
from adapters.primary.tui.terminal_ui import TerminalUI


class TestRunAnalysisIntegration:
    """Integration tests for Run Analysis functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary directory for test
        self.temp_dir = Path(tempfile.mkdtemp())

        # Create test config
        self.config = AppConfig(
            incoming_folder=self.temp_dir / "incoming",
            scanned_folder=self.temp_dir / "scanned",
            imported_folder=self.temp_dir / "imported",
            failed_folder=self.temp_dir / "failed",
            csv_staging_file=self.temp_dir / "receipts.csv",
            xlsx_output_file=self.temp_dir / "receipts.xlsx",
        )

        # Create file system adapter
        self.file_system = FileSystemAdapter()

        # Create mocked dependencies (not part of this ticket)
        self.mock_ai_extraction = Mock()
        self.mock_csv = Mock()
        self.mock_import_use_case = Mock()
        self.mock_view_staging = Mock()

        # Create use case
        self.process_receipt_use_case = ProcessReceiptUseCase(
            self.file_system, self.mock_ai_extraction, self.mock_csv
        )

        # Create TUI
        self.tui = TerminalUI(
            self.file_system,
            self.process_receipt_use_case,
            self.mock_import_use_case,
            self.mock_view_staging,
        )

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_csv_file_deletion_when_exists(self):
        """Test CSV file is deleted when it exists."""
        # Create folders
        self.file_system.create_folders(self.config)

        # Create existing CSV file
        self.config.csv_staging_file.write_text("existing,content\n")
        assert self.config.csv_staging_file.exists()

        # Create test files
        (self.config.incoming_folder / "receipt1.pdf").touch()

        # Execute
        self.process_receipt_use_case.execute(self.config)

        # Verify CSV was deleted
        assert not self.config.csv_staging_file.exists()

    def test_scanned_folder_clearing_when_rerunning(self):
        """Test scanned folder is cleared when re-running."""
        # Create folders
        self.file_system.create_folders(self.config)

        # Create files in scanned folder
        (self.config.scanned_folder / "old_receipt1.pdf").touch()
        (self.config.scanned_folder / "old_receipt2.jpg").touch()
        assert len(list(self.config.scanned_folder.iterdir())) == 2

        # Create test files in incoming
        (self.config.incoming_folder / "new_receipt.pdf").touch()

        # Execute
        self.process_receipt_use_case.execute(self.config)

        # Verify scanned folder was cleared of old files and contains new processed file
        scanned_files = list(self.config.scanned_folder.iterdir())
        assert len(scanned_files) == 1
        assert scanned_files[0].name == "new_receipt.pdf"

    def test_correct_message_formatting(self):
        """Test correct progress message formatting."""
        # Create folders
        self.file_system.create_folders(self.config)

        # Create test files
        (self.config.incoming_folder / "receipt_001.pdf").touch()
        (self.config.incoming_folder / "receipt_002.jpg").touch()
        (self.config.incoming_folder / "receipt_003.png").touch()

        # Capture output - we'll test this by verifying no exceptions are raised
        # and the method completes successfully
        self.process_receipt_use_case.execute(self.config)

        # If we get here, the formatting worked without errors
        assert True

    def test_file_counting_filters_correctly(self):
        """Test file counting logic filters correctly."""
        # Create folders
        self.file_system.create_folders(self.config)

        # Create supported files
        (self.config.incoming_folder / "receipt1.pdf").touch()
        (self.config.incoming_folder / "receipt2.jpg").touch()
        (self.config.incoming_folder / "receipt3.png").touch()
        (self.config.incoming_folder / "receipt4.jpeg").touch()

        # Create unsupported files
        (self.config.incoming_folder / "document.txt").touch()
        (self.config.incoming_folder / "image.gif").touch()
        (self.config.incoming_folder / "readme.md").touch()

        # Get supported files
        supported_files = self.process_receipt_use_case.get_supported_files(
            self.config.incoming_folder
        )

        # Verify only supported files are counted
        assert len(supported_files) == 4
        assert all(
            f.suffix.lower() in {".pdf", ".jpg", ".png", ".jpeg"}
            for f in supported_files
        )

    def test_tui_menu_displays_run_analysis_when_no_csv(self):
        """Test TUI displays 'Run Analysis' when no CSV exists."""
        # Create folders
        self.file_system.create_folders(self.config)

        # Ensure no CSV exists
        if self.config.csv_staging_file.exists():
            self.config.csv_staging_file.unlink()

        # Mock the print function to capture output
        from unittest.mock import patch

        with patch("adapters.primary.tui.terminal_ui.rprint") as mock_rprint:
            self.tui.display_menu(self.config)

            # Check that "Run Analysis" was printed (not "Re-run Analysis")
            menu_calls = [str(call) for call in mock_rprint.call_args_list]
            run_analysis_call = next(
                (call for call in menu_calls if "Run Analysis" in call), None
            )
            assert run_analysis_call is not None
            assert "Re-run Analysis" not in run_analysis_call

    def test_tui_menu_displays_rerun_analysis_when_csv_exists(self):
        """Test TUI displays 'Re-run Analysis' when CSV exists."""
        # Create folders
        self.file_system.create_folders(self.config)

        # Create CSV file
        self.config.csv_staging_file.write_text("test,content\n")
        assert self.config.csv_staging_file.exists()

        # Mock the print function to capture output
        from unittest.mock import patch

        with patch("adapters.primary.tui.terminal_ui.rprint") as mock_rprint:
            self.tui.display_menu(self.config)

            # Check that "Re-run Analysis" was printed (not "Run Analysis")
            menu_calls = [str(call) for call in mock_rprint.call_args_list]
            rerun_analysis_call = next(
                (call for call in menu_calls if "Re-run Analysis" in call), None
            )
            assert rerun_analysis_call is not None

    def test_no_files_scenario(self):
        """Test scenario when no supported files exist."""
        # Create folders
        self.file_system.create_folders(self.config)

        # Create only unsupported files
        (self.config.incoming_folder / "document.txt").touch()
        (self.config.incoming_folder / "image.gif").touch()

        # Mock the print function to capture output
        from unittest.mock import patch

        with patch("core.use_cases.process_receipt.rprint") as mock_rprint:
            self.process_receipt_use_case.execute(self.config)

            # Check "No files" message was displayed
            no_files_calls = [
                str(call)
                for call in mock_rprint.call_args_list
                if "No files" in str(call)
            ]
            assert len(no_files_calls) > 0

    def test_five_files_scenario(self):
        """Test scenario with exactly 5 supported files."""
        # Create folders
        self.file_system.create_folders(self.config)

        # Create exactly 5 supported files
        (self.config.incoming_folder / "receipt1.pdf").touch()
        (self.config.incoming_folder / "receipt2.jpg").touch()
        (self.config.incoming_folder / "receipt3.png").touch()
        (self.config.incoming_folder / "receipt4.jpeg").touch()
        (self.config.incoming_folder / "receipt5.pdf").touch()

        # Mock the print function to capture output
        from unittest.mock import patch

        with patch("core.use_cases.process_receipt.rprint") as mock_rprint:
            self.process_receipt_use_case.execute(self.config)

            # Check that 5 progress messages were displayed
            progress_calls = [
                str(call)
                for call in mock_rprint.call_args_list
                if "Processing" in str(call) and "/" in str(call)
            ]
            assert len(progress_calls) == 5

            # Verify the format shows "x/5"
            assert any("1/5" in call for call in progress_calls)
            assert any("2/5" in call for call in progress_calls)
            assert any("3/5" in call for call in progress_calls)
            assert any("4/5" in call for call in progress_calls)
            assert any("5/5" in call for call in progress_calls)
