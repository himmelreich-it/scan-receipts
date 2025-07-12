"""Main script entry point for receipt processing terminal interface."""

import sys
import signal
import csv
from pathlib import Path
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
from ai_extraction import ExtractionFacade, ImageExtractionRequest


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


def get_next_csv_id(csv_file_path: str) -> int:
    """Get the next available ID for CSV entries."""
    if not Path(csv_file_path).exists():
        return 1
    
    try:
        with open(csv_file_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            max_id = 0
            for row in reader:
                try:
                    current_id = int(row.get('ID', 0))
                    max_id = max(max_id, current_id)
                except (ValueError, TypeError):
                    continue
            return max_id + 1
    except Exception:
        return 1


def write_csv_header(csv_file_path: str) -> None:
    """Write CSV header if file doesn't exist."""
    if not Path(csv_file_path).exists():
        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ID', 'Amount', 'Tax', 'Description', 'Currency', 'Date', 'Confidence', 'Hash'])


def write_extraction_to_csv(extraction_result, csv_file_path: str, file_id: int, file_hash: str) -> None:
    """Write extraction result to CSV file."""
    data = extraction_result.get_data()
    
    with open(csv_file_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            file_id,
            float(data.amount),
            float(data.tax),
            data.description,
            data.currency,
            data.date,
            data.confidence,
            file_hash
        ])


def move_processed_file(source_path: Path, done_directory: str, file_id: int) -> None:
    """Move processed file to done directory with timestamp naming."""
    import shutil
    from datetime import datetime
    
    # Create done directory if it doesn't exist
    done_path = Path(done_directory)
    done_path.mkdir(exist_ok=True)
    
    # Generate timestamp
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S%f')
    
    # Create new filename: {ID}-{timestamp}-{original-filename}
    new_filename = f"{file_id}-{timestamp}-{source_path.name}"
    destination_path = done_path / new_filename
    
    # Move the file
    shutil.move(str(source_path), str(destination_path))


def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash of file for duplicate detection."""
    import hashlib
    
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


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

        # Execute receipt processing workflow to get files
        input_directory = config.get_input_directory()
        result = workflow.process_input_directory(input_directory)

        if result.total_processed == 0:
            print("No supported files found to process")
            sys.exit(0)

        # Initialize AI extraction and CSV processing
        extraction_facade = ExtractionFacade()
        csv_file_path = "receipts.csv"
        
        # Ensure CSV file exists with headers
        write_csv_header(csv_file_path)
        
        # Get starting ID for CSV entries
        current_id = get_next_csv_id(csv_file_path)
        
        # Process each successfully read file with AI extraction
        success_count = 0
        error_count = 0
        duplicate_count = 0
        
        print(f"Starting AI extraction for {len(result.successful_files)} files...")
        
        for processable_file in result.successful_files:
            try:
                print(f"Processing {processable_file.file_path.name}...")
                
                # Calculate file hash for duplicate detection
                file_hash = calculate_file_hash(Path(processable_file.file_path.path))
                
                # Check for duplicates (basic implementation)
                # TODO: Implement proper duplicate detection against existing CSV
                
                # Create extraction request
                file_path = processable_file.file_path.path
                file_path_obj = Path(file_path)
                with open(file_path, 'rb') as f:
                    image_data = f.read()
                
                # Determine MIME type based on file extension
                extension = file_path_obj.suffix.lower()
                mime_type_map = {
                    '.pdf': 'application/pdf',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png'
                }
                mime_type = mime_type_map.get(extension, 'application/octet-stream')
                
                extraction_request = ImageExtractionRequest(
                    file_path=file_path_obj,
                    image_data=image_data,
                    mime_type=mime_type
                )
                
                # Extract data using AI
                extraction_result = extraction_facade.extract_from_image(extraction_request)
                
                # Write result to CSV
                write_extraction_to_csv(extraction_result, csv_file_path, current_id, file_hash)
                
                # Move processed file to done directory
                move_processed_file(file_path_obj, "done", current_id)
                
                # Log result
                if extraction_result.success:
                    data = extraction_result.data
                    print(f"✓ Extracted: {data.amount} {data.currency} (confidence: {data.confidence}%)")
                    success_count += 1
                else:
                    error_data = extraction_result.error_data
                    print(f"✗ Failed: {error_data.description}")
                    error_count += 1
                
                current_id += 1
                
            except KeyboardInterrupt:
                print("\nProcessing interrupted by user")
                sys.exit(0)
            except Exception as e:
                print(f"✗ Error processing {processable_file.file_path.name}: {str(e)}")
                error_count += 1
                current_id += 1

        # Add failed files from initial processing to error count
        error_count += len(result.failed_files)

        # Display final summary
        print(f"\nProcessing complete!")
        summary = SummaryDisplay()
        summary.set_counters(success_count, error_count, duplicate_count)
        summary.display_summary()

        # Exit with success code
        sys.exit(0)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
