"""BDD step definitions for View Staging Table functionality."""

import csv
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import Mock

from behave import given, then, when  # type: ignore

from adapters.primary.tui.terminal_ui import TerminalUI
from adapters.secondary.csv_adapter import CSVAdapter
from adapters.secondary.file_system_adapter import FileSystemAdapter
from core.domain.configuration import AppConfig
from core.use_cases.view_staging import ViewStagingUseCase


@given("the receipts.csv file does not exist")  # type: ignore
def step_csv_file_not_exists(context: Any) -> None:
    """Ensure CSV file does not exist."""
    if not hasattr(context, "tmpdir"):
        context.tmpdir = tempfile.mkdtemp()

    csv_path = Path(context.tmpdir) / "receipts.csv"
    if csv_path.exists():
        csv_path.unlink()

    context.csv_path = csv_path
    context.config = Mock(spec=AppConfig)
    context.config.csv_staging_file = csv_path


@given("the receipts.csv file exists but is empty")  # type: ignore
def step_csv_file_empty(context: Any) -> None:
    """Create an empty CSV file."""
    if not hasattr(context, "tmpdir"):
        context.tmpdir = tempfile.mkdtemp()

    csv_path = Path(context.tmpdir) / "receipts.csv"
    with open(csv_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Amount",
                "Tax",
                "TaxPercentage",
                "Description",
                "Currency",
                "Date",
                "Confidence",
                "Hash",
                "DoneFilename",
            ]
        )

    context.csv_path = csv_path
    context.config = Mock(spec=AppConfig)
    context.config.csv_staging_file = csv_path


@given("the receipts.csv file exists with data")  # type: ignore
def step_csv_file_with_data(context: Any) -> None:
    """Create CSV file with data from the table."""
    if not hasattr(context, "tmpdir"):
        context.tmpdir = tempfile.mkdtemp()

    csv_path = Path(context.tmpdir) / "receipts.csv"

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "Amount",
            "Tax",
            "TaxPercentage",
            "Description",
            "Currency",
            "Date",
            "Confidence",
            "Hash",
            "DoneFilename",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in context.table:
            writer.writerow(
                {
                    "Amount": row["Amount"],
                    "Tax": row["Tax"],
                    "TaxPercentage": row["TaxPercentage"],
                    "Description": row["Description"],
                    "Currency": row["Currency"],
                    "Date": row["Date"],
                    "Confidence": row["Confidence"],
                    "Hash": row["Hash"],
                    "DoneFilename": row["DoneFilename"],
                }
            )

    context.csv_path = csv_path
    context.config = Mock(spec=AppConfig)
    context.config.csv_staging_file = csv_path


@given("the receipts.csv file exists but is corrupted")  # type: ignore
def step_csv_file_corrupted(context: Any) -> None:
    """Create a corrupted CSV file."""
    if not hasattr(context, "tmpdir"):
        context.tmpdir = tempfile.mkdtemp()

    csv_path = Path(context.tmpdir) / "receipts.csv"

    # Write invalid CSV content
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("Invalid,CSV,Content\n")
        f.write("This is not,a valid,CSV file\n")
        f.write("Missing quotes and,commas in wrong places")

    context.csv_path = csv_path
    context.config = Mock(spec=AppConfig)
    context.config.csv_staging_file = csv_path


@when('the user selects "View Staging Table"')  # type: ignore
def step_select_view_staging_table(context: Any) -> None:
    """Simulate user selecting View Staging Table option."""
    # Set up components
    file_system = FileSystemAdapter()
    csv_adapter = CSVAdapter()
    view_staging_use_case = ViewStagingUseCase(file_system, csv_adapter)

    # Mock other use cases
    mock_process_receipt = Mock()
    mock_import_xlsx = Mock()

    # Create TUI
    tui = TerminalUI(
        file_system, mock_process_receipt, mock_import_xlsx, view_staging_use_case
    )

    # Capture output
    import io
    from contextlib import redirect_stdout

    output_buffer = io.StringIO()
    with redirect_stdout(output_buffer):
        tui.display_staging_table(context.config)

    context.output = output_buffer.getvalue()


# Removed specific step since generic step in tui_steps.py handles this case


# Removed specific steps since generic step in tui_steps.py handles these cases


@then("it should display a formatted table with headers")  # type: ignore
def step_display_formatted_table(context: Any) -> None:
    """Check that formatted table with headers is displayed."""
    output = context.output

    # Check for table presence
    assert "Staging Table" in output

    # Check for headers from the table
    for header in context.table.headings:
        assert header in output


@then("the table should contain the receipt data")  # type: ignore
def step_table_contains_data(context: Any) -> None:
    """Check that table contains the expected receipt data."""
    output = context.output

    # Check that all data from the Given table is present
    for row in context.table:
        assert row["Amount"] in output
        assert row["Description"] in output
        assert row["Currency"] in output
        assert row["Date"] in output


# Removed specific step since generic step in tui_steps.py handles this case


@then("it should display a formatted table")  # type: ignore
def step_display_table_general(context: Any) -> None:
    """Check that a table is displayed."""
    assert "Staging Table" in context.output


@then('the Hash column should show "abcdef12..." for long hashes')  # type: ignore
def step_hash_truncated(context: Any) -> None:
    """Check that long hashes are truncated."""
    assert "abcdef12..." in context.output


# Removed duplicate step - already defined in run_analysis_steps.py
