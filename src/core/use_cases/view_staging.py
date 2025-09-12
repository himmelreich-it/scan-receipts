"""Use case for viewing staging data."""

from typing import Optional

from core.domain.configuration import AppConfig
from core.domain.receipt import StagingInfo
from ports.file_system import FileSystemPort


class ViewStagingUseCase:
    """Use case for viewing staging data information."""
    
    def __init__(self, file_system: FileSystemPort):
        self.file_system = file_system
    
    def execute(self, config: AppConfig) -> Optional[StagingInfo]:
        """Get staging information.
        
        Args:
            config: Application configuration.
            
        Returns:
            StagingInfo if staging data exists, None otherwise.
        """
        return self.file_system.get_staging_info(config.csv_staging_file)