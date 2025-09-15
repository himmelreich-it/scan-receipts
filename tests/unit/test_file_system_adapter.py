"""Unit tests for FileSystemAdapter."""

from pathlib import Path


from adapters.secondary.file_system_adapter import FileSystemAdapter


class TestFileSystemAdapter:
    """Test FileSystemAdapter functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = FileSystemAdapter()

    def test_get_supported_files_empty_folder(self, tmp_path: Path):
        """Test get_supported_files with empty folder."""
        result = self.adapter.get_supported_files(tmp_path)
        assert result == []

    def test_get_supported_files_nonexistent_folder(self, tmp_path: Path):
        """Test get_supported_files with nonexistent folder."""
        nonexistent = tmp_path / "nonexistent"
        result = self.adapter.get_supported_files(nonexistent)
        assert result == []

    def test_get_supported_files_with_supported_files(self, tmp_path: Path):
        """Test get_supported_files with various file types."""
        # Create test files
        (tmp_path / "receipt1.pdf").touch()
        (tmp_path / "receipt2.jpg").touch()
        (tmp_path / "receipt3.PNG").touch()  # Test case insensitivity
        (tmp_path / "document.txt").touch()  # Not supported
        (tmp_path / "image.gif").touch()  # Not supported

        result = self.adapter.get_supported_files(tmp_path)

        assert len(result) == 3
        assert any(f.name == "receipt1.pdf" for f in result)
        assert any(f.name == "receipt2.jpg" for f in result)
        assert any(f.name == "receipt3.PNG" for f in result)
        # Check files are sorted
        assert result == sorted(result)

    def test_remove_file_if_exists_existing_file(self, tmp_path: Path):
        """Test remove_file_if_exists with existing file."""
        test_file = tmp_path / "test.txt"
        test_file.touch()

        result = self.adapter.remove_file_if_exists(test_file)

        assert result is True
        assert not test_file.exists()

    def test_remove_file_if_exists_nonexistent_file(self, tmp_path: Path):
        """Test remove_file_if_exists with nonexistent file."""
        nonexistent_file = tmp_path / "nonexistent.txt"

        result = self.adapter.remove_file_if_exists(nonexistent_file)

        assert result is False

    def test_clear_folder_with_files(self, tmp_path: Path):
        """Test clear_folder removes all files."""
        # Create test files
        (tmp_path / "file1.txt").touch()
        (tmp_path / "file2.pdf").touch()
        (tmp_path / "file3.jpg").touch()

        # Create subdirectory (should be left alone)
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "nested.txt").touch()

        self.adapter.clear_folder(tmp_path)

        # Files should be removed
        assert not (tmp_path / "file1.txt").exists()
        assert not (tmp_path / "file2.pdf").exists()
        assert not (tmp_path / "file3.jpg").exists()

        # Subdirectory should remain
        assert subdir.exists()
        assert (subdir / "nested.txt").exists()

    def test_clear_folder_nonexistent_folder(self, tmp_path: Path):
        """Test clear_folder with nonexistent folder."""
        nonexistent = tmp_path / "nonexistent"

        # Should not raise exception
        self.adapter.clear_folder(nonexistent)

    def test_clear_folder_empty_folder(self, tmp_path: Path):
        """Test clear_folder with empty folder."""
        # Should not raise exception
        self.adapter.clear_folder(tmp_path)
