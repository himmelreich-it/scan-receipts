"""Use case for processing receipts."""

import logging

from rich import print as rprint

from core.domain.configuration import AppConfig
from ports.ai_extraction import AIExtractionPort
from ports.csv import CSVPort
from ports.file_system import FileSystemPort

logger = logging.getLogger(__name__)


class ProcessReceiptUseCase:
    """Use case for processing receipt files."""

    def __init__(
        self, file_system: FileSystemPort, ai_extraction: AIExtractionPort, csv: CSVPort
    ):
        self.file_system = file_system
        self.ai_extraction = ai_extraction
        self.csv = csv

    def execute(self, config: AppConfig) -> None:
        """Process receipt files from incoming folder.

        Args:
            config: Application configuration.
        """
        logger.info("Starting receipt analysis")

        # Get supported files from incoming folder
        incoming_files = self.file_system.get_supported_files(config.incoming_folder)

        if not incoming_files:
            rprint(f"No files in {config.incoming_folder} folder")
            return

        # Clear receipts.csv if it exists (requirement)
        if self.file_system.remove_file_if_exists(config.csv_staging_file):
            logger.info("Removed existing receipts.csv")

        # Clear scanned folder if re-running
        self.file_system.clear_folder(config.scanned_folder)
        logger.info("Cleared scanned folder")

        # Process each file with progress messages
        total_files = len(incoming_files)
        for i, file_path in enumerate(incoming_files, 1):
            rprint(f"Processing {i}/{total_files}: {file_path.name}")

        # Show completion message
        rprint("TODO: Implement actual processing")
        logger.info("Receipt analysis completed")
