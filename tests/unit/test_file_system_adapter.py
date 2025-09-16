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

    def test_calculate_file_hash_existing_file(self, tmp_path: Path):
        """Test calculate_file_hash with existing file."""
        test_file = tmp_path / "test.pdf"
        test_content = b"This is test content for hashing"
        test_file.write_bytes(test_content)

        result = self.adapter.calculate_file_hash(test_file)

        assert result is not None
        assert result.file_path == test_file
        assert isinstance(result.hash_value, str)
        assert len(result.hash_value) == 32  # MD5 hash length

    def test_calculate_file_hash_nonexistent_file(self, tmp_path: Path):
        """Test calculate_file_hash with nonexistent file."""
        nonexistent_file = tmp_path / "nonexistent.pdf"

        result = self.adapter.calculate_file_hash(nonexistent_file)

        assert result is None

    def test_calculate_file_hash_consistent_results(self, tmp_path: Path):
        """Test calculate_file_hash produces consistent results."""
        test_file = tmp_path / "test.pdf"
        test_content = b"This is test content for hashing"
        test_file.write_bytes(test_content)

        result1 = self.adapter.calculate_file_hash(test_file)
        result2 = self.adapter.calculate_file_hash(test_file)

        assert result1 is not None
        assert result2 is not None
        assert result1.hash_value == result2.hash_value

    def test_calculate_file_hash_different_content_different_hash(self, tmp_path: Path):
        """Test calculate_file_hash produces different hashes for different content."""
        file1 = tmp_path / "file1.pdf"
        file2 = tmp_path / "file2.pdf"
        file1.write_bytes(b"Content 1")
        file2.write_bytes(b"Content 2")

        hash1 = self.adapter.calculate_file_hash(file1)
        hash2 = self.adapter.calculate_file_hash(file2)

        assert hash1 is not None
        assert hash2 is not None
        assert hash1.hash_value != hash2.hash_value

    def test_get_file_hashes_from_folder_empty_folder(self, tmp_path: Path):
        """Test get_file_hashes_from_folder with empty folder."""
        result = self.adapter.get_file_hashes_from_folder(tmp_path)
        assert result == []

    def test_get_file_hashes_from_folder_nonexistent_folder(self, tmp_path: Path):
        """Test get_file_hashes_from_folder with nonexistent folder."""
        nonexistent = tmp_path / "nonexistent"
        result = self.adapter.get_file_hashes_from_folder(nonexistent)
        assert result == []

    def test_get_file_hashes_from_folder_with_supported_files(self, tmp_path: Path):
        """Test get_file_hashes_from_folder with supported files."""
        # Create supported files
        (tmp_path / "receipt1.pdf").write_bytes(b"PDF content 1")
        (tmp_path / "receipt2.jpg").write_bytes(b"JPG content 2")
        (tmp_path / "receipt3.png").write_bytes(b"PNG content 3")
        # Create unsupported file
        (tmp_path / "document.txt").write_bytes(b"Text content")

        result = self.adapter.get_file_hashes_from_folder(tmp_path)

        assert len(result) == 3
        hash_values = [fh.hash_value for fh in result]
        assert len(set(hash_values)) == 3  # All hashes should be different

        # Check that all results have valid file paths
        file_names = [fh.file_path.name for fh in result]
        assert "receipt1.pdf" in file_names
        assert "receipt2.jpg" in file_names
        assert "receipt3.png" in file_names
        assert "document.txt" not in file_names
