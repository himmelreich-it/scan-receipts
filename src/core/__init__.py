"""Core module containing domain logic and use cases."""

# Re-export domain entities and use cases at the core level
from .domain import (
    DomainError,
    InvalidReceiptError,
    ProcessingError,
    Receipt,
    is_recent_date,
    is_valid_amount,
    is_valid_confidence,
    is_valid_receipt_file,
    is_valid_vendor,
)
from .use_cases import (
    ImportToXLSXUseCase,
    ProcessReceiptUseCase,
    ViewStagingDataUseCase,
)

__all__ = [
    # Domain
    "Receipt",
    "DomainError",
    "InvalidReceiptError", 
    "ProcessingError",
    "is_valid_receipt_file",
    "is_valid_amount",
    "is_valid_confidence",
    "is_valid_vendor",
    "is_recent_date",
    # Use Cases
    "ProcessReceiptUseCase",
    "ImportToXLSXUseCase",
    "ViewStagingDataUseCase",
]