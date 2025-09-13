"""Use case for processing receipts."""

import logging
from pathlib import Path

from rich import print as rprint

from core.domain.configuration import AppConfig
from core.domain.receipt import RECEIPT_EXTENSIONS
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

    def get_supported_files(self, folder: Path) -> list[Path]:
        """Get list of supported receipt files from folder.

        Args:
            folder: Path to folder to scan

        Returns:
            List of supported file paths
        """
        if not folder.exists():
            return []

        supported_files: list[Path] = []
        for file_path in folder.iterdir():
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in RECEIPT_EXTENSIONS:
                    supported_files.append(file_path)

        return sorted(supported_files)

    def execute(self, config: AppConfig) -> None:
        """Process receipt files from incoming folder.

        Args:
            config: Application configuration.
        """
        logger.info("Starting receipt processing")

        # Get supported files from incoming folder
        supported_files = self.get_supported_files(config.incoming_folder)

        if not supported_files:
            rprint(f"No files in {config.incoming_folder} folder")
            return

        # Clear receipts.csv if it exists
        if config.csv_staging_file.exists():
            config.csv_staging_file.unlink()
            logger.info("Cleared existing receipts.csv")

        # Clear scanned folder when re-running
        if config.scanned_folder.exists():
            for file_path in config.scanned_folder.iterdir():
                if file_path.is_file():
                    file_path.unlink()
            logger.info("Cleared scanned folder")

        # Process each file
        total_files = len(supported_files)
        processed_count = 0
        failed_count = 0

        for i, file_path in enumerate(supported_files, 1):
            rprint(f"Processing {i}/{total_files}: {file_path.name}")

            try:
                # Extract receipt data using AI
                receipt_data = self.ai_extraction.extract_receipt_data(file_path)

                # Save to CSV
                self.csv.append_receipt(config.csv_staging_file, receipt_data)

                # Move processed file to scanned folder
                destination = config.scanned_folder / file_path.name
                self.file_system.move_file(file_path, destination)

                processed_count += 1
                logger.info(f"Successfully processed {file_path.name}")

            except Exception as e:
                logger.error(f"Failed to process {file_path.name}: {e}")

                # Move failed file to failed folder
                try:
                    destination = config.failed_folder / file_path.name
                    self.file_system.move_file(file_path, destination)
                    failed_count += 1
                except Exception as move_error:
                    logger.error(
                        f"Failed to move {file_path.name} to failed folder: {move_error}"
                    )

        # Final message
        if processed_count > 0:
            rprint(f"Successfully processed {processed_count} files")
        if failed_count > 0:
            rprint(f"Failed to process {failed_count} files (moved to failed folder)")

        logger.info(
            f"Receipt processing completed: {processed_count} processed, {failed_count} failed"
        )
