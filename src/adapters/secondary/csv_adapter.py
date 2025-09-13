"""CSV operations adapter implementation."""

import csv
import logging
from pathlib import Path
from typing import Any, List, Optional

from core.domain.receipt import ReceiptData, StagingTableData
from ports.csv import CSVPort

logger = logging.getLogger(__name__)


class CSVAdapter(CSVPort):
    """CSV operations implementation."""

    def read_staging_data(self, csv_path: str) -> List[Any]:
        """Read staging data from CSV.

        Args:
            csv_path: Path to CSV file.

        Returns:
            List of staging data records.
        """
        logger.warning("PLACEHOLDER: CSV read_staging_data not yet implemented")
        return []

    def read_staging_table(self, csv_path: Path) -> Optional[StagingTableData]:
        """Read complete staging table data from CSV.

        Args:
            csv_path: Path to CSV file.

        Returns:
            StagingTableData if file exists, None otherwise.
        """
        if not csv_path.exists():
            return StagingTableData(file_path=csv_path, headers=[], receipts=[])

        try:
            receipts: List[ReceiptData] = []
            headers: List[str] = []

            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                if reader.fieldnames:
                    headers = list(reader.fieldnames)

                    for row in reader:
                        receipt = ReceiptData(
                            amount=row.get("Amount", ""),
                            tax=row.get("Tax", ""),
                            tax_percentage=row.get("TaxPercentage", ""),
                            description=row.get("Description", ""),
                            currency=row.get("Currency", ""),
                            date=row.get("Date", ""),
                            confidence=row.get("Confidence", ""),
                            hash=row.get("Hash", ""),
                            done_filename=row.get("DoneFilename", ""),
                        )
                        receipts.append(receipt)

            return StagingTableData(
                file_path=csv_path, headers=headers, receipts=receipts
            )
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            return None

    def write_staging_data(self, csv_path: str, data: List[Any]) -> None:
        """Write staging data to CSV.

        Args:
            csv_path: Path to CSV file.
            data: Data to write.
        """
        logger.warning("PLACEHOLDER: CSV write_staging_data not yet implemented")

    def append_receipt(self, csv_path: Path, receipt_data: ReceiptData) -> None:
        """Append receipt data to CSV file.

        Args:
            csv_path: Path to CSV file.
            receipt_data: Receipt data to append.
        """
        # Ensure the CSV file exists with headers
        file_exists = csv_path.exists()
        headers = [
            "Amount",
            "Tax",
            "TaxPercentage",
            "Description",
            "Currency",
            "Date",
            "Confidence",
            "Hash",
            "DoneFilename",
        ]

        try:
            with open(csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)

                # Write header if file is new
                if not file_exists:
                    writer.writeheader()

                # Write the receipt data
                writer.writerow(
                    {
                        "Amount": receipt_data.amount,
                        "Tax": receipt_data.tax,
                        "TaxPercentage": receipt_data.tax_percentage,
                        "Description": receipt_data.description,
                        "Currency": receipt_data.currency,
                        "Date": receipt_data.date,
                        "Confidence": receipt_data.confidence,
                        "Hash": receipt_data.hash,
                        "DoneFilename": receipt_data.done_filename,
                    }
                )

            logger.info(f"Appended receipt data to {csv_path}")
        except Exception as e:
            logger.error(f"Failed to append receipt to CSV: {e}")
            raise
