"""Tests for terminal interface main module."""

import pytest
import sys
import signal
from unittest.mock import patch, MagicMock
from src.terminal_interface.main import main, setup_signal_handlers


def test_script_starts_when_executed():
    """Test: Script starts when executed with `python main.py`."""
    with patch('sys.exit') as mock_exit:
        with patch('builtins.print') as mock_print:
            main()
            mock_exit.assert_called_with(0)
            mock_print.assert_called()


def test_handles_command_line_execution_properly():
    """Test: handles command-line execution properly."""
    with patch('sys.exit') as mock_exit:
        main()
        mock_exit.assert_called_with(0)


def test_provides_clean_exit_codes():
    """Test: provides clean exit codes (0 for success, 1 for errors)."""
    # Test success case
    with patch('sys.exit') as mock_exit:
        main()
        mock_exit.assert_called_with(0)
    
    # Test error case - mock the logging.warning to raise an exception
    with patch('sys.exit') as mock_exit:
        with patch('logging.warning', side_effect=Exception("Test error")):
            main()
            mock_exit.assert_called_with(1)


def test_main_successful_execution():
    """Test main function completes successfully and returns exit code 0."""
    with patch('sys.exit') as mock_exit:
        main()
        mock_exit.assert_called_with(0)


def test_main_handles_exceptions():
    """Test main function catches exceptions and returns exit code 1."""
    with patch('sys.exit') as mock_exit:
        with patch('logging.warning', side_effect=Exception("Test error")):
            main()
            mock_exit.assert_called_with(1)


def test_main_handles_keyboard_interrupt():
    """Test main function handles Ctrl+C gracefully."""
    # Test signal handler setup
    with patch('signal.signal') as mock_signal:
        setup_signal_handlers()
        # Check that signal.signal was called for SIGINT and SIGTERM
        assert mock_signal.call_count >= 2
        call_args = [call[0] for call in mock_signal.call_args_list]
        assert any(signal.SIGINT in args for args in call_args)
        assert any(signal.SIGTERM in args for args in call_args)


def test_signal_handler_handles_sigint():
    """Test signal handler handles SIGINT (Ctrl+C) gracefully."""
    with patch('sys.exit') as mock_exit:
        with patch('builtins.print') as mock_print:
            setup_signal_handlers()
            
            # Get the signal handler that was set
            current_handler = signal.signal(signal.SIGINT, signal.SIG_DFL)
            # Reset to our handler
            signal.signal(signal.SIGINT, current_handler)
            
            # Simulate SIGINT by calling the handler directly
            if callable(current_handler):
                current_handler(signal.SIGINT, None)
                mock_print.assert_called_with("\nOperation cancelled by user.")
                mock_exit.assert_called_with(0)