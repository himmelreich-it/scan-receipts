"""CSV-based repository for receipt data persistence."""

import csv
import logging
from pathlib import Path
from typing import Set
from ..application.ports import ReceiptRepositoryPort
from ..domain.entities import Receipt


logger = logging.getLogger(__name__)


class CsvRepositoryAdapter(ReceiptRepositoryPort):
    """Adapter for CSV-based receipt data persistence."""

    def __init__(self, csv_file_path: str = "receipts.csv"):
        """Initialize CSV repository.

        Args:
            csv_file_path: Path to CSV file for data storage
        """
        self.csv_file_path = Path(csv_file_path)
        self.fieldnames = [
            "ID",
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
        self._current_id = 1
        self._processed_hashes: Set[str] = set()

        # Initialize CSV file if it doesn't exist
        self._initialize_csv_file()

    def save_receipt(self, receipt: Receipt) -> None:
        """Save receipt to CSV file.

        Args:
            receipt: Receipt entity to save
        """
        try:
            # Skip saving duplicates to CSV
            if receipt.processing_status.value == "duplicate":
                return

            csv_row = receipt.to_csv_row()
            csv_row["ID"] = self._current_id

            # Write to CSV file
            with open(self.csv_file_path, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                writer.writerow(csv_row)

            # Update tracking
            self._processed_hashes.add(receipt.file_hash)
            self._current_id += 1

            logger.debug(f"Saved receipt to CSV: {receipt.file_path}")

        except Exception as e:
            logger.error(f"Failed to save receipt to CSV: {e}")
            raise

    def get_processed_hashes(self) -> Set[str]:
        """Get set of all processed file hashes.

        Returns:
            Set of file hashes that have been processed
        """
        return self._processed_hashes.copy()

    def _initialize_csv_file(self) -> None:
        """Initialize CSV file with headers if it doesn't exist."""
        try:
            if not self.csv_file_path.exists():
                with open(
                    self.csv_file_path, "w", newline="", encoding="utf-8"
                ) as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                    writer.writeheader()
                logger.info(f"Created new CSV file: {self.csv_file_path}")
            else:
                # Load existing hashes if file exists
                self._load_existing_hashes()
        except Exception as e:
            logger.error(f"Failed to initialize CSV file: {e}")
            raise

    def _load_existing_hashes(self) -> None:
        """Load existing hashes from CSV file to prevent duplicates."""
        try:
            max_id = 0
            with open(self.csv_file_path, "r", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if "Hash" in row and row["Hash"]:
                        self._processed_hashes.add(row["Hash"])
                    if "ID" in row and row["ID"].isdigit():
                        max_id = max(max_id, int(row["ID"]))

            # Set next ID to continue sequence
            self._current_id = max_id + 1

            logger.debug(
                f"Loaded {len(self._processed_hashes)} existing hashes, next ID: {self._current_id}"
            )

        except Exception as e:
            logger.warning(f"Could not load existing hashes: {e}")
            # Continue with empty set and ID 1
            self._processed_hashes = set()
            self._current_id = 1

    def reset(self) -> None:
        """Reset CSV file and internal state (for fresh processing)."""
        try:
            if self.csv_file_path.exists():
                self.csv_file_path.unlink()

            self._processed_hashes = set()
            self._current_id = 1
            self._initialize_csv_file()

            logger.info("CSV repository reset for fresh processing")

        except Exception as e:
            logger.error(f"Failed to reset CSV repository: {e}")
            raise
