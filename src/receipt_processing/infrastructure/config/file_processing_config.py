"""Configuration for file processing operations."""

from typing import List


class FileProcessingConfig:
    """Hardcoded configuration for file processing."""
    
    # Hardcoded configuration as requested
    SUPPORTED_FILE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.pdf']
    INPUT_DIRECTORY = '../input'
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """Get the list of supported file extensions."""
        return cls.SUPPORTED_FILE_EXTENSIONS.copy()
    
    @classmethod
    def get_input_directory(cls) -> str:
        """Get the input directory path."""
        return cls.INPUT_DIRECTORY