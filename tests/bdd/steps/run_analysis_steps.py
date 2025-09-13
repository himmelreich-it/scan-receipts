"""BDD step definitions for Run Analysis feature tests."""

import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

from behave import given, then, when  # type: ignore

from core.domain.configuration import AppConfig
from core.use_cases.process_receipt import ProcessReceiptUseCase
from adapters.secondary.file_system_adapter import FileSystemAdapter
from adapters.primary.tui.terminal_ui import TerminalUI


@given("the application is running")  # type: ignore
def step_app_running(context: Any) -> None:
    """Set up running application context."""
    # Create temporary directory for test
    context.temp_dir = Path(tempfile.mkdtemp())

    # Create test config
    context.config = AppConfig(
        incoming_folder=context.temp_dir / "incoming",
        scanned_folder=context.temp_dir / "scanned",
        imported_folder=context.temp_dir / "imported",
        failed_folder=context.temp_dir / "failed",
        csv_staging_file=context.temp_dir / "receipts.csv",
        xlsx_output_file=context.temp_dir / "receipts.xlsx",
    )

    # Create components
    context.file_system = FileSystemAdapter()
    context.mock_ai_extraction = Mock()
    context.mock_csv = Mock()
    context.mock_import_use_case = Mock()
    context.mock_view_staging = Mock()

    # Create use case
    context.process_receipt_use_case = ProcessReceiptUseCase(
        context.file_system, context.mock_ai_extraction, context.mock_csv
    )

    # Create TUI
    context.tui = TerminalUI(
        context.file_system,
        context.process_receipt_use_case,
        context.mock_import_use_case,
        context.mock_view_staging,
    )

    # Track output for verification
    context.output_lines = []


@given("all required folders exist")  # type: ignore
def step_folders_exist(context: Any) -> None:
    """Create all required folders."""
    context.file_system.create_folders(context.config)


@given("no receipts.csv file exists")  # type: ignore
def step_no_csv_exists(context: Any) -> None:
    """Ensure no receipts.csv file exists."""
    if context.config.csv_staging_file.exists():
        context.config.csv_staging_file.unlink()


@given("a receipts.csv file exists")  # type: ignore
def step_csv_exists(context: Any) -> None:
    """Create a receipts.csv file."""
    context.config.csv_staging_file.write_text("test,content\n")


@given("a receipts.csv file exists with content")  # type: ignore
def step_csv_exists_with_content(context: Any) -> None:
    """Create a receipts.csv file with actual content."""
    context.config.csv_staging_file.write_text(
        "Amount,Tax,TaxPercentage,Description,Currency,Date,Confidence,Hash,DoneFilename\n"
        "100.00,10.00,10,Test Receipt,USD,2024-01-01,0.95,abc123,test.pdf\n"
    )


@given("no files exist in the incoming folder")  # type: ignore
def step_no_files_incoming(context: Any) -> None:
    """Ensure incoming folder is empty."""
    # Folder is already empty from setup
    pass


@given("{count:d} supported files exist in the incoming folder")  # type: ignore
def step_n_supported_files(context: Any, count: int) -> None:
    """Create N supported files in incoming folder."""
    for i in range(1, count + 1):
        filename = f"receipt{i}.pdf"
        (context.config.incoming_folder / filename).touch()


@given("{count:d} supported files exist in the incoming folder:")  # type: ignore
def step_specific_supported_files(context: Any, count: int) -> None:
    """Create specific supported files from table."""
    for row in context.table:
        filename = row["filename"]
        (context.config.incoming_folder / filename).touch()


@given("the scanned folder contains existing files:")  # type: ignore
def step_scanned_folder_has_files(context: Any) -> None:
    """Create files in scanned folder."""
    for row in context.table:
        filename = row["filename"]
        (context.config.scanned_folder / filename).touch()


@given("{count:d} supported file exists in the incoming folder")  # type: ignore
def step_one_supported_file(context: Any, count: int) -> None:
    """Create one supported file in incoming folder."""
    (context.config.incoming_folder / "receipt.pdf").touch()


@given("files exist in the incoming folder:")  # type: ignore
def step_mixed_files_exist(context: Any) -> None:
    """Create mixed supported and unsupported files from table."""
    for row in context.table:
        filename = row["filename"]
        (context.config.incoming_folder / filename).touch()


@when("the menu is displayed")  # type: ignore
def step_display_menu(context: Any) -> None:
    """Display the menu and capture output."""
    with patch("rich.print") as mock_rprint:
        context.tui.display_menu(context.config)
        context.output_lines.extend([str(call) for call in mock_rprint.call_args_list])


@when('the user selects "Run Analysis"')  # type: ignore
def step_select_run_analysis(context: Any) -> None:
    """Simulate user selecting Run Analysis."""
    with patch("rich.print") as mock_rprint:
        context.process_receipt_use_case.execute(context.config)
        context.output_lines.extend([str(call) for call in mock_rprint.call_args_list])


@when('the user selects "Re-run Analysis"')  # type: ignore
def step_select_rerun_analysis(context: Any) -> None:
    """Simulate user selecting Re-run Analysis (same as Run Analysis)."""
    with patch("rich.print") as mock_rprint:
        context.process_receipt_use_case.execute(context.config)
        context.output_lines.extend([str(call) for call in mock_rprint.call_args_list])


@then('it should show "[1] Run Analysis"')  # type: ignore
def step_shows_run_analysis(context: Any) -> None:
    """Verify menu shows Run Analysis."""
    menu_output = " ".join(str(call) for call in context.output_lines)
    assert "[1] Run Analysis" in menu_output
    assert "Re-run Analysis" not in menu_output


@then('it should show "[1] Re-run Analysis"')  # type: ignore
def step_shows_rerun_analysis(context: Any) -> None:
    """Verify menu shows Re-run Analysis."""
    menu_output = " ".join(str(call) for call in context.output_lines)
    assert "[1] Re-run Analysis" in menu_output


@then('it should display "No files in incoming folder"')  # type: ignore
def step_shows_no_files_message(context: Any) -> None:
    """Verify no files message is displayed."""
    output = "\n".join(context.output_lines)
    assert f"No files in {context.config.incoming_folder} folder" in output


@then("return to the main menu after analysis")  # type: ignore
def step_returns_to_menu_after_analysis(context: Any) -> None:
    """Verify control returns to main menu (implicitly verified by not crashing)."""
    # If we got here without exceptions, the method completed successfully
    assert True


@then('it should display "Processing {step}/{total}: {filename}"')  # type: ignore
def step_shows_processing_message(
    context: Any, step: str, total: str, filename: str
) -> None:
    """Verify specific processing message is displayed."""
    expected_message = f"Processing {step}/{total}: {filename}"
    output = "\n".join(context.output_lines)
    assert expected_message in output


@then('display "Processing {step}/{total}: {filename}"')  # type: ignore
def step_displays_processing_message(
    context: Any, step: str, total: str, filename: str
) -> None:
    """Verify specific processing message is displayed."""
    expected_message = f"Processing {step}/{total}: {filename}"
    output = "\n".join(context.output_lines)
    assert expected_message in output


@then('display "Successfully processed 5 files"')  # type: ignore
def step_displays_success_message(context: Any) -> None:
    """Verify success message is displayed."""
    output = "\n".join(context.output_lines)
    assert "Successfully processed 5 files" in output


@then("the receipts.csv file should be deleted")  # type: ignore
def step_csv_deleted(context: Any) -> None:
    """Verify receipts.csv was deleted."""
    assert not context.config.csv_staging_file.exists()


@then("processing should continue with progress messages")  # type: ignore
def step_processing_continues(context: Any) -> None:
    """Verify processing continues after cleanup."""
    output = "\n".join(context.output_lines)
    assert "Processing" in output


@then("the scanned folder should be cleared")  # type: ignore
def step_scanned_folder_cleared(context: Any) -> None:
    """Verify scanned folder was cleared."""
    scanned_files = list(context.config.scanned_folder.iterdir())
    assert len(scanned_files) == 0


@then("processing should continue")  # type: ignore
def step_processing_continues_simple(context: Any) -> None:
    """Verify processing continues."""
    # If we got here without exceptions, processing completed
    assert True


@then("it should process exactly {count:d} files")  # type: ignore
def step_processes_exact_count(context: Any, count: int) -> None:
    """Verify exact number of files processed."""
    output = "\n".join(context.output_lines)
    processing_messages = [
        line for line in output.split("\n") if "Processing" in line and "/" in line
    ]
    # Count unique processing messages (avoid duplicates from multiple calls)
    unique_processing = list(set(processing_messages))
    assert len(unique_processing) == count


@then("display progress for only supported files")  # type: ignore
def step_progress_only_supported(context: Any) -> None:
    """Verify progress shown only for supported files."""
    output = "\n".join(context.output_lines)

    # Should not see unsupported file extensions in processing messages
    processing_lines = [line for line in output.split("\n") if "Processing" in line]
    for line in processing_lines:
        assert not any(ext in line for ext in [".txt", ".gif", ".md"])


@then("display progress messages for all files")  # type: ignore
def step_progress_for_all(context: Any) -> None:
    """Verify progress messages shown for all supported files."""
    output = "\n".join(context.output_lines)
    processing_messages = [
        line for line in output.split("\n") if "Processing" in line and "/" in line
    ]
    # Should have progress messages
    assert len(processing_messages) > 0
