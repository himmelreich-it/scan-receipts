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
        mock_exit = mocker.patch('sys.exit')
        mock_file_system = Mock()
        mock_process_receipt = Mock()
        mock_import_xlsx = Mock()
        mock_view_staging = Mock()

        tui = TerminalUI(
            mock_file_system,
            mock_process_receipt,
            mock_import_xlsx,
            mock_view_staging
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
            self.mock_view_staging
        )

        self.config = AppConfig(
            incoming_folder=Path("/tmp/incoming"),
            scanned_folder=Path("/tmp/scanned"),
            imported_folder=Path("/tmp/imported"),
            failed_folder=Path("/tmp/failed"),
            csv_staging_file=Path("/tmp/receipts.csv"),
            xlsx_output_file=Path("/tmp/output.xlsx")
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