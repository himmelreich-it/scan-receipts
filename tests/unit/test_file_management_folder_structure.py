"""Unit tests for FOLDER_MGMT_A8D2: Four-Folder Structure Management and Validation."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from file_management.adapters import FileSystemAdapter
from file_management.models import FileErrorCode


class TestFourFolderStructureManagement:
    """Test folder structure management and validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = FileSystemAdapter()
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_create_missing_folders_automatically(self):
        """Test: When system starts, automatically create missing folders if they don't exist"""
        # Test all four folders
        folder_names = ["incoming", "scanned", "imported", "failed"]
        
        for folder_name in folder_names:
            folder_path = self.temp_dir / folder_name
            assert not folder_path.exists()
            
            result = self.adapter.ensure_folder_exists(folder_path)
            
            assert result.success is True
            assert result.exists is True
            assert result.is_writable is True
            assert folder_path.exists()
            assert folder_path.is_dir()
    
    def test_preserve_existing_folders(self):
        """Test: When folders exist, preserve them and validate writability"""
        folder_path = self.temp_dir / "existing_folder"
        folder_path.mkdir()
        
        # Add a test file to ensure folder isn't modified
        test_file = folder_path / "test.txt"
        test_file.write_text("test content")
        
        result = self.adapter.ensure_folder_exists(folder_path)
        
        assert result.success is True
        assert result.exists is True
        assert result.is_writable is True
        assert test_file.exists()
        assert test_file.read_text() == "test content"
    
    def test_clear_scanned_folder_preserving_others(self):
        """Test: When analysis begins, clear scanned folder completely while preserving other folders"""
        # Create folders with test files
        folders = ["incoming", "scanned", "imported", "failed"]
        test_files = {}
        
        for folder_name in folders:
            folder_path = self.temp_dir / folder_name
            folder_path.mkdir()
            test_file = folder_path / "test.txt"
            test_file.write_text(f"content from {folder_name}")
            test_files[folder_name] = test_file
        
        # Clear only scanned folder
        scanned_folder = self.temp_dir / "scanned"
        result = self.adapter.clear_folder(scanned_folder)
        
        assert result.success is True
        assert not test_files["scanned"].exists()
        
        # Verify other folders are preserved
        for folder_name in ["incoming", "imported", "failed"]:
            assert test_files[folder_name].exists()
            assert test_files[folder_name].read_text() == f"content from {folder_name}"
    
    def test_validate_folder_structure_exists_and_writable(self):
        """Test: When system checks folder structure, validate all four folders exist and are writable"""
        # Create all folders
        folders = ["incoming", "scanned", "imported", "failed"]
        results = []
        
        for folder_name in folders:
            folder_path = self.temp_dir / folder_name
            folder_path.mkdir()
            result = self.adapter.ensure_folder_exists(folder_path)
            results.append(result)
        
        # Verify all validations succeed
        for result in results:
            assert result.success is True
            assert result.exists is True
            assert result.is_writable is True
    
    def test_folder_creation_permission_denied(self):
        """Test: When folder creation fails due to permissions, return error code FOLDER_PERMISSION_DENIED with folder path"""
        folder_path = self.temp_dir / "restricted_folder"
        
        # Mock os operations to simulate permission error
        with patch('pathlib.Path.mkdir', side_effect=PermissionError("Permission denied")):
            result = self.adapter.ensure_folder_exists(folder_path)
            
            assert result.success is False
            assert result.error_code == FileErrorCode.FOLDER_PERMISSION_DENIED
            assert str(folder_path) in result.error_message
            assert result.folder_path == folder_path
    
    def test_folder_not_writable(self):
        """Test: When folder is not writable, return error code FOLDER_NOT_WRITABLE with folder path"""
        folder_path = self.temp_dir / "readonly_folder"
        folder_path.mkdir()
        
        # Mock the write test to simulate non-writable folder
        with patch('pathlib.Path.touch', side_effect=PermissionError("Permission denied")):
            result = self.adapter.ensure_folder_exists(folder_path)
            
            assert result.success is False
            assert result.error_code == FileErrorCode.FOLDER_NOT_WRITABLE
            assert str(folder_path) in result.error_message
            assert result.folder_path == folder_path
    
    def test_incoming_folder_missing_files_continues_without_error(self):
        """Test: When incoming folder is missing files, system continues without error"""
        incoming_folder = self.temp_dir / "incoming"
        incoming_folder.mkdir()
        
        # Ensure folder exists and is empty
        result = self.adapter.ensure_folder_exists(incoming_folder)
        files = self.adapter.list_files(incoming_folder)
        
        assert result.success is True
        assert len(files) == 0  # No files, but no error
    
    def test_imported_folder_preserves_files_permanently(self):
        """Test: When imported folder contains files, preserve all files permanently"""
        imported_folder = self.temp_dir / "imported" 
        imported_folder.mkdir()
        
        # Add test files
        test_files = ["001-20231215-receipt1.pdf", "002-20231216-receipt2.pdf"]
        for filename in test_files:
            (imported_folder / filename).write_text("test content")
        
        # Validate folder (should not affect files)
        result = self.adapter.ensure_folder_exists(imported_folder)
        
        assert result.success is True
        for filename in test_files:
            assert (imported_folder / filename).exists()
    
    def test_failed_folder_preserves_files_permanently(self):
        """Test: When failed folder contains files, preserve all files permanently"""
        failed_folder = self.temp_dir / "failed"
        failed_folder.mkdir()
        
        # Add test files and error logs
        test_files = ["corrupted_receipt.pdf", "corrupted_receipt.pdf.log"]
        for filename in test_files:
            (failed_folder / filename).write_text("test content")
        
        # Validate folder (should not affect files)
        result = self.adapter.ensure_folder_exists(failed_folder)
        
        assert result.success is True
        for filename in test_files:
            assert (failed_folder / filename).exists()
    
    def test_invalid_path_not_directory(self):
        """Test error handling when path exists but is not a directory"""
        file_path = self.temp_dir / "not_a_directory.txt"
        file_path.write_text("test content")
        
        result = self.adapter.ensure_folder_exists(file_path)
        
        assert result.success is False
        assert result.error_code == FileErrorCode.INVALID_PATH
        assert "not a directory" in result.error_message.lower()
        assert result.folder_path == file_path
    
    def test_clear_nonexistent_folder(self):
        """Test clearing a folder that doesn't exist"""
        nonexistent_folder = self.temp_dir / "does_not_exist"
        
        result = self.adapter.clear_folder(nonexistent_folder)
        
        assert result.success is False
        assert result.error_code == FileErrorCode.FILE_NOT_FOUND
        assert result.file_path == nonexistent_folder
    
    def test_clear_folder_with_subdirectories(self):
        """Test clearing folder that contains subdirectories"""
        test_folder = self.temp_dir / "test_folder"
        test_folder.mkdir()
        
        # Create nested structure
        sub_dir = test_folder / "subdir"
        sub_dir.mkdir()
        (sub_dir / "file.txt").write_text("nested content")
        (test_folder / "root_file.txt").write_text("root content")
        
        result = self.adapter.clear_folder(test_folder)
        
        assert result.success is True
        assert len(list(test_folder.iterdir())) == 0
        assert test_folder.exists()  # Folder itself should remain
    
    @patch('os.path.exists')
    def test_disk_space_full_error(self, mock_exists):
        """Test handling of disk space full error"""
        mock_exists.return_value = False
        folder_path = self.temp_dir / "space_test"
        
        # Create OSError with errno 28 (No space left on device)
        disk_full_error = OSError()
        disk_full_error.errno = 28
        
        with patch('pathlib.Path.mkdir', side_effect=disk_full_error):
            result = self.adapter.ensure_folder_exists(folder_path)
            
            assert result.success is False
            assert result.error_code == FileErrorCode.DISK_SPACE_FULL
            assert "disk space" in result.error_message.lower()