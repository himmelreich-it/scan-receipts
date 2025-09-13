"""Unit tests for ProcessReceiptUseCase."""

from pathlib import Path
from unittest.mock import Mock, patch
import tempfile


from core.domain.configuration import AppConfig
from core.use_cases.process_receipt import ProcessReceiptUseCase


class TestProcessReceiptUseCase:
    """Test ProcessReceiptUseCase functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_file_system = Mock()
        self.mock_ai_extraction = Mock()
        self.mock_csv = Mock()
        self.use_case = ProcessReceiptUseCase(
            self.mock_file_system, self.mock_ai_extraction, self.mock_csv
        )

        # Create mock config with temporary paths
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config = Mock(spec=AppConfig)
        self.config.incoming_folder = self.temp_dir / "incoming"
        self.config.scanned_folder = self.temp_dir / "scanned"
        self.config.csv_staging_file = self.temp_dir / "receipts.csv"

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_supported_files_empty_folder(self):
        """Test getting supported files from empty folder."""
        non_existent_folder = Path("/path/that/does/not/exist")
        result = self.use_case.get_supported_files(non_existent_folder)
        assert result == []

    def test_get_supported_files_with_supported_extensions(self):
        """Test filtering supported file types."""
        # Create test files
        self.config.incoming_folder.mkdir(parents=True, exist_ok=True)

        # Create supported files
        (self.config.incoming_folder / "receipt1.pdf").touch()
        (self.config.incoming_folder / "receipt2.jpg").touch()
        (self.config.incoming_folder / "receipt3.png").touch()
        (self.config.incoming_folder / "receipt4.jpeg").touch()

        # Create unsupported files
        (self.config.incoming_folder / "document.txt").touch()
        (self.config.incoming_folder / "image.gif").touch()

        result = self.use_case.get_supported_files(self.config.incoming_folder)

        assert len(result) == 4
        assert all(
            f.suffix.lower() in {".pdf", ".jpg", ".png", ".jpeg"} for f in result
        )
        # Check files are sorted
        assert result == sorted(result)

    def test_get_supported_files_case_insensitive(self):
        """Test file extension matching is case insensitive."""
        # Create test files
        self.config.incoming_folder.mkdir(parents=True, exist_ok=True)

        (self.config.incoming_folder / "receipt1.PDF").touch()
        (self.config.incoming_folder / "receipt2.JPG").touch()
        (self.config.incoming_folder / "receipt3.PNG").touch()
        (self.config.incoming_folder / "receipt4.JPEG").touch()

        result = self.use_case.get_supported_files(self.config.incoming_folder)

        assert len(result) == 4
        assert all(
            f.suffix.upper() in {".PDF", ".JPG", ".PNG", ".JPEG"} for f in result
        )

    @patch("core.use_cases.process_receipt.rprint")
    def test_execute_no_files(self, mock_rprint):
        """Test execution when no supported files are found."""
        self.config.incoming_folder.mkdir(parents=True, exist_ok=True)

        self.use_case.execute(self.config)

        mock_rprint.assert_called_with(
            f"No files in {self.config.incoming_folder} folder"
        )

    @patch("core.use_cases.process_receipt.rprint")
    def test_execute_with_files_no_existing_csv(self, mock_rprint):
        """Test execution with files and no existing CSV."""
        # Create test files
        self.config.incoming_folder.mkdir(parents=True, exist_ok=True)
        self.config.scanned_folder.mkdir(parents=True, exist_ok=True)

        (self.config.incoming_folder / "receipt1.pdf").touch()
        (self.config.incoming_folder / "receipt2.jpg").touch()

        self.use_case.execute(self.config)

        # Check progress messages were displayed
        actual_calls = mock_rprint.call_args_list
        assert len(actual_calls) >= 3
        assert any("Processing 1/2: receipt1.pdf" in str(call) for call in actual_calls)
        assert any("Processing 2/2: receipt2.jpg" in str(call) for call in actual_calls)
        # Should show success message instead of TODO
        assert any(
            "Successfully processed 2 files" in str(call) for call in actual_calls
        )

    @patch("core.use_cases.process_receipt.rprint")
    def test_execute_clears_existing_csv(self, mock_rprint):
        """Test that existing CSV is cleared."""
        # Create test files
        self.config.incoming_folder.mkdir(parents=True, exist_ok=True)
        self.config.scanned_folder.mkdir(parents=True, exist_ok=True)

        # Create existing CSV file
        self.config.csv_staging_file.touch()
        assert self.config.csv_staging_file.exists()

        (self.config.incoming_folder / "receipt1.pdf").touch()

        self.use_case.execute(self.config)

        # Check CSV was removed
        assert not self.config.csv_staging_file.exists()

    @patch("core.use_cases.process_receipt.rprint")
    def test_execute_clears_scanned_folder(self, mock_rprint):
        """Test that scanned folder is cleared."""
        # Create test files
        self.config.incoming_folder.mkdir(parents=True, exist_ok=True)
        self.config.scanned_folder.mkdir(parents=True, exist_ok=True)

        # Create files in scanned folder
        (self.config.scanned_folder / "old_receipt1.pdf").touch()
        (self.config.scanned_folder / "old_receipt2.jpg").touch()

        (self.config.incoming_folder / "new_receipt.pdf").touch()

        self.use_case.execute(self.config)

        # Check scanned folder was cleared
        scanned_files = list(self.config.scanned_folder.iterdir())
        assert len(scanned_files) == 0

    @patch("core.use_cases.process_receipt.rprint")
    def test_execute_progress_messages_correct_order(self, mock_rprint):
        """Test that progress messages are displayed in correct order."""
        # Create test files
        self.config.incoming_folder.mkdir(parents=True, exist_ok=True)
        self.config.scanned_folder.mkdir(parents=True, exist_ok=True)

        # Create files with names that should be sorted
        (self.config.incoming_folder / "c_receipt.pdf").touch()
        (self.config.incoming_folder / "a_receipt.jpg").touch()
        (self.config.incoming_folder / "b_receipt.png").touch()

        self.use_case.execute(self.config)

        # Check progress messages were displayed in sorted order
        actual_calls = mock_rprint.call_args_list
        progress_messages = [
            str(call) for call in actual_calls if "Processing" in str(call)
        ]

        assert len(progress_messages) == 3
        assert "a_receipt.jpg" in progress_messages[0]
        assert "b_receipt.png" in progress_messages[1]
        assert "c_receipt.pdf" in progress_messages[2]
