"""Use case for viewing staging data."""

from typing import Optional

from core.domain.configuration import AppConfig
from core.domain.receipt import StagingInfo, StagingTableData
from ports.file_system import FileSystemPort
from adapters.secondary.csv_adapter import CSVAdapter


class ViewStagingUseCase:
    """Use case for viewing staging data information."""

    def __init__(
        self, file_system: FileSystemPort, csv_adapter: Optional[CSVAdapter] = None
    ):
        self.file_system = file_system
        self.csv_adapter = csv_adapter or CSVAdapter()

    def execute(self, config: AppConfig) -> Optional[StagingInfo]:
        """Get staging information.

        Args:
            config: Application configuration.

        Returns:
            StagingInfo if staging data exists, None otherwise.
        """
        return self.file_system.get_staging_info(config.csv_staging_file)

    def get_full_table(self, config: AppConfig) -> StagingTableData:
        """Get full staging table data.

        Args:
            config: Application configuration.

        Returns:
            StagingTableData with all receipt records, empty if file doesn't exist.
        """
        return self.csv_adapter.read_staging_table(config.csv_staging_file)
