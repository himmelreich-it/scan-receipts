"""Console progress reporting and error logging."""

import logging
import sys
from typing import Optional


class ConsoleLogger:
    """Logger for console progress reporting and error messages."""

    def __init__(self, level: str = "INFO"):
        """Initialize console logger with specified level.

        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.logger = logging.getLogger("receipt_processor_console")
        self.logger.setLevel(getattr(logging, level.upper()))

        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, level.upper()))

        # Create formatter
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)
        self.logger.propagate = False

    def log_processing_start(self, filename: str) -> None:
        """Log start of file processing.

        Args:
            filename: Name of file being processed
        """
        self.logger.info(f"Processing: {filename}")

    def log_processing_success(self, filename: str, confidence: int) -> None:
        """Log successful processing completion.

        Args:
            filename: Name of processed file
            confidence: Confidence score from extraction
        """
        self.logger.info(
            f"✓ Successfully processed {filename} (confidence: {confidence}%)"
        )

    def log_processing_error(
        self, filename: str, error_type: str, message: str
    ) -> None:
        """Log processing error.

        Args:
            filename: Name of file that failed
            error_type: Type of error (API_FAILURE, FILE_CORRUPT, etc.)
            message: Error message details
        """
        self.logger.error(f"✗ {error_type} for {filename}: {message}")

    def log_duplicate_skipped(
        self, filename: str, original_filename: Optional[str] = None
    ) -> None:
        """Log when duplicate file is skipped.

        Args:
            filename: Name of duplicate file
            original_filename: Name of original file if known
        """
        if original_filename:
            self.logger.info(
                f"Duplicate file skipped: {filename} (matches {original_filename})"
            )
        else:
            self.logger.info(f"Duplicate file skipped: {filename}")

    def log_summary(
        self, total_files: int, successful: int, errors: int, duplicates: int
    ) -> None:
        """Log processing summary.

        Args:
            total_files: Total number of files processed
            successful: Number of successfully processed files
            errors: Number of files with errors
            duplicates: Number of duplicate files skipped
        """
        self.logger.info("\\nProcessing Summary:")
        self.logger.info(f"  Total files: {total_files}")
        self.logger.info(f"  Successful: {successful}")
        self.logger.info(f"  Errors: {errors}")
        self.logger.info(f"  Duplicates: {duplicates}")

        if errors > 0:
            self.logger.warning(
                f"\\n⚠️  {errors} files had processing errors - check error messages above"
            )

        if successful > 0:
            self.logger.info(f"\\n✅ {successful} files processed successfully")
