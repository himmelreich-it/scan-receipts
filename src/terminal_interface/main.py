"""Main script entry point for receipt processing terminal interface."""

import sys
import signal
from terminal_interface.display.messages import display_startup_message
from terminal_interface.display.summary_display import SummaryDisplay
from cleanup.cleaner import CleanupManager
from receipt_processing import (
    SequentialProcessingWorkflow,
    LocalFileRepository,
    FileFilteringService,
    FileContentReader,
    SupportedFileExtensionSpecification,
    FileProcessingConfig
)


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

        # Execute cleanup operations before processing begins
        cleanup_manager = CleanupManager("done", "receipts.csv")
        cleanup_manager.execute_cleanup()

        # Initialize receipt processing workflow
        config = FileProcessingConfig()
        repository = LocalFileRepository()
        spec = SupportedFileExtensionSpecification(config.get_supported_extensions())
        filtering_service = FileFilteringService(spec)
        content_reader = FileContentReader()
        
        workflow = SequentialProcessingWorkflow(
            repository,
            filtering_service,
            content_reader
        )

        # Execute receipt processing workflow
        input_directory = config.get_input_directory()
        result = workflow.process_input_directory(input_directory)

        # Display results using terminal interface components
        if result.total_processed > 0:
            print(f"Processing complete: {result.total_processed} files processed")
            
            summary = SummaryDisplay()
            summary.set_counters(
                result.success_count,
                result.error_count,
                0  # No duplicate handling in current implementation
            )
            summary.display_summary()
        else:
            print("No supported files found to process")

        # Exit with success code
        sys.exit(0)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
