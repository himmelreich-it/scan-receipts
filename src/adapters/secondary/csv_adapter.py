"""CSV adapter implementation."""

import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from core.domain import Receipt
from ports import CSVPort, StagingInfo

logger = logging.getLogger(__name__)


class CSVAdapter(CSVPort):
    """CSV adapter implementation."""

    def get_staging_info(self, csv_path: Path) -> Optional[StagingInfo]:
        """Get information about staging CSV file.
        
        Args:
            csv_path: Path to CSV file.
            
        Returns:
            StagingInfo if file exists, None otherwise.
        """
        if not csv_path.exists():
            return None
        
        try:
            modified_time = datetime.fromtimestamp(csv_path.stat().st_mtime)
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                lines = list(reader)
                # Subtract 1 for header row, but ensure it's not negative
                entry_count = max(0, len(lines) - 1) if lines else 0
            
            return StagingInfo(
                file_path=csv_path,
                modified_time=modified_time,
                entry_count=entry_count
            )
        except Exception as e:
            logger.error(f"Error getting staging info for {csv_path}: {e}")
            return None

    def save_receipt_data(self, receipts: list[Receipt], csv_path: Path) -> None:
        """Save receipt data to CSV file.
        
        Args:
            receipts: List of receipts to save.
            csv_path: Path to CSV file.
        """
        if not receipts:
            logger.warning("No receipts to save")
            return
        
        try:
            # Ensure parent directory exists
            csv_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if file exists to determine if we need header
            write_header = not csv_path.exists()
            
            with open(csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                if write_header:
                    writer.writerow(['filename', 'vendor', 'total', 'date', 'confidence'])
                
                for receipt in receipts:
                    writer.writerow([
                        receipt.filename,
                        receipt.vendor or '',
                        receipt.total or '',
                        receipt.date.isoformat() if receipt.date else '',
                        receipt.confidence or '',
                    ])
            
            logger.info(f"Saved {len(receipts)} receipts to {csv_path}")
            
        except Exception as e:
            logger.error(f"Error saving receipts to {csv_path}: {e}")
            raise