"""BDD steps for duplicate detection feature."""

import tempfile
from pathlib import Path
from unittest.mock import Mock

from behave import given, when, then  # type: ignore
from behave.runner import Context  # type: ignore

from adapters.secondary.duplicate_detection_adapter import DuplicateDetectionAdapter
from adapters.secondary.file_system_adapter import FileSystemAdapter
from core.domain.configuration import AppConfig
from core.use_cases.process_receipt import ProcessReceiptUseCase


@given("the system is initialized with test folders")  # type: ignore
def step_system_initialized_with_test_folders(context: Context) -> None:
    """Initialize system with test folder structure."""
    # Create temporary directory structure
    context.temp_dir = Path(tempfile.mkdtemp())
    context.incoming = context.temp_dir / "incoming"
    context.scanned = context.temp_dir / "scanned"
    context.imported = context.temp_dir / "imported"
    context.failed = context.temp_dir / "failed"
    context.csv_file = context.temp_dir / "receipts.csv"

    # Create all directories
    for folder in [context.incoming, context.scanned, context.imported, context.failed]:
        folder.mkdir(parents=True, exist_ok=True)

    # Create configuration
    context.config = AppConfig(
        incoming_folder=context.incoming,
        scanned_folder=context.scanned,
        imported_folder=context.imported,
        failed_folder=context.failed,
        csv_staging_file=context.csv_file,
        xlsx_output_file=context.temp_dir / "test.xlsx",
    )

    # Initialize adapters and use case
    context.file_system = FileSystemAdapter()
    context.duplicate_detection = DuplicateDetectionAdapter(context.file_system)

    # Mock AI extraction and CSV for isolated testing
    context.mock_ai_extraction = Mock()
    context.mock_csv = Mock()

    context.use_case = ProcessReceiptUseCase(
        context.file_system,
        context.mock_ai_extraction,
        context.mock_csv,
        context.duplicate_detection,
    )


@given("the incoming folder contains some receipt files")  # type: ignore
def step_incoming_folder_contains_receipt_files(context: Context) -> None:
    """Ensure incoming folder exists."""
    context.incoming.mkdir(exist_ok=True)


@given("the CSV staging file is cleared")  # type: ignore
def step_csv_staging_file_cleared(context: Context) -> None:
    """Clear the CSV staging file."""
    context.file_system.remove_file_if_exists(context.csv_file)


@given('a receipt file "{filename}" exists in the incoming folder')  # type: ignore
def step_receipt_file_exists_in_incoming(context: Context, filename: str) -> None:
    """Create a receipt file in the incoming folder."""
    if not hasattr(context, "file_contents"):
        context.file_contents = {}

    file_path = context.incoming / filename
    content = f"Receipt content for {filename}".encode()
    file_path.write_bytes(content)
    context.file_contents[filename] = content


@given('an identical file "{filename}" exists in the imported folder')  # type: ignore
def step_identical_file_exists_in_imported(context: Context, filename: str) -> None:
    """Create an identical file in the imported folder."""
    # Get the original filename from the step parameter
    # We need to find the corresponding file in incoming folder
    original_filename = None
    for key in context.file_contents:
        if key.endswith(".pdf"):  # Find the first PDF file
            original_filename = key
            break

    if original_filename:
        content = context.file_contents[original_filename]
        imported_file = context.imported / filename
        imported_file.write_bytes(content)


@given('an identical file "{filename}" exists in the scanned folder')  # type: ignore
def step_identical_file_exists_in_scanned(context: Context, filename: str) -> None:
    """Create an identical file in the scanned folder."""
    # Get the original filename from the step parameter
    original_filename = None
    for key in context.file_contents:
        if key.endswith(".pdf"):  # Find the first PDF file
            original_filename = key
            break

    if original_filename:
        content = context.file_contents[original_filename]
        scanned_file = context.scanned / filename
        scanned_file.write_bytes(content)


@given("no duplicate exists in imported or scanned folders")  # type: ignore
def step_no_duplicate_exists(context: Context) -> None:
    """Ensure no duplicates exist in imported or scanned folders."""
    # This is implicitly true if we don't create duplicates
    pass


@given('a corrupted file "{filename}" exists in the incoming folder')  # type: ignore
def step_corrupted_file_exists_in_incoming(context: Context, filename: str) -> None:
    """Create a corrupted file that will cause hash calculation to fail."""
    # Create a directory instead of a file to trigger hash calculation error
    corrupted_path = context.incoming / filename
    corrupted_path.mkdir()  # This will cause calculate_file_hash to fail


@given("multiple files exist in the incoming folder")  # type: ignore
def step_multiple_files_exist_in_incoming(context: Context) -> None:
    """Create multiple files based on the table data."""
    if not hasattr(context, "file_contents"):
        context.file_contents = {}

    for row in context.table:
        filename = row["filename"]
        file_path = context.incoming / filename

        if "type" in row:
            # Handle files by type (for error scenarios)
            if row["type"] == "valid":
                content = f"Valid receipt content for {filename}".encode()
                file_path.write_bytes(content)
            elif row["type"] == "corrupted":
                # Create directory instead of file to trigger error
                file_path.mkdir()
        else:
            # Handle files with duplicate information
            content = f"Receipt content for {filename}".encode()
            file_path.write_bytes(content)
            context.file_contents[filename] = content

            if row["has_duplicate"] == "yes":
                if row["duplicate_location"] == "imported":
                    duplicate_file = context.imported / f"dup_{filename}"
                    duplicate_file.write_bytes(content)
                elif row["duplicate_location"] == "scanned":
                    duplicate_file = context.scanned / f"dup_{filename}"
                    duplicate_file.write_bytes(content)


@when("I run the receipt analysis")  # type: ignore
def step_run_receipt_analysis(context: Context) -> None:
    """Execute the receipt analysis process."""
    # Redirect stdout to capture output
    import io
    from contextlib import redirect_stdout

    captured_output = io.StringIO()

    try:
        with redirect_stdout(captured_output):
            context.use_case.execute(context.config)
    except Exception as e:
        # Store exception for later verification
        context.execution_error = e

    context.output = captured_output.getvalue()


@then("the system should detect the duplicate")  # type: ignore
def step_system_should_detect_duplicate(context: Context) -> None:
    """Verify that duplicate was detected."""
    assert "Duplicate detected" in context.output or "skipping" in context.output


@then('the file should be skipped with a message about "{folder_name}" folder')  # type: ignore
def step_file_should_be_skipped_with_folder_message(
    context: Context, folder_name: str
) -> None:
    """Verify file was skipped with correct folder message."""
    assert f"{folder_name} folder" in context.output


@then("no AI analysis should be performed for this file")  # type: ignore
def step_no_ai_analysis_performed(context: Context) -> None:
    """Verify AI analysis was not called."""
    # Since AI is mocked, we can check it wasn't called
    context.mock_ai_extraction.extract_receipt_data.assert_not_called()


@then("the system should not detect any duplicates")  # type: ignore
def step_system_should_not_detect_duplicates(context: Context) -> None:
    """Verify no duplicates were detected."""
    assert "Duplicate detected" not in context.output


@then("the file should proceed to AI analysis")  # type: ignore
def step_file_should_proceed_to_ai_analysis(context: Context) -> None:
    """Verify file proceeded to AI analysis."""
    assert "Analyzing with AI" in context.output


@then("the system should display a hash calculation error")  # type: ignore
def step_system_should_display_hash_error(context: Context) -> None:
    """Verify hash calculation error was displayed."""
    assert "Hash calculation failed" in context.output


@then("the system should continue processing remaining files")  # type: ignore
def step_system_should_continue_processing(context: Context) -> None:
    """Verify system continued processing after error."""
    assert "Processing complete" in context.output


@then("the system should show a summary")  # type: ignore
def step_system_should_show_summary(context: Context) -> None:
    """Verify processing summary is shown with expected counts."""
    assert "Processing complete" in context.output

    # Extract expected values from table
    for row in context.table:
        processed = row["processed"]
        duplicates_skipped = row["duplicates_skipped"]
        errors = row["errors"]

        assert f"Processed: {processed}" in context.output
        assert f"Duplicates skipped: {duplicates_skipped}" in context.output
        assert f"Errors: {errors}" in context.output


@then("the system should show a summary with")  # type: ignore
def step_system_should_show_summary_with(context: Context) -> None:
    """Verify processing summary with specific counts."""
    assert "Processing complete" in context.output

    for row in context.table:
        processed = row["processed"]
        duplicates_skipped = row["duplicates_skipped"]
        errors = row["errors"]

        assert f"Processed: {processed}" in context.output
        assert f"Duplicates skipped: {duplicates_skipped}" in context.output
        assert f"Errors: {errors}" in context.output
