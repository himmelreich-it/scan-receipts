# One-Off Processing Mode Implementation Specification

## Package: cleanup
**Path**: `src/cleanup/`  
**Purpose**: Handles one-off processing mode cleanup operations for done folder and receipts.csv file  
**User Stories**: DONE_FOLDER_CLEANUP_X1Y2, CSV_FILE_REMOVAL_Z3A4, CLEANUP_ERROR_HANDLE_B5C6  
**Dependencies**: Standard library only (os, shutil, sys, pathlib)

## Architecture Overview
The cleanup package implements a simple, focused approach to file and directory cleanup with proper error handling. It follows the fail-fast principle and provides clear error messages when cleanup operations cannot be completed.

### Module: cleanup.cleaner
**File**: `src/cleanup/cleaner.py`  
**Libraries**: 
- `import os` - File operations
- `import shutil` - Directory tree operations  
- `import sys` - System exit functionality
- `from pathlib import Path` - Path handling
- `from typing import None` - Type hints

**Purpose**: Core cleanup functionality for one-off processing mode  
**Implements**: DONE_FOLDER_CLEANUP_X1Y2, CSV_FILE_REMOVAL_Z3A4, CLEANUP_ERROR_HANDLE_B5C6

#### Class: CleanupManager
**Purpose**: Manages cleanup operations with proper error handling  
**Instantiation**: `CleanupManager(done_folder_path: str, csv_file_path: str)`

##### Constructor Parameters
- `done_folder_path: str` - Path to the done folder (typically "done")
- `csv_file_path: str` - Path to the CSV file (typically "receipts.csv")

##### Methods

###### `execute_cleanup() -> None`
**Purpose**: Main entry point for cleanup operations  
**Implementation**: 
1. Call `_clear_done_folder()` first
2. Call `_remove_csv_file()` second
3. If any operation fails, terminate execution immediately

**Error Handling**: Propagates exceptions from cleanup operations

###### `_clear_done_folder() -> None`
**Purpose**: Clears all files and subdirectories from done folder  
**Implementation**:
```python
def _clear_done_folder(self) -> None:
    """Clear all files and subdirectories from done folder.
    
    Silently succeeds if folder doesn't exist.
    Raises exception if files are in use.
    """
    done_path = Path(self._done_folder_path)
    
    if not done_path.exists():
        return  # Silent success if folder doesn't exist
    
    try:
        # Remove all contents of the directory
        for item in done_path.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
    except (PermissionError, OSError) as e:
        self._handle_cleanup_error(str(done_path), str(e))
```

**Error Scenarios**: Files in use, permission errors, disk full

###### `_remove_csv_file() -> None`
**Purpose**: Removes the receipts.csv file  
**Implementation**:
```python
def _remove_csv_file(self) -> None:
    """Remove the receipts.csv file.
    
    Silently succeeds if file doesn't exist.
    Raises exception if file is in use.
    """
    csv_path = Path(self._csv_file_path)
    
    if not csv_path.exists():
        return  # Silent success if file doesn't exist
    
    try:
        csv_path.unlink()
    except (PermissionError, OSError) as e:
        self._handle_cleanup_error(str(csv_path), str(e))
```

**Error Scenarios**: File in use, permission errors

###### `_handle_cleanup_error(file_path: str, error_message: str) -> None`
**Purpose**: Handles cleanup errors with proper error messages and termination  
**Implementation**:
```python
def _handle_cleanup_error(self, file_path: str, error_message: str) -> None:
    """Handle cleanup errors by displaying message and terminating.
    
    Args:
        file_path: Path of the file/folder that caused the error
        error_message: Original error message from the exception
    """
    print(f"Error: {file_path} is currently in use by another process")
    sys.exit(1)
```

**Error Message Format**: "Error: [filename] is currently in use by another process"  
**Termination**: Uses `sys.exit(1)` to terminate script execution

##### Private Properties
- `_done_folder_path: str` - Stored done folder path
- `_csv_file_path: str` - Stored CSV file path

### Module: cleanup.__init__
**File**: `src/cleanup/__init__.py`  
**Purpose**: Package initialization and public API  
**Exports**: `CleanupManager`

```python
"""One-off processing mode cleanup package."""

from .cleaner import CleanupManager

__all__ = ['CleanupManager']
```

## Usage Examples

### Basic Usage
```python
from cleanup import CleanupManager

# Initialize cleanup manager
cleanup_manager = CleanupManager(
    done_folder_path="done",
    csv_file_path="receipts.csv"
)

# Execute cleanup (will terminate on error)
cleanup_manager.execute_cleanup()

# If we reach here, cleanup was successful
print("Cleanup completed successfully")
```

### Integration with Main Script
```python
import sys
from cleanup import CleanupManager

def main():
    # Initialize cleanup at start of script
    cleanup_manager = CleanupManager("done", "receipts.csv")
    
    try:
        cleanup_manager.execute_cleanup()
    except SystemExit:
        # Cleanup failed, script already terminated
        pass
    
    # Continue with receipt processing...
    process_receipts()

if __name__ == "__main__":
    main()
```

## Configuration
**File**: `src/cleanup/config.py`  
**Purpose**: Configuration constants for cleanup operations

```python
"""Configuration for cleanup operations."""

# Default paths
DEFAULT_DONE_FOLDER = "done"
DEFAULT_CSV_FILE = "receipts.csv"

# Error messages
ERROR_MESSAGE_TEMPLATE = "Error: {file_path} is currently in use by another process"
```

## Testing Requirements

### Test Module: tests/unit/test_cleanup/test_cleaner.py
**Purpose**: Unit tests for CleanupManager class

#### Test Scenarios

##### Happy Path Tests
```python
def test_execute_cleanup_success_both_exist(tmp_path):
    """Test successful cleanup when both folder and file exist."""
    
def test_execute_cleanup_success_neither_exist():
    """Test successful cleanup when neither folder nor file exist."""
    
def test_execute_cleanup_success_only_folder_exists(tmp_path):
    """Test successful cleanup when only done folder exists."""
    
def test_execute_cleanup_success_only_csv_exists(tmp_path):
    """Test successful cleanup when only CSV file exists."""
```

##### Error Handling Tests
```python
def test_cleanup_folder_permission_error(tmp_path, monkeypatch):
    """Test cleanup failure when done folder files are in use."""
    
def test_cleanup_csv_permission_error(tmp_path, monkeypatch):
    """Test cleanup failure when CSV file is in use."""
    
def test_cleanup_error_message_format(capsys):
    """Test error message format matches requirements."""
    
def test_cleanup_terminates_on_error(monkeypatch):
    """Test that cleanup terminates script on error."""
```

#### Mock Requirements
- Mock `sys.exit()` to test termination behavior
- Mock `Path.unlink()` and `shutil.rmtree()` to simulate permission errors
- Use `tmp_path` fixture for filesystem operations

#### Test Data
```python
@pytest.fixture
def sample_done_folder(tmp_path):
    """Create sample done folder with files and subdirectories."""
    done_dir = tmp_path / "done"
    done_dir.mkdir()
    
    # Create sample files
    (done_dir / "file1.txt").write_text("content1")
    (done_dir / "file2.pdf").write_text("content2")
    
    # Create subdirectory
    sub_dir = done_dir / "subdir"
    sub_dir.mkdir()
    (sub_dir / "file3.jpg").write_text("content3")
    
    return done_dir

@pytest.fixture
def sample_csv_file(tmp_path):
    """Create sample CSV file."""
    csv_file = tmp_path / "receipts.csv"
    csv_file.write_text("ID,Amount,Tax,Description\n1,10.00,1.00,Test\n")
    return csv_file
```

## Error Handling Specifications

### Exception Types
- `PermissionError`: File/folder in use by another process
- `OSError`: General file system errors
- `FileNotFoundError`: Handled gracefully (silent success)

### Error Recovery
- No recovery mechanisms - fail fast approach
- Script terminates immediately on any cleanup error
- Clear error messages indicate specific files that are in use

### Error Message Requirements
- Format: "Error: [filename] is currently in use by another process"
- Display to console before termination
- Use actual file path in error message

## Performance Considerations
- Minimal performance requirements - cleanup is one-time operation at script start
- Operations are synchronous and blocking
- No caching or optimization needed

## Security Considerations
- Path validation to prevent directory traversal (using pathlib.Path)
- No external dependencies or network operations
- File operations limited to specified paths only

## Integration Points

### Dependencies
- **None** - This package has no dependencies on other user stories

### Used By
- **Terminal Script Interface** - For error display and script termination
- **Batch Processing Workflow** - Must execute before any processing begins

### Interface Requirements
- Must be callable at start of script execution
- Must terminate script on error (no graceful degradation)
- Must be silent on success (no console output)

## Deployment Considerations
- No special deployment requirements
- Uses only standard library components
- Cross-platform compatible (Windows, Linux, macOS)

## User Story Implementation Mapping

### DONE_FOLDER_CLEANUP_X1Y2
**Implemented by**: `CleanupManager._clear_done_folder()`  
**Acceptance Criteria Coverage**:
- ✅ Clears all files and subdirectories from done folder
- ✅ Silent success if folder doesn't exist  
- ✅ Executes at start of script
- ✅ Silent operation (no console output)
- ✅ Removes all file types and subdirectories

### CSV_FILE_REMOVAL_Z3A4
**Implemented by**: `CleanupManager._remove_csv_file()`  
**Acceptance Criteria Coverage**:
- ✅ Removes receipts.csv file at start
- ✅ Silent success if file doesn't exist
- ✅ Executes before receipt processing
- ✅ Silent operation (no console output)
- ✅ Only removes receipts.csv, not other CSV files

### CLEANUP_ERROR_HANDLE_B5C6
**Implemented by**: `CleanupManager._handle_cleanup_error()`  
**Acceptance Criteria Coverage**:
- ✅ Detects files in use in done folder
- ✅ Detects CSV file in use
- ✅ Displays clear error message with filename
- ✅ Terminates script immediately on cleanup failure
- ✅ Does not proceed with processing if cleanup fails
- ✅ Error message format matches specification