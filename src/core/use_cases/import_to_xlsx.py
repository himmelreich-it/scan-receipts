"""Import to XLSX use case."""

import logging
from pathlib import Path
from typing import List

from core.domain import ProcessingError, Receipt
from ports import CSVPort, FileSystemPort, XLSXPort

logger = logging.getLogger(__name__)


class ImportToXLSXUseCase:
    """Use case for importing staged data to XLSX."""

    def __init__(
        self,
        csv_port: CSVPort,
        xlsx_port: XLSXPort,
        file_system_port: FileSystemPort,
    ):
        self._csv = csv_port
        self._xlsx = xlsx_port
        self._file_system = file_system_port

    def execute(
        self,
        staging_csv: Path,
        xlsx_file: Path,
        imported_folder: Path,
    ) -> int:
        """Execute import workflow from staging to XLSX.
        
        Args:
            staging_csv: CSV file with staged data.
            xlsx_file: Target XLSX file.
            imported_folder: Folder for imported receipt files.
            
        Returns:
            Number of receipts imported.
            
        Raises:
            ProcessingError: If import workflow fails.
        """
        logger.info("Starting XLSX import workflow")
        
        staging_info = self._csv.get_staging_info(staging_csv)
        if not staging_info or staging_info.entry_count == 0:
            logger.info("No staging data found for import")
            return 0

        try:
            # Read existing XLSX data to avoid duplicates
            existing_receipts = self._xlsx.read_existing_data(xlsx_file)
            existing_files = {r.filename for r in existing_receipts}
            
            # TODO: Implement CSV reading of receipts
            # For now, this is a placeholder implementation
            logger.warning("CSV receipt reading not yet implemented")
            staging_receipts: List[Receipt] = []
            
            # Filter out duplicates
            new_receipts = [
                r for r in staging_receipts 
                if r.filename not in existing_files
            ]
            
            if new_receipts:
                # Append to XLSX
                self._xlsx.append_receipts(new_receipts, xlsx_file)
                
                # Move receipt files to imported folder
                for receipt in new_receipts:
                    if receipt.file_path.exists():
                        imported_path = imported_folder / receipt.filename
                        self._file_system.move_file(receipt.file_path, imported_path)
                
                logger.info(f"Imported {len(new_receipts)} receipts to XLSX")
                return len(new_receipts)
            else:
                logger.info("No new receipts to import (all duplicates)")
                return 0
                
        except Exception as e:
            logger.error(f"Import workflow failed: {e}")
            raise ProcessingError(f"Failed to import to XLSX: {e}")