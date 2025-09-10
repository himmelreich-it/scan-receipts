"""Unit tests for FILE_MOVEMENT_B9E3: File Movement and Naming Convention Pipeline."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from file_management.adapters import FileSystemAdapter
from file_management.models import FileErrorCode, FileMovementRequest


class TestFileMovement:
    """Test file movement operations with naming conventions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = FileSystemAdapter()
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create test folders
        self.incoming_folder = self.temp_dir / "incoming"
        self.scanned_folder = self.temp_dir / "scanned"
        self.imported_folder = self.temp_dir / "imported"
        self.failed_folder = self.temp_dir / "failed"
        
        for folder in [self.incoming_folder, self.scanned_folder, 
                      self.imported_folder, self.failed_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_move_file_from_incoming_to_scanned_copy_file_and_apply_naming(self):
        """Test: When moving file from incoming to scanned, copy file (preserve original) and apply naming "{yyyyMMdd}-{description}.{ext}" """
        # Create test file in incoming
        source_file = self.incoming_folder / "receipt.pdf"
        source_file.write_text("test receipt content")
        
        # Create movement request
        request = FileMovementRequest(
            source_path=source_file,
            target_folder=self.scanned_folder,
            description="grocery store receipt",
            date="20240315"
        )
        
        # Execute movement
        result = self.adapter.move_to_scanned(request)
        
        # Verify success
        assert result.success is True
        assert result.source_path == source_file
        
        # Verify original file still exists (copy operation)
        assert source_file.exists()
        
        # Verify target file created with correct naming (15 char limit)
        expected_target = self.scanned_folder / "20240315-grocery_store_r.pdf"
        assert result.target_path == expected_target
        assert expected_target.exists()
        assert expected_target.read_text() == "test receipt content"
    
    def test_move_file_from_scanned_to_imported_move_file_and_apply_numbered_naming(self):
        """Test: When moving file from scanned to imported, move file (remove from source) and apply naming "{number}-{yyyyMMdd}-{description}.{ext}" """
        # Create test file in scanned
        source_file = self.scanned_folder / "20240315-grocery.pdf"
        source_file.write_text("test receipt content")
        
        # Create movement request with sequence number
        request = FileMovementRequest(
            source_path=source_file,
            target_folder=self.imported_folder,
            description="grocery store receipt",
            date="20240315",
            sequence_number=42
        )
        
        # Execute movement
        result = self.adapter.move_to_imported(request)
        
        # Verify success
        assert result.success is True
        assert result.source_path == source_file
        
        # Verify source file no longer exists (move operation)
        assert not source_file.exists()
        
        # Verify target file created with correct naming (15 char limit)
        expected_target = self.imported_folder / "42-20240315-grocery_store_r.pdf"
        assert result.target_path == expected_target
        assert expected_target.exists()
        assert expected_target.read_text() == "test receipt content"
    
    def test_move_file_to_failed_folder_copy_with_original_filename(self):
        """Test: When moving file to failed folder, copy file (preserve original) with original filename"""
        # Create test file in incoming
        source_file = self.incoming_folder / "problematic_receipt.jpg"
        source_file.write_text("corrupted image data")
        
        # Create movement request
        request = FileMovementRequest(
            source_path=source_file,
            target_folder=self.failed_folder,
            description="error occurred",
            date="20240315"
        )
        
        # Execute copy to failed
        result = self.adapter.copy_to_failed(request)
        
        # Verify success
        assert result.success is True
        assert result.source_path == source_file
        
        # Verify original file still exists (copy operation)
        assert source_file.exists()
        
        # Verify target file created with original filename
        expected_target = self.failed_folder / "problematic_receipt.jpg"
        assert result.target_path == expected_target
        assert expected_target.exists()
        assert expected_target.read_text() == "corrupted image data"
    
    def test_file_move_copy_fails_due_to_file_lock_return_error_code_file_locked(self):
        """Test: When file move/copy fails due to file lock, return error code FILE_LOCKED with filename"""
        source_file = self.incoming_folder / "locked_file.pdf"
        source_file.write_text("test content")
        
        # Mock file operations to simulate file lock
        with patch.object(self.adapter, 'copy_file') as mock_copy:
            mock_copy.return_value = MagicMock()
            mock_copy.return_value.success = False
            mock_copy.return_value.error_code = FileErrorCode.FILE_LOCKED
            mock_copy.return_value.error_message = "File is locked: locked_file.pdf"
            
            request = FileMovementRequest(
                source_path=source_file,
                target_folder=self.scanned_folder,
                description="test",
                date="20240315"
            )
            
            result = self.adapter.move_to_scanned(request)
            
            assert result.success is False
            assert result.error_code == FileErrorCode.FILE_LOCKED
            assert "locked_file.pdf" in str(result.error_message)
    
    def test_target_file_already_exists_return_error_code_file_exists(self):
        """Test: When target file already exists, return error code FILE_EXISTS with target filename"""
        # Create source file
        source_file = self.incoming_folder / "receipt.pdf"
        source_file.write_text("test content")
        
        # Create existing target file
        target_file = self.scanned_folder / "20240315-test.pdf"
        target_file.write_text("existing content")
        
        # Mock copy_file to return FILE_EXISTS
        with patch.object(self.adapter, 'copy_file') as mock_copy:
            mock_copy.return_value = MagicMock()
            mock_copy.return_value.success = False
            mock_copy.return_value.error_code = FileErrorCode.FILE_EXISTS
            mock_copy.return_value.error_message = f"Target file already exists: {target_file}"
            
            request = FileMovementRequest(
                source_path=source_file,
                target_folder=self.scanned_folder,
                description="test",
                date="20240315"
            )
            
            result = self.adapter.move_to_scanned(request)
            
            assert result.success is False
            assert result.error_code == FileErrorCode.FILE_EXISTS
            assert str(target_file) in str(result.error_message)
    
    def test_source_file_does_not_exist_return_error_code_file_not_found(self):
        """Test: When source file doesn't exist, return error code FILE_NOT_FOUND with source filename"""
        # Create non-existent source file
        source_file = self.incoming_folder / "nonexistent.pdf"
        
        # Mock copy_file to return FILE_NOT_FOUND
        with patch.object(self.adapter, 'copy_file') as mock_copy:
            mock_copy.return_value = MagicMock()
            mock_copy.return_value.success = False
            mock_copy.return_value.error_code = FileErrorCode.FILE_NOT_FOUND
            mock_copy.return_value.error_message = f"Source file does not exist: {source_file}"
            
            request = FileMovementRequest(
                source_path=source_file,
                target_folder=self.scanned_folder,
                description="test",
                date="20240315"
            )
            
            result = self.adapter.move_to_scanned(request)
            
            assert result.success is False
            assert result.error_code == FileErrorCode.FILE_NOT_FOUND
            assert str(source_file) in str(result.error_message)


class TestDescriptionCleaning:
    """Test description cleaning and filesystem safety."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = FileSystemAdapter()
    
    def test_description_contains_non_latin_characters_convert_to_latin_equivalents(self):
        """Test: When description contains non-latin characters (ñ, ü, é, etc.), convert to latin equivalents (n, u, e, etc.)"""
        test_cases = [
            ("café", "cafe"),
            ("niño", "nino"),
            ("bücher", "bucher"),
            ("résumé", "resume"),
            ("naïve", "naive")
        ]
        
        for input_desc, expected in test_cases:
            result = self.adapter.clean_description(input_desc)
            assert result == expected
    
    def test_description_contains_unsafe_filesystem_characters_replace_with_underscores(self):
        """Test: When description contains unsafe filesystem characters (/, \\, :, *, ?, ", <, >, |), replace with underscores"""
        unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        
        for char in unsafe_chars:
            input_desc = f"test{char}file"
            result = self.adapter.clean_description(input_desc)
            assert char not in result
            assert "test_file" == result
    
    def test_description_exceeds_15_characters_truncate_to_15_characters(self):
        """Test: When description exceeds 15 characters, truncate to exactly 15 characters"""
        long_description = "this is a very long description that exceeds fifteen characters"
        result = self.adapter.clean_description(long_description)
        
        assert len(result) == 15
        assert result == "this_is_a_very_"
    
    def test_description_has_leading_trailing_whitespace_trim_whitespace_before_processing(self):
        """Test: When description has leading/trailing whitespace, trim whitespace before processing"""
        input_desc = "   test description   "
        result = self.adapter.clean_description(input_desc)
        
        assert result == "test_descriptio"
        assert not result.startswith(" ")
        assert not result.endswith(" ")
    
    def test_description_is_empty_or_only_whitespace_use_unknown_as_default(self):
        """Test: When description is empty or only whitespace, use "unknown" as default"""
        empty_cases = ["", "   ", "\t\n "]
        
        for input_desc in empty_cases:
            result = self.adapter.clean_description(input_desc)
            assert result == "unknown"
    
    def test_description_contains_multiple_consecutive_spaces_collapse_to_single_underscore(self):
        """Test: When description contains multiple consecutive spaces or underscores, collapse to single underscore"""
        test_cases = [
            ("test    multiple    spaces", "test_multiple_s"),
            ("test____underscores", "test_underscore"),
            ("test  __  mixed", "test_mixed")
        ]
        
        for input_desc, expected in test_cases:
            result = self.adapter.clean_description(input_desc)
            assert result == expected
    
    def test_description_ends_up_as_only_underscores_after_cleaning_use_document_as_fallback(self):
        """Test: When description ends up as only underscores after cleaning, use "document" as fallback"""
        problematic_inputs = ["____", "///", "***", "???"]
        
        for input_desc in problematic_inputs:
            result = self.adapter.clean_description(input_desc)
            assert result == "document"
    
    def test_processing_succeeds_return_cleaned_description_exactly_as_it_will_appear_in_filename(self):
        """Test: When processing succeeds, return cleaned description exactly as it will appear in filename"""
        input_desc = "Café München Résumé#2024.pdf"
        result = self.adapter.clean_description(input_desc)
        
        # Should be: Cafe Munchen Resume_2024.pdf -> Cafe_Munchen_Re (15 chars)
        assert result == "Cafe_Munchen_Re"
        assert len(result) == 15
        
        # Verify it's filesystem safe
        import re
        unsafe_pattern = r'[/\\:*?"<>|]'
        assert not re.search(unsafe_pattern, result)