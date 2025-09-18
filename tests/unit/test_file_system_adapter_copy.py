"""Unit tests for file system adapter copy functionality."""

from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from adapters.secondary.file_system_adapter import FileSystemAdapter


class TestFileSystemAdapterCopy:
    """Test cases for file system adapter copy functionality."""

    def test_copy_file_to_folder_success(self):
        """Test successful file copy operation."""
        adapter = FileSystemAdapter()
        source_file = Path("/test/source/receipt.jpg")
        destination_folder = Path("/test/destination")

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.mkdir") as mock_mkdir:
                with patch("shutil.copy2") as mock_copy:
                    result = adapter.copy_file_to_folder(source_file, destination_folder)

        # Verify destination folder was created
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

        # Verify file was copied
        expected_destination = destination_folder / "receipt.jpg"
        mock_copy.assert_called_once_with(source_file, expected_destination)

        # Verify return value
        assert result == expected_destination

    def test_copy_file_to_folder_source_not_exists(self):
        """Test copy operation fails when source file doesn't exist."""
        adapter = FileSystemAdapter()
        source_file = Path("/test/nonexistent.jpg")
        destination_folder = Path("/test/destination")

        with patch("pathlib.Path.exists", return_value=False):
            with pytest.raises(OSError, match="Source file does not exist"):
                adapter.copy_file_to_folder(source_file, destination_folder)

    def test_copy_file_to_folder_copy_fails(self):
        """Test copy operation handles copy failure."""
        adapter = FileSystemAdapter()
        source_file = Path("/test/source/receipt.jpg")
        destination_folder = Path("/test/destination")

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.mkdir"):
                with patch("shutil.copy2", side_effect=OSError("Permission denied")):
                    with pytest.raises(OSError, match="Failed to copy file"):
                        adapter.copy_file_to_folder(source_file, destination_folder)

    def test_write_error_log_success(self):
        """Test successful error log writing."""
        adapter = FileSystemAdapter()
        failed_folder = Path("/test/failed")
        filename = "receipt.jpg"
        error_message = "AI extraction failed"

        mock_file = mock_open()
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            with patch("builtins.open", mock_file):
                with patch("datetime.datetime") as mock_datetime:
                    mock_datetime.now.return_value.strftime.return_value = "2024-03-15 14:30:00"
                    adapter.write_error_log(failed_folder, filename, error_message)

        # Verify failed folder was created
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

        # Verify file was opened for writing
        expected_log_path = failed_folder / "receipt_error.txt"
        mock_file.assert_called_once_with(expected_log_path, "w", encoding="utf-8")

        # Verify log content was written
        written_content = "".join(call.args[0] for call in mock_file().write.call_args_list)
        assert "Error processing file: receipt.jpg" in written_content
        assert "Timestamp: 2024-03-15 14:30:00" in written_content
        assert "Error: AI extraction failed" in written_content

    def test_write_error_log_with_extension(self):
        """Test error log writing strips file extension correctly."""
        adapter = FileSystemAdapter()
        failed_folder = Path("/test/failed")
        filename = "complex.receipt.name.pdf"
        error_message = "Processing error"

        mock_file = mock_open()
        with patch("pathlib.Path.mkdir"):
            with patch("builtins.open", mock_file):
                with patch("datetime.datetime") as mock_datetime:
                    mock_datetime.now.return_value.strftime.return_value = "2024-03-15 14:30:00"
                    adapter.write_error_log(failed_folder, filename, error_message)

        # Verify correct log filename (extension stripped)
        expected_log_path = failed_folder / "complex.receipt.name_error.txt"
        mock_file.assert_called_once_with(expected_log_path, "w", encoding="utf-8")

    def test_write_error_log_handles_write_failure(self):
        """Test error log writing handles file write failure gracefully."""
        adapter = FileSystemAdapter()
        failed_folder = Path("/test/failed")
        filename = "receipt.jpg"
        error_message = "AI extraction failed"

        with patch("pathlib.Path.mkdir"):
            with patch("builtins.open", side_effect=IOError("Write failed")):
                # Should not raise exception
                adapter.write_error_log(failed_folder, filename, error_message)

    def test_write_error_log_handles_special_characters(self):
        """Test error log writing handles special characters in filename and error."""
        adapter = FileSystemAdapter()
        failed_folder = Path("/test/failed")
        filename = "café_receipt_€.jpg"
        error_message = "Error with special chars: 'quotes' and \"double quotes\""

        mock_file = mock_open()
        with patch("pathlib.Path.mkdir"):
            with patch("builtins.open", mock_file):
                with patch("datetime.datetime") as mock_datetime:
                    mock_datetime.now.return_value.strftime.return_value = "2024-03-15 14:30:00"
                    adapter.write_error_log(failed_folder, filename, error_message)

        # Verify file was opened (filename should be sanitized)
        expected_log_path = failed_folder / "café_receipt_€_error.txt"
        mock_file.assert_called_once_with(expected_log_path, "w", encoding="utf-8")

        # Verify error message with special characters was written
        written_content = "".join(call.args[0] for call in mock_file().write.call_args_list)
        assert "Error with special chars: 'quotes' and \"double quotes\"" in written_content