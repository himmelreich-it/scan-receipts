"""XLSX adapter - placeholder implementation."""

import logging
from pathlib import Path

from core.domain import Receipt
from ports import XLSXPort

logger = logging.getLogger(__name__)


class XLSXAdapter(XLSXPort):
    """PLACEHOLDER: Excel file adapter."""

    def append_receipts(self, receipts: list[Receipt], xlsx_path: Path) -> None:
        """PLACEHOLDER: Append receipts to Excel file.
        
        Args:
            receipts: List of receipts to append.
            xlsx_path: Path to Excel file.
        """
        logger.warning(f"PLACEHOLDER: Appending {len(receipts)} receipts to {xlsx_path}")
        
        # Placeholder implementation - would use openpyxl or similar
        logger.info(f"Would append receipts: {[r.filename for r in receipts]}")

    def read_existing_data(self, xlsx_path: Path) -> list[Receipt]:
        """PLACEHOLDER: Read existing receipt data from Excel file.
        
        Args:
            xlsx_path: Path to Excel file.
            
        Returns:
            Empty list as placeholder.
        """
        logger.warning(f"PLACEHOLDER: Reading existing data from {xlsx_path}")
        
        # Placeholder implementation - would read Excel file
        return []