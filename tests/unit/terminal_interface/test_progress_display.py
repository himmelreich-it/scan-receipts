"""Unit tests for terminal interface progress display module."""

import pytest
from unittest.mock import patch
from terminal_interface.display.progress_display import ProgressDisplay


class TestProgressDisplay:
    """Test cases for progress display functionality."""
    
    def test_progress_display_initialization(self):
        """Test progress display initializes correctly with total file count."""
        total_files = 10
        progress = ProgressDisplay(total_files)
        assert progress.total_files == total_files
    
    @patch('builtins.print')
    def test_display_file_progress_format(self, mock_print):
        """Test progress display shows correct format: 'Processing file X of Y: filename'."""
        progress = ProgressDisplay(5)
        progress.display_file_progress(3, "test_file.txt")
        
        mock_print.assert_called_once_with(
            "Processing file 3 of 5: test_file.txt", 
            flush=True
        )
    
    @patch('builtins.print')
    def test_display_file_progress_sequence(self, mock_print):
        """Test progress display updates for each file in sequence."""
        progress = ProgressDisplay(3)
        
        # Simulate processing 3 files
        progress.display_file_progress(1, "file1.txt")
        progress.display_file_progress(2, "file2.txt")
        progress.display_file_progress(3, "file3.txt")
        
        # Verify all calls were made with correct parameters
        assert mock_print.call_count == 3
        mock_print.assert_any_call("Processing file 1 of 3: file1.txt", flush=True)
        mock_print.assert_any_call("Processing file 2 of 3: file2.txt", flush=True)
        mock_print.assert_any_call("Processing file 3 of 3: file3.txt", flush=True)
    
    @patch('builtins.print')
    def test_display_file_progress_maintains_consistent_format(self, mock_print):
        """Test progress display maintains consistent format across all files."""
        progress = ProgressDisplay(100)
        
        # Test with different file numbers and names
        test_cases = [
            (1, "short.txt"),
            (50, "medium_filename.pdf"),
            (100, "very_long_filename_with_many_characters.jpg")
        ]
        
        for file_num, filename in test_cases:
            progress.display_file_progress(file_num, filename)
        
        # Verify all calls follow the same format pattern
        for i, (file_num, filename) in enumerate(test_cases):
            call_args = mock_print.call_args_list[i]
            expected_message = f"Processing file {file_num} of 100: {filename}"
            assert call_args[0][0] == expected_message
            assert call_args[1]['flush'] is True
    
    @patch('builtins.print')
    def test_display_file_progress_handles_long_filenames(self, mock_print):
        """Test progress display handles very long filenames properly."""
        progress = ProgressDisplay(1)
        
        # Create a filename longer than 80 characters
        long_filename = "a" * 90 + ".txt"
        
        progress.display_file_progress(1, long_filename)
        
        # Verify the filename was truncated
        call_args = mock_print.call_args_list[0]
        printed_message = call_args[0][0]
        
        # Should contain truncated filename (77 chars + "...")
        assert "aaa..." in printed_message
        assert len(printed_message) <= 110  # Reasonable total length including prefix
        assert "Processing file 1 of 1:" in printed_message
    
    @patch('builtins.print')
    def test_display_file_progress_handles_special_characters(self, mock_print):
        """Test progress display handles special characters in filenames properly."""
        progress = ProgressDisplay(1)
        
        # Test with various special characters
        special_filename = "file_with_üñíçøde_chars_and_spaces.txt"
        
        progress.display_file_progress(1, special_filename)
        
        mock_print.assert_called_once_with(
            f"Processing file 1 of 1: {special_filename}",
            flush=True
        )
    
    @patch('builtins.print')
    def test_display_file_progress_uses_flush_for_immediate_output(self, mock_print):
        """Test progress display uses flush=True for immediate output."""
        progress = ProgressDisplay(1)
        
        progress.display_file_progress(1, "test.txt")
        
        # Verify flush=True was used to handle terminal output buffering
        call_args = mock_print.call_args_list[0]
        assert call_args[1]['flush'] is True
    
    @patch('builtins.print')
    def test_display_file_progress_with_zero_files(self, mock_print):
        """Test progress display handles edge case of zero total files."""
        progress = ProgressDisplay(0)
        
        # This shouldn't normally happen, but test graceful handling
        progress.display_file_progress(1, "test.txt")
        
        mock_print.assert_called_once_with(
            "Processing file 1 of 0: test.txt",
            flush=True
        )
    
    @patch('builtins.print')
    def test_display_file_progress_with_large_numbers(self, mock_print):
        """Test progress display handles large file counts properly."""
        progress = ProgressDisplay(99999)
        
        progress.display_file_progress(12345, "test.txt")
        
        mock_print.assert_called_once_with(
            "Processing file 12345 of 99999: test.txt",
            flush=True
        )
    
    @patch('builtins.print', side_effect=Exception("Print error"))
    def test_display_file_progress_handles_print_errors(self, mock_print):
        """Test progress display handles terminal output errors gracefully."""
        progress = ProgressDisplay(1)
        
        # This test ensures that if print fails, the exception propagates
        # as expected (we don't suppress it in the current implementation)
        with pytest.raises(Exception, match="Print error"):
            progress.display_file_progress(1, "test.txt")
    
    def test_filename_truncation_boundary(self):
        """Test filename truncation at exactly 80 characters."""
        progress = ProgressDisplay(1)
        
        # Test filename exactly at boundary
        exactly_80_chars = "a" * 76 + ".txt"  # 80 characters total
        with patch('builtins.print') as mock_print:
            progress.display_file_progress(1, exactly_80_chars)
            
            call_args = mock_print.call_args_list[0]
            printed_message = call_args[0][0]
            assert exactly_80_chars in printed_message
            assert "..." not in printed_message
        
        # Test filename just over boundary
        exactly_81_chars = "a" * 77 + ".txt"  # 81 characters total
        with patch('builtins.print') as mock_print:
            progress.display_file_progress(1, exactly_81_chars)
            
            call_args = mock_print.call_args_list[0]
            printed_message = call_args[0][0]
            assert "aaa..." in printed_message
            assert exactly_81_chars not in printed_message