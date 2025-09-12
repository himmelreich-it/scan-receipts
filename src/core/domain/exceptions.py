"""Domain exceptions."""


class DomainError(Exception):
    """Base exception for domain errors."""
    pass


class InvalidReceiptError(DomainError):
    """Raised when receipt data is invalid."""
    pass


class ProcessingError(DomainError):
    """Raised when receipt processing fails."""
    pass