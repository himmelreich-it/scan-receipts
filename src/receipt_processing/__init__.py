"""Receipt Image Processing Feature Package.

This package implements the Receipt Image Processing feature (RECEIPT_IMG_E5F6)
which handles scanning, filtering, reading, and processing receipt images and PDFs.

Feature Components:
- Domain layer: Core business logic and entities
- Application layer: Workflow orchestration and DTOs
- Infrastructure layer: File system adapters and configuration

User Stories Implemented:
- INPUT_SCAN_FILTER_A1B2: Input folder scanning and file filtering
- FILE_READ_PROCESS_C3D4: File content reading and processing  
- SEQ_PROCESS_WORKFLOW_E5F6: Sequential processing workflow management
"""

from .domain import (
    FilePath, FileExtension, FileContent, ProcessableFile,
    FileFilteringService, FileContentReader, SupportedFileExtensionSpecification,
    FileSystemRepository
)
from .infrastructure import FileProcessingConfig, LocalFileRepository
from .application import SequentialProcessingWorkflow, ProcessingResult

__all__ = [
    # Domain models
    "FilePath",
    "FileExtension", 
    "FileContent",
    "ProcessableFile",
    # Domain services
    "FileFilteringService",
    "FileContentReader", 
    "SupportedFileExtensionSpecification",
    "FileSystemRepository",
    # Infrastructure
    "FileProcessingConfig",
    "LocalFileRepository",
    # Application
    "SequentialProcessingWorkflow",
    "ProcessingResult",
]