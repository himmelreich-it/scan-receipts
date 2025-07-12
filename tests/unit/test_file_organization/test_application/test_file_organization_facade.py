"""Unit tests for FileOrganizationFacade."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from file_organization.application import FileOrganizationFacade
from file_organization.domain.exceptions import FolderCreationError, FileAccessError, FileCopyError
from file_organization.domain.models import ArchiveResult


class TestFileOrganizationFacade:
    """Test FileOrganizationFacade - Integration of all stories."""

    def test_facade_initialization_default_root(self):
        """Test: Facade initializes with default project root"""
        facade = FileOrganizationFacade()
        
        assert facade.project_root == Path.cwd()
        assert facade.folder_manager is not None
        assert facade.file_archiver is not None

    def test_facade_initialization_custom_root(self):
        """Test: Facade initializes with custom project root"""
        custom_root = Path("/custom/path")
        facade = FileOrganizationFacade(custom_root)
        
        assert facade.project_root == custom_root

    def test_initialize_folder_structure_delegates_to_folder_manager(self):
        """Test: initialize_folder_structure delegates to folder manager"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            facade = FileOrganizationFacade(temp_path)
            
            # Mock folder manager
            facade.folder_manager = Mock()
            
            facade.initialize_folder_structure()
            
            facade.folder_manager.ensure_folder_structure.assert_called_once()

    def test_initialize_folder_structure_propagates_errors(self):
        """Test: initialize_folder_structure propagates FolderCreationError"""
        facade = FileOrganizationFacade()
        
        # Mock folder manager to raise error
        facade.folder_manager = Mock()
        facade.folder_manager.ensure_folder_structure.side_effect = FolderCreationError(
            "input", "Permission denied"
        )
        
        with pytest.raises(FolderCreationError):
            facade.initialize_folder_structure()

    def test_archive_processed_file_absolute_path(self):
        """Test: archive_processed_file handles absolute source paths"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            done_folder = temp_path / "done"
            done_folder.mkdir()
            
            # Create source file
            source_file = temp_path / "receipt.jpg"
            source_file.write_text("content")
            
            facade = FileOrganizationFacade(temp_path)
            
            # Mock file archiver
            mock_result = ArchiveResult(
                source_filename="receipt.jpg",
                archived_filename="1-timestamp-receipt.jpg",
                archive_timestamp=Mock(),
                file_id=1
            )
            facade.file_archiver = Mock()
            facade.file_archiver.archive_file.return_value = mock_result
            
            result = facade.archive_processed_file(source_file, 1)
            
            assert result == mock_result
            facade.file_archiver.archive_file.assert_called_once_with(source_file, 1)

    def test_archive_processed_file_relative_path(self):
        """Test: archive_processed_file resolves relative source paths"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            facade = FileOrganizationFacade(temp_path)
            
            # Mock file archiver
            mock_result = ArchiveResult(
                source_filename="receipt.jpg",
                archived_filename="1-timestamp-receipt.jpg",
                archive_timestamp=Mock(),
                file_id=1
            )
            facade.file_archiver = Mock()
            facade.file_archiver.archive_file.return_value = mock_result
            
            relative_path = Path("input/receipt.jpg")
            result = facade.archive_processed_file(relative_path, 1)
            
            # Should resolve relative path against project root
            expected_absolute_path = temp_path / "input/receipt.jpg"
            facade.file_archiver.archive_file.assert_called_once_with(expected_absolute_path, 1)

    def test_archive_processed_file_propagates_file_access_error(self):
        """Test: archive_processed_file propagates FileAccessError from archiver"""
        facade = FileOrganizationFacade()
        
        # Mock file archiver to raise error
        facade.file_archiver = Mock()
        facade.file_archiver.archive_file.side_effect = FileAccessError(
            "/path/to/file", "read", "File not found"
        )
        
        with pytest.raises(FileAccessError):
            facade.archive_processed_file(Path("/path/to/file"), 1)

    def test_archive_processed_file_propagates_file_copy_error(self):
        """Test: archive_processed_file propagates FileCopyError from archiver"""
        facade = FileOrganizationFacade()
        
        # Mock file archiver to raise error
        facade.file_archiver = Mock()
        facade.file_archiver.archive_file.side_effect = FileCopyError(
            "/source", "/target", "Permission denied"
        )
        
        with pytest.raises(FileCopyError):
            facade.archive_processed_file(Path("/source"), 1)

    def test_complete_workflow_integration(self):
        """Test: Complete workflow from folder initialization through file archiving"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create source file in input folder
            input_folder = temp_path / "input"
            input_folder.mkdir()
            source_file = input_folder / "receipt.pdf"
            source_file.write_bytes(b"PDF content")
            
            facade = FileOrganizationFacade(temp_path)
            
            # Step 1: Initialize folder structure
            facade.initialize_folder_structure()
            
            # Verify done folder was created
            done_folder = temp_path / "done"
            assert done_folder.exists()
            
            # Step 2: Archive processed file
            result = facade.archive_processed_file(source_file, 42)
            
            # Verify result
            assert isinstance(result, ArchiveResult)
            assert result.source_filename == "receipt.pdf"
            assert result.file_id == 42
            assert result.archived_filename.startswith("42-")
            assert result.archived_filename.endswith("-receipt.pdf")
            
            # Verify file was copied
            archived_file = done_folder / result.archived_filename
            assert archived_file.exists()
            assert archived_file.read_bytes() == b"PDF content"
            
            # Verify original file still exists (copy, not move)
            assert source_file.exists()

    def test_error_handling_consistency(self):
        """Test: Error handling is consistent across all operations - Story FS_ERROR_HANDLE_H5C6"""
        facade = FileOrganizationFacade()
        
        # Test folder creation error format
        facade.folder_manager = Mock()
        folder_error = FolderCreationError("input", "Permission denied")
        facade.folder_manager.ensure_folder_structure.side_effect = folder_error
        
        with pytest.raises(FolderCreationError) as exc_info:
            facade.initialize_folder_structure()
        
        error_msg = str(exc_info.value)
        assert "Cannot create input folder: Permission denied" in error_msg
        
        # Test file copy error format
        facade.file_archiver = Mock()
        copy_error = FileCopyError("/source.jpg", "/target.jpg", "Permission denied")
        facade.file_archiver.archive_file.side_effect = copy_error
        
        with pytest.raises(FileCopyError) as exc_info:
            facade.archive_processed_file(Path("/source.jpg"), 1)
        
        error_msg = str(exc_info.value)
        assert "Cannot copy file /source.jpg: Permission denied" in error_msg

    def test_facade_maintains_clean_state_on_errors(self):
        """Test: When file system errors occur, ensure no partial state is left"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            facade = FileOrganizationFacade(temp_path)
            
            # Mock archiver to fail after validation but before copy completion
            facade.file_archiver = Mock()
            facade.file_archiver.archive_file.side_effect = FileCopyError(
                "/source", "/target", "Disk full"
            )
            
            source_file = temp_path / "test.jpg"
            source_file.write_text("content")
            
            with pytest.raises(FileCopyError):
                facade.archive_processed_file(source_file, 1)
            
            # Original file should still exist
            assert source_file.exists()
            
            # No partial files should exist in done folder
            done_folder = temp_path / "done"
            if done_folder.exists():
                # If done folder exists, it should be empty
                assert len(list(done_folder.iterdir())) == 0