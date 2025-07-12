"""
AI Data Extraction package for receipt processing.

Provides AI-powered extraction of financial data from receipt images
using Anthropic's Claude API with comprehensive error handling.
"""

from .application import ExtractionFacade
from .domain import (
    ImageExtractionRequest,
    ReceiptData,
    ErrorReceiptData,
    ExtractionResult,
    ExtractionError,
    ApiExtractionError,
    FileExtractionError,
    ParseExtractionError,
    UnknownExtractionError,
)

__all__ = [
    'ExtractionFacade',
    'ImageExtractionRequest',
    'ReceiptData',
    'ErrorReceiptData',
    'ExtractionResult',
    'ExtractionError',
    'ApiExtractionError',
    'FileExtractionError',
    'ParseExtractionError',
    'UnknownExtractionError',
]

__version__ = '1.0.0'