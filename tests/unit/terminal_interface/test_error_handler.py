"""Unit tests for terminal interface error handler module."""

import pytest
import sys
from unittest.mock import patch, MagicMock
from terminal_interface.errors.error_handler import ErrorHandler


class TestErrorHandler:
    """Test cases for error handler functionality."""
    
    def test_error_handler_initialization(self):
        """Test error handler initializes with zero error count."""
        error_handler = ErrorHandler()
        assert error_handler.error_count == 0
    
    @patch('sys.stderr')
    @patch('builtins.print')
    def test_display_file_error_format(self, mock_print, mock_stderr):
        """Test error display shows correct format: 'ERROR processing filename: error_message'."""
        error_handler = ErrorHandler()
        
        error_handler.display_file_error("test_file.txt", "File not found")
        
        mock_print.assert_called_once_with(
            "ERROR processing test_file.txt: File not found",
            file=sys.stderr,
            flush=True
        )
    
    @patch('sys.stderr')
    @patch('builtins.print')
    def test_display_file_error_increments_counter(self, mock_print, mock_stderr):
        """Test error display increments error counter."""
        error_handler = ErrorHandler()
        
        assert error_handler.get_error_count() == 0
        
        error_handler.display_file_error("test1.txt", "Error 1")
        assert error_handler.get_error_count() == 1
        
        error_handler.display_file_error("test2.txt", "Error 2")
        assert error_handler.get_error_count() == 2
    
    @patch('sys.stderr')
    @patch('builtins.print')
    def test_display_processing_error_with_exception(self, mock_print, mock_stderr):
        """Test error display handles exceptions properly."""
        error_handler = ErrorHandler()
        
        # Create a mock exception
        test_exception = ValueError("Invalid file format")
        
        error_handler.display_processing_error("test.txt", test_exception)
        
        mock_print.assert_called_once_with(
            "ERROR processing test.txt: Invalid file format",
            file=sys.stderr,
            flush=True
        )
        assert error_handler.get_error_count() == 1
    
    @patch('sys.stderr')
    @patch('builtins.print')
    def test_display_processing_error_with_none_exception(self, mock_print, mock_stderr):
        """Test error display handles None exception gracefully."""
        error_handler = ErrorHandler()
        
        error_handler.display_processing_error("test.txt", None)
        
        mock_print.assert_called_once_with(
            "ERROR processing test.txt: Unknown error",
            file=sys.stderr,
            flush=True
        )
        assert error_handler.get_error_count() == 1
    
    @patch('sys.stderr')
    @patch('builtins.print')
    def test_display_multiple_errors_continues_processing(self, mock_print, mock_stderr):
        """Test error display allows processing to continue after errors."""
        error_handler = ErrorHandler()
        
        # Simulate multiple file processing errors
        errors = [
            ("file1.txt", "Permission denied"),
            ("file2.txt", "File corrupted"),
            ("file3.txt", "Invalid format")
        ]
        
        for filename, error_msg in errors:
            error_handler.display_file_error(filename, error_msg)
        
        # Verify all errors were displayed
        assert mock_print.call_count == 3
        assert error_handler.get_error_count() == 3
        
        # Verify each error was displayed correctly
        expected_calls = [
            (f"ERROR processing {filename}: {error_msg}",),
            (f"ERROR processing {filename}: {error_msg}",),
            (f"ERROR processing {filename}: {error_msg}",)
        ]
        for i, (filename, error_msg) in enumerate(errors):
            call_args = mock_print.call_args_list[i]
            assert call_args[0][0] == f"ERROR processing {filename}: {error_msg}"
            assert call_args[1]['file'] == sys.stderr
            assert call_args[1]['flush'] is True
    
    @patch('sys.stderr')
    @patch('builtins.print')
    def test_error_handler_uses_stderr_for_output(self, mock_print, mock_stderr):
        """Test error handler uses stderr for error output."""
        error_handler = ErrorHandler()
        
        error_handler.display_file_error("test.txt", "Test error")
        
        # Verify stderr was used for output
        call_args = mock_print.call_args_list[0]
        assert call_args[1]['file'] == sys.stderr
    
    @patch('sys.stderr')
    @patch('builtins.print')
    def test_error_handler_uses_flush_for_immediate_output(self, mock_print, mock_stderr):
        """Test error handler uses flush=True for immediate output."""
        error_handler = ErrorHandler()
        
        error_handler.display_file_error("test.txt", "Test error")
        
        # Verify flush=True was used for immediate output
        call_args = mock_print.call_args_list[0]
        assert call_args[1]['flush'] is True
    
    @patch('sys.stderr')
    @patch('builtins.print')
    def test_error_handler_handles_special_characters(self, mock_print, mock_stderr):
        """Test error handler handles special characters in filenames and messages."""
        error_handler = ErrorHandler()
        
        # Test with special characters in filename and error message
        special_filename = "file_with_üñíçøde_chars.txt"
        special_error = "Error with special chars: ñø permissions"
        
        error_handler.display_file_error(special_filename, special_error)
        
        mock_print.assert_called_once_with(
            f"ERROR processing {special_filename}: {special_error}",
            file=sys.stderr,
            flush=True
        )
    
    @patch('sys.stderr')
    @patch('builtins.print')
    def test_error_handler_handles_long_filenames(self, mock_print, mock_stderr):
        """Test error handler handles very long filenames."""
        error_handler = ErrorHandler()
        
        # Create a very long filename
        long_filename = "a" * 200 + ".txt"
        
        error_handler.display_file_error(long_filename, "Test error")
        
        call_args = mock_print.call_args_list[0]
        printed_message = call_args[0][0]
        
        # Should display the full filename (no truncation in error messages)
        assert long_filename in printed_message
        assert "ERROR processing" in printed_message
    
    @patch('sys.stderr')
    @patch('builtins.print')
    def test_error_handler_handles_long_error_messages(self, mock_print, mock_stderr):
        """Test error handler handles very long error messages."""
        error_handler = ErrorHandler()
        
        # Create a very long error message
        long_error = "This is a very long error message that describes in detail what went wrong during processing: " + "x" * 500
        
        error_handler.display_file_error("test.txt", long_error)
        
        call_args = mock_print.call_args_list[0]
        printed_message = call_args[0][0]
        
        # Should display the full error message (no truncation)
        assert long_error in printed_message
        assert "ERROR processing test.txt:" in printed_message
    
    def test_get_error_count_returns_correct_count(self):
        """Test get_error_count returns the correct number of errors."""
        error_handler = ErrorHandler()
        
        assert error_handler.get_error_count() == 0
        
        with patch('sys.stderr'), patch('builtins.print'):
            error_handler.display_file_error("file1.txt", "Error 1")
            error_handler.display_file_error("file2.txt", "Error 2")
            error_handler.display_file_error("file3.txt", "Error 3")
        
        assert error_handler.get_error_count() == 3
    
    def test_reset_error_count_resets_to_zero(self):
        """Test reset_error_count resets counter to zero."""
        error_handler = ErrorHandler()
        
        with patch('sys.stderr'), patch('builtins.print'):
            error_handler.display_file_error("file1.txt", "Error 1")
            error_handler.display_file_error("file2.txt", "Error 2")
        
        assert error_handler.get_error_count() == 2
        
        error_handler.reset_error_count()
        assert error_handler.get_error_count() == 0
    
    @patch('sys.stderr')
    @patch('builtins.print', side_effect=Exception("Print error"))
    def test_error_handler_propagates_print_errors(self, mock_print, mock_stderr):
        """Test error handler propagates print errors if they occur."""
        error_handler = ErrorHandler()
        
        # This test ensures that if print fails, the exception propagates
        with pytest.raises(Exception, match="Print error"):
            error_handler.display_file_error("test.txt", "Test error")
    
    @patch('sys.stderr')
    @patch('builtins.print')
    def test_error_handler_handles_cascading_errors(self, mock_print, mock_stderr):
        """Test error handler handles multiple cascading errors gracefully."""
        error_handler = ErrorHandler()
        
        # Simulate cascading errors from the same file
        cascading_errors = [
            ("problem_file.txt", "Permission denied"),
            ("problem_file.txt", "File locked by another process"),
            ("problem_file.txt", "Disk full")
        ]
        
        for filename, error_msg in cascading_errors:
            error_handler.display_file_error(filename, error_msg)
        
        # Each error should be counted separately
        assert error_handler.get_error_count() == 3
        assert mock_print.call_count == 3
    
    def test_error_handler_maintains_count_across_methods(self):
        """Test error handler maintains consistent count across different methods."""
        error_handler = ErrorHandler()
        
        with patch('sys.stderr'), patch('builtins.print'):
            # Mix of direct error display and exception handling
            error_handler.display_file_error("file1.txt", "Direct error")
            error_handler.display_processing_error("file2.txt", ValueError("Exception error"))
            error_handler.display_file_error("file3.txt", "Another direct error")
        
        assert error_handler.get_error_count() == 3