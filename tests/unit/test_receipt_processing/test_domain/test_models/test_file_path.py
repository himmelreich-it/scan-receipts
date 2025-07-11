"""Tests for FilePath value object."""

import pytest
from unittest.mock import patch
from src.receipt_processing.domain.models.file_path import FilePath


class TestFilePath:
    """Test cases for FilePath value object."""
    
    def test_creation_with_valid_path(self):
        """Test creating FilePath with valid path."""
        file_path = FilePath("/path/to/file.pdf")
        assert file_path.path == "/path/to/file.pdf"
    
    def test_creation_with_empty_path_raises_error(self):
        """Test creating FilePath with empty path raises ValueError."""
        with pytest.raises(ValueError, match="File path cannot be empty"):
            FilePath("")
    
    def test_creation_with_non_string_raises_error(self):
        """Test creating FilePath with non-string raises TypeError."""
        with pytest.raises(TypeError, match="File path must be a string"):
            FilePath(123)
    
    def test_name_property(self):
        """Test name property returns filename."""
        file_path = FilePath("/path/to/file.pdf")
        assert file_path.name == "file.pdf"
    
    def test_directory_property(self):
        """Test directory property returns directory path."""
        file_path = FilePath("/path/to/file.pdf")
        assert file_path.directory == "/path/to"
    
    @patch('os.path.exists')
    def test_exists_returns_true_when_file_exists(self, mock_exists):
        """Test exists method returns True when file exists."""
        mock_exists.return_value = True
        file_path = FilePath("/path/to/file.pdf")
        assert file_path.exists() is True
        mock_exists.assert_called_once_with("/path/to/file.pdf")
    
    @patch('os.path.exists')
    def test_exists_returns_false_when_file_does_not_exist(self, mock_exists):
        """Test exists method returns False when file does not exist."""
        mock_exists.return_value = False
        file_path = FilePath("/path/to/file.pdf")
        assert file_path.exists() is False
        mock_exists.assert_called_once_with("/path/to/file.pdf")
    
    def test_immutability(self):
        """Test FilePath is immutable."""
        file_path = FilePath("/path/to/file.pdf")
        with pytest.raises(AttributeError):
            file_path.path = "/new/path"