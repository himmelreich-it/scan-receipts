"""Use case for processing receipts."""

import logging
from typing import List

from rich import print as rprint

from core.domain.configuration import AppConfig
from core.domain.receipt import FileHash
from ports.ai_extraction import AIExtractionPort
from ports.csv import CSVPort
from ports.duplicate_detection import DuplicateDetectionPort
from ports.file_system import FileSystemPort

logger = logging.getLogger(__name__)


class ProcessReceiptUseCase:
    """Use case for processing receipt files."""

    def __init__(
        self,
        file_system: FileSystemPort,
        ai_extraction: AIExtractionPort,
        csv: CSVPort,
        duplicate_detection: DuplicateDetectionPort,
    ):
        self.file_system = file_system
        self.ai_extraction = ai_extraction
        self.csv = csv
        self.duplicate_detection = duplicate_detection

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

        # Get existing file hashes for duplicate detection
        existing_hashes = self._get_existing_hashes(config)

        # Process each file with duplicate detection
        total_files = len(incoming_files)
        processed_count = 0
        duplicate_count = 0
        error_count = 0

        for i, file_path in enumerate(incoming_files, 1):
            rprint(f"Processing {i}/{total_files}: {file_path.name}")

            # Check for duplicates
            duplicate_result = self.duplicate_detection.check_duplicate(
                file_path, existing_hashes
            )

            if duplicate_result.has_error:
                rprint(
                    f"  ❌ Hash calculation failed: {duplicate_result.error_message}"
                )
                error_count += 1
                # Continue processing other files
                continue

            if duplicate_result.is_duplicate:
                location_name = duplicate_result.location_name
                rprint(f"  ⏭️  Duplicate detected in {location_name} folder - skipping")
                duplicate_count += 1
                # Continue to next file without AI analysis
                continue

            # File is not a duplicate - process with AI
            rprint("  🔍 Analyzing with AI...")
            # TODO: Implement AI analysis and CSV staging
            processed_count += 1

        # Show completion summary
        rprint("\n📊 Processing complete:")
        rprint(f"  • Processed: {processed_count}")
        rprint(f"  • Duplicates skipped: {duplicate_count}")
        rprint(f"  • Errors: {error_count}")
        logger.info(
            f"Receipt analysis completed - processed: {processed_count}, "
            f"duplicates: {duplicate_count}, errors: {error_count}"
        )

    def _get_existing_hashes(self, config: AppConfig) -> List[FileHash]:
        """Get file hashes from imported and scanned folders.

        Args:
            config: Application configuration.

        Returns:
            Combined list of file hashes from both folders.
        """
        existing_hashes: List[FileHash] = []

        # Get hashes from imported folder (persistent duplicates)
        imported_hashes = self.file_system.get_file_hashes_from_folder(
            config.imported_folder
        )
        existing_hashes.extend(imported_hashes)
        logger.info(f"Found {len(imported_hashes)} hashes in imported folder")

        # Get hashes from scanned folder (current session)
        scanned_hashes = self.file_system.get_file_hashes_from_folder(
            config.scanned_folder
        )
        existing_hashes.extend(scanned_hashes)
        logger.info(f"Found {len(scanned_hashes)} hashes in scanned folder")

        return existing_hashes
