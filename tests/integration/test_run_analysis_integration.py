"""Integration tests for Run Analysis feature."""

from pathlib import Path


from adapters.secondary.csv_adapter import CSVAdapter
from adapters.secondary.file_system_adapter import FileSystemAdapter
from adapters.secondary.anthropic_adapter import AnthropicAdapter
from adapters.secondary.duplicate_detection_adapter import DuplicateDetectionAdapter
from core.domain.configuration import AppConfig
from core.use_cases.process_receipt import ProcessReceiptUseCase


class TestRunAnalysisIntegration:
    """Test Run Analysis feature integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.file_system = FileSystemAdapter()
        self.ai_extraction = AnthropicAdapter()
        self.csv = CSVAdapter()
        self.duplicate_detection = DuplicateDetectionAdapter(self.file_system)
        self.use_case = ProcessReceiptUseCase(
            self.file_system, self.ai_extraction, self.csv, self.duplicate_detection
        )

    def test_run_analysis_no_files(self, tmp_path: Path):
        """Test Run Analysis with no files in incoming folder."""
        config = self._create_test_config(tmp_path)

        # Execute use case
        self.use_case.execute(config)

        # Verify no changes were made
        assert not config.csv_staging_file.exists()
        assert len(list(config.scanned_folder.iterdir())) == 0

    def test_run_analysis_with_files(self, tmp_path: Path):
        """Test Run Analysis with files in incoming folder."""
        config = self._create_test_config(tmp_path)

        # Create test files
        (config.incoming_folder / "receipt1.pdf").touch()
        (config.incoming_folder / "receipt2.jpg").touch()
        (config.incoming_folder / "receipt3.png").touch()
        (config.incoming_folder / "not_supported.txt").touch()

        # Create existing receipts.csv to test removal
        config.csv_staging_file.touch()
        assert config.csv_staging_file.exists()

        # Create files in scanned folder to test clearing
        (config.scanned_folder / "old_file.jpg").touch()

        # Execute use case
        self.use_case.execute(config)

        # Verify receipts.csv was removed
        assert not config.csv_staging_file.exists()

        # Verify scanned folder was cleared
        assert len(list(config.scanned_folder.iterdir())) == 0

        # Verify incoming files still exist (not moved yet in this implementation)
        incoming_files = list(config.incoming_folder.glob("*"))
        supported_files = [
            f for f in incoming_files if f.suffix.lower() in [".pdf", ".jpg", ".png"]
        ]
        assert len(supported_files) == 3

    def test_run_analysis_rerun_scenario(self, tmp_path: Path):
        """Test Re-run Analysis scenario."""
        config = self._create_test_config(tmp_path)

        # Create test files
        (config.incoming_folder / "receipt.pdf").touch()

        # Create existing receipts.csv (re-run scenario)
        config.csv_staging_file.write_text(
            "Amount,Tax,TaxPercentage,Description,Currency,Date,Confidence,Hash,DoneFilename\n"
        )

        # Create files in scanned folder from previous run
        (config.scanned_folder / "previous_receipt.jpg").touch()

        initial_scanned_count = len(list(config.scanned_folder.iterdir()))
        assert initial_scanned_count > 0

        # Execute use case
        self.use_case.execute(config)

        # Verify receipts.csv was removed
        assert not config.csv_staging_file.exists()

        # Verify scanned folder was cleared
        assert len(list(config.scanned_folder.iterdir())) == 0

    def _create_test_config(self, tmp_path: Path) -> AppConfig:
        """Create test configuration."""
        # Create required folders
        incoming = tmp_path / "incoming"
        scanned = tmp_path / "scanned"
        imported = tmp_path / "imported"
        failed = tmp_path / "failed"

        incoming.mkdir()
        scanned.mkdir()
        imported.mkdir()
        failed.mkdir()

        return AppConfig(
            incoming_folder=incoming,
            scanned_folder=scanned,
            imported_folder=imported,
            failed_folder=failed,
            csv_staging_file=tmp_path / "receipts.csv",
            xlsx_output_file=tmp_path / "output.xlsx",
        )
