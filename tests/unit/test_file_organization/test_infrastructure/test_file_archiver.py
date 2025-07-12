"""Unit tests for FileArchiver service."""

import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, Mock

import pytest

from file_organization.domain.exceptions import FileAccessError, FileCopyError
from file_organization.domain.models import ArchiveResult
from file_organization.infrastructure.services import FileArchiver


class TestFileArchiver:
    """Test FileArchiver service - Story FILE_ARCHIVE_G3B4."""

    def test_file_archiver_initialization_default_folder(self):
        """Test: FileArchiver initializes with default done folder"""
        archiver = FileArchiver()
        
        # Should use default from config
        assert archiver.done_folder.name == "done"

    def test_file_archiver_initialization_custom_folder(self):
        """Test: FileArchiver initializes with custom done folder"""
        custom_done = Path("/custom/done")
        archiver = FileArchiver(custom_done)
        
        assert archiver.done_folder == custom_done

    def test_archive_file_successful_copy(self):
        """Test: When a receipt file is successfully processed, copy file from input/ to done/ folder"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            done_folder = temp_path / "done"
            done_folder.mkdir()
            
            # Create source file
            source_file = temp_path / "receipt.jpg"
            source_file.write_text("test receipt content")
            
            archiver = FileArchiver(done_folder)
            
            result = archiver.archive_file(source_file, 1)
            
            # Verify result object
            assert isinstance(result, ArchiveResult)
            assert result.source_filename == "receipt.jpg"
            assert result.file_id == 1
            assert result.archived_filename.startswith("1-")
            assert result.archived_filename.endswith("-receipt.jpg")
            
            # Verify file was copied
            archived_file = done_folder / result.archived_filename
            assert archived_file.exists()
            assert archived_file.read_text() == "test receipt content"

    def test_archive_file_generates_correct_filename_format(self):
        """Test: When copying file, generate new filename using format: {ID}-{timestamp}-{original-filename}"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            done_folder = temp_path / "done"
            done_folder.mkdir()
            
            source_file = temp_path / "test-receipt.pdf"
            source_file.write_bytes(b"pdf content")
            
            archiver = FileArchiver(done_folder)
            
            # Mock datetime to get predictable timestamp
            fixed_time = datetime(2024, 3, 15, 14, 30, 52, 123456)
            with patch('file_organization.infrastructure.services.file_archiver.datetime') as mock_datetime:
                mock_datetime.now.return_value = fixed_time
                
                result = archiver.archive_file(source_file, 42)
                
                expected_filename = "42-20240315-143052123456-test-receipt.pdf"
                assert result.archived_filename == expected_filename

    def test_archive_file_timestamp_format(self):
        """Test: When generating timestamp, use format %Y%m%d-%H%M%S%f"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            done_folder = temp_path / "done"
            done_folder.mkdir()
            
            source_file = temp_path / "receipt.jpg"
            source_file.write_text("content")
            
            archiver = FileArchiver(done_folder)
            
            result = archiver.archive_file(source_file, 1)
            
            # Extract timestamp from filename: 1-TIMESTAMP-receipt.jpg
            filename_parts = result.archived_filename.split("-")
            # Timestamp spans parts 1 and 2: YYYYMMDD-HHMMSSffffff
            timestamp_str = filename_parts[1] + "-" + filename_parts[2]
            
            # Verify timestamp format (20240315-143052123456)
            assert len(timestamp_str) == 21  # YYYYMMDD-HHMMSSffffff (8+1+12)
            assert timestamp_str[8] == "-"  # Separator between date and time
            
            # Verify it can be parsed back
            parsed_time = datetime.strptime(timestamp_str, "%Y%m%d-%H%M%S%f")
            assert isinstance(parsed_time, datetime)

    def test_archive_file_records_done_filename(self):
        """Test: When file copy operation completes, record new filename (without path) in CSV DoneFilename field"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            done_folder = temp_path / "done"
            done_folder.mkdir()
            
            source_file = temp_path / "invoice.png"
            source_file.write_bytes(b"image data")
            
            archiver = FileArchiver(done_folder)
            
            result = archiver.archive_file(source_file, 5)
            
            # get_done_filename should return just the filename, no path
            done_filename = result.get_done_filename()
            assert "/" not in done_filename  # No path separators
            assert done_filename == result.archived_filename
            assert done_filename.startswith("5-")
            assert done_filename.endswith("-invoice.png")

    def test_archive_file_permission_error(self):
        """Test: When copy operation fails due to permissions, display error and halt with exit code 1"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            done_folder = temp_path / "done"
            done_folder.mkdir()
            
            source_file = temp_path / "receipt.jpg"
            source_file.write_text("content")
            
            archiver = FileArchiver(done_folder)
            
            # Mock shutil.copy2 to raise PermissionError
            with patch('shutil.copy2') as mock_copy:
                mock_copy.side_effect = PermissionError("Access denied")
                
                with pytest.raises(FileCopyError) as exc_info:
                    archiver.archive_file(source_file, 1)
                
                assert "Permission denied" in str(exc_info.value)
                assert str(source_file) in str(exc_info.value)

    def test_archive_file_disk_space_error(self):
        """Test: When copy operation fails due to disk space, display error and halt with exit code 1"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            done_folder = temp_path / "done"
            done_folder.mkdir()
            
            source_file = temp_path / "receipt.jpg"
            source_file.write_text("content")
            
            archiver = FileArchiver(done_folder)
            
            # Mock shutil.copy2 to raise disk space error
            with patch('shutil.copy2') as mock_copy:
                mock_copy.side_effect = OSError("No space left on device")
                
                with pytest.raises(FileCopyError) as exc_info:
                    archiver.archive_file(source_file, 1)
                
                assert "Insufficient disk space" in str(exc_info.value)

    def test_archive_file_source_not_accessible(self):
        """Test: When original file becomes inaccessible during copy, display error and halt with exit code 1"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            done_folder = temp_path / "done"
            done_folder.mkdir()
            
            # Use non-existent source file
            source_file = temp_path / "nonexistent.jpg"
            
            archiver = FileArchiver(done_folder)
            
            with pytest.raises(FileAccessError) as exc_info:
                archiver.archive_file(source_file, 1)
            
            assert "read source" in str(exc_info.value)
            assert "File does not exist" in str(exc_info.value)

    def test_generate_archive_filename(self):
        """Test: _generate_archive_filename creates correct format"""
        archiver = FileArchiver()
        timestamp = datetime(2024, 3, 15, 14, 30, 52, 123456)
        
        filename = archiver._generate_archive_filename("receipt.jpg", 1, timestamp)
        
        assert filename == "1-20240315-143052123456-receipt.jpg"

    def test_generate_archive_filename_different_extensions(self):
        """Test: _generate_archive_filename works with different file extensions"""
        archiver = FileArchiver()
        timestamp = datetime(2024, 1, 1, 0, 0, 0, 0)
        
        # Test PDF
        pdf_filename = archiver._generate_archive_filename("invoice.pdf", 10, timestamp)
        assert pdf_filename == "10-20240101-000000000000-invoice.pdf"
        
        # Test PNG
        png_filename = archiver._generate_archive_filename("receipt.png", 5, timestamp)
        assert png_filename == "5-20240101-000000000000-receipt.png"

    def test_validate_source_file_exists_and_readable(self):
        """Test: _validate_source_file succeeds for existing readable file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source_file = temp_path / "test.txt"
            source_file.write_text("test content")
            
            archiver = FileArchiver()
            
            # Should not raise exception
            archiver._validate_source_file(source_file)

    def test_validate_source_file_not_exists(self):
        """Test: _validate_source_file raises error for non-existent file"""
        archiver = FileArchiver()
        nonexistent_file = Path("/nonexistent/file.txt")
        
        with pytest.raises(FileAccessError) as exc_info:
            archiver._validate_source_file(nonexistent_file)
        
        assert "File does not exist" in str(exc_info.value)

    def test_validate_source_file_is_directory(self):
        """Test: _validate_source_file raises error if path is directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            archiver = FileArchiver()
            
            with pytest.raises(FileAccessError) as exc_info:
                archiver._validate_source_file(temp_path)
            
            assert "Path is not a file" in str(exc_info.value)

    def test_perform_copy_operation_successful(self):
        """Test: _perform_copy_operation successfully copies file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            source_file = temp_path / "source.txt"
            source_file.write_text("test content")
            
            target_file = temp_path / "target.txt"
            
            archiver = FileArchiver()
            archiver._perform_copy_operation(source_file, target_file)
            
            assert target_file.exists()
            assert target_file.read_text() == "test content"

    @patch('shutil.copy2')
    def test_perform_copy_operation_copy_fails_but_no_target(self, mock_copy):
        """Test: _perform_copy_operation handles case where copy completes but target doesn't exist"""
        mock_copy.return_value = None  # copy2 completed
        
        archiver = FileArchiver()
        source_file = Path("/source.txt")
        target_file = Path("/nonexistent/target.txt")
        
        with pytest.raises(FileCopyError) as exc_info:
            archiver._perform_copy_operation(source_file, target_file)
        
        assert "Copy operation completed but target file does not exist" in str(exc_info.value)