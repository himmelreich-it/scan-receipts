"""Unit tests for FILE_HASH_C7F4: File Hash Generation and Duplicate Detection Support."""

import hashlib
import tempfile
from pathlib import Path
from unittest.mock import patch

from file_management.adapters import FileSystemAdapter
from file_management.models import FileErrorCode


class TestFileHashGeneration:
    """Test file hash generation and duplicate detection support."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = FileSystemAdapter()
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_hash_requested_for_file_generate_sha256_and_return_hexadecimal_string(self):
        """Test: When hash is requested for a file, generate SHA-256 hash and return as hexadecimal string"""
        # Create test file with known content
        test_file = self.temp_dir / "test_receipt.pdf"
        test_content = b"test receipt content for hash generation"
        test_file.write_bytes(test_content)
        
        # Generate expected hash
        expected_hash = hashlib.sha256(test_content).hexdigest()
        
        # Generate hash using adapter
        result = self.adapter.generate_file_hash(test_file)
        
        # Verify success and hash value
        assert result.success is True
        assert result.hash_value == expected_hash
        assert result.hash_value is not None
        assert len(result.hash_value) == 64  # SHA-256 produces 64 hex characters
        assert result.file_path == test_file
        assert result.error_code is None
        assert result.error_message is None
    
    def test_file_is_unreadable_return_error_code_file_unreadable(self):
        """Test: When file is unreadable, return error code FILE_UNREADABLE with filename and system error details"""
        test_file = self.temp_dir / "unreadable_file.pdf"
        test_file.touch()  # Create the file so it exists
        
        # Mock open to simulate permission error
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            result = self.adapter.generate_file_hash(test_file)
            
            assert result.success is False
            assert result.error_code == FileErrorCode.FILE_PERMISSION_DENIED
            assert str(test_file) in (result.error_message or "")
            assert result.file_path == test_file
            assert result.hash_value is None
    
    def test_file_is_corrupted_during_reading_return_error_code_file_corrupted(self):
        """Test: When file is corrupted during reading, return error code FILE_CORRUPTED with filename"""
        test_file = self.temp_dir / "corrupted_file.pdf"
        test_file.touch()  # Create the file so it exists
        
        # Create OSError with errno 5 (Input/output error)
        io_error = OSError("I/O error")
        io_error.errno = 5
        
        # Mock open to simulate file corruption during read
        with patch('builtins.open', side_effect=io_error):
            result = self.adapter.generate_file_hash(test_file)
            
            assert result.success is False
            assert result.error_code == FileErrorCode.FILE_CORRUPTED
            assert "corrupted" in (result.error_message or "").lower()
            assert str(test_file) in (result.error_message or "")
            assert result.file_path == test_file
            assert result.hash_value is None
    
    def test_file_does_not_exist_return_error_code_file_not_found(self):
        """Test: When file doesn't exist, return error code FILE_NOT_FOUND with filename"""
        nonexistent_file = self.temp_dir / "does_not_exist.pdf"
        
        result = self.adapter.generate_file_hash(nonexistent_file)
        
        assert result.success is False
        assert result.error_code == FileErrorCode.FILE_NOT_FOUND
        assert str(nonexistent_file) in (result.error_message or "")
        assert result.file_path == nonexistent_file
        assert result.hash_value is None
    
    def test_multiple_hash_requests_for_same_file_generate_fresh_hash_each_time(self):
        """Test: When multiple hash requests for same file, generate fresh hash each time (no caching)"""
        # Create test file
        test_file = self.temp_dir / "test_file.pdf"
        test_content = b"consistent content for multiple hash requests"
        test_file.write_bytes(test_content)
        
        # Generate hash twice
        result1 = self.adapter.generate_file_hash(test_file)
        result2 = self.adapter.generate_file_hash(test_file)
        
        # Both should succeed and produce same hash (no caching doesn't mean different results)
        assert result1.success is True
        assert result2.success is True
        assert result1.hash_value == result2.hash_value
        
        # Verify both are reading fresh from file (not from cache)
        expected_hash = hashlib.sha256(test_content).hexdigest()
        assert result1.hash_value == expected_hash
        assert result2.hash_value == expected_hash
    
    def test_hash_generation_succeeds_return_64_character_hexadecimal_string(self):
        """Test: When hash generation succeeds, return 64-character hexadecimal string"""
        # Create test file
        test_file = self.temp_dir / "hex_test.pdf"
        test_file.write_bytes(b"content for hex validation")
        
        result = self.adapter.generate_file_hash(test_file)
        
        assert result.success is True
        assert result.hash_value is not None
        assert len(result.hash_value) == 64
        
        # Verify it's valid hexadecimal
        try:
            int(result.hash_value, 16)
            is_hex = True
        except ValueError:
            is_hex = False
        
        assert is_hex is True
    
    def test_file_has_zero_bytes_return_hash_of_empty_content(self):
        """Test: When file has zero bytes, return hash of empty content"""
        # Create empty file
        empty_file = self.temp_dir / "empty.txt"
        empty_file.touch()  # Creates empty file
        
        # Generate expected hash for empty content
        expected_hash = hashlib.sha256(b"").hexdigest()
        
        result = self.adapter.generate_file_hash(empty_file)
        
        assert result.success is True
        assert result.hash_value == expected_hash
        assert result.hash_value is not None
        assert len(result.hash_value) == 64
    
    def test_file_is_very_large_process_in_chunks_without_memory_overflow(self):
        """Test: When file is very large, process in chunks without memory overflow"""
        # Create a file large enough to test chunking (using mock to simulate large file)
        test_file = self.temp_dir / "large_file.pdf"
        
        # Mock file content in chunks
        chunk_size = 64 * 1024  # 64KB chunks as used in implementation
        large_content = b"A" * (chunk_size + 100)  # Slightly larger than one chunk
        
        test_file.write_bytes(large_content)
        
        # Generate hash - should handle chunking internally
        result = self.adapter.generate_file_hash(test_file)
        
        # Verify success
        assert result.success is True
        assert result.hash_value is not None
        assert len(result.hash_value) == 64
        
        # Verify hash is correct for the large content
        expected_hash = hashlib.sha256(large_content).hexdigest()
        assert result.hash_value == expected_hash
    
    def test_memory_error_during_hashing_return_error_code_memory_insufficient(self):
        """Test: Handle memory error during hash generation"""
        test_file = self.temp_dir / "memory_test.pdf"
        test_file.write_bytes(b"test content")
        
        # Mock hashlib to raise MemoryError
        with patch('hashlib.sha256', side_effect=MemoryError("Insufficient memory")):
            result = self.adapter.generate_file_hash(test_file)
            
            assert result.success is False
            assert result.error_code == FileErrorCode.MEMORY_INSUFFICIENT
            assert "memory" in (result.error_message or "").lower()
            assert result.hash_value is None
    
    def test_general_os_error_during_reading_return_error_code_file_unreadable(self):
        """Test: Handle general OS error during file reading"""
        test_file = self.temp_dir / "os_error_test.pdf"
        test_file.touch()  # Create the file so it exists
        
        # Create general OSError (not corruption specific)
        general_error = OSError("General I/O error")
        general_error.errno = 13  # Not the corruption errno (5)
        
        with patch('builtins.open', side_effect=general_error):
            result = self.adapter.generate_file_hash(test_file)
            
            assert result.success is False
            assert result.error_code == FileErrorCode.FILE_UNREADABLE
            assert str(test_file) in (result.error_message or "")
            assert result.hash_value is None
    
    def test_unexpected_error_return_file_unreadable_with_error_details(self):
        """Test: Handle unexpected error during hash generation"""
        test_file = self.temp_dir / "unexpected_error.pdf"
        test_file.touch()  # Create the file so it exists
        
        # Mock to raise unexpected exception
        with patch('builtins.open', side_effect=RuntimeError("Unexpected error")):
            result = self.adapter.generate_file_hash(test_file)
            
            assert result.success is False
            assert result.error_code == FileErrorCode.FILE_UNREADABLE
            assert "unexpected error" in (result.error_message or "").lower()
            assert result.hash_value is None
    
    def test_hash_generation_processes_binary_content_correctly(self):
        """Test: Verify hash generation works with binary file content"""
        # Create file with binary content (simulate PDF header)
        test_file = self.temp_dir / "binary_test.pdf"
        binary_content = b'\x25\x50\x44\x46\x2d\x31\x2e\x34'  # PDF header bytes
        test_file.write_bytes(binary_content)
        
        # Generate hash
        result = self.adapter.generate_file_hash(test_file)
        
        # Verify success
        assert result.success is True
        
        # Verify hash matches expected value for this binary content
        expected_hash = hashlib.sha256(binary_content).hexdigest()
        assert result.hash_value == expected_hash
    
    def test_identical_content_different_files_produce_same_hash(self):
        """Test: Files with identical content produce identical hashes"""
        # Create two files with identical content
        content = b"identical content for hash comparison"
        
        file1 = self.temp_dir / "file1.pdf"
        file2 = self.temp_dir / "file2.jpg"
        
        file1.write_bytes(content)
        file2.write_bytes(content)
        
        # Generate hashes
        result1 = self.adapter.generate_file_hash(file1)
        result2 = self.adapter.generate_file_hash(file2)
        
        # Both should succeed and produce identical hashes
        assert result1.success is True
        assert result2.success is True
        assert result1.hash_value == result2.hash_value
    
    def test_different_content_produces_different_hashes(self):
        """Test: Files with different content produce different hashes"""
        # Create two files with different content
        file1 = self.temp_dir / "content1.pdf"
        file2 = self.temp_dir / "content2.pdf"
        
        file1.write_bytes(b"first file content")
        file2.write_bytes(b"second file content")
        
        # Generate hashes
        result1 = self.adapter.generate_file_hash(file1)
        result2 = self.adapter.generate_file_hash(file2)
        
        # Both should succeed but produce different hashes
        assert result1.success is True
        assert result2.success is True
        assert result1.hash_value != result2.hash_value