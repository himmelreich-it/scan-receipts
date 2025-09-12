"""Use case for processing receipts."""

import logging

from core.domain.configuration import AppConfig
from ports.ai_extraction import AIExtractionPort
from ports.csv import CSVPort
from ports.file_system import FileSystemPort

logger = logging.getLogger(__name__)


class ProcessReceiptUseCase:
    """Use case for processing receipt files."""
    
    def __init__(
        self, 
        file_system: FileSystemPort,
        ai_extraction: AIExtractionPort,
        csv: CSVPort
    ):
        self.file_system = file_system
        self.ai_extraction = ai_extraction
        self.csv = csv
    
    def execute(self, config: AppConfig) -> None:
        """Process receipt files from incoming folder.
        
        Args:
            config: Application configuration.
        """
        logger.info("PLACEHOLDER: Receipt processing not yet implemented")
        # This is a placeholder - actual implementation would:
        # 1. Get files from incoming folder 
        # 2. Extract data using AI
        # 3. Stage data in CSV
        # 4. Move files to appropriate folders