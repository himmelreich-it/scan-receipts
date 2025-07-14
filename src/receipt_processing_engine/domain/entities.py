"""Core business entities and aggregates."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any
from .value_objects import ExtractionData


class ProcessingStatus(Enum):
    """Processing status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DUPLICATE = "duplicate"


@dataclass
class Receipt:
    """Receipt aggregate root containing file metadata and extraction results."""

    file_path: str
    file_hash: str
    extraction_data: Optional[ExtractionData] = None
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    original_filename: Optional[str] = None

    def mark_as_processed(self, data: ExtractionData) -> None:
        """Mark receipt as successfully processed with extraction data."""
        self.extraction_data = data
        self.processing_status = ProcessingStatus.COMPLETED
        self.error_message = None
        self.error_type = None

    def mark_as_failed(self, error_message: str, error_type: str = "UNKNOWN") -> None:
        """Mark receipt as failed with error message and type."""
        self.processing_status = ProcessingStatus.FAILED
        self.error_message = error_message
        self.error_type = error_type
        self.extraction_data = None

    def mark_as_duplicate(self) -> None:
        """Mark receipt as duplicate."""
        self.processing_status = ProcessingStatus.DUPLICATE
        self.error_message = None
        self.error_type = None
        self.extraction_data = None

    def is_duplicate(self, other_hash: str) -> bool:
        """Check if this receipt is a duplicate of another hash."""
        return self.file_hash == other_hash

    def to_csv_row(self) -> Dict[str, Any]:
        """Convert receipt to CSV row format."""
        import os

        filename = os.path.basename(self.file_path)

        if (
            self.processing_status == ProcessingStatus.COMPLETED
            and self.extraction_data
        ):
            return {
                "Amount": str(self.extraction_data.amount.value),
                "Tax": str(self.extraction_data.tax.value)
                if self.extraction_data.tax
                else "",
                "TaxPercentage": str(self.extraction_data.tax_percentage.value)
                if self.extraction_data.tax_percentage
                else "",
                "Description": self.extraction_data.description.text,
                "Currency": self.extraction_data.currency.code,
                "Date": self.extraction_data.date.to_string(),
                "Confidence": str(self.extraction_data.confidence.score),
                "Hash": self.file_hash,
                "DoneFilename": filename,
            }
        else:
            error_description = self.error_message if self.error_message else "ERROR"
            return {
                "Amount": "0",
                "Tax": "",
                "TaxPercentage": "",
                "Description": error_description,
                "Currency": "",
                "Date": "",
                "Confidence": "0",
                "Hash": self.file_hash,
                "DoneFilename": filename,
            }
