"""Unit tests for CleanupManager class."""

import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

from src.cleanup.cleaner import CleanupManager


class TestCleanupManager:
    """Test suite for CleanupManager class."""
    
    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.done_folder_path = "test_done"
        self.csv_file_path = "test_receipts.csv"
        self.cleanup_manager = CleanupManager(self.done_folder_path, self.csv_file_path)
    
    # Happy Path Tests - Story 1 & 2
    
    def test_execute_cleanup_success_both_exist(self, tmp_path):
        """Test successful cleanup when both folder and file exist.
        
        Tests acceptance criteria:
        - Story 1: Clears all files and subdirectories from done folder
        - Story 2: Removes receipts.csv file
        - Both operations are silent (no console output)
        """
        # Create test files and directories
        done_dir = tmp_path / "done"
        done_dir.mkdir()
        
        # Create sample files in done folder
        (done_dir / "file1.txt").write_text("content1")
        (done_dir / "file2.pdf").write_text("content2")
        
        # Create subdirectory with file
        sub_dir = done_dir / "subdir"
        sub_dir.mkdir()
        (sub_dir / "file3.jpg").write_text("content3")
        
        # Create CSV file
        csv_file = tmp_path / "receipts.csv"
        csv_file.write_text("ID,Amount,Tax,Description\\n1,10.00,1.00,Test\\n")
        
        # Initialize cleanup manager with test paths
        cleanup_manager = CleanupManager(str(done_dir), str(csv_file))
        
        # Execute cleanup
        cleanup_manager.execute_cleanup()
        
        # Verify done folder is empty but still exists
        assert done_dir.exists()
        assert len(list(done_dir.iterdir())) == 0
        
        # Verify CSV file is removed
        assert not csv_file.exists()
    
    def test_execute_cleanup_success_neither_exist(self, tmp_path):
        """Test successful cleanup when neither folder nor file exist.
        
        Tests acceptance criteria:
        - Story 1: Silent success if folder doesn't exist
        - Story 2: Silent success if file doesn't exist
        """
        # Use paths that don't exist
        done_dir = tmp_path / "nonexistent_done"
        csv_file = tmp_path / "nonexistent.csv"
        
        cleanup_manager = CleanupManager(str(done_dir), str(csv_file))
        
        # Should not raise any exceptions
        cleanup_manager.execute_cleanup()
        
        # Verify paths still don't exist
        assert not done_dir.exists()
        assert not csv_file.exists()
    
    def test_execute_cleanup_success_only_folder_exists(self, tmp_path):
        """Test successful cleanup when only done folder exists.
        
        Tests acceptance criteria:
        - Story 1: Clears files from existing folder
        - Story 2: Silent success when CSV doesn't exist
        """
        done_dir = tmp_path / "done"
        done_dir.mkdir()
        (done_dir / "test_file.txt").write_text("content")
        
        csv_file = tmp_path / "nonexistent.csv"
        
        cleanup_manager = CleanupManager(str(done_dir), str(csv_file))
        cleanup_manager.execute_cleanup()
        
        # Verify folder is cleared
        assert done_dir.exists()
        assert len(list(done_dir.iterdir())) == 0
        
        # Verify CSV still doesn't exist
        assert not csv_file.exists()
    
    def test_execute_cleanup_success_only_csv_exists(self, tmp_path):
        """Test successful cleanup when only CSV file exists.
        
        Tests acceptance criteria:
        - Story 1: Silent success when folder doesn't exist
        - Story 2: Removes existing CSV file
        """
        done_dir = tmp_path / "nonexistent_done"
        csv_file = tmp_path / "receipts.csv"
        csv_file.write_text("ID,Amount\\n1,10.00\\n")
        
        cleanup_manager = CleanupManager(str(done_dir), str(csv_file))
        cleanup_manager.execute_cleanup()
        
        # Verify folder still doesn't exist
        assert not done_dir.exists()
        
        # Verify CSV is removed
        assert not csv_file.exists()
    
    def test_clear_done_folder_removes_all_file_types(self, tmp_path):
        """Test that all file types are removed from done folder.
        
        Tests acceptance criteria:
        - Story 1: All file types are removed (images, PDFs, etc.)
        """
        done_dir = tmp_path / "done"
        done_dir.mkdir()
        
        # Create various file types
        (done_dir / "image.jpg").write_text("jpg_content")
        (done_dir / "document.pdf").write_text("pdf_content")
        (done_dir / "text.txt").write_text("txt_content")
        (done_dir / "data.csv").write_text("csv_content")
        
        cleanup_manager = CleanupManager(str(done_dir), "nonexistent.csv")
        cleanup_manager._clear_done_folder()
        
        # Verify all files are removed
        assert done_dir.exists()
        assert len(list(done_dir.iterdir())) == 0
    
    def test_clear_done_folder_removes_subdirectories(self, tmp_path):
        """Test that subdirectories within done folder are removed.
        
        Tests acceptance criteria:
        - Story 1: Subdirectories within done folder are also removed
        """
        done_dir = tmp_path / "done"
        done_dir.mkdir()
        
        # Create nested directory structure
        sub1 = done_dir / "subdir1"
        sub1.mkdir()
        (sub1 / "file1.txt").write_text("content1")
        
        sub2 = done_dir / "subdir2"
        sub2.mkdir()
        sub2_nested = sub2 / "nested"
        sub2_nested.mkdir()
        (sub2_nested / "file2.txt").write_text("content2")
        
        cleanup_manager = CleanupManager(str(done_dir), "nonexistent.csv")
        cleanup_manager._clear_done_folder()
        
        # Verify all subdirectories are removed
        assert done_dir.exists()
        assert len(list(done_dir.iterdir())) == 0
    
    def test_remove_csv_file_only_removes_specified_file(self, tmp_path):
        """Test that only receipts.csv is removed, not other CSV files.
        
        Tests acceptance criteria:
        - Story 2: Only removes receipts.csv, not other CSV files
        """
        csv_file = tmp_path / "receipts.csv"
        csv_file.write_text("ID,Amount\\n1,10.00\\n")
        
        other_csv = tmp_path / "other_data.csv"
        other_csv.write_text("Name,Value\\nTest,123\\n")
        
        cleanup_manager = CleanupManager("nonexistent", str(csv_file))
        cleanup_manager._remove_csv_file()
        
        # Verify only receipts.csv is removed
        assert not csv_file.exists()
        assert other_csv.exists()
    
    # Error Handling Tests - Story 3
    
    def test_cleanup_folder_permission_error(self, tmp_path, monkeypatch):
        """Test cleanup failure when done folder files are in use.
        
        Tests acceptance criteria:
        - Story 3: Detects when files in done folder are in use
        - Story 3: Displays clear error message
        - Story 3: Terminates script execution immediately
        """
        done_dir = tmp_path / "done"
        done_dir.mkdir()
        (done_dir / "locked_file.txt").write_text("content")
        
        # Mock Path.iterdir to raise PermissionError
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.iterdir.side_effect = PermissionError("Permission denied")
        mock_path.__str__ = Mock(return_value=str(done_dir))
        
        with patch('src.cleanup.cleaner.Path') as mock_path_class:
            mock_path_class.return_value = mock_path
            
            with patch('sys.exit') as mock_exit:
                with patch('builtins.print') as mock_print:
                    cleanup_manager = CleanupManager(str(done_dir), "test.csv")
                    cleanup_manager._clear_done_folder()
                    
                    # Verify error message is displayed
                    mock_print.assert_called_once_with(
                        f"Error: {done_dir} is currently in use by another process"
                    )
                    
                    # Verify script terminates
                    mock_exit.assert_called_once_with(1)
    
    def test_cleanup_csv_permission_error(self, tmp_path, monkeypatch):
        """Test cleanup failure when CSV file is in use.
        
        Tests acceptance criteria:
        - Story 3: Detects when receipts.csv is in use
        - Story 3: Displays clear error message
        - Story 3: Terminates script execution immediately
        """
        csv_file = tmp_path / "receipts.csv"
        csv_file.write_text("ID,Amount\\n1,10.00\\n")
        
        # Mock Path.unlink to raise PermissionError
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.unlink.side_effect = PermissionError("Permission denied")
        mock_path.__str__ = Mock(return_value=str(csv_file))
        
        with patch('src.cleanup.cleaner.Path') as mock_path_class:
            mock_path_class.return_value = mock_path
            
            with patch('sys.exit') as mock_exit:
                with patch('builtins.print') as mock_print:
                    cleanup_manager = CleanupManager("nonexistent", str(csv_file))
                    cleanup_manager._remove_csv_file()
                    
                    # Verify error message is displayed
                    mock_print.assert_called_once_with(
                        f"Error: {csv_file} is currently in use by another process"
                    )
                    
                    # Verify script terminates
                    mock_exit.assert_called_once_with(1)
    
    def test_cleanup_error_message_format(self, tmp_path):
        """Test error message format matches requirements.
        
        Tests acceptance criteria:
        - Story 3: Error message format: "Error: [filename] is currently in use by another process"
        """
        test_path = "/test/path/file.txt"
        test_error = "Some error message"
        
        with patch('sys.exit') as mock_exit:
            with patch('builtins.print') as mock_print:
                cleanup_manager = CleanupManager("done", "receipts.csv")
                cleanup_manager._handle_cleanup_error(test_path, test_error)
                
                # Verify exact error message format
                expected_message = f"Error: {test_path} is currently in use by another process"
                mock_print.assert_called_once_with(expected_message)
                
                # Verify script terminates with exit code 1
                mock_exit.assert_called_once_with(1)
    
    def test_cleanup_terminates_on_error(self):
        """Test that cleanup terminates script on error.
        
        Tests acceptance criteria:
        - Story 3: Terminates script execution immediately when cleanup fails
        - Story 3: Does not proceed with processing if cleanup fails
        """
        with patch('sys.exit') as mock_exit:
            with patch('builtins.print'):
                cleanup_manager = CleanupManager("done", "receipts.csv")
                cleanup_manager._handle_cleanup_error("test_file", "test_error")
                
                # Verify sys.exit is called with code 1
                mock_exit.assert_called_once_with(1)
    
    def test_execute_cleanup_error_order(self, tmp_path):
        """Test that cleanup operations happen in correct order.
        
        Tests implementation requirement:
        - Cleanup order: done folder first, then receipts.csv
        - If done folder cleanup fails, CSV cleanup should not occur
        """
        done_dir = tmp_path / "done"
        done_dir.mkdir()
        csv_file = tmp_path / "receipts.csv"
        csv_file.write_text("content")
        
        # Mock done folder cleanup to fail
        with patch.object(CleanupManager, '_clear_done_folder') as mock_clear:
            mock_clear.side_effect = SystemExit(1)
            
            with patch.object(CleanupManager, '_remove_csv_file') as mock_remove:
                cleanup_manager = CleanupManager(str(done_dir), str(csv_file))
                
                with pytest.raises(SystemExit):
                    cleanup_manager.execute_cleanup()
                
                # Verify done folder cleanup was called
                mock_clear.assert_called_once()
                
                # Verify CSV cleanup was NOT called (due to early termination)
                mock_remove.assert_not_called()


class TestCleanupManagerIntegration:
    """Integration tests for complete cleanup workflow."""
    
    def test_complete_cleanup_workflow(self, tmp_path):
        """Test complete cleanup workflow across all user stories.
        
        Tests integration of:
        - Story 1: Done Folder Cleanup
        - Story 2: CSV File Removal
        - Story 3: Error Handling (success path)
        """
        # Set up complex test scenario
        done_dir = tmp_path / "done"
        done_dir.mkdir()
        
        # Create various files and directories
        (done_dir / "receipt1.jpg").write_text("image_content")
        (done_dir / "receipt2.pdf").write_text("pdf_content")
        
        # Create nested directory structure
        sub_dir = done_dir / "processed"
        sub_dir.mkdir()
        (sub_dir / "old_receipt.png").write_text("old_content")
        
        # Create CSV file with data
        csv_file = tmp_path / "receipts.csv"
        csv_file.write_text("ID,Amount,Tax,Description\\n1,10.00,1.00,Test Receipt\\n")
        
        # Create other files that should NOT be affected
        other_file = tmp_path / "other_data.csv"
        other_file.write_text("Name,Value\\nTest,123\\n")
        
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        (input_dir / "new_receipt.jpg").write_text("new_receipt_content")
        
        # Execute complete cleanup
        cleanup_manager = CleanupManager(str(done_dir), str(csv_file))
        cleanup_manager.execute_cleanup()
        
        # Verify all acceptance criteria are met:
        
        # Story 1: Done folder cleanup
        assert done_dir.exists()  # Folder itself should still exist
        assert len(list(done_dir.iterdir())) == 0  # But be empty
        
        # Story 2: CSV file removal
        assert not csv_file.exists()  # CSV file should be removed
        
        # Story 3: Error handling (success path - no errors)
        # No exceptions should be raised
        
        # Verify other files are NOT affected
        assert other_file.exists()
        assert input_dir.exists()
        assert (input_dir / "new_receipt.jpg").exists()
    
    def test_cleanup_silent_operation(self, tmp_path, capsys):
        """Test that cleanup operations are silent on success.
        
        Tests acceptance criteria:
        - Story 1: Operation is silent - no console output
        - Story 2: Operation is silent - no console output
        """
        # Set up test files
        done_dir = tmp_path / "done"
        done_dir.mkdir()
        (done_dir / "test_file.txt").write_text("content")
        
        csv_file = tmp_path / "receipts.csv"
        csv_file.write_text("ID,Amount\\n1,10.00\\n")
        
        # Execute cleanup
        cleanup_manager = CleanupManager(str(done_dir), str(csv_file))
        cleanup_manager.execute_cleanup()
        
        # Verify no console output
        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""