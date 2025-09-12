"""Environment configuration adapter implementation."""

from pathlib import Path

from ports import ConfigurationPort
from scan_receipts.config import AppConfig


class EnvConfigAdapter(ConfigurationPort):
    """Environment configuration adapter using AppConfig."""

    def __init__(self, config: AppConfig):
        self._config = config

    def get_incoming_folder(self) -> Path:
        """Get incoming folder path."""
        return self._config.incoming_folder

    def get_scanned_folder(self) -> Path:
        """Get scanned folder path."""
        return self._config.scanned_folder

    def get_imported_folder(self) -> Path:
        """Get imported folder path."""
        return self._config.imported_folder

    def get_failed_folder(self) -> Path:
        """Get failed folder path."""
        return self._config.failed_folder

    def get_csv_staging_file(self) -> Path:
        """Get CSV staging file path."""
        return self._config.csv_staging_file

    def get_xlsx_output_file(self) -> Path:
        """Get XLSX output file path."""
        return self._config.xlsx_output_file