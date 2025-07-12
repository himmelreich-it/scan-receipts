"""Unit tests for FolderManager service."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock

import pytest

from file_organization.domain.exceptions import FolderCreationError, FileAccessError
from file_organization.infrastructure.services import FolderManager


class TestFolderManager:
    """Test FolderManager service - Story FOLDER_MGMT_F1A2."""

    def test_folder_manager_initialization_default_root(self):
        """Test: FolderManager initializes with default project root"""
        manager = FolderManager()
        
        assert manager.project_root == Path.cwd()
        assert manager.input_folder == Path.cwd() / "input"
        assert manager.done_folder == Path.cwd() / "done"

    def test_folder_manager_initialization_custom_root(self):
        """Test: FolderManager initializes with custom project root"""
        custom_root = Path("/custom/path")
        manager = FolderManager(custom_root)
        
        assert manager.project_root == custom_root
        assert manager.input_folder == custom_root / "input"
        assert manager.done_folder == custom_root / "done"

    def test_ensure_folder_structure_creates_missing_folders(self):
        """Test: When folders are missing, create input/ and done/ folders and continue execution"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manager = FolderManager(temp_path)
            
            # Verify folders don't exist initially
            assert not manager.input_folder.exists()
            assert not manager.done_folder.exists()
            
            # Run ensure_folder_structure
            manager.ensure_folder_structure()
            
            # Verify folders were created
            assert manager.input_folder.exists()
            assert manager.input_folder.is_dir()
            assert manager.done_folder.exists()
            assert manager.done_folder.is_dir()

    def test_ensure_folder_structure_existing_folders(self):
        """Test: When folders exist, proceed without error"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manager = FolderManager(temp_path)
            
            # Create folders manually
            manager.input_folder.mkdir()
            manager.done_folder.mkdir()
            
            # Run ensure_folder_structure - should not raise error
            manager.ensure_folder_structure()
            
            # Verify folders still exist
            assert manager.input_folder.exists()
            assert manager.done_folder.exists()

    @patch('os.makedirs')
    def test_ensure_folder_structure_permission_error_input(self, mock_makedirs):
        """Test: When input/ folder creation fails due to permissions, display error and halt with exit code 1"""
        mock_makedirs.side_effect = PermissionError("Permission denied")
        
        manager = FolderManager(Path("/test"))
        
        with pytest.raises(FolderCreationError) as exc_info:
            manager.ensure_folder_structure()
        
        assert exc_info.value.folder_path == "input"
        assert "Permission denied" in str(exc_info.value)

    @patch('pathlib.Path.mkdir')
    def test_ensure_folder_structure_disk_space_error_input(self, mock_mkdir):
        """Test: When input/ folder creation fails due to disk space, display error and halt with exit code 1"""
        mock_mkdir.side_effect = OSError("No space left on device")
        
        manager = FolderManager(Path("/test"))
        
        with pytest.raises(FolderCreationError) as exc_info:
            manager.ensure_folder_structure()
        
        assert exc_info.value.folder_path == "input"
        assert "Insufficient disk space" in str(exc_info.value)

    @patch('pathlib.Path.mkdir')
    def test_ensure_folder_structure_permission_error_done(self, mock_mkdir):
        """Test: When done/ folder creation fails, display error with specific error and halt with exit code 1"""
        # Test the done folder creation directly
        manager = FolderManager(Path("/test"))
        
        # Test the private method directly for done folder
        mock_mkdir.side_effect = PermissionError("Access denied")
        
        with pytest.raises(FolderCreationError) as exc_info:
            manager._create_folder_if_missing(manager.done_folder, "done")
        
        assert exc_info.value.folder_path == "done"
        assert "Permission denied" in str(exc_info.value)

    def test_validate_folder_permissions_existing_writable(self):
        """Test: validate_folder_permissions succeeds for existing writable folder"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manager = FolderManager()
            
            # Should not raise exception
            manager.validate_folder_permissions(temp_path)

    def test_validate_folder_permissions_nonexistent_folder(self):
        """Test: validate_folder_permissions raises error for non-existent folder"""
        manager = FolderManager()
        nonexistent_path = Path("/nonexistent/folder")
        
        with pytest.raises(FileAccessError) as exc_info:
            manager.validate_folder_permissions(nonexistent_path)
        
        assert "Folder does not exist" in str(exc_info.value)

    @patch('os.access')
    def test_validate_folder_permissions_not_writable(self, mock_access):
        """Test: validate_folder_permissions raises error for non-writable folder"""
        mock_access.return_value = False
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manager = FolderManager()
            
            with pytest.raises(FileAccessError) as exc_info:
                manager.validate_folder_permissions(temp_path)
            
            assert "Permission denied" in str(exc_info.value)

    def test_create_folder_if_missing_creates_folder(self):
        """Test: _create_folder_if_missing creates folder when missing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manager = FolderManager(temp_path)
            test_folder = temp_path / "test_folder"
            
            assert not test_folder.exists()
            
            manager._create_folder_if_missing(test_folder, "test")
            
            assert test_folder.exists()
            assert test_folder.is_dir()

    def test_create_folder_if_missing_existing_folder(self):
        """Test: _create_folder_if_missing does nothing when folder exists"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manager = FolderManager(temp_path)
            test_folder = temp_path / "existing_folder"
            test_folder.mkdir()
            
            # Should not raise error
            manager._create_folder_if_missing(test_folder, "existing")