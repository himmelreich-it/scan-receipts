"""Core domain module."""

from .exceptions import DomainError, InvalidReceiptError, ProcessingError
from .receipt import Receipt
from .validation import (
    is_recent_date,
    is_valid_amount,
    is_valid_confidence,
    is_valid_receipt_file,
    is_valid_vendor,
)

__all__ = [
    "Receipt",
    "DomainError", 
    "InvalidReceiptError",
    "ProcessingError",
    "is_valid_receipt_file",
    "is_valid_amount", 
    "is_valid_confidence",
    "is_valid_vendor",
    "is_recent_date",
]