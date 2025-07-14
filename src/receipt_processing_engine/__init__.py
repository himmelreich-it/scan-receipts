from pathlib import Path

from .domain.entities import Receipt, ProcessingStatus
from .domain.value_objects import ExtractionData, Amount, Currency, Confidence, Description, ReceiptDate
from .domain.exceptions import (
    ReceiptProcessingError,
    InvalidFileFormatError,
    DuplicateFileError,
)
from .application.use_cases import (
    ProcessReceiptUseCase,
    ExtractDataUseCase,
)
from .application.ports import (
    AIExtractionPort,
    FileSystemPort,
    DuplicateDetectionPort,
    ReceiptRepositoryPort,
)
from .infrastructure.anthropic_adapter import AnthropicAIAdapter
from .infrastructure.file_adapter import FileSystemAdapter
from .infrastructure.duplicate_adapter import DuplicateDetectionAdapter


def create_receipt_processor(
    api_key: str,
    done_folder: Path,
    failed_folder: Path,
) -> ProcessReceiptUseCase:
    """Factory function to create configured receipt processor.

    Args:
        api_key: Anthropic API key for Claude integration
        done_folder: Path to folder containing successfully processed receipts
        failed_folder: Path to folder for failed receipts with error logs

    Returns:
        Configured ProcessReceiptUseCase instance
    """
    # Initialize infrastructure adapters
    ai_adapter = AnthropicAIAdapter(api_key)
    file_adapter = FileSystemAdapter(done_folder, failed_folder)
    duplicate_adapter = DuplicateDetectionAdapter()

    # Create and return use case with dependencies
    return ProcessReceiptUseCase(
        ai_extraction=ai_adapter,
        file_system=file_adapter,
        duplicate_detection=duplicate_adapter,
    )


__all__ = [
    "Receipt",
    "ProcessingStatus",
    "ExtractionData",
    "Amount",
    "Currency",
    "Confidence",
    "Description",
    "ReceiptDate",
    "ReceiptProcessingError",
    "InvalidFileFormatError",
    "DuplicateFileError",
    "ProcessReceiptUseCase",
    "ExtractDataUseCase",
    "AIExtractionPort",
    "FileSystemPort",
    "DuplicateDetectionPort",
    "ReceiptRepositoryPort",
    "AnthropicAIAdapter",
    "FileSystemAdapter",
    "DuplicateDetectionAdapter",
    "create_receipt_processor",
]
