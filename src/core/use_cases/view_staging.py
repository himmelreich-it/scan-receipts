"""View staging data use case."""

import logging
from pathlib import Path
from typing import List, Optional

from core.domain import Receipt
from ports import CSVPort, StagingInfo

logger = logging.getLogger(__name__)


class ViewStagingDataUseCase:
    """Use case for viewing staged receipt data."""

    def __init__(self, csv_port: CSVPort):
        self._csv = csv_port

    def get_staging_summary(self, staging_csv: Path) -> Optional[StagingInfo]:
        """Get summary information about staging data.
        
        Args:
            staging_csv: Path to staging CSV file.
            
        Returns:
            StagingInfo if file exists, None otherwise.
        """
        logger.info("Getting staging data summary")
        return self._csv.get_staging_info(staging_csv)

    def get_staging_data(self, staging_csv: Path) -> List[Receipt]:
        """Get detailed staging data.
        
        Args:
            staging_csv: Path to staging CSV file.
            
        Returns:
            List of receipts in staging.
        """
        logger.info("Loading detailed staging data")
        
        # TODO: Implement CSV reading of receipts
        logger.warning("CSV receipt reading not yet implemented")
        return []