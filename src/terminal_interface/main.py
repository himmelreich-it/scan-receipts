"""Main script entry point for receipt processing terminal interface."""

import sys
import signal
import logging


def setup_signal_handlers() -> None:
    """Configure signal handlers for graceful shutdown.
    
    Sets up handlers for SIGINT (Ctrl+C) and SIGTERM to allow clean exit.
    """
    def signal_handler(signum, frame):
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
        # PLACEHOLDER: Main processing workflow not yet implemented
        # This will be implemented when the file processing user stories are completed
        logging.warning("UNIMPLEMENTED_DEPENDENCY: main processing workflow from story SCRIPT_EXEC_T1A2 requires file processing stories")
        
        # For now, just display that the script is starting
        print("Receipt processing script started successfully.")
        print("Main processing workflow is not yet implemented.")
        
        # Exit with success code
        sys.exit(0)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()