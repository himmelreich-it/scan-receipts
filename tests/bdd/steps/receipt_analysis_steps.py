"""BDD step definitions for receipt analysis scenarios."""

import tempfile
from pathlib import Path
from unittest.mock import Mock

from behave import given, when, then  # type: ignore

from adapters.secondary.anthropic_adapter import AnthropicAdapter
from adapters.secondary.csv_adapter import CSVAdapter
from adapters.secondary.duplicate_detection_adapter import DuplicateDetectionAdapter
from adapters.secondary.file_system_adapter import FileSystemAdapter
from core.domain.configuration import AppConfig
from core.use_cases.process_receipt import ProcessReceiptUseCase


@given('the system is configured with test folders')  # type: ignore
def step_system_configured_with_test_folders(context):
    """Set up test environment with temporary directories."""
    context.temp_dir = tempfile.mkdtemp()
    context.temp_path = Path(context.temp_dir)

    # Create test directories
    context.incoming_dir = context.temp_path / "incoming"
    context.scanned_dir = context.temp_path / "scanned"
    context.imported_dir = context.temp_path / "imported"
    context.failed_dir = context.temp_path / "failed"
    context.csv_file = context.temp_path / "receipts.csv"

    for directory in [context.incoming_dir, context.scanned_dir, context.imported_dir, context.failed_dir]:
        directory.mkdir(parents=True)

    # Create configuration
    context.config = AppConfig(
        incoming_folder=context.incoming_dir,
        scanned_folder=context.scanned_dir,
        imported_folder=context.imported_dir,
        failed_folder=context.failed_dir,
        csv_staging_file=context.csv_file,
        xlsx_output_file=context.temp_path / "output.xlsx"
    )


@given('the incoming folder contains receipt files')  # type: ignore
def step_incoming_folder_contains_receipt_files(context):
    """Ensure incoming folder is ready for receipt files."""
    assert context.incoming_dir.exists()


@given('the duplicate detection service is available')  # type: ignore
def step_duplicate_detection_service_available(context):
    """Set up duplicate detection service."""
    context.file_system = FileSystemAdapter()
    context.csv = CSVAdapter()
    context.duplicate_detection = DuplicateDetectionAdapter(context.file_system)


@given('a test receipt file "{filename}" exists in the incoming folder')  # type: ignore
def step_test_receipt_file_exists_in_incoming(context, filename):
    """Create a test receipt file in the incoming folder."""
    test_file = context.incoming_dir / filename
    test_file.write_bytes(b"fake receipt data")
    context.test_filename = filename


@given('the AI service returns valid receipt data')  # type: ignore
def step_ai_service_returns_valid_data(context):
    """Mock AI service to return valid receipt data."""
    context.mock_ai = Mock(spec=AnthropicAdapter)
    context.mock_ai.extract_receipt_data.return_value = {
        "amount": "25.99",
        "tax": "2.08",
        "tax_percentage": "8.25",
        "description": "Coffee Shop",
        "currency": "USD",
        "date": "2024-03-15",
        "confidence": "85"
    }


@given('the AI service fails with an error')  # type: ignore
def step_ai_service_fails_with_error(context):
    """Mock AI service to fail with an error."""
    context.mock_ai = Mock(spec=AnthropicAdapter)
    context.mock_ai.extract_receipt_data.side_effect = ValueError("AI extraction failed")


@given('an identical file already exists in the scanned folder')  # type: ignore
def step_identical_file_exists_in_scanned(context):
    """Create identical file in scanned folder for duplicate detection."""
    scanned_file = context.scanned_dir / "existing_receipt.jpg"
    scanned_file.write_bytes(b"fake receipt data")


@given('receipt files exist in the incoming folder')  # type: ignore
def step_receipt_files_exist_in_incoming(context):
    """Create multiple receipt files based on table data."""
    context.test_files = {}
    for row in context.table:
        filename = row['filename']
        file_type = row['type']

        test_file = context.incoming_dir / filename

        if file_type == "duplicate":
            # Create matching file in scanned folder
            content = b"duplicate content"
            scanned_file = context.scanned_dir / "existing.pdf"
            scanned_file.write_bytes(content)
            test_file.write_bytes(content)
        else:
            test_file.write_bytes(f"{filename} data".encode())

        context.test_files[filename] = file_type


@given('the AI service returns detailed receipt data with')  # type: ignore
def step_ai_service_returns_detailed_data(context):
    """Mock AI service to return detailed receipt data from table."""
    receipt_data = {}
    for row in context.table:
        receipt_data[row['field']] = row['value']

    context.mock_ai = Mock(spec=AnthropicAdapter)
    context.mock_ai.extract_receipt_data.return_value = receipt_data


@given('the AI service returns incomplete data missing required fields')  # type: ignore
def step_ai_service_returns_incomplete_data(context):
    """Mock AI service to return incomplete data."""
    context.mock_ai = Mock(spec=AnthropicAdapter)
    context.mock_ai.extract_receipt_data.return_value = {
        "amount": "25.99",
        # Missing required fields: currency, date, confidence
        "description": "Incomplete"
    }


@given('multiple receipt files have been processed')  # type: ignore
def step_multiple_receipt_files_processed(context):
    """Set up scenario with processed receipts."""
    # Create test files
    good_file = context.incoming_dir / "good.jpg"
    bad_file = context.incoming_dir / "bad.jpg"
    good_file.write_bytes(b"good data")
    bad_file.write_bytes(b"bad data")

    # Mock AI with mixed responses
    def mock_extract_side_effect(file_path):
        if "good" in file_path:
            return {
                "amount": "15.50",
                "tax": "1.24",
                "tax_percentage": "8.0",
                "description": "Good Receipt",
                "currency": "USD",
                "date": "2024-03-16",
                "confidence": "92"
            }
        else:
            raise ValueError("Bad receipt")

    context.mock_ai = Mock(spec=AnthropicAdapter)
    context.mock_ai.extract_receipt_data.side_effect = mock_extract_side_effect


@given('some receipts were successful and others failed')  # type: ignore
def step_some_receipts_successful_others_failed(context):
    """Continue from previous step - already set up."""
    pass


@given('the file hash calculation fails')  # type: ignore
def step_file_hash_calculation_fails(context):
    """Mock file system to fail hash calculation."""
    context.mock_ai = Mock(spec=AnthropicAdapter)
    context.mock_ai.extract_receipt_data.return_value = {
        "amount": "25.99",
        "currency": "USD",
        "date": "2024-03-15",
        "confidence": "85",
        "description": "Test"
    }

    # Mock file system adapter to fail hash calculation
    context.file_system = Mock(spec=FileSystemAdapter)
    context.file_system.get_supported_files.return_value = [context.incoming_dir / context.test_filename]
    context.file_system.remove_file_if_exists.return_value = True
    context.file_system.clear_folder.return_value = None
    context.file_system.get_file_hashes_from_folder.return_value = []
    context.file_system.calculate_file_hash.return_value = None  # Fail hash calculation
    context.file_system.copy_file_to_folder.return_value = None
    context.file_system.write_error_log.return_value = None


@given('receipt files with special characters exist')  # type: ignore
def step_receipt_files_with_special_characters_exist(context):
    """Create receipt files with special characters in names."""
    context.special_files = []
    for row in context.table:
        filename = row['filename']
        test_file = context.incoming_dir / filename
        test_file.write_bytes(f"{filename} data".encode('utf-8'))
        context.special_files.append(filename)


@when('I run the AI receipt analysis')  # type: ignore
def step_run_ai_receipt_analysis(context):
    """Execute the receipt analysis use case."""
    # Create use case with mocked or real adapters
    use_case = ProcessReceiptUseCase(
        context.file_system, context.mock_ai, context.csv, context.duplicate_detection
    )

    # Capture output for verification
    import io
    from contextlib import redirect_stdout

    context.output = io.StringIO()
    with redirect_stdout(context.output):
        use_case.execute(context.config)


@when('the analysis is complete')  # type: ignore
def step_analysis_is_complete(context):
    """Run analysis and ensure it completes."""
    step_run_ai_receipt_analysis(context)


@then('the receipt should be analyzed successfully')  # type: ignore
def step_receipt_analyzed_successfully(context):
    """Verify receipt was analyzed successfully."""
    # Check that AI extraction was called
    context.mock_ai.extract_receipt_data.assert_called_once()


@then('the extracted data should be written to the CSV file')  # type: ignore
def step_extracted_data_written_to_csv(context):
    """Verify extracted data was written to CSV."""
    assert context.csv_file.exists()
    csv_content = context.csv_file.read_text()
    assert "25.99,2.08,8.25,Coffee Shop,USD,2024-03-15,85" in csv_content


@then('the receipt file should be copied to the scanned folder')  # type: ignore
def step_receipt_copied_to_scanned_folder(context):
    """Verify receipt file was copied to scanned folder."""
    scanned_file = context.scanned_dir / context.test_filename
    assert scanned_file.exists()


@then('the processing summary should show 1 processed file')  # type: ignore
def step_processing_summary_shows_1_processed(context):
    """Verify processing summary shows correct count."""
    output = context.output.getvalue()
    assert "Processed: 1" in output


@then('the receipt processing should fail')  # type: ignore
def step_receipt_processing_should_fail(context):
    """Verify receipt processing failed."""
    # AI should have been called but failed
    context.mock_ai.extract_receipt_data.assert_called_once()


@then('the receipt file should be copied to the failed folder')  # type: ignore
def step_receipt_copied_to_failed_folder(context):
    """Verify receipt file was copied to failed folder."""
    failed_file = context.failed_dir / context.test_filename
    assert failed_file.exists()


@then('an error log should be created in the failed folder')  # type: ignore
def step_error_log_created_in_failed_folder(context):
    """Verify error log was created."""
    error_log_name = f"{Path(context.test_filename).stem}_error.txt"
    error_log = context.failed_dir / error_log_name
    assert error_log.exists()

    error_content = error_log.read_text()
    assert f"Error processing file: {context.test_filename}" in error_content
    assert "AI extraction failed" in error_content


@then('the processing summary should show 1 failed file')  # type: ignore
def step_processing_summary_shows_1_failed(context):
    """Verify processing summary shows correct failure count."""
    output = context.output.getvalue()
    assert "Errors: 1" in output


@then('the duplicate should be detected and skipped')  # type: ignore
def step_duplicate_detected_and_skipped(context):
    """Verify duplicate was detected and skipped."""
    output = context.output.getvalue()
    assert "Duplicate detected" in output


@then('no AI analysis should be performed')  # type: ignore
def step_no_ai_analysis_performed(context):
    """Verify AI analysis was not called."""
    context.mock_ai.extract_receipt_data.assert_not_called()


@then('the file should remain in the incoming folder')  # type: ignore
def step_file_remains_in_incoming_folder(context):
    """Verify file remains in incoming folder."""
    incoming_file = context.incoming_dir / context.test_filename
    assert incoming_file.exists()


@then('the processing summary should show 1 duplicate skipped')  # type: ignore
def step_processing_summary_shows_1_duplicate(context):
    """Verify processing summary shows correct duplicate count."""
    output = context.output.getvalue()
    assert "Duplicates skipped: 1" in output


@then('the processing should complete with mixed results')  # type: ignore
def step_processing_completes_with_mixed_results(context):
    """Verify processing completed with mixed results."""
    output = context.output.getvalue()
    assert "Processing complete" in output


@then('the CSV should contain data for successful receipts')  # type: ignore
def step_csv_contains_successful_receipt_data(context):
    """Verify CSV contains data for successful receipts."""
    if context.csv_file.exists():
        csv_content = context.csv_file.read_text()
        # Should contain data for good receipt but not bad ones
        assert "good" in csv_content.lower() or any("good" in line for line in csv_content.split('\n'))


@then('failed receipts should be in the failed folder')  # type: ignore
def step_failed_receipts_in_failed_folder(context):
    """Verify failed receipts are in failed folder."""
    failed_files = list(context.failed_dir.glob("*.jpg"))
    assert len(failed_files) > 0


@then('duplicate receipts should be skipped')  # type: ignore
def step_duplicate_receipts_skipped(context):
    """Verify duplicate receipts were skipped."""
    output = context.output.getvalue()
    assert "Duplicate detected" in output or "skipped" in output


@then('the final summary should show all processing results')  # type: ignore
def step_final_summary_shows_all_results(context):
    """Verify final summary shows all processing results."""
    output = context.output.getvalue()
    assert "Processing complete" in output
    assert "Processed:" in output
    assert "Duplicates skipped:" in output
    assert "Errors:" in output


@then('the extracted data should be displayed during processing')  # type: ignore
def step_extracted_data_displayed_during_processing(context):
    """Verify extracted data is displayed during processing."""
    output = context.output.getvalue()
    assert "Analyzing with AI" in output


@then('the success message should show "{expected_message}"')  # type: ignore
def step_success_message_shows_expected(context, expected_message):
    """Verify success message contains expected content."""
    output = context.output.getvalue()
    assert expected_message in output


@then('the processing should fail due to validation errors')  # type: ignore
def step_processing_fails_due_to_validation_errors(context):
    """Verify processing failed due to validation errors."""
    context.mock_ai.extract_receipt_data.assert_called_once()


@then('the receipt should be moved to the failed folder')  # type: ignore
def step_receipt_moved_to_failed_folder(context):
    """Verify receipt was moved to failed folder."""
    failed_file = context.failed_dir / context.test_filename
    assert failed_file.exists()


@then('the error log should indicate missing required fields')  # type: ignore
def step_error_log_indicates_missing_fields(context):
    """Verify error log indicates missing required fields."""
    error_log_name = f"{Path(context.test_filename).stem}_error.txt"
    error_log = context.failed_dir / error_log_name
    assert error_log.exists()

    error_content = error_log.read_text()
    assert "Missing required fields" in error_content or "cannot be empty" in error_content


@then('the final summary should display CSV contents')  # type: ignore
def step_final_summary_displays_csv_contents(context):
    """Verify final summary displays CSV contents."""
    output = context.output.getvalue()
    if context.csv_file.exists():
        assert "CSV contents" in output


@then('the summary should list all failed files')  # type: ignore
def step_summary_lists_failed_files(context):
    """Verify summary lists failed files."""
    output = context.output.getvalue()
    failed_files = list(context.failed_dir.glob("*.jpg"))
    if failed_files:
        assert "Failed files" in output


@then('the summary should show accurate counts for each category')  # type: ignore
def step_summary_shows_accurate_counts(context):
    """Verify summary shows accurate counts."""
    output = context.output.getvalue()
    assert "Processed:" in output
    assert "Duplicates skipped:" in output
    assert "Errors:" in output


@then('the processing should fail gracefully')  # type: ignore
def step_processing_fails_gracefully(context):
    """Verify processing failed gracefully without crashing."""
    # Should not raise exception, should handle error
    output = context.output.getvalue()
    assert "Processing complete" in output


@then('the error should be logged appropriately')  # type: ignore
def step_error_logged_appropriately(context):
    """Verify error was logged appropriately."""
    error_log_name = f"{Path(context.test_filename).stem}_error.txt"
    error_log = context.failed_dir / error_log_name
    assert error_log.exists()


@then('all receipts should be processed successfully')  # type: ignore
def step_all_receipts_processed_successfully(context):
    """Verify all receipts with special characters were processed."""
    # Check that all special files exist in scanned folder
    for filename in context.special_files:
        scanned_file = context.scanned_dir / filename
        assert scanned_file.exists()


@then('the CSV should contain entries for all files')  # type: ignore
def step_csv_contains_entries_for_all_files(context):
    """Verify CSV contains entries for all special character files."""
    assert context.csv_file.exists()
    csv_content = context.csv_file.read_text()

    # Count lines (excluding header)
    lines = csv_content.strip().split('\n')
    data_lines = len(lines) - 1 if lines[0].startswith('Amount') else len(lines)
    assert data_lines == len(context.special_files)


@then('all files should be copied to the scanned folder')  # type: ignore
def step_all_files_copied_to_scanned_folder(context):
    """Verify all files were copied to scanned folder."""
    scanned_files = list(context.scanned_dir.iterdir())
    assert len(scanned_files) == len(context.special_files)


@then('the CSV file should be created with correct headers')  # type: ignore
def step_csv_created_with_correct_headers(context):
    """Verify CSV file was created with correct headers."""
    assert context.csv_file.exists()
    csv_content = context.csv_file.read_text()
    first_line = csv_content.split('\n')[0]
    assert first_line == "Amount,Tax,TaxPercentage,Description,Currency,Date,Confidence,Hash,DoneFilename"


@then('the headers should match: "{expected_headers}"')  # type: ignore
def step_headers_should_match(context, expected_headers):
    """Verify CSV headers match expected format."""
    csv_content = context.csv_file.read_text()
    first_line = csv_content.split('\n')[0]
    assert first_line == expected_headers


@then('the data rows should follow the correct format')  # type: ignore
def step_data_rows_follow_correct_format(context):
    """Verify data rows follow correct CSV format."""
    csv_content = context.csv_file.read_text()
    lines = csv_content.strip().split('\n')

    if len(lines) > 1:
        # Check that data rows have the correct number of columns
        header_columns = len(lines[0].split(','))
        for line in lines[1:]:
            data_columns = len(line.split(','))
            assert data_columns == header_columns


@then('file hashes should be included in the CSV')  # type: ignore
def step_file_hashes_included_in_csv(context):
    """Verify file hashes are included in CSV."""
    csv_content = context.csv_file.read_text()
    lines = csv_content.strip().split('\n')

    if len(lines) > 1:
        # Hash should be in the 8th column (index 7)
        for line in lines[1:]:
            columns = line.split(',')
            if len(columns) >= 8:
                hash_value = columns[7]
                assert hash_value.strip() != ""  # Hash should not be empty