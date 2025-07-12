"""Domain layer for AI extraction."""

from .models import ImageExtractionRequest, ReceiptData, ErrorReceiptData, ExtractionResult
from .exceptions import (
    ExtractionError,
    ApiExtractionError,
    FileExtractionError,
    ParseExtractionError,
    UnknownExtractionError,
)

__all__ = [
    "ImageExtractionRequest",
    "ReceiptData",
    "ErrorReceiptData",
    "ExtractionResult",
    "ExtractionError",
    "ApiExtractionError",
    "FileExtractionError", 
    "ParseExtractionError",
    "UnknownExtractionError",
]