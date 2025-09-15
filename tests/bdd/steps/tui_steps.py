"""BDD step definitions for TUI interface tests."""

import csv
import os
import signal
import tempfile
from pathlib import Path
from typing import Any
from unittest import mock

from behave import given, then, when  # type: ignore

from core.domain.configuration import AppConfig
from adapters.secondary.file_system_adapter import FileSystemAdapter
from adapters.primary.tui.terminal_ui import TerminalUI


@given("no environment variables are set")  # type: ignore
def step_no_env_vars(context: Any) -> None:
    """Clear all environment variables."""
    context.env_patch = mock.patch.dict(os.environ, {}, clear=True)
    context.env_patch.start()


@given("all required environment variables are set")  # type: ignore
def step_all_env_vars(context: Any) -> None:
    """Set all required environment variables."""
    context.tmpdir = tempfile.mkdtemp()
    context.env_vars = {
        "INCOMING_RECEIPTS_FOLDER": f"{context.tmpdir}/incoming",
        "SCANNED_FOLDER": f"{context.tmpdir}/scanned",
        "IMPORTED_FOLDER": f"{context.tmpdir}/imported",
        "FAILED_FOLDER": f"{context.tmpdir}/failed",
        "CSV_STAGING_FILE": f"{context.tmpdir}/receipts.csv",
        "XLSX_OUTPUT_FILE": f"{context.tmpdir}/output.xlsx",
    }
    context.env_patch = mock.patch.dict(os.environ, context.env_vars, clear=True)
    context.env_patch.start()


@given("the application is running")  # type: ignore
def step_app_running(context: Any) -> None:
    """Set up a running application context."""
    tmpdir = tempfile.mkdtemp()
    config = AppConfig(
        incoming_folder=Path(tmpdir) / "incoming",
        scanned_folder=Path(tmpdir) / "scanned",
        imported_folder=Path(tmpdir) / "imported",
        failed_folder=Path(tmpdir) / "failed",
        csv_staging_file=Path(tmpdir) / "receipts.csv",
        xlsx_output_file=Path(tmpdir) / "output.xlsx",
    )
    file_system = FileSystemAdapter()
    file_system.create_folders(config)
    context.tmpdir = tmpdir
    context.config = config


@given("no receipt files exist")  # type: ignore
def step_no_receipt_files(context: Any) -> None:
    """Ensure no receipt files exist."""
    pass


@given("no staging CSV exists")  # type: ignore
def step_no_staging_csv(context: Any) -> None:
    """Ensure no staging CSV exists."""
    if context.config.csv_staging_file.exists():
        context.config.csv_staging_file.unlink()


@given("{count:d} files exist in the incoming folder")  # type: ignore
def step_incoming_files(context: Any, count: int) -> None:
    """Create receipt files in incoming folder."""
    for i in range(count):
        (context.config.incoming_folder / f"receipt{i}.pdf").touch()


@given("{count:d} files exist in the failed folder")  # type: ignore
def step_failed_files(context: Any, count: int) -> None:
    """Create receipt files in failed folder."""
    for i in range(count):
        ext = ".jpg" if i % 2 == 0 else ".png"
        (context.config.failed_folder / f"failed{i}{ext}").touch()


@given("staging CSV contains {count:d} entries")  # type: ignore
def step_staging_csv_entries(context: Any, count: int) -> None:
    """Create staging CSV with specified number of entries."""
    with open(context.config.csv_staging_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["Amount", "Tax", "Description", "Date"])
        for i in range(count):
            writer.writerow([f"{100+i}.00", "19.00", f"Purchase {i}", "2025-01-15"])


@when("the application starts")  # type: ignore
def step_app_starts(context: Any) -> None:
    """Attempt to start the application."""
    try:
        config = AppConfig.from_env(load_dotenv_file=False)
        file_system = FileSystemAdapter()
        file_system.create_folders(config)
        context.config = config
        context.startup_success = True
    except ValueError as e:
        context.startup_error = str(e)
        context.startup_success = False
    except OSError as e:
        context.startup_error = str(e)
        context.startup_success = False


@when("the status is displayed")  # type: ignore
def step_display_status(context: Any) -> None:
    """Display system status."""
    file_system = FileSystemAdapter()
    context.input_count = file_system.count_receipt_files(context.config.incoming_folder)
    context.failed_count = file_system.count_receipt_files(context.config.failed_folder)
    context.staging_info = file_system.get_staging_info(context.config.csv_staging_file)


@when("the user selects option {option}")  # type: ignore
def step_select_option(context: Any, option: str) -> None:
    """Handle menu option selection."""
    # Create a mock TUI to test menu choice handling
    from unittest.mock import Mock
    mock_file_system = Mock()
    mock_process_receipt = Mock()
    mock_import_xlsx = Mock()
    mock_view_staging = Mock()
    tui = TerminalUI(mock_file_system, mock_process_receipt, mock_import_xlsx, mock_view_staging)
    context.menu_result = tui.handle_menu_choice(option, context.config)
    context.selected_option = option


@when('the user enters invalid input "{input_text}"')  # type: ignore
def step_invalid_input(context: Any, input_text: str) -> None:
    """Handle invalid menu input."""
    # Create a mock TUI to test menu choice handling
    from unittest.mock import Mock
    mock_file_system = Mock()
    mock_process_receipt = Mock()
    mock_import_xlsx = Mock()
    mock_view_staging = Mock()
    tui = TerminalUI(mock_file_system, mock_process_receipt, mock_import_xlsx, mock_view_staging)
    context.menu_result = tui.handle_menu_choice(input_text, context.config)
    context.invalid_input = input_text


@when("the user presses Ctrl+C")  # type: ignore
def step_ctrl_c(context: Any) -> None:
    """Simulate Ctrl+C signal."""
    with mock.patch('sys.exit') as mock_exit:
        # Create a mock TUI to test signal handling
        from unittest.mock import Mock
        mock_file_system = Mock()
        mock_process_receipt = Mock()
        mock_import_xlsx = Mock()
        mock_view_staging = Mock()
        tui = TerminalUI(mock_file_system, mock_process_receipt, mock_import_xlsx, mock_view_staging)
        tui.signal_handler(signal.SIGINT, None)
        context.exit_called = mock_exit.called


@then('it should fail with "Missing environment variables"')  # type: ignore
def step_fail_missing_vars(context: Any) -> None:
    """Verify failure due to missing environment variables."""
    assert not context.startup_success
    assert "Missing environment variables" in context.startup_error


@then("list all {count:d} missing variables")  # type: ignore
def step_list_missing_vars(context: Any, count: int) -> None:
    """Verify all missing variables are listed."""
    required_vars = [
        "INCOMING_RECEIPTS_FOLDER",
        "SCANNED_FOLDER",
        "IMPORTED_FOLDER",
        "FAILED_FOLDER",
        "CSV_STAGING_FILE",
        "XLSX_OUTPUT_FILE",
    ]
    for var in required_vars:
        assert var in context.startup_error


@then("all {count:d} folders should be created if missing")  # type: ignore
def step_folders_created(context: Any, count: int) -> None:
    """Verify all folders are created."""
    assert context.config.incoming_folder.exists()
    assert context.config.scanned_folder.exists()
    assert context.config.imported_folder.exists()
    assert context.config.failed_folder.exists()


@then("the TUI should display successfully")  # type: ignore
def step_tui_displays(context: Any) -> None:
    """Verify TUI displays successfully."""
    assert context.startup_success


@then('it should show "{expected_text}"')  # type: ignore
def step_show_text(context: Any, expected_text: str) -> None:
    """Verify expected text is shown."""
    if "Input Folder:" in expected_text:
        count = int(expected_text.split(": ")[1].split(" ")[0])
        assert context.input_count == count
    elif "Failed Folder:" in expected_text:
        count = int(expected_text.split(": ")[1].split(" ")[0])
        assert context.failed_count == count
    elif "No staging data" in expected_text:
        assert context.staging_info is None


@then('show "{text}"')  # type: ignore
def step_show_alt(context: Any, text: str) -> None:
    """Alternative step for showing text."""
    step_show_text(context, text)


@then('show staging file with "{count} entries"')  # type: ignore
def step_show_staging(context: Any, count: str) -> None:
    """Verify staging file entry count."""
    entry_count = int(count.split(" ")[0])
    assert context.staging_info is not None
    assert context.staging_info.entry_count == entry_count


@then('it should display "{message}"')  # type: ignore
def step_display_message(context: Any, message: str) -> None:
    """Verify message is displayed."""
    if hasattr(context, 'selected_option') and context.selected_option:
        if context.selected_option in ["1", "2", "3"]:
            assert context.menu_result is True
        elif context.selected_option == "4":
            assert context.menu_result is False


@then("return to the menu")  # type: ignore
def step_return_to_menu(context: Any) -> None:
    """Verify return to menu."""
    assert context.menu_result is True


@then("exit the application")  # type: ignore
def step_exit_app(context: Any) -> None:
    """Verify application exit."""
    assert context.menu_result is False


@then("it should display error message")  # type: ignore
def step_display_error(context: Any) -> None:
    """Verify error message is displayed."""
    assert context.menu_result is True


@then("re-prompt for input")  # type: ignore
def step_reprompt(context: Any) -> None:
    """Verify re-prompting for input."""
    assert context.menu_result is True


@then("exit cleanly")  # type: ignore
def step_exit_cleanly(context: Any) -> None:
    """Verify clean exit."""
    assert context.exit_called