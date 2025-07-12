"""Unit tests for file organization domain exceptions."""

import pytest

from file_organization.domain.exceptions import (
    FileOrganizationError,
    FolderCreationError,
    FileCopyError,
    FileAccessError,
)


class TestFileOrganizationError:
    """Test FileOrganizationError base exception."""

    def test_error_with_message_only(self):
        """Test: Error initialized with message only"""
        error = FileOrganizationError("Test error message")
        
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.operation is None

    def test_error_with_message_and_operation(self):
        """Test: Error initialized with message and operation"""
        error = FileOrganizationError("Test error message", "Test Operation")
        
        assert str(error) == "Test Operation: Test error message"
        assert error.message == "Test error message"
        assert error.operation == "Test Operation"


class TestFolderCreationError:
    """Test FolderCreationError exception."""

    def test_folder_creation_error_attributes(self):
        """Test: FolderCreationError sets correct attributes"""
        error = FolderCreationError("input", "Permission denied")
        
        assert error.folder_path == "input"
        assert error.reason == "Permission denied"
        assert error.operation == "Folder Creation"
        assert "Cannot create input folder: Permission denied" in str(error)

    def test_folder_creation_error_inheritance(self):
        """Test: FolderCreationError inherits from FileOrganizationError"""
        error = FolderCreationError("done", "Disk full")
        
        assert isinstance(error, FileOrganizationError)
        assert isinstance(error, Exception)


class TestFileCopyError:
    """Test FileCopyError exception."""

    def test_file_copy_error_attributes(self):
        """Test: FileCopyError sets correct attributes"""
        source = "/input/test.jpg"
        target = "/done/1-timestamp-test.jpg"
        reason = "Permission denied"
        
        error = FileCopyError(source, target, reason)
        
        assert error.source_path == source
        assert error.target_path == target
        assert error.reason == reason
        assert error.operation == "File Copy"
        assert f"Cannot copy file {source}: {reason}" in str(error)

    def test_file_copy_error_inheritance(self):
        """Test: FileCopyError inherits from FileOrganizationError"""
        error = FileCopyError("source", "target", "reason")
        
        assert isinstance(error, FileOrganizationError)
        assert isinstance(error, Exception)


class TestFileAccessError:
    """Test FileAccessError exception."""

    def test_file_access_error_attributes(self):
        """Test: FileAccessError sets correct attributes"""
        file_path = "/input/test.jpg"
        operation = "read"
        reason = "File not found"
        
        error = FileAccessError(file_path, operation, reason)
        
        assert error.file_path == file_path
        assert error.access_operation == operation
        assert error.reason == reason
        assert error.operation == "File Access"
        assert f"Cannot {operation} file {file_path}: {reason}" in str(error)

    def test_file_access_error_inheritance(self):
        """Test: FileAccessError inherits from FileOrganizationError"""
        error = FileAccessError("path", "operation", "reason")
        
        assert isinstance(error, FileOrganizationError)
        assert isinstance(error, Exception)