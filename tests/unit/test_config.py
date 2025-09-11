"""Unit tests for configuration management."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from scan_receipts.config import AppConfig, REQUIRED_ENV_VARS


class TestAppConfig:
    """Test AppConfig class."""
    
    def test_from_env_with_all_variables(self):
        """Test configuration loading with all required variables present."""
        env_vars = {
            "INCOMING_RECEIPTS_FOLDER": "/tmp/incoming",
            "SCANNED_FOLDER": "/tmp/scanned",
            "IMPORTED_FOLDER": "/tmp/imported",
            "FAILED_FOLDER": "/tmp/failed",
            "CSV_STAGING_FILE": "/tmp/receipts.csv",
            "XLSX_OUTPUT_FILE": "/tmp/output.xlsx",
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = AppConfig.from_env()
            
            assert config.incoming_folder == Path("/tmp/incoming")
            assert config.scanned_folder == Path("/tmp/scanned")
            assert config.imported_folder == Path("/tmp/imported")
            assert config.failed_folder == Path("/tmp/failed")
            assert config.csv_staging_file == Path("/tmp/receipts.csv")
            assert config.xlsx_output_file == Path("/tmp/output.xlsx")
    
    def test_from_env_missing_single_variable(self):
        """Test configuration loading fails when one variable is missing."""
        env_vars = {
            "INCOMING_RECEIPTS_FOLDER": "/tmp/incoming",
            "SCANNED_FOLDER": "/tmp/scanned",
            "IMPORTED_FOLDER": "/tmp/imported",
            "FAILED_FOLDER": "/tmp/failed",
            "CSV_STAGING_FILE": "/tmp/receipts.csv",
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError) as exc_info:
                AppConfig.from_env()
            
            assert "Missing environment variables: XLSX_OUTPUT_FILE" in str(exc_info.value)
    
    def test_from_env_missing_multiple_variables(self):
        """Test configuration loading fails when multiple variables are missing."""
        env_vars = {
            "INCOMING_RECEIPTS_FOLDER": "/tmp/incoming",
            "IMPORTED_FOLDER": "/tmp/imported",
            "CSV_STAGING_FILE": "/tmp/receipts.csv",
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError) as exc_info:
                AppConfig.from_env()
            
            error_msg = str(exc_info.value)
            assert "Missing environment variables:" in error_msg
            assert "SCANNED_FOLDER" in error_msg
            assert "FAILED_FOLDER" in error_msg
            assert "XLSX_OUTPUT_FILE" in error_msg
    
    def test_from_env_all_missing(self):
        """Test configuration loading fails when all variables are missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                AppConfig.from_env()
            
            error_msg = str(exc_info.value)
            for var in REQUIRED_ENV_VARS:
                assert var in error_msg
    
    def test_config_immutability(self):
        """Test that AppConfig is immutable."""
        env_vars = {
            "INCOMING_RECEIPTS_FOLDER": "/tmp/incoming",
            "SCANNED_FOLDER": "/tmp/scanned",
            "IMPORTED_FOLDER": "/tmp/imported",
            "FAILED_FOLDER": "/tmp/failed",
            "CSV_STAGING_FILE": "/tmp/receipts.csv",
            "XLSX_OUTPUT_FILE": "/tmp/output.xlsx",
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = AppConfig.from_env()
            
            with pytest.raises(AttributeError):
                config.incoming_folder = Path("/new/path")  # type: ignore