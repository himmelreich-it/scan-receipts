"""Integration tests for the TUI application."""

import csv
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from scan_receipts.config import AppConfig
from scan_receipts.folders import count_receipt_files, create_folders, get_staging_info


class TestTUIIntegration:
    """Integration tests for TUI components."""
    
    def test_full_configuration_and_folder_creation(self):
        """Test complete configuration loading and folder creation flow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_vars = {
                "INCOMING_RECEIPTS_FOLDER": f"{tmpdir}/incoming",
                "SCANNED_FOLDER": f"{tmpdir}/scanned",
                "IMPORTED_FOLDER": f"{tmpdir}/imported",
                "FAILED_FOLDER": f"{tmpdir}/failed",
                "CSV_STAGING_FILE": f"{tmpdir}/receipts.csv",
                "XLSX_OUTPUT_FILE": f"{tmpdir}/output.xlsx",
            }
            
            with patch.dict(os.environ, env_vars, clear=True):
                config = AppConfig.from_env(load_dotenv_file=False)
                create_folders(config)
                
                assert config.incoming_folder.exists()
                assert config.scanned_folder.exists()
                assert config.imported_folder.exists()
                assert config.failed_folder.exists()
    
    def test_startup_display_with_no_data(self):
        """Test startup display when no files or staging data exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = AppConfig(
                incoming_folder=Path(tmpdir) / "incoming",
                scanned_folder=Path(tmpdir) / "scanned",
                imported_folder=Path(tmpdir) / "imported",
                failed_folder=Path(tmpdir) / "failed",
                csv_staging_file=Path(tmpdir) / "receipts.csv",
                xlsx_output_file=Path(tmpdir) / "output.xlsx",
            )
            
            create_folders(config)
            
            assert count_receipt_files(config.incoming_folder) == 0
            assert count_receipt_files(config.failed_folder) == 0
            assert get_staging_info(config.csv_staging_file) is None
    
    def test_startup_display_with_files_and_staging(self):
        """Test startup display with receipt files and staging data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = AppConfig(
                incoming_folder=Path(tmpdir) / "incoming",
                scanned_folder=Path(tmpdir) / "scanned",
                imported_folder=Path(tmpdir) / "imported",
                failed_folder=Path(tmpdir) / "failed",
                csv_staging_file=Path(tmpdir) / "receipts.csv",
                xlsx_output_file=Path(tmpdir) / "output.xlsx",
            )
            
            create_folders(config)
            
            for i in range(15):
                (config.incoming_folder / f"receipt{i}.pdf").touch()
            
            (config.failed_folder / "failed1.jpg").touch()
            (config.failed_folder / "failed2.png").touch()
            
            with open(config.csv_staging_file, 'w') as f:
                writer = csv.writer(f)
                writer.writerow(["Amount", "Tax", "Description", "Date"])
                for i in range(8):
                    writer.writerow([f"{100+i}.00", "19.00", f"Purchase {i}", "2025-01-15"])
            
            assert count_receipt_files(config.incoming_folder) == 15
            assert count_receipt_files(config.failed_folder) == 2
            
            staging_info = get_staging_info(config.csv_staging_file)
            assert staging_info is not None
            assert staging_info.entry_count == 8
    
    def test_environment_validation_fail_fast(self):
        """Test that application fails fast with missing environment variables."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                AppConfig.from_env(load_dotenv_file=False)
            
            error_msg = str(exc_info.value)
            assert "Missing environment variables:" in error_msg
            assert "INCOMING_RECEIPTS_FOLDER" in error_msg
            assert "SCANNED_FOLDER" in error_msg
            assert "IMPORTED_FOLDER" in error_msg
            assert "FAILED_FOLDER" in error_msg
            assert "CSV_STAGING_FILE" in error_msg
            assert "XLSX_OUTPUT_FILE" in error_msg
    
    def test_folder_creation_with_permissions_error(self):
        """Test error handling when folder creation fails."""
        config = AppConfig(
            incoming_folder=Path("/root/incoming"),
            scanned_folder=Path("/root/scanned"),
            imported_folder=Path("/root/imported"),
            failed_folder=Path("/root/failed"),
            csv_staging_file=Path("/tmp/receipts.csv"),
            xlsx_output_file=Path("/tmp/output.xlsx"),
        )
        
        with pytest.raises(OSError) as exc_info:
            create_folders(config)
        
        assert "Failed to create folder" in str(exc_info.value)