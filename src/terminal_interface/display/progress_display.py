"""Real-time progress display during file processing."""


class ProgressDisplay:
    """Manages real-time progress display during file processing."""
    
    def __init__(self, total_files: int) -> None:
        """Initialize progress display with total file count.
        
        Args:
            total_files: Total number of files to process
        """
        self.total_files = total_files
    
    def display_file_progress(self, current_file: int, filename: str) -> None:
        """Display progress for current file being processed.
        
        Args:
            current_file: Current file number (1-based)
            filename: Name of file being processed
            
        Format: "Processing file X of Y: filename"
        """
        # Handle very long filenames by truncating if necessary
        display_filename = filename
        if len(filename) > 80:
            display_filename = filename[:77] + "..."
        
        # Use flush=True for immediate output to handle terminal buffering
        print(f"Processing file {current_file} of {self.total_files}: {display_filename}", flush=True)