"""Business rules and domain services."""

import logging
from typing import Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from .exceptions import InvalidFileFormatError, DuplicateFileError


class ProcessingPolicies:
    """Domain service containing business rules and policies."""

    @staticmethod
    def should_process_file(file_path: str, known_hashes: Set[str]) -> bool:
        """Determine if file should be processed based on business rules."""
        import hashlib

        # Calculate file hash locally to avoid circular dependency
        try:
            with open(file_path, "rb") as file:
                file_content = file.read()
            file_hash = hashlib.sha256(file_content).hexdigest()
            return file_hash not in known_hashes
        except Exception:
            return True  # Process file if hash calculation fails

    @staticmethod
    def classify_processing_error(exception: Exception) -> str:
        """Classify processing errors into business categories."""
        if isinstance(exception, InvalidFileFormatError):
            return "UNSUPPORTED_FORMAT"
        elif isinstance(exception, (FileNotFoundError, PermissionError, OSError)):
            return "FILE_CORRUPT"
        elif isinstance(exception, DuplicateFileError):
            return "DUPLICATE"
        elif "api" in str(exception).lower() or "anthropic" in str(exception).lower():
            return "API_FAILURE"
        elif "network" in str(exception).lower() or "timeout" in str(exception).lower():
            return "API_FAILURE"
        else:
            logging.warning(
                f"Unclassified error: {type(exception).__name__}: {exception}"
            )
            return "FILE_CORRUPT"

    @staticmethod
    def is_confidence_acceptable(confidence: int) -> bool:
        """Check if confidence score meets business requirements."""
        return 0 <= confidence <= 100


@dataclass(frozen=True)
class ValidationResult:
    """Result of validation operations."""

    is_valid: bool
    error_message: str = ""


class DateValidationPolicy:
    """Domain service for date validation business rules."""

    @staticmethod
    def validate_date(date: datetime) -> ValidationResult:
        """Validate date is not future and not older than 1 year.

        Business Rules:
        - Date must not be in the future
        - Date must not be older than 1 year from current date
        """
        now = datetime.now()
        one_year_ago = now - timedelta(days=365)

        if date > now:
            return ValidationResult(
                is_valid=False, error_message="Date validation failed: future date"
            )

        if date < one_year_ago:
            return ValidationResult(
                is_valid=False, error_message="Date validation failed: date too old"
            )

        return ValidationResult(is_valid=True)

    @staticmethod
    def is_date_in_future(date: datetime) -> bool:
        """Check if date is in the future."""
        return date > datetime.now()

    @staticmethod
    def is_date_too_old(date: datetime) -> bool:
        """Check if date is older than 1 year."""
        one_year_ago = datetime.now() - timedelta(days=365)
        return date < one_year_ago
