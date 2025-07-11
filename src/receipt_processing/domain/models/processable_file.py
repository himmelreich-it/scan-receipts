"""ProcessableFile entity for receipt processing."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .file_path import FilePath
from .file_extension import FileExtension
from .file_content import FileContent


@dataclass
class ProcessableFile:
    """Entity representing a file that can be processed."""
    
    file_path: FilePath
    extension: FileExtension
    content: Optional[FileContent] = None
    processing_status: str = "pending"  # pending, processed, error
    error_message: Optional[str] = None
    processed_at: Optional[datetime] = None
    
    def mark_as_processed(self) -> None:
        """Mark the file as successfully processed."""
        self.processing_status = "processed"
        self.processed_at = datetime.now()
    
    def mark_as_error(self, error_message: str) -> None:
        """Mark the file as having an error during processing."""
        self.processing_status = "error"
        self.error_message = error_message
        self.processed_at = datetime.now()
    
    def is_ready_for_processing(self) -> bool:
        """Check if the file is ready for processing."""
        return self.content is not None and self.processing_status == "pending"