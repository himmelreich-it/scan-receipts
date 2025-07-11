"""Processing result data transfer object."""

from dataclasses import dataclass
from typing import List

from receipt_processing.domain.models.processable_file import ProcessableFile


@dataclass
class ProcessingResult:
    """Result of processing files in a directory."""
    
    successful_files: List[ProcessableFile]
    failed_files: List[ProcessableFile]
    total_processed: int
    
    @property
    def success_count(self) -> int:
        """Number of successfully processed files."""
        return len(self.successful_files)
    
    @property
    def error_count(self) -> int:
        """Number of files that failed processing."""
        return len(self.failed_files)