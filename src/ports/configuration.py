"""Configuration port definition."""

from abc import ABC, abstractmethod
from pathlib import Path


class ConfigurationPort(ABC):
    """Port for configuration management."""

    @abstractmethod
    def get_incoming_folder(self) -> Path:
        """Get incoming folder path."""
        pass

    @abstractmethod
    def get_scanned_folder(self) -> Path:
        """Get scanned folder path."""
        pass

    @abstractmethod
    def get_imported_folder(self) -> Path:
        """Get imported folder path."""
        pass

    @abstractmethod
    def get_failed_folder(self) -> Path:
        """Get failed folder path."""
        pass

    @abstractmethod
    def get_csv_staging_file(self) -> Path:
        """Get CSV staging file path."""
        pass

    @abstractmethod
    def get_xlsx_output_file(self) -> Path:
        """Get XLSX output file path."""
        pass