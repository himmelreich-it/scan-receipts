"""Unit tests for TUI module."""

from unittest.mock import Mock
from pytest_mock import MockerFixture  # type: ignore[import-untyped]

from adapters.primary.tui.terminal_ui import TerminalUI
from core.domain.configuration import AppConfig


class TestTerminalUI:
    """Test TerminalUI class."""

    def test_signal_handler_exits(self, mocker: MockerFixture) -> None:
        """Test that signal handler calls sys.exit."""
        mock_exit = mocker.patch("sys.exit")

        # Create TUI instance with mock dependencies
        file_system = Mock()
        process_receipt_use_case = Mock()
        import_to_xlsx_use_case = Mock()
        view_staging_use_case = Mock()

        tui = TerminalUI(
            file_system,
            process_receipt_use_case,
            import_to_xlsx_use_case,
            view_staging_use_case,
        )

        tui.signal_handler(2, None)
        mock_exit.assert_called_once_with(0)

    def test_handle_menu_choice_option_1(self) -> None:
        """Test handling option 1 - Run Analysis."""
        # Create TUI instance with mock dependencies
        file_system = Mock()
        process_receipt_use_case = Mock()
        import_to_xlsx_use_case = Mock()
        view_staging_use_case = Mock()

        tui = TerminalUI(
            file_system,
            process_receipt_use_case,
            import_to_xlsx_use_case,
            view_staging_use_case,
        )

        config = Mock(spec=AppConfig)
        result = tui.handle_menu_choice("1", config)
        assert result is True
        process_receipt_use_case.execute.assert_called_once_with(config)

    def test_handle_menu_choice_option_2(self) -> None:
        """Test handling option 2 - Import to XLSX."""
        # Create TUI instance with mock dependencies
        file_system = Mock()
        process_receipt_use_case = Mock()
        import_to_xlsx_use_case = Mock()
        view_staging_use_case = Mock()

        tui = TerminalUI(
            file_system,
            process_receipt_use_case,
            import_to_xlsx_use_case,
            view_staging_use_case,
        )

        config = Mock(spec=AppConfig)
        result = tui.handle_menu_choice("2", config)
        assert result is True
        import_to_xlsx_use_case.execute.assert_called_once_with(config)

    def test_handle_menu_choice_option_3(self) -> None:
        """Test handling option 3 - View Staging Table."""
        # Create TUI instance with mock dependencies
        file_system = Mock()
        process_receipt_use_case = Mock()
        import_to_xlsx_use_case = Mock()
        view_staging_use_case = Mock()

        tui = TerminalUI(
            file_system,
            process_receipt_use_case,
            import_to_xlsx_use_case,
            view_staging_use_case,
        )

        config = Mock(spec=AppConfig)
        result = tui.handle_menu_choice("3", config)
        assert result is True

    def test_handle_menu_choice_option_4(self) -> None:
        """Test handling option 4 - Exit."""
        # Create TUI instance with mock dependencies
        file_system = Mock()
        process_receipt_use_case = Mock()
        import_to_xlsx_use_case = Mock()
        view_staging_use_case = Mock()

        tui = TerminalUI(
            file_system,
            process_receipt_use_case,
            import_to_xlsx_use_case,
            view_staging_use_case,
        )

        config = Mock(spec=AppConfig)
        result = tui.handle_menu_choice("4", config)
        assert result is False

    def test_handle_menu_choice_invalid(self) -> None:
        """Test handling invalid menu choice."""
        # Create TUI instance with mock dependencies
        file_system = Mock()
        process_receipt_use_case = Mock()
        import_to_xlsx_use_case = Mock()
        view_staging_use_case = Mock()

        tui = TerminalUI(
            file_system,
            process_receipt_use_case,
            import_to_xlsx_use_case,
            view_staging_use_case,
        )

        config = Mock(spec=AppConfig)

        result = tui.handle_menu_choice("5", config)
        assert result is True

        result = tui.handle_menu_choice("0", config)
        assert result is True

        result = tui.handle_menu_choice("abc", config)
        assert result is True

        result = tui.handle_menu_choice("", config)
        assert result is True
