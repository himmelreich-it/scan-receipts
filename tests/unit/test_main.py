"""Unit tests for main TUI module."""

from pathlib import Path
from unittest.mock import Mock

from pytest_mock import MockerFixture  # type: ignore[import-untyped]

from adapters.primary.tui.terminal_ui import TerminalUI
from core.domain.configuration import AppConfig


class TestSignalHandler:
    """Test signal handling."""

    def test_signal_handler_exits(self, mocker: MockerFixture) -> None:
        """Test that signal handler calls sys.exit."""
        mock_exit = mocker.patch("sys.exit")
        mock_file_system = Mock()
        mock_process_receipt = Mock()
        mock_import_xlsx = Mock()
        mock_view_staging = Mock()

        tui = TerminalUI(
            mock_file_system, mock_process_receipt, mock_import_xlsx, mock_view_staging
        )

        tui.signal_handler(2, None)
        mock_exit.assert_called_once_with(0)


class TestHandleMenuChoice:
    """Test menu choice handling."""

    def setup_method(self):
        """Set up test fixture."""
        self.mock_file_system = Mock()
        self.mock_process_receipt = Mock()
        self.mock_import_xlsx = Mock()
        self.mock_view_staging = Mock()

        self.tui = TerminalUI(
            self.mock_file_system,
            self.mock_process_receipt,
            self.mock_import_xlsx,
            self.mock_view_staging,
        )

        self.config = AppConfig(
            incoming_folder=Path("/tmp/incoming"),
            scanned_folder=Path("/tmp/scanned"),
            imported_folder=Path("/tmp/imported"),
            failed_folder=Path("/tmp/failed"),
            csv_staging_file=Path("/tmp/receipts.csv"),
            xlsx_output_file=Path("/tmp/output.xlsx"),
        )

    def test_handle_menu_choice_option_1(self):
        """Test handling option 1 - Run Analysis."""
        result = self.tui.handle_menu_choice("1", self.config)
        assert result is True
        self.mock_process_receipt.execute.assert_called_once_with(self.config)

    def test_handle_menu_choice_option_2(self):
        """Test handling option 2 - Import to XLSX."""
        result = self.tui.handle_menu_choice("2", self.config)
        assert result is True
        self.mock_import_xlsx.execute.assert_called_once_with(self.config)

    def test_handle_menu_choice_option_3(self):
        """Test handling option 3 - View Staging Table."""
        result = self.tui.handle_menu_choice("3", self.config)
        assert result is True
        # View staging table doesn't call execute, it calls display_staging_table internally

    def test_handle_menu_choice_option_4(self):
        """Test handling option 4 - Exit."""
        result = self.tui.handle_menu_choice("4", self.config)
        assert result is False

    def test_handle_menu_choice_invalid(self):
        """Test handling invalid menu choice."""
        result = self.tui.handle_menu_choice("5", self.config)
        assert result is True

        result = self.tui.handle_menu_choice("0", self.config)
        assert result is True

        result = self.tui.handle_menu_choice("abc", self.config)
        assert result is True

        result = self.tui.handle_menu_choice("", self.config)
        assert result is True


class TestDisplayStatus:
    """Test status display functionality."""

    def setup_method(self):
        """Set up test fixture."""
        self.mock_file_system = Mock()
        self.mock_process_receipt = Mock()
        self.mock_import_xlsx = Mock()
        self.mock_view_staging = Mock()

        self.tui = TerminalUI(
            self.mock_file_system,
            self.mock_process_receipt,
            self.mock_import_xlsx,
            self.mock_view_staging,
        )

        self.config = AppConfig(
            incoming_folder=Path("/tmp/incoming"),
            scanned_folder=Path("/tmp/scanned"),
            imported_folder=Path("/tmp/imported"),
            failed_folder=Path("/tmp/failed"),
            csv_staging_file=Path("/tmp/receipts.csv"),
            xlsx_output_file=Path("/tmp/output.xlsx"),
        )

    def test_display_status_shows_configured_paths(self, mocker: MockerFixture) -> None:
        """Test that display_status shows all configured paths with labels."""
        mock_rprint = mocker.patch("adapters.primary.tui.terminal_ui.rprint")
        self.mock_file_system.count_receipt_files.return_value = 5
        self.mock_view_staging.execute.return_value = "test staging info"

        self.tui.display_status(self.config)

        # Verify all paths are displayed with their labels
        mock_rprint.assert_any_call("Configured Paths:")
        mock_rprint.assert_any_call(
            f"Incoming: {self.config.incoming_folder.resolve()}"
        )
        mock_rprint.assert_any_call(f"Scanned: {self.config.scanned_folder.resolve()}")
        mock_rprint.assert_any_call(
            f"Imported: {self.config.imported_folder.resolve()}"
        )
        mock_rprint.assert_any_call(f"Failed: {self.config.failed_folder.resolve()}")
        mock_rprint.assert_any_call(f"XLSX: {self.config.xlsx_output_file.resolve()}")
        mock_rprint.assert_any_call(f"CSV: {self.config.csv_staging_file.resolve()}")

    def test_display_status_shows_file_counts_after_paths(
        self, mocker: MockerFixture
    ) -> None:
        """Test that file counts are displayed after configured paths."""
        mock_rprint = mocker.patch("adapters.primary.tui.terminal_ui.rprint")
        self.mock_file_system.count_receipt_files.side_effect = [3, 1]  # input, failed
        self.mock_view_staging.execute.return_value = "test staging info"

        self.tui.display_status(self.config)

        # Verify file counts are still displayed
        mock_rprint.assert_any_call("Input Folder: 3 files")
        mock_rprint.assert_any_call("Failed Folder: 1 files")
        mock_rprint.assert_any_call("Staging: test staging info")

    def test_display_status_converts_relative_paths_to_absolute(
        self, mocker: MockerFixture
    ) -> None:
        """Test that relative paths are converted to absolute paths."""
        mock_rprint = mocker.patch("adapters.primary.tui.terminal_ui.rprint")
        self.mock_file_system.count_receipt_files.return_value = 0
        self.mock_view_staging.execute.return_value = None

        # Create config with relative paths
        config_with_relative = AppConfig(
            incoming_folder=Path("./incoming"),
            scanned_folder=Path("./scanned"),
            imported_folder=Path("./imported"),
            failed_folder=Path("./failed"),
            csv_staging_file=Path("./receipts.csv"),
            xlsx_output_file=Path("./output.xlsx"),
        )

        self.tui.display_status(config_with_relative)

        # Check that resolve() was called by verifying absolute paths are displayed
        calls = mock_rprint.call_args_list
        call_strings = [str(call) for call in calls]

        # Verify that absolute paths are displayed (should start with '/')
        path_calls = [
            call
            for call in call_strings
            if any(
                label in call
                for label in [
                    "Incoming:",
                    "Scanned:",
                    "Imported:",
                    "Failed:",
                    "XLSX:",
                    "CSV:",
                ]
            )
        ]
        for call_str in path_calls:
            # Extract the path from the call string
            if ":" in call_str:
                path_part = call_str.split(":", 1)[1].strip().strip("')")
                # Should be absolute path (starts with /)
                assert path_part.startswith("/"), (
                    f"Path should be absolute: {path_part}"
                )
