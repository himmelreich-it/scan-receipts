"""Main script entry point for receipt processing terminal interface."""

import sys
import signal
import logging
import time
from .display.messages import display_startup_message
from .display.progress_display import ProgressDisplay
from .display.summary_display import SummaryDisplay
from .errors.error_handler import ErrorHandler


def setup_signal_handlers() -> None:
    """Configure signal handlers for graceful shutdown.
    
    Sets up handlers for SIGINT (Ctrl+C) and SIGTERM to allow clean exit.
    """
    def signal_handler(signum, frame):
        del signum, frame  # Unused parameters
        print("\nOperation cancelled by user.")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main() -> None:
    """Main entry point for receipt processing script.
    
    Handles script execution with proper exception handling and exit codes.
    Provides clean entry point following if __name__ == "__main__" pattern.
    
    Returns:
        None
        
    Raises:
        SystemExit: With code 0 for success, 1 for errors
    """
    setup_signal_handlers()
    
    try:
        # Display startup message before processing begins
        display_startup_message()
        
        # PLACEHOLDER: Main processing workflow not yet implemented
        # This will be implemented when the file processing user stories are completed
        logging.warning("UNIMPLEMENTED_DEPENDENCY: main processing workflow from story SCRIPT_EXEC_T1A2 requires file processing stories")
        
        # Mock demonstration of complete terminal interface functionality
        # This shows how all components work together in the real implementation
        mock_files = ["receipt1.pdf", "receipt2.jpg", "receipt3.png", "very_long_filename_that_exceeds_normal_length.pdf", "corrupted_file.pdf", "duplicate_receipt.pdf"]
        print(f"Mock processing demonstration with {len(mock_files)} files:")
        
        progress = ProgressDisplay(len(mock_files))
        error_handler = ErrorHandler()
        summary = SummaryDisplay()
        
        processed_count = 0
        duplicate_count = 0
        
        for i, filename in enumerate(mock_files, 1):
            progress.display_file_progress(i, filename)
            time.sleep(0.3)  # Brief pause to simulate processing
            
            # Mock processing scenarios for demonstration
            if filename == "corrupted_file.pdf":
                error_handler.display_file_error(filename, "File corrupted or unreadable")
            elif filename == "very_long_filename_that_exceeds_normal_length.pdf":
                error_handler.display_processing_error(filename, ValueError("Invalid file format"))
            elif filename == "duplicate_receipt.pdf":
                print(f"DUPLICATE: {filename} already processed, skipping")
                duplicate_count += 1
            else:
                processed_count += 1
        
        print("Mock processing complete.")
        
        # Display comprehensive summary
        summary.set_counters(processed_count, error_handler.get_error_count(), duplicate_count)
        summary.display_summary()
        
        # Exit with success code
        sys.exit(0)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()