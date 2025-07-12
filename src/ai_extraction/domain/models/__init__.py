"""Domain models for AI extraction."""

from .extraction_request import ImageExtractionRequest
from .extraction_result import ReceiptData, ErrorReceiptData, ExtractionResult

__all__ = [
    "ImageExtractionRequest",
    "ReceiptData",
    "ErrorReceiptData", 
    "ExtractionResult",
]