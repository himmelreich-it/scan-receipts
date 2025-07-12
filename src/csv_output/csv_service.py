"""Service for managing CSV output file operations."""

import csv
import os
import logging
from typing import List
from .config import (
    CSV_FILENAME,
    CSV_HEADERS,
    CSV_ENCODING,
    ERROR_API,
    ERROR_FILE,
    ERROR_PARSE,
    ERROR_UNKNOWN,
)

logger = logging.getLogger(__name__)


class CsvService:
    """Service for managing CSV output file operations."""

    def __init__(self, csv_file_path: str = CSV_FILENAME):
        """
        Initialize CSV service.

        Args:
            csv_file_path: Path to CSV file (default: receipts.csv)
        """
        self.csv_file_path = csv_file_path
        self._next_id = 1

    def ensure_csv_exists(self) -> None:
        """
        Create new CSV file with correct headers.

        Always creates fresh file (assumes existing file removed by cleanup).

        Logs:
            - "Created receipts.csv with headers" on success

        Raises:
            SystemExit(1): If file cannot be created due to permissions
        """
        try:
            with open(
                self.csv_file_path, "w", newline="", encoding=CSV_ENCODING
            ) as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(CSV_HEADERS)
            logger.info("Created receipts.csv with headers")
        except PermissionError as e:
            logger.error(f"Cannot create receipts.csv: {e}")
            raise SystemExit(1)
        except Exception as e:
            logger.error(f"Cannot create receipts.csv: {e}")
            raise SystemExit(1)

    def get_next_id(self) -> int:
        """
        Get next auto-incrementing ID for new record.

        Returns:
            Next ID number (1 for new file, last_id + 1 for records added during current run)
        """
        if not os.path.exists(self.csv_file_path):
            return 1

        try:
            with open(self.csv_file_path, "r", encoding=CSV_ENCODING) as csvfile:
                reader = csv.reader(csvfile)
                rows = list(reader)

                # Skip header row
                if len(rows) <= 1:
                    return 1

                # Get last row's ID
                last_row = rows[-1]
                if last_row and last_row[0].isdigit():
                    return int(last_row[0]) + 1
                else:
                    return 1
        except Exception:
            # If we can't read the file, start with ID 1
            return 1

    def append_record(
        self,
        amount: float,
        tax: float,
        tax_percentage: float,
        description: str,
        currency: str,
        date: str,
        confidence: int,
        hash_value: str,
        done_filename: str,
    ) -> int:
        """
        Append new record to CSV file with auto-generated ID.

        Args:
            amount: Purchase amount (formatted to 2 decimal places)
            tax: Tax amount (formatted to 2 decimal places)
            tax_percentage: Tax percentage (formatted to 2 decimal places)
            description: Business description (CSV-escaped if needed)
            currency: Currency code (e.g., EUR, USD)
            date: Date in dd-MM-YYYY format
            confidence: Confidence score 0-100
            hash_value: File hash for duplicate detection
            done_filename: Timestamped filename in done folder

        Returns:
            ID of the appended record

        Logs:
            - "Added record ID {id} for file {original_filename}" on success
            - "Failed to write record: {error}" on failure (continues processing)
        """
        record_id = self.get_next_id()

        try:
            # Format the record
            formatted_record = [
                str(record_id),
                self._format_currency_field(amount),
                self._format_currency_field(tax),
                self._format_currency_field(tax_percentage),
                self._escape_csv_field(description),
                currency,
                date,
                str(confidence),
                hash_value,
                done_filename,
            ]

            # Append to CSV file
            with open(
                self.csv_file_path, "a", newline="", encoding=CSV_ENCODING
            ) as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(formatted_record)

            # Extract original filename from done filename for logging
            original_filename = self._extract_original_filename(done_filename)
            logger.info(f"Added record ID {record_id} for file {original_filename}")

            return record_id

        except Exception as e:
            logger.error(f"Failed to write record: {e}")
            return record_id  # Return the ID even if write failed for consistency

    def append_error_record(
        self, error_type: str, hash_value: str, done_filename: str
    ) -> int:
        """
        Append error record to CSV file.

        Args:
            error_type: One of ERROR-API, ERROR-FILE, ERROR-PARSE, ERROR-UNKNOWN
            hash_value: File hash
            done_filename: Timestamped filename in done folder

        Returns:
            ID of the appended error record

        Creates record with:
            - amount: 0.00
            - tax: 0.00
            - tax_percentage: 0.00
            - description: error_type
            - currency: "" (empty)
            - date: "" (empty)
            - confidence: 0
        """
        # Validate error type
        valid_errors = {ERROR_API, ERROR_FILE, ERROR_PARSE, ERROR_UNKNOWN}
        if error_type not in valid_errors:
            logger.warning(f"Invalid error type {error_type}, using ERROR-UNKNOWN")
            error_type = ERROR_UNKNOWN

        record_id = self.append_record(
            amount=0.0,
            tax=0.0,
            tax_percentage=0.0,
            description=error_type,
            currency="",
            date="",
            confidence=0,
            hash_value=hash_value,
            done_filename=done_filename,
        )

        # Extract original filename from done filename for logging
        original_filename = self._extract_original_filename(done_filename)
        logger.info(
            f"Added error record ID {record_id} for file {original_filename}: {error_type}"
        )

        return record_id

    def _format_currency_field(self, value: float) -> str:
        """Format currency fields to 2 decimal places."""
        return f"{value:.2f}"

    def _escape_csv_field(self, field: str) -> str:
        """Escape CSV field if contains commas or quotes."""
        # CSV writer handles escaping automatically, so we just return the field as-is
        # The csv.writer will properly quote and escape when needed
        return field

    def _validate_headers(self, existing_headers: List[str]) -> bool:
        """Validate that existing headers match expected format."""
        return existing_headers == CSV_HEADERS

    def _extract_original_filename(self, done_filename: str) -> str:
        """Extract original filename from timestamped done filename."""
        # Done filename format: ID-YYYYMMDD-HHMMSSNNNNNN-original_filename
        # Extract everything after the third dash
        parts = done_filename.split("-", 3)
        if len(parts) >= 4:
            return parts[3]
        else:
            return done_filename  # Return as-is if format is unexpected
