"""Service for filtering files by supported extensions."""

import os
from typing import List

from receipt_processing.domain.models.file_path import FilePath
from receipt_processing.domain.models.file_extension import FileExtension
from receipt_processing.domain.models.processable_file import ProcessableFile
from receipt_processing.domain.specifications.supported_file_spec import SupportedFileExtensionSpecification


class FileFilteringService:
    """Domain service for filtering files by supported extensions."""
    
    def __init__(self, supported_extensions_spec: SupportedFileExtensionSpecification):
        self.supported_extensions_spec = supported_extensions_spec
    
    def filter_supported_files(self, file_paths: List[FilePath]) -> List[ProcessableFile]:
        """Filter file paths to only include supported file types."""
        processable_files = []
        for file_path in file_paths:
            try:
                extension_str = os.path.splitext(file_path.path)[1]
                if extension_str:  # Only process files with extensions
                    extension = FileExtension(extension_str)
                    if self.supported_extensions_spec.is_satisfied_by(extension):
                        processable_files.append(ProcessableFile(file_path, extension))
            except ValueError:
                # Skip files with invalid extensions (no console output per requirements)
                continue
        return processable_files