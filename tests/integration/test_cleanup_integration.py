"""Integration tests for One-Off Processing Mode cleanup feature."""

import os
from unittest.mock import patch

from src.cleanup import CleanupManager


class TestCleanupFeatureIntegration:
    """Integration tests for complete One-Off Processing Mode feature."""
    
    def test_complete_one_off_processing_mode_workflow(self, tmp_path):
        """Test complete One-Off Processing Mode workflow from user perspective.
        
        This test simulates a user running the receipt processing script
        multiple times and verifying that cleanup happens correctly each time.
        
        User Story Integration:
        - DONE_FOLDER_CLEANUP_X1Y2: Done folder cleanup
        - CSV_FILE_REMOVAL_Z3A4: CSV file removal  
        - CLEANUP_ERROR_HANDLE_B5C6: Error handling (success path)
        """
        # Simulate script working directory
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            # Set up initial state - simulate previous script run
            done_dir = tmp_path / "done"
            done_dir.mkdir()
            
            # Create various processed files from previous runs
            (done_dir / "1-20250101-receipt1.jpg").write_text("previous_receipt1")
            (done_dir / "2-20250102-receipt2.pdf").write_text("previous_receipt2")
            
            # Create subdirectory with processed files
            archived_dir = done_dir / "archived"
            archived_dir.mkdir()
            (archived_dir / "old_receipt.png").write_text("old_receipt")
            
            # Create CSV file with previous data
            csv_file = tmp_path / "receipts.csv"
            csv_file.write_text(
                "ID,Amount,Tax,Description,Currency,Date,Confidence,Hash\\n"
                "1,10.50,1.05,Coffee Shop,USD,01-01-2025,95,abc123\\n"
                "2,25.00,2.50,Restaurant,USD,02-01-2025,90,def456\\n"
            )
            
            # Create input folder with new receipts (should NOT be affected)
            input_dir = tmp_path / "input"
            input_dir.mkdir()
            (input_dir / "new_receipt1.jpg").write_text("new_receipt1")
            (input_dir / "new_receipt2.pdf").write_text("new_receipt2")
            
            # Create other files that should NOT be affected
            other_csv = tmp_path / "other_data.csv"
            other_csv.write_text("Name,Value\\nTest,123\\n")
            
            # Verify initial state
            assert done_dir.exists()
            assert len(list(done_dir.iterdir())) == 3  # 2 files + 1 subdirectory
            assert csv_file.exists()
            assert input_dir.exists()
            assert len(list(input_dir.iterdir())) == 2
            assert other_csv.exists()
            
            # FIRST RUN: Execute One-Off Processing Mode cleanup
            cleanup_manager = CleanupManager("done", "receipts.csv")
            cleanup_manager.execute_cleanup()
            
            # Verify cleanup results after first run
            assert done_dir.exists()  # Folder still exists
            assert len(list(done_dir.iterdir())) == 0  # But is empty
            assert not csv_file.exists()  # CSV is removed
            
            # Verify other files are unaffected
            assert input_dir.exists()
            assert len(list(input_dir.iterdir())) == 2
            assert other_csv.exists()
            
            # Simulate processing some receipts (create new processed files)
            (done_dir / "3-20250103-receipt3.jpg").write_text("processed_receipt3")
            csv_file.write_text(
                "ID,Amount,Tax,Description,Currency,Date,Confidence,Hash\\n"
                "3,15.75,1.58,Gas Station,USD,03-01-2025,88,ghi789\\n"
            )
            
            # SECOND RUN: Execute cleanup again (typical user workflow)
            cleanup_manager.execute_cleanup()
            
            # Verify cleanup results after second run
            assert done_dir.exists()
            assert len(list(done_dir.iterdir())) == 0  # Empty again
            assert not csv_file.exists()  # CSV removed again
            
            # Verify input folder still intact
            assert input_dir.exists()
            assert len(list(input_dir.iterdir())) == 2
            assert other_csv.exists()
            
            # THIRD RUN: Execute cleanup when nothing to clean (edge case)
            cleanup_manager.execute_cleanup()
            
            # Should succeed silently
            assert done_dir.exists()
            assert len(list(done_dir.iterdir())) == 0
            assert not csv_file.exists()
            
        finally:
            # Restore original working directory
            os.chdir(original_cwd)
    
    def test_cleanup_with_complex_folder_structure(self, tmp_path):
        """Test cleanup with complex nested folder structure.
        
        Verifies that cleanup handles:
        - Multiple levels of nesting
        - Mixed file types at different levels
        - Empty subdirectories
        """
        # Create complex folder structure
        done_dir = tmp_path / "done"
        done_dir.mkdir()
        
        # Level 1 files
        (done_dir / "receipt1.jpg").write_text("receipt1")
        (done_dir / "receipt2.pdf").write_text("receipt2")
        
        # Level 2 directories and files
        processed_dir = done_dir / "processed"
        processed_dir.mkdir()
        (processed_dir / "old_receipt.png").write_text("old_receipt")
        
        errors_dir = done_dir / "errors"
        errors_dir.mkdir()
        (errors_dir / "corrupted.jpg").write_text("corrupted")
        
        # Level 3 nested structure
        archived_dir = processed_dir / "archived"
        archived_dir.mkdir()
        (archived_dir / "very_old.pdf").write_text("very_old")
        
        # Empty directory
        empty_dir = done_dir / "empty"
        empty_dir.mkdir()
        
        # Verify initial complex structure
        assert len(list(done_dir.rglob("*"))) == 9  # 4 dirs + 5 files
        
        # Execute cleanup
        cleanup_manager = CleanupManager(str(done_dir), "nonexistent.csv")
        cleanup_manager.execute_cleanup()
        
        # Verify all structure is cleaned
        assert done_dir.exists()
        assert len(list(done_dir.iterdir())) == 0
        assert len(list(done_dir.rglob("*"))) == 0
    
    def test_cleanup_error_handling_integration(self, tmp_path):
        """Test error handling in realistic scenario.
        
        Simulates file being locked by another process and verifies
        proper error handling and script termination.
        """
        # Create test files
        done_dir = tmp_path / "done"
        done_dir.mkdir()
        (done_dir / "test_file.txt").write_text("content")
        
        csv_file = tmp_path / "receipts.csv"
        csv_file.write_text("ID,Amount\\n1,10.00\\n")
        
        # Test done folder permission error
        cleanup_manager = CleanupManager(str(done_dir), str(csv_file))
        
        # Mock permission error during folder cleanup
        with patch('src.cleanup.cleaner.Path') as mock_path_class:
            mock_path = mock_path_class.return_value
            mock_path.exists.return_value = True
            mock_path.iterdir.side_effect = PermissionError("Permission denied")
            mock_path.__str__ = lambda self: str(done_dir)
            
            with patch('sys.exit') as mock_exit:
                with patch('builtins.print') as mock_print:
                    cleanup_manager.execute_cleanup()
                    
                    # Verify error message and termination
                    mock_print.assert_called_once_with(
                        f"Error: {done_dir} is currently in use by another process"
                    )
                    mock_exit.assert_called_once_with(1)
    
    def test_cleanup_silent_operation_integration(self, tmp_path, capsys):
        """Test that cleanup operations are completely silent on success.
        
        Verifies acceptance criteria across all user stories:
        - No console output during successful operations
        - Only errors are displayed to user
        """
        # Create test files
        done_dir = tmp_path / "done"
        done_dir.mkdir()
        (done_dir / "file1.txt").write_text("content1")
        (done_dir / "file2.pdf").write_text("content2")
        
        sub_dir = done_dir / "subdir"
        sub_dir.mkdir()
        (sub_dir / "file3.jpg").write_text("content3")
        
        csv_file = tmp_path / "receipts.csv"
        csv_file.write_text("ID,Amount,Tax\\n1,10.00,1.00\\n")
        
        # Execute cleanup
        cleanup_manager = CleanupManager(str(done_dir), str(csv_file))
        cleanup_manager.execute_cleanup()
        
        # Verify no console output
        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""
        
        # Verify cleanup was successful
        assert done_dir.exists()
        assert len(list(done_dir.iterdir())) == 0
        assert not csv_file.exists()
    
    def test_cleanup_preserves_input_folder_integration(self, tmp_path):
        """Test that cleanup never affects input folder.
        
        Verifies implementation requirement:
        - The input folder is never modified by this feature
        """
        # Create input folder with receipts
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        (input_dir / "receipt1.jpg").write_text("new_receipt1")
        (input_dir / "receipt2.pdf").write_text("new_receipt2")
        
        # Create done folder and CSV (to be cleaned)
        done_dir = tmp_path / "done"
        done_dir.mkdir()
        (done_dir / "processed.jpg").write_text("processed")
        
        csv_file = tmp_path / "receipts.csv"
        csv_file.write_text("ID,Amount\\n1,10.00\\n")
        
        # Execute cleanup
        cleanup_manager = CleanupManager(str(done_dir), str(csv_file))
        cleanup_manager.execute_cleanup()
        
        # Verify input folder is completely untouched
        assert input_dir.exists()
        assert len(list(input_dir.iterdir())) == 2
        assert (input_dir / "receipt1.jpg").exists()
        assert (input_dir / "receipt2.pdf").exists()
        
        # Verify content is unchanged
        assert (input_dir / "receipt1.jpg").read_text() == "new_receipt1"
        assert (input_dir / "receipt2.pdf").read_text() == "new_receipt2"
        
        # Verify cleanup happened
        assert done_dir.exists()
        assert len(list(done_dir.iterdir())) == 0
        assert not csv_file.exists()
    
    def test_cleanup_order_integration(self, tmp_path):
        """Test that cleanup operations happen in correct order.
        
        Verifies implementation requirement:
        - Cleanup order: done folder first, then receipts.csv
        """
        # Create test files
        done_dir = tmp_path / "done"
        done_dir.mkdir()
        (done_dir / "test_file.txt").write_text("content")
        
        csv_file = tmp_path / "receipts.csv"
        csv_file.write_text("ID,Amount\\n1,10.00\\n")
        
        # Track call order
        call_order = []
        
        def track_clear_folder(original_method):
            def wrapper(self):
                call_order.append("clear_folder")
                return original_method(self)
            return wrapper
        
        def track_remove_csv(original_method):
            def wrapper(self):
                call_order.append("remove_csv")
                return original_method(self)
            return wrapper
        
        # Patch methods to track call order
        with patch.object(CleanupManager, '_clear_done_folder', 
                         track_clear_folder(CleanupManager._clear_done_folder)):
            with patch.object(CleanupManager, '_remove_csv_file',
                             track_remove_csv(CleanupManager._remove_csv_file)):
                
                cleanup_manager = CleanupManager(str(done_dir), str(csv_file))
                cleanup_manager.execute_cleanup()
                
                # Verify correct order
                assert call_order == ["clear_folder", "remove_csv"]
                
                # Verify cleanup was successful
                assert done_dir.exists()
                assert len(list(done_dir.iterdir())) == 0
                assert not csv_file.exists()