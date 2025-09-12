"""Unit tests for main TUI module."""

from typing import Any
from unittest.mock import patch

from scan_receipts.main import handle_menu_choice, signal_handler


class TestSignalHandler:
    """Test signal handling."""
    
    @patch('sys.exit')
    def test_signal_handler_exits(self, mock_exit: Any) -> None:
        """Test that signal handler calls sys.exit."""
        signal_handler(2, None)
        mock_exit.assert_called_once_with(0)


class TestHandleMenuChoice:
    """Test menu choice handling."""
    
    def test_handle_menu_choice_option_1(self):
        """Test handling option 1 - Run Analysis."""
        result = handle_menu_choice("1")
        assert result is True
    
    def test_handle_menu_choice_option_2(self):
        """Test handling option 2 - Import to XLSX."""
        result = handle_menu_choice("2")
        assert result is True
    
    def test_handle_menu_choice_option_3(self):
        """Test handling option 3 - View Staging Table."""
        result = handle_menu_choice("3")
        assert result is True
    
    def test_handle_menu_choice_option_4(self):
        """Test handling option 4 - Exit."""
        result = handle_menu_choice("4")
        assert result is False
    
    def test_handle_menu_choice_invalid(self):
        """Test handling invalid menu choice."""
        result = handle_menu_choice("5")
        assert result is True
        
        result = handle_menu_choice("0")
        assert result is True
        
        result = handle_menu_choice("abc")
        assert result is True
        
        result = handle_menu_choice("")
        assert result is True