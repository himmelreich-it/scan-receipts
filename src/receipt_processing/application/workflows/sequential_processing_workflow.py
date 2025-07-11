"""Sequential processing workflow orchestrator."""

import sys
from typing import List

from receipt_processing.domain.repositories.file_system_repository import FileSystemRepository
from receipt_processing.domain.services.file_filtering_service import FileFilteringService
from receipt_processing.domain.services.file_content_reader import FileContentReader
from receipt_processing.domain.models.processable_file import ProcessableFile
from receipt_processing.application.dtos.processing_result import ProcessingResult


class SequentialProcessingWorkflow:
    """Orchestrates the sequential processing of files in a directory."""
    
    def __init__(
        self,
        file_repository: FileSystemRepository,
        filtering_service: FileFilteringService,
        content_reader: FileContentReader
    ):
        self.file_repository = file_repository
        self.filtering_service = filtering_service
        self.content_reader = content_reader
    
    def process_input_directory(self, input_directory: str) -> ProcessingResult:
        """Process all supported files in the input directory."""
        # User Story 1: Input folder scanning and filtering
        try:
            self.file_repository.ensure_directory_exists(input_directory)
        except PermissionError:
            print("Permission denied: cannot access input folder")
            sys.exit(1)
        
        file_paths = self.file_repository.list_files_in_directory(input_directory)
        
        if not file_paths:
            print("No files found in input folder")
            return ProcessingResult([], [], 0)
        
        processable_files = self.filtering_service.filter_supported_files(file_paths)
        
        # User Story 2 & 3: Sequential processing
        successful_files = []
        failed_files = []
        
        try:
            for processable_file in processable_files:
                try:
                    # User Story 2: File content reading
                    self.content_reader.read_file_content(processable_file)
                    
                    if processable_file.processing_status == "error":
                        self._log_file_error(processable_file)
                        failed_files.append(processable_file)
                    else:
                        # File ready for downstream processing
                        processable_file.mark_as_processed()
                        successful_files.append(processable_file)
                        
                except KeyboardInterrupt:
                    print("Processing interrupted by user")
                    sys.exit(0)
                except Exception as e:
                    processable_file.mark_as_error(f"Processing failed: {str(e)}")
                    print(f"Processing failed for {processable_file.file_path.name}: {str(e)}")
                    failed_files.append(processable_file)
        
        except KeyboardInterrupt:
            print("Processing stopped by user")
            sys.exit(0)
        
        return ProcessingResult(successful_files, failed_files, len(processable_files))
    
    def _log_file_error(self, processable_file: ProcessableFile) -> None:
        """Log file processing errors based on error type."""
        error_msg = processable_file.error_message or ""
        filename = processable_file.file_path.name
        
        if "File no longer accessible" in error_msg:
            print(f"File no longer accessible: {filename}")
        elif "Permission denied" in error_msg:
            print(f"Permission denied: {filename}")
        elif "File too large" in error_msg:
            print(f"File too large: {filename}")
        elif "Failed to read file" in error_msg:
            print(f"File corrupted: {filename}")
        else:
            print(f"Invalid file format: {filename}")
    
    def get_processed_files(self) -> List[ProcessableFile]:
        """Interface for downstream components to get processed files."""
        # This would be implemented based on downstream component needs
        # For now, return empty list as interface placeholder
        return []