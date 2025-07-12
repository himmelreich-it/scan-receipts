"""Tests for SequentialProcessingWorkflow."""

import pytest
from unittest.mock import Mock, patch, call
from src.receipt_processing.application.workflows.sequential_processing_workflow import SequentialProcessingWorkflow
from src.receipt_processing.domain.models.file_path import FilePath
from src.receipt_processing.domain.models.file_extension import FileExtension
from src.receipt_processing.domain.models.processable_file import ProcessableFile
from src.receipt_processing.domain.models.file_content import FileContent


class TestSequentialProcessingWorkflow:
    """Test cases for SequentialProcessingWorkflow."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_repository = Mock()
        self.mock_filtering_service = Mock()
        self.mock_content_reader = Mock()
        
        self.workflow = SequentialProcessingWorkflow(
            self.mock_repository,
            self.mock_filtering_service,
            self.mock_content_reader
        )
    
    @patch('builtins.print')
    def test_process_input_directory_creates_directory_if_missing(self, mock_print):
        """Test that workflow creates input directory if it doesn't exist."""
        self.mock_repository.list_files_in_directory.return_value = []
        
        result = self.workflow.process_input_directory("input")
        
        self.mock_repository.ensure_directory_exists.assert_called_once_with("input")
        mock_print.assert_called_with("No files found in input folder")
        assert result.total_processed == 0
    
    @patch('builtins.print')
    @patch('sys.exit')
    def test_process_input_directory_exits_on_permission_error(self, mock_exit, mock_print):
        """Test that workflow exits on permission error."""
        self.mock_repository.ensure_directory_exists.side_effect = PermissionError()
        # Prevent the workflow from continuing after sys.exit mock
        mock_exit.side_effect = SystemExit(1)
        
        with pytest.raises(SystemExit):
            self.workflow.process_input_directory("input")
        
        mock_print.assert_called_with("Permission denied: cannot access input folder")
        mock_exit.assert_called_with(1)
    
    @patch('builtins.print')
    def test_process_input_directory_empty_folder(self, mock_print):
        """Test processing empty input folder."""
        self.mock_repository.list_files_in_directory.return_value = []
        
        result = self.workflow.process_input_directory("input")
        
        mock_print.assert_called_with("No files found in input folder")
        assert result.successful_files == []
        assert result.failed_files == []
        assert result.total_processed == 0
    
    def test_process_input_directory_successful_processing(self):
        """Test successful processing of files."""
        # Setup file paths
        file_paths = [
            FilePath("/input/file1.pdf"),
            FilePath("/input/file2.jpg")
        ]
        
        # Setup processable files
        processable_files = [
            ProcessableFile(file_paths[0], FileExtension(".pdf")),
            ProcessableFile(file_paths[1], FileExtension(".jpg"))
        ]
        
        # Add content to processable files to simulate successful reading
        for pf in processable_files:
            pf.content = FileContent("base64data", "application/pdf", 1024)
        
        self.mock_repository.list_files_in_directory.return_value = file_paths
        self.mock_filtering_service.filter_supported_files.return_value = processable_files
        
        result = self.workflow.process_input_directory("input")
        
        self.mock_content_reader.read_file_content.assert_has_calls([
            call(processable_files[0]),
            call(processable_files[1])
        ])
        
        assert len(result.successful_files) == 2
        assert len(result.failed_files) == 0
        assert result.total_processed == 2
        
        # Verify files are marked as processed
        for pf in processable_files:
            assert pf.processing_status == "processed"
    
    @patch('builtins.print')
    def test_process_input_directory_with_file_errors(self, mock_print):
        """Test processing with file reading errors."""
        file_paths = [FilePath("/input/file1.pdf")]
        processable_file = ProcessableFile(file_paths[0], FileExtension(".pdf"))
        
        # Simulate file reading error - use "Failed to read file" to trigger "File corrupted" message
        def mock_read_content(pf):
            pf.mark_as_error("Failed to read file: file1.pdf")
        
        self.mock_repository.list_files_in_directory.return_value = file_paths
        self.mock_filtering_service.filter_supported_files.return_value = [processable_file]
        self.mock_content_reader.read_file_content.side_effect = mock_read_content
        
        result = self.workflow.process_input_directory("input")
        
        assert len(result.successful_files) == 0
        assert len(result.failed_files) == 1
        assert result.total_processed == 1
        mock_print.assert_called_with("File corrupted: file1.pdf")
    
    @patch('builtins.print')
    @patch('sys.exit')
    def test_process_input_directory_keyboard_interrupt_during_processing(self, mock_exit, mock_print):
        """Test handling of keyboard interrupt during file processing."""
        file_paths = [FilePath("/input/file1.pdf")]
        processable_file = ProcessableFile(file_paths[0], FileExtension(".pdf"))
        
        self.mock_repository.list_files_in_directory.return_value = file_paths
        self.mock_filtering_service.filter_supported_files.return_value = [processable_file]
        self.mock_content_reader.read_file_content.side_effect = KeyboardInterrupt()
        
        self.workflow.process_input_directory("input")
        
        mock_print.assert_called_with("Processing interrupted by user")
        mock_exit.assert_called_with(0)
    
    @patch('builtins.print')
    @patch('sys.exit')
    def test_process_input_directory_keyboard_interrupt_before_processing(self, mock_exit, mock_print):
        """Test handling of keyboard interrupt before processing loop."""
        file_paths = [FilePath("/input/file1.pdf")]
        
        self.mock_repository.list_files_in_directory.return_value = file_paths
        self.mock_filtering_service.filter_supported_files.side_effect = KeyboardInterrupt()
        
        self.workflow.process_input_directory("input")
        
        mock_print.assert_called_with("Processing stopped by user")
        mock_exit.assert_called_with(0)
    
    @patch('builtins.print')
    def test_process_input_directory_unexpected_error_during_processing(self, mock_print):
        """Test handling of unexpected error during processing."""
        file_paths = [FilePath("/input/file1.pdf")]
        processable_file = ProcessableFile(file_paths[0], FileExtension(".pdf"))
        
        self.mock_repository.list_files_in_directory.return_value = file_paths
        self.mock_filtering_service.filter_supported_files.return_value = [processable_file]
        self.mock_content_reader.read_file_content.side_effect = Exception("Unexpected error")
        
        result = self.workflow.process_input_directory("input")
        
        assert len(result.failed_files) == 1
        mock_print.assert_called_with("Processing failed for file1.pdf: Unexpected error")
    
    def test_log_file_error_different_error_types(self):
        """Test different error message logging."""
        file_path = FilePath("/input/test.pdf")
        processable_file = ProcessableFile(file_path, FileExtension(".pdf"))
        
        with patch('builtins.print') as mock_print:
            # Test file no longer accessible
            processable_file.mark_as_error("File no longer accessible: test.pdf")
            self.workflow._log_file_error(processable_file)
            mock_print.assert_called_with("File no longer accessible: test.pdf")
            
            # Test permission denied
            processable_file.mark_as_error("Permission denied: test.pdf")
            self.workflow._log_file_error(processable_file)
            mock_print.assert_called_with("Permission denied: test.pdf")
            
            # Test file too large
            processable_file.mark_as_error("File too large: test.pdf")
            self.workflow._log_file_error(processable_file)
            mock_print.assert_called_with("File too large: test.pdf")
            
            # Test corrupted file
            processable_file.mark_as_error("Failed to read file: test.pdf")
            self.workflow._log_file_error(processable_file)
            mock_print.assert_called_with("File corrupted: test.pdf")
            
            # Test other errors
            processable_file.mark_as_error("Some other error")
            self.workflow._log_file_error(processable_file)
            mock_print.assert_called_with("Invalid file format: test.pdf")
    
    def test_get_processed_files_placeholder(self):
        """Test get_processed_files placeholder implementation."""
        result = self.workflow.get_processed_files()
        assert result == []