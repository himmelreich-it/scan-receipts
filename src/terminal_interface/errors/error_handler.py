"""Error display and logging for file processing failures."""

import sys
from typing import Optional


class ErrorHandler:
    """Handles error display and logging for file processing failures."""
    
    def __init__(self) -> None:
        """Initialize error handler with zero error count."""
        self.error_count = 0
    
    def display_file_error(self, filename: str, error_message: str) -> None:
        """Display error message for a failed file processing operation.
        
        Args:
            filename: Name of the file that failed to process
            error_message: Description of the error that occurred
            
        Displays format: "ERROR processing filename: error_message"
        """
        # Display error message immediately to console
        print(f"ERROR processing {filename}: {error_message}", file=sys.stderr, flush=True)
        
        # Increment error counter for summary tracking
        self.error_count += 1
    
    def display_processing_error(self, filename: str, exception: Exception) -> None:
        """Display error message for a file processing exception.
        
        Args:
            filename: Name of the file that failed to process
            exception: The exception that occurred during processing
            
        Displays format: "ERROR processing filename: exception_message"
        """
        error_message = str(exception) if exception else "Unknown error"
        self.display_file_error(filename, error_message)
    
    def get_error_count(self) -> int:
        """Get the total number of errors encountered.
        
        Returns:
            Total count of errors that have been logged
        """
        return self.error_count
    
    def reset_error_count(self) -> None:
        """Reset error counter to zero.
        
        Useful for starting a new processing session.
        """
        self.error_count = 0