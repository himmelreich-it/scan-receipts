"""BDD step definitions for Run Analysis feature."""

import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import Mock

from behave import given, when, then  # type: ignore

from adapters.secondary.file_system_adapter import FileSystemAdapter
from adapters.secondary.anthropic_adapter import AnthropicAdapter
from adapters.secondary.csv_adapter import CSVAdapter
from adapters.primary.tui.terminal_ui import TerminalUI
from core.domain.configuration import AppConfig
from core.use_cases.process_receipt import ProcessReceiptUseCase
from core.use_cases.import_to_xlsx import ImportToXLSXUseCase
from core.use_cases.view_staging import ViewStagingUseCase


@given("the application environment is properly configured")  # type: ignore
def step_app_environment_configured(context: Any) -> None:
    """Set up proper application environment."""
    context.temp_dir = Path(tempfile.mkdtemp())

    # Create folder structure
    context.incoming_folder = context.temp_dir / "incoming"
    context.scanned_folder = context.temp_dir / "scanned"
    context.imported_folder = context.temp_dir / "imported"
    context.failed_folder = context.temp_dir / "failed"

    context.receipts_csv = context.temp_dir / "receipts.csv"
    context.xlsx_output = context.temp_dir / "output.xlsx"


@given("required folders exist")  # type: ignore
def step_required_folders_exist(context: Any) -> None:
    """Create required folder structure."""
    context.incoming_folder.mkdir(parents=True, exist_ok=True)
    context.scanned_folder.mkdir(parents=True, exist_ok=True)
    context.imported_folder.mkdir(parents=True, exist_ok=True)
    context.failed_folder.mkdir(parents=True, exist_ok=True)


@given("no receipts.csv file exists")  # type: ignore
def step_no_receipts_csv_exists(context: Any) -> None:
    """Ensure receipts.csv doesn't exist."""
    if context.receipts_csv.exists():
        context.receipts_csv.unlink()


@given("a receipts.csv file exists")  # type: ignore
def step_receipts_csv_exists(context):
    """Create an empty receipts.csv file."""
    context.receipts_csv.touch()


@given("a receipts.csv file exists with data")  # type: ignore
def step_receipts_csv_exists_with_data(context):
    """Create a receipts.csv file with sample data."""
    context.receipts_csv.write_text(
        "Amount,Tax,TaxPercentage,Description,Currency,Date,Confidence,Hash,DoneFilename\n"
        "10.50,1.50,14.29,Test Receipt,USD,2024-01-01,0.95,abc123,receipt1.pdf\n"
    )


@given("no supported files exist in the incoming folder")  # type: ignore
def step_no_supported_files_exist(context):
    """Ensure no supported files in incoming folder."""
    # Clear the folder
    for file in context.incoming_folder.glob("*"):
        if file.is_file():
            file.unlink()


@given("{count:d} supported files exist in the incoming folder")  # type: ignore
def step_supported_files_exist_count(context, count):
    """Create specified number of supported files."""
    for i in range(count):
        filename = f"receipt{i + 1}.pdf"
        (context.incoming_folder / filename).touch()


@given("{count:d} supported files exist in the incoming folder:")  # type: ignore
def step_supported_files_exist_with_table(context, count):
    """Create supported files based on table data."""
    for row in context.table:
        filename = row["filename"]
        (context.incoming_folder / filename).touch()


@given("files exist in the incoming folder")  # type: ignore
def step_files_exist_in_incoming(context):
    """Create files based on table data."""
    for row in context.table:
        filename = row["filename"]
        (context.incoming_folder / filename).touch()


@given("files exist in the incoming folder:")  # type: ignore
def step_files_exist_in_incoming_table(context):
    """Create files based on table data with colon."""
    for row in context.table:
        filename = row["filename"]
        (context.incoming_folder / filename).touch()


@given("the scanned folder contains files")  # type: ignore
def step_scanned_folder_contains_files(context):
    """Create files in scanned folder based on table data."""
    for row in context.table:
        filename = row["filename"]
        (context.scanned_folder / filename).touch()


@given("the scanned folder contains files:")  # type: ignore
def step_scanned_folder_contains_files_table(context):
    """Create files in scanned folder based on table data with colon."""
    for row in context.table:
        filename = row["filename"]
        (context.scanned_folder / filename).touch()


@when("the application displays the menu")  # type: ignore
def step_app_displays_menu(context):
    """Capture menu display output."""
    config = AppConfig(
        incoming_folder=context.incoming_folder,
        scanned_folder=context.scanned_folder,
        imported_folder=context.imported_folder,
        failed_folder=context.failed_folder,
        csv_staging_file=context.receipts_csv,
        xlsx_output_file=context.xlsx_output,
    )

    # Create TUI instance
    file_system = FileSystemAdapter()
    ai_extraction = AnthropicAdapter()
    csv_adapter = CSVAdapter()

    process_use_case = ProcessReceiptUseCase(file_system, ai_extraction, csv_adapter)
    import_use_case = ImportToXLSXUseCase(csv_adapter, Mock(), file_system)
    view_use_case = ViewStagingUseCase(file_system, csv_adapter)

    tui = TerminalUI(file_system, process_use_case, import_use_case, view_use_case)

    # Capture output by mocking print
    import io
    from contextlib import redirect_stdout

    context.captured_output = io.StringIO()
    with redirect_stdout(context.captured_output):
        tui.display_menu(config)


@when('the user selects "Run Analysis"')  # type: ignore
def step_user_selects_run_analysis(context):
    """Execute Run Analysis use case."""
    config = AppConfig(
        incoming_folder=context.incoming_folder,
        scanned_folder=context.scanned_folder,
        imported_folder=context.imported_folder,
        failed_folder=context.failed_folder,
        csv_staging_file=context.receipts_csv,
        xlsx_output_file=context.xlsx_output,
    )

    # Create use case and execute
    file_system = FileSystemAdapter()
    ai_extraction = AnthropicAdapter()
    csv_adapter = CSVAdapter()

    use_case = ProcessReceiptUseCase(file_system, ai_extraction, csv_adapter)

    # Capture output
    import io
    from contextlib import redirect_stdout

    context.captured_output = io.StringIO()
    with redirect_stdout(context.captured_output):
        use_case.execute(config)


@when('the user selects "Re-run Analysis"')  # type: ignore
def step_user_selects_rerun_analysis(context):
    """Execute Re-run Analysis (same as Run Analysis)."""
    step_user_selects_run_analysis(context)


@then('it should show "[1] Run Analysis"')  # type: ignore
def step_should_show_run_analysis_menu(context):
    """Verify menu shows Run Analysis option."""
    output = context.captured_output.getvalue()
    assert "[1] Run Analysis" in output


@then('it should show "[1] Re-run Analysis"')  # type: ignore
def step_should_show_rerun_analysis_menu(context):
    """Verify menu shows Re-run Analysis option."""
    output = context.captured_output.getvalue()
    assert "[1] Re-run Analysis" in output


@then('it should display "No files in {incoming} folder"')  # type: ignore
def step_should_display_no_files_message(context, incoming):
    """Verify no files message is displayed."""
    output = context.captured_output.getvalue()
    expected = f"No files in {context.incoming_folder} folder"
    assert expected in output


@then("return to the main menu")  # type: ignore
def step_return_to_main_menu(context):
    """Verify the operation returns (doesn't hang)."""
    # This is implied by the fact that the use case completes
    pass


@then("it should display progress messages")  # type: ignore
def step_should_display_progress_messages(context):
    """Verify progress messages are displayed."""
    output = context.captured_output.getvalue()
    for row in context.table:
        expected_message = row["message"]
        assert expected_message in output


@then("it should display progress messages:")  # type: ignore
def step_should_display_progress_messages_table(context):
    """Verify progress messages are displayed with colon."""
    output = context.captured_output.getvalue()
    for row in context.table:
        expected_message = row["message"]
        assert expected_message in output


@then('display "TODO: Implement actual processing"')  # type: ignore
def step_should_display_todo_message(context):
    """Verify TODO message is displayed."""
    output = context.captured_output.getvalue()
    assert "TODO: Implement actual processing" in output


@then("the receipts.csv file should be removed")  # type: ignore
def step_receipts_csv_should_be_removed(context):
    """Verify receipts.csv file was removed."""
    assert not context.receipts_csv.exists()


@then("the scanned folder should be cleared")  # type: ignore
def step_scanned_folder_should_be_cleared(context):
    """Verify scanned folder is empty."""
    files = list(context.scanned_folder.glob("*"))
    assert len(files) == 0


@then("it should display progress messages for {count:d} supported files only")  # type: ignore
def step_should_display_progress_for_supported_only(context, count):
    """Verify progress messages only for supported files."""
    output = context.captured_output.getvalue()

    # Count "Processing" messages
    processing_count = output.count("Processing")
    assert processing_count == count

    # Verify the format includes total count
    assert f"/{count}:" in output
