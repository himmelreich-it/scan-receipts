"""Process receipt use case."""

import logging
from pathlib import Path
from typing import List

from core.domain import ProcessingError, Receipt
from ports import AIExtractionPort, CSVPort, FileSystemPort

logger = logging.getLogger(__name__)


class ProcessReceiptUseCase:
    """Use case for processing receipt files."""

    def __init__(
        self,
        file_system_port: FileSystemPort,
        ai_extraction_port: AIExtractionPort,
        csv_port: CSVPort,
    ):
        self._file_system = file_system_port
        self._ai_extraction = ai_extraction_port
        self._csv = csv_port

    def execute(
        self,
        incoming_folder: Path,
        scanned_folder: Path,
        failed_folder: Path,
        staging_csv: Path,
    ) -> List[Receipt]:
        """Execute receipt processing workflow.
        
        Args:
            incoming_folder: Folder containing new receipts.
            scanned_folder: Folder for successfully processed receipts.
            failed_folder: Folder for failed receipts.
            staging_csv: CSV file for staging processed data.
            
        Returns:
            List of successfully processed receipts.
            
        Raises:
            ProcessingError: If processing workflow fails.
        """
        logger.info("Starting receipt processing workflow")
        
        # Get receipt files from incoming folder
        receipt_files = self._file_system.get_receipt_files(incoming_folder)
        if not receipt_files:
            logger.info("No receipt files found in incoming folder")
            return []

        processed_receipts: List[Receipt] = []
        
        for file_path in receipt_files:
            try:
                logger.info(f"Processing receipt: {file_path.name}")
                
                # Extract data using AI
                receipt = self._ai_extraction.extract_receipt_data(file_path)
                
                if receipt.is_valid:
                    # Move to scanned folder
                    scanned_path = scanned_folder / file_path.name
                    self._file_system.move_file(file_path, scanned_path)
                    
                    # Update receipt with new path
                    receipt = Receipt(
                        file_path=scanned_path,
                        total=receipt.total,
                        vendor=receipt.vendor,
                        date=receipt.date,
                        confidence=receipt.confidence,
                    )
                    
                    processed_receipts.append(receipt)
                    logger.info(f"Successfully processed: {file_path.name}")
                    
                else:
                    # Move to failed folder
                    failed_path = failed_folder / file_path.name
                    self._file_system.move_file(file_path, failed_path)
                    logger.warning(f"Invalid receipt data: {file_path.name}")
                    
            except Exception as e:
                # Move to failed folder on any error
                failed_path = failed_folder / file_path.name
                self._file_system.move_file(file_path, failed_path)
                logger.error(f"Failed to process {file_path.name}: {e}")

        if processed_receipts:
            # Save to staging CSV
            try:
                self._csv.save_receipt_data(processed_receipts, staging_csv)
                logger.info(f"Saved {len(processed_receipts)} receipts to staging")
            except Exception as e:
                logger.error(f"Failed to save to staging CSV: {e}")
                raise ProcessingError(f"Failed to save staging data: {e}")
        
        logger.info(f"Processing complete: {len(processed_receipts)} receipts processed")
        return processed_receipts