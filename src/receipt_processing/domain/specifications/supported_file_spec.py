"""Specification for supported file extensions."""

from typing import List

from ..models.file_extension import FileExtension


class SupportedFileExtensionSpecification:
    """Specification that determines if a file extension is supported."""
    
    def __init__(self, supported_extensions: List[str]):
        self.supported_extensions = [FileExtension(ext) for ext in supported_extensions]
    
    def is_satisfied_by(self, extension: FileExtension) -> bool:
        """Check if the given extension is supported."""
        return any(ext.matches(extension) for ext in self.supported_extensions)