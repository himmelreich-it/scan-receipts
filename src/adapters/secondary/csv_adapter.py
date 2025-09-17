"""CSV operations adapter implementation."""

import csv
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional

from core.domain.receipt import ReceiptData, StagingTableData
from ports.csv import CSVPort

logger = logging.getLogger(__name__)

# CSV field mappings - centralized to prevent typos and ensure consistency
CSV_FIELD_MAPPINGS = {
    "amount": "Amount",
    "tax": "Tax",
    "tax_percentage": "TaxPercentage",
    "description": "Description",
    "currency": "Currency",
    "date": "Date",
    "confidence": "Confidence",
    "hash": "Hash",
    "done_filename": "DoneFilename",
}

# CSV headers in order
CSV_HEADERS = list(CSV_FIELD_MAPPINGS.values())

# CSV field mappings to prevent typos and ensure consistency
CSV_FIELDS = {
    "amount": "Amount",
    "tax": "Tax",
    "tax_percentage": "TaxPercentage",
    "description": "Description",
    "currency": "Currency",
    "date": "Date",
    "confidence": "Confidence",
    "hash": "Hash",
    "done_filename": "DoneFilename",
}

# CSV headers matching ReceiptData structure
CSV_HEADERS = list(CSV_FIELDS.values())


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
                            amount=row.get(CSV_FIELD_MAPPINGS["amount"], ""),
                            tax=row.get(CSV_FIELD_MAPPINGS["tax"], ""),
                            tax_percentage=row.get(CSV_FIELD_MAPPINGS["tax_percentage"], ""),
                            description=row.get(CSV_FIELD_MAPPINGS["description"], ""),
                            currency=row.get(CSV_FIELD_MAPPINGS["currency"], ""),
                            date=row.get(CSV_FIELD_MAPPINGS["date"], ""),
                            confidence=row.get(CSV_FIELD_MAPPINGS["confidence"], ""),
                            hash=row.get(CSV_FIELD_MAPPINGS["hash"], ""),
                            done_filename=row.get(CSV_FIELD_MAPPINGS["done_filename"], ""),
                            amount=row.get(CSV_FIELDS["amount"], ""),
                            tax=row.get(CSV_FIELDS["tax"], ""),
                            tax_percentage=row.get(CSV_FIELDS["tax_percentage"], ""),
                            description=row.get(CSV_FIELDS["description"], ""),
                            currency=row.get(CSV_FIELDS["currency"], ""),
                            date=row.get(CSV_FIELDS["date"], ""),
                            confidence=row.get(CSV_FIELDS["confidence"], ""),
                            hash=row.get(CSV_FIELDS["hash"], ""),
                            done_filename=row.get(CSV_FIELDS["done_filename"], ""),
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

    def append_receipt_data(
        self, csv_path: Path, receipt_data: Dict[str, str], file_hash: str, filename: str
    ) -> None:
        """Append receipt data to CSV file.

        Args:
            csv_path: Path to CSV file.
            receipt_data: Extracted receipt data containing amount, tax, etc.
            file_hash: Hash of the processed file.
            filename: Name of the processed file.
        """
        try:
            # Check if file exists to determine if we need headers
            file_exists = csv_path.exists()

            # Prepare row data using centralized field mappings
            row_data = {
                CSV_FIELD_MAPPINGS["amount"]: receipt_data.get("amount", ""),
                CSV_FIELD_MAPPINGS["tax"]: receipt_data.get("tax", ""),
                CSV_FIELD_MAPPINGS["tax_percentage"]: receipt_data.get("tax_percentage", ""),
                CSV_FIELD_MAPPINGS["description"]: receipt_data.get("description", ""),
                CSV_FIELD_MAPPINGS["currency"]: receipt_data.get("currency", ""),
                CSV_FIELD_MAPPINGS["date"]: receipt_data.get("date", ""),
                CSV_FIELD_MAPPINGS["confidence"]: receipt_data.get("confidence", ""),
                CSV_FIELD_MAPPINGS["hash"]: file_hash,
                CSV_FIELD_MAPPINGS["done_filename"]: filename,
            }

            # Ensure parent directory exists
            csv_path.parent.mkdir(parents=True, exist_ok=True)

            # Append to CSV file
            with open(csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)

                # Write headers if file is new
                if not file_exists:
                    writer.writeheader()

                # Write row data
                writer.writerow(row_data)

            logger.info(f"Appended receipt data to CSV: {filename}")

        except Exception as e:
            logger.error(f"Error appending to CSV file: {e}")
            raise ValueError(f"Failed to write to CSV: {e}")

    def append_receipt_data(
        self, csv_path: Path, receipt_data: Dict[str, str], file_hash: str, filename: str
    ) -> None:
        """Append receipt data to CSV file.

        Args:
            csv_path: Path to CSV file.
            receipt_data: Extracted receipt data containing amount, tax, etc.
            file_hash: Hash of the processed file.
            filename: Name of the processed file.
        """
        try:
            # Check if file exists to determine if we need headers
            file_exists = csv_path.exists()

            # Prepare row data using centralized field mappings
            row_data = {
                CSV_FIELDS["amount"]: receipt_data.get("amount", ""),
                CSV_FIELDS["tax"]: receipt_data.get("tax", ""),
                CSV_FIELDS["tax_percentage"]: receipt_data.get("tax_percentage", ""),
                CSV_FIELDS["description"]: receipt_data.get("description", ""),
                CSV_FIELDS["currency"]: receipt_data.get("currency", ""),
                CSV_FIELDS["date"]: receipt_data.get("date", ""),
                CSV_FIELDS["confidence"]: receipt_data.get("confidence", ""),
                CSV_FIELDS["hash"]: file_hash,
                CSV_FIELDS["done_filename"]: filename,
            }

            # Ensure parent directory exists
            csv_path.parent.mkdir(parents=True, exist_ok=True)

            # Append to CSV file
            with open(csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)

                # Write headers if file is new
                if not file_exists:
                    writer.writeheader()

                # Write row data
                writer.writerow(row_data)

            logger.info(f"Appended receipt data to CSV: {filename}")

        except Exception as e:
            logger.error(f"Error appending to CSV file: {e}")
            raise ValueError(f"Failed to write to CSV: {e}")