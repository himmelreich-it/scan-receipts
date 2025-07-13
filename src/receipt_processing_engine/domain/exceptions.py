"""Domain-specific exceptions for receipt processing."""


class ReceiptProcessingError(Exception):
    """Base exception for receipt processing errors."""

    pass


class InvalidFileFormatError(ReceiptProcessingError):
    """Exception raised when file format is not supported."""

    pass


class DuplicateFileError(ReceiptProcessingError):
    """Exception raised when duplicate file is detected."""

    pass


class ExtractionValidationError(ReceiptProcessingError):
    """Exception raised when extracted data validation fails."""

    pass
