"""Integration tests for file organization system."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from file_organization.application import FileOrganizationFacade
from file_organization.domain.exceptions import FolderCreationError, FileAccessError, FileCopyError


class TestFileOrganizationIntegration:
    """Integration tests for complete file organization system."""

    def test_complete_file_organization_workflow(self):
        """Test: Complete workflow from folder initialization through file archiving"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Initialize facade
            facade = FileOrganizationFacade(temp_path)
            
            # Step 1: Initialize folder structure
            facade.initialize_folder_structure()
            
            # Verify folders were created
            input_folder = temp_path / "input"
            done_folder = temp_path / "done"
            assert input_folder.exists() and input_folder.is_dir()
            assert done_folder.exists() and done_folder.is_dir()
            
            # Step 2: Create test files in input folder
            test_files = [
                ("receipt1.jpg", b"JPEG image data"),
                ("invoice.pdf", b"PDF document content"),
                ("receipt2.png", b"PNG image data"),
            ]
            
            for filename, content in test_files:
                file_path = input_folder / filename
                file_path.write_bytes(content)
            
            # Step 3: Archive each file
            results = []
            for file_id, (filename, content) in enumerate(test_files, 1):
                source_path = input_folder / filename
                result = facade.archive_processed_file(source_path, file_id)
                results.append(result)
                
                # Verify result properties
                assert result.source_filename == filename
                assert result.file_id == file_id
                assert result.archived_filename.startswith(f"{file_id}-")
                assert result.archived_filename.endswith(f"-{filename}")
                
                # Verify file was copied to done folder
                archived_path = done_folder / result.archived_filename
                assert archived_path.exists()
                assert archived_path.read_bytes() == content
                
                # Verify original file still exists (copy, not move)
                assert source_path.exists()
                assert source_path.read_bytes() == content
            
            # Step 4: Verify all files have unique archived names
            archived_filenames = [r.archived_filename for r in results]
            assert len(archived_filenames) == len(set(archived_filenames))  # All unique
            
            # Step 5: Verify CSV integration data
            for result in results:
                done_filename = result.get_done_filename()
                assert "/" not in done_filename  # No path, just filename
                assert done_filename == result.archived_filename

    def test_folder_structure_creation_with_permissions(self):
        """Test: Folder creation with real file system permissions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            facade = FileOrganizationFacade(temp_path)
            
            # Test multiple initializations (should be idempotent)
            facade.initialize_folder_structure()
            facade.initialize_folder_structure()
            facade.initialize_folder_structure()
            
            # Verify folders exist and are writable
            input_folder = temp_path / "input"
            done_folder = temp_path / "done"
            
            assert input_folder.exists()
            assert done_folder.exists()
            
            # Test write permissions by creating test files
            test_input = input_folder / "test_input.txt"
            test_input.write_text("input test")
            assert test_input.exists()
            
            test_done = done_folder / "test_done.txt"
            test_done.write_text("done test")
            assert test_done.exists()

    def test_file_archiving_with_different_file_types(self):
        """Test: File archiving with various file types and sizes"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            facade = FileOrganizationFacade(temp_path)
            
            facade.initialize_folder_structure()
            
            # Test different file types and sizes
            test_cases = [
                ("small.txt", b"small"),
                ("medium.jpg", b"x" * 1024),  # 1KB
                ("large.pdf", b"y" * 10240),  # 10KB
                ("unicode_文件.png", b"unicode filename test"),
                ("spaces in name.doc", b"filename with spaces"),
                ("UPPERCASE.PDF", b"uppercase extension"),
                ("multiple.dots.in.name.jpeg", b"multiple dots"),
            ]
            
            input_folder = temp_path / "input"
            done_folder = temp_path / "done"
            
            for file_id, (filename, content) in enumerate(test_cases, 1):
                # Create source file
                source_path = input_folder / filename
                source_path.write_bytes(content)
                
                # Archive file
                result = facade.archive_processed_file(source_path, file_id)
                
                # Verify archiving
                archived_path = done_folder / result.archived_filename
                assert archived_path.exists()
                assert archived_path.read_bytes() == content
                
                # Verify filename format
                assert result.archived_filename.startswith(f"{file_id}-")
                assert result.archived_filename.endswith(f"-{filename}")

    def test_timestamp_uniqueness_across_rapid_operations(self):
        """Test: Timestamp precision ensures unique filenames even for rapid processing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            facade = FileOrganizationFacade(temp_path)
            
            facade.initialize_folder_structure()
            
            input_folder = temp_path / "input"
            
            # Create multiple files with same name in different subdirectories
            # then archive them rapidly
            results = []
            for i in range(10):
                source_path = input_folder / f"receipt_{i}.jpg"
                source_path.write_bytes(f"content {i}".encode())
                
                result = facade.archive_processed_file(source_path, i + 1)
                results.append(result)
            
            # Verify all archived filenames are unique
            archived_filenames = [r.archived_filename for r in results]
            assert len(archived_filenames) == len(set(archived_filenames))
            
            # Verify timestamp format in all filenames
            for result in results:
                filename_parts = result.archived_filename.split("-")
                assert len(filename_parts) >= 3
                
                # Extract timestamp (spans parts 1 and 2: YYYYMMDD-HHMMSSffffff)
                timestamp_str = filename_parts[1] + "-" + filename_parts[2]
                assert len(timestamp_str) == 21  # YYYYMMDD-HHMMSSffffff format (8+1+12)
                
                # Verify it's a valid timestamp
                parsed_time = datetime.strptime(timestamp_str, "%Y%m%d-%H%M%S%f")
                assert isinstance(parsed_time, datetime)

    def test_error_scenarios_integration(self):
        """Test: Error handling integration across all components"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            facade = FileOrganizationFacade(temp_path)
            
            # Test 1: Archive file before folder initialization
            source_file = temp_path / "test.jpg"
            source_file.write_text("content")
            
            # This should fail because done folder doesn't exist
            with pytest.raises(FileCopyError):
                facade.archive_processed_file(source_file, 1)
            
            # Test 2: Initialize folders then try to archive non-existent file
            facade.initialize_folder_structure()
            
            non_existent = temp_path / "does_not_exist.pdf"
            with pytest.raises(FileAccessError) as exc_info:
                facade.archive_processed_file(non_existent, 1)
            
            assert "File does not exist" in str(exc_info.value)
            
            # Test 3: Try to archive a directory instead of file
            directory_path = temp_path / "input" / "not_a_file"
            directory_path.mkdir()
            
            with pytest.raises(FileAccessError) as exc_info:
                facade.archive_processed_file(directory_path, 1)
            
            assert "Path is not a file" in str(exc_info.value)

    def test_relative_vs_absolute_path_handling(self):
        """Test: Facade correctly handles both relative and absolute paths"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            facade = FileOrganizationFacade(temp_path)
            
            facade.initialize_folder_structure()
            
            input_folder = temp_path / "input"
            
            # Create test file
            source_file = input_folder / "test.jpg"
            source_file.write_text("test content")
            
            # Test 1: Absolute path
            result1 = facade.archive_processed_file(source_file, 1)
            assert result1.source_filename == "test.jpg"
            
            # Test 2: Relative path (relative to project root)
            relative_path = Path("input") / "test.jpg"
            result2 = facade.archive_processed_file(relative_path, 2)
            assert result2.source_filename == "test.jpg"
            
            # Both should succeed and create different archived files
            done_folder = temp_path / "done"
            archived1 = done_folder / result1.archived_filename
            archived2 = done_folder / result2.archived_filename
            
            assert archived1.exists()
            assert archived2.exists()
            assert result1.archived_filename != result2.archived_filename

    def test_concurrent_folder_access_safety(self):
        """Test: Folder operations are safe with multiple facade instances"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create multiple facade instances
            facade1 = FileOrganizationFacade(temp_path)
            facade2 = FileOrganizationFacade(temp_path)
            
            # Both should be able to initialize safely
            facade1.initialize_folder_structure()
            facade2.initialize_folder_structure()
            
            # Both should be able to archive files
            input_folder = temp_path / "input"
            
            file1 = input_folder / "file1.txt"
            file1.write_text("content1")
            
            file2 = input_folder / "file2.txt"
            file2.write_text("content2")
            
            result1 = facade1.archive_processed_file(file1, 1)
            result2 = facade2.archive_processed_file(file2, 2)
            
            # Both operations should succeed
            done_folder = temp_path / "done"
            assert (done_folder / result1.archived_filename).exists()
            assert (done_folder / result2.archived_filename).exists()

    def test_metadata_preservation_integration(self):
        """Test: File metadata is preserved during archiving"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            facade = FileOrganizationFacade(temp_path)
            
            facade.initialize_folder_structure()
            
            input_folder = temp_path / "input"
            source_file = input_folder / "test.pdf"
            
            # Create file with specific content
            original_content = b"PDF content with specific bytes"
            source_file.write_bytes(original_content)
            
            # Get original file stats
            original_size = source_file.stat().st_size
            
            # Archive file
            result = facade.archive_processed_file(source_file, 1)
            
            # Verify archived file
            done_folder = temp_path / "done"
            archived_file = done_folder / result.archived_filename
            
            assert archived_file.exists()
            assert archived_file.read_bytes() == original_content
            assert archived_file.stat().st_size == original_size