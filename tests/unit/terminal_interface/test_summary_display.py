"""Unit tests for terminal interface summary display module."""

import pytest
from unittest.mock import patch
from terminal_interface.display.summary_display import SummaryDisplay


class TestSummaryDisplay:
    """Test cases for summary display functionality."""
    
    def _extract_print_calls(self, mock_print):
        """Helper to extract print call arguments safely."""
        calls = []
        for call in mock_print.call_args_list:
            if call[0]:  # If there are positional arguments
                calls.append(call[0][0])
            else:  # Empty print() call
                calls.append("")
        return calls
    
    def test_summary_display_initialization(self):
        """Test summary display initializes with zero counters."""
        summary = SummaryDisplay()
        assert summary.processed_count == 0
        assert summary.error_count == 0
        assert summary.duplicate_count == 0
    
    def test_set_counters_updates_all_values(self):
        """Test set_counters updates all counter values correctly."""
        summary = SummaryDisplay()
        
        summary.set_counters(10, 2, 3)
        
        assert summary.processed_count == 10
        assert summary.error_count == 2
        assert summary.duplicate_count == 3
    
    @patch('builtins.print')
    def test_display_summary_format_with_no_errors(self, mock_print):
        """Test summary display format when no errors occurred."""
        summary = SummaryDisplay()
        summary.set_counters(5, 0, 1)
        
        summary.display_summary()
        
        # Verify the correct number of print calls
        assert mock_print.call_count == 7
        
        # Verify specific content by checking call arguments
        calls = self._extract_print_calls(mock_print)
        
        assert "" in calls  # Empty line
        assert "=== PROCESSING SUMMARY ===" in calls
        assert "Files processed successfully: 5" in calls
        assert "Errors encountered: 0" in calls
        assert "Duplicates skipped: 1" in calls
        assert "Total files attempted: 6" in calls
        assert "Processing completed successfully!" in calls
    
    @patch('builtins.print')
    def test_display_summary_format_with_errors(self, mock_print):
        """Test summary display format when errors occurred."""
        summary = SummaryDisplay()
        summary.set_counters(8, 3, 2)
        
        summary.display_summary()
        
        # Verify the correct number of print calls
        assert mock_print.call_count == 7
        
        # Verify specific content
        calls = self._extract_print_calls(mock_print)
        assert "" in calls  # Empty line
        assert "=== PROCESSING SUMMARY ===" in calls
        assert "Files processed successfully: 8" in calls
        assert "Errors encountered: 3" in calls
        assert "Duplicates skipped: 2" in calls
        assert "Total files attempted: 13" in calls
        assert "Processing completed with 3 error(s)." in calls
    
    @patch('builtins.print')
    def test_display_summary_shows_all_counters(self, mock_print):
        """Test summary display shows all required counters."""
        summary = SummaryDisplay()
        summary.set_counters(15, 4, 7)
        
        summary.display_summary()
        
        # Check that all required information is displayed
        calls = self._extract_print_calls(mock_print)
        all_output = ' '.join(calls)
        assert "Files processed successfully: 15" in all_output
        assert "Errors encountered: 4" in all_output
        assert "Duplicates skipped: 7" in all_output
        assert "Total files attempted: 26" in all_output
    
    @patch('builtins.print')
    def test_display_summary_shows_after_processing_completes(self, mock_print):
        """Test summary display shows completion message."""
        summary = SummaryDisplay()
        summary.set_counters(10, 0, 0)
        
        summary.display_summary()
        
        # Verify completion message appears
        calls = self._extract_print_calls(mock_print)
        assert "Processing completed successfully!" in calls
    
    @patch('builtins.print')
    def test_display_summary_formats_numbers_clearly(self, mock_print):
        """Test summary display formats numbers clearly."""
        summary = SummaryDisplay()
        summary.set_counters(9999, 123, 456)
        
        summary.display_summary()
        
        # Verify large numbers are displayed clearly
        calls = self._extract_print_calls(mock_print)
        assert "Files processed successfully: 9999" in calls
        assert "Errors encountered: 123" in calls
        assert "Duplicates skipped: 456" in calls
        assert "Total files attempted: 10578" in calls
    
    def test_get_total_attempted_calculates_correctly(self):
        """Test get_total_attempted returns correct sum."""
        summary = SummaryDisplay()
        
        # Test with various combinations
        test_cases = [
            (0, 0, 0, 0),
            (5, 0, 0, 5),
            (10, 2, 3, 15),
            (100, 25, 50, 175),
            (1, 1, 1, 3)
        ]
        
        for processed, errors, duplicates, expected_total in test_cases:
            summary.set_counters(processed, errors, duplicates)
            assert summary.get_total_attempted() == expected_total
    
    def test_get_success_rate_calculates_correctly(self):
        """Test get_success_rate returns correct percentage."""
        summary = SummaryDisplay()
        
        # Test with various scenarios
        test_cases = [
            (0, 0, 0, 0.0),  # No files attempted
            (10, 0, 0, 100.0),  # All successful
            (5, 5, 0, 50.0),  # Half successful
            (8, 1, 1, 80.0),  # 8 out of 10 successful
            (1, 3, 0, 25.0),  # 1 out of 4 successful
        ]
        
        for processed, errors, duplicates, expected_rate in test_cases:
            summary.set_counters(processed, errors, duplicates)
            assert summary.get_success_rate() == expected_rate
    
    def test_reset_counters_resets_to_zero(self):
        """Test reset_counters resets all counters to zero."""
        summary = SummaryDisplay()
        
        # Set some non-zero values
        summary.set_counters(10, 5, 3)
        assert summary.processed_count == 10
        assert summary.error_count == 5
        assert summary.duplicate_count == 3
        
        # Reset and verify
        summary.reset_counters()
        assert summary.processed_count == 0
        assert summary.error_count == 0
        assert summary.duplicate_count == 0
    
    @patch('builtins.print')
    def test_display_summary_handles_zero_values(self, mock_print):
        """Test summary display handles zero values correctly."""
        summary = SummaryDisplay()
        summary.set_counters(0, 0, 0)
        
        summary.display_summary()
        
        calls = self._extract_print_calls(mock_print)
        assert "Files processed successfully: 0" in calls
        assert "Errors encountered: 0" in calls
        assert "Duplicates skipped: 0" in calls
        assert "Total files attempted: 0" in calls
        assert "Processing completed successfully!" in calls
    
    @patch('builtins.print')
    def test_display_summary_handles_large_numbers(self, mock_print):
        """Test summary display handles very large numbers."""
        summary = SummaryDisplay()
        summary.set_counters(999999, 12345, 67890)
        
        summary.display_summary()
        
        calls = self._extract_print_calls(mock_print)
        assert "Files processed successfully: 999999" in calls
        assert "Errors encountered: 12345" in calls
        assert "Duplicates skipped: 67890" in calls
        assert "Total files attempted: 1080234" in calls
    
    @patch('builtins.print')
    def test_display_summary_visual_separation(self, mock_print):
        """Test summary display includes visual separation."""
        summary = SummaryDisplay()
        summary.set_counters(1, 0, 0)
        
        summary.display_summary()
        
        # First call should be empty line for visual separation
        calls = self._extract_print_calls(mock_print)
        assert calls[0] == ""
        
        # Second call should be the header
        assert calls[1] == "=== PROCESSING SUMMARY ==="
    
    @patch('builtins.print')
    def test_display_summary_error_message_singular_vs_plural(self, mock_print):
        """Test summary display uses correct singular/plural for errors."""
        summary = SummaryDisplay()
        
        # Test singular (1 error)
        summary.set_counters(5, 1, 0)
        summary.display_summary()
        
        calls = self._extract_print_calls(mock_print)
        assert "Processing completed with 1 error(s)." in calls
        
        # Reset mock for next test
        mock_print.reset_mock()
        
        # Test plural (multiple errors)
        summary.set_counters(5, 3, 0)
        summary.display_summary()
        
        calls = self._extract_print_calls(mock_print)
        assert "Processing completed with 3 error(s)." in calls
    
    @patch('builtins.print', side_effect=Exception("Print error"))
    def test_display_summary_propagates_print_errors(self, mock_print):
        """Test summary display propagates print errors if they occur."""
        summary = SummaryDisplay()
        summary.set_counters(1, 0, 0)
        
        # This test ensures that if print fails, the exception propagates
        with pytest.raises(Exception, match="Print error"):
            summary.display_summary()
    
    def test_counters_handle_edge_cases(self):
        """Test counters handle edge case values correctly."""
        summary = SummaryDisplay()
        
        # Test with maximum typical values
        summary.set_counters(2**31 - 1, 2**31 - 1, 2**31 - 1)
        assert summary.processed_count == 2**31 - 1
        assert summary.error_count == 2**31 - 1
        assert summary.duplicate_count == 2**31 - 1
        
        # Test total calculation doesn't overflow for reasonable values
        summary.set_counters(1000000, 1000000, 1000000)
        assert summary.get_total_attempted() == 3000000
        assert summary.get_success_rate() == pytest.approx(33.333333, rel=1e-5)
    
    def test_success_rate_precision(self):
        """Test success rate calculation precision."""
        summary = SummaryDisplay()
        
        # Test cases that might have precision issues
        summary.set_counters(1, 2, 0)  # 1/3 = 0.333...
        rate = summary.get_success_rate()
        assert abs(rate - 33.333333333333336) < 0.001
        
        summary.set_counters(2, 1, 0)  # 2/3 = 0.666...
        rate = summary.get_success_rate()
        assert abs(rate - 66.66666666666667) < 0.001