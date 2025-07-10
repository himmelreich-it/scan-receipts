"""Unit tests for terminal interface messages module."""

import pytest
from unittest.mock import patch
from terminal_interface.display.messages import display_startup_message


class TestDisplayStartupMessage:
    """Test cases for startup message display functionality."""
    
    @patch('builtins.print')
    def test_display_startup_message(self, mock_print):
        """Test startup message displays correctly."""
        display_startup_message()
        
        # Verify the expected messages are printed
        assert mock_print.call_count == 3
        mock_print.assert_any_call("Receipt Processing Script")
        mock_print.assert_any_call("Scanning input folder for receipt files...")
        mock_print.assert_any_call()  # Empty line
    
    @patch('builtins.print')
    def test_startup_message_content(self, mock_print):
        """Test startup message content meets acceptance criteria."""
        display_startup_message()
        
        # Get all printed messages
        printed_messages = [call.args[0] for call in mock_print.call_args_list if call.args]
        
        # Check that message mentions receipt processing operation
        assert any("Receipt Processing" in msg for msg in printed_messages)
        
        # Check that message mentions input folder scanning
        assert any("input folder" in msg for msg in printed_messages)
        
        # Check that message is concise (reasonable length)
        for msg in printed_messages:
            assert len(msg) <= 100  # Keep messages concise
    
    @patch('builtins.print')
    def test_startup_message_appears_first(self, mock_print):
        """Test startup message appears before any processing begins."""
        display_startup_message()
        
        # First call should be the title
        first_call = mock_print.call_args_list[0]
        assert first_call.args[0] == "Receipt Processing Script"
        
        # Second call should be about scanning
        second_call = mock_print.call_args_list[1]
        assert "Scanning input folder" in second_call.args[0]
    
    @patch('builtins.print', side_effect=Exception("Print error"))
    def test_startup_message_handles_print_errors(self, mock_print):
        """Test startup message handles terminal output issues gracefully."""
        # This test ensures that if print fails, the exception propagates
        # as expected (we don't suppress it in the current implementation)
        with pytest.raises(Exception, match="Print error"):
            display_startup_message()
    
    def test_startup_message_no_side_effects(self):
        """Test startup message function has no side effects beyond printing."""
        # Test that the function doesn't modify any global state
        # and returns None as expected
        result = display_startup_message()
        assert result is None