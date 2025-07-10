# Implementation Specification: Terminal Interface Package

## Package: terminal_interface
**Path**: `src/terminal_interface/`  
**Purpose**: Provides command-line interface functionality for receipt processing script execution, including progress display, error reporting, and user interaction  
**User Stories**: SCRIPT_EXEC_T1A2, STARTUP_MSG_T3B4, PROGRESS_DISP_T5C6, ERROR_DISP_T7D8, SUMMARY_DISP_T9E0  
**Dependencies**: Standard Python library only (no external dependencies)

## Module Structure Overview

```
src/terminal_interface/
├── __init__.py
├── main.py
├── display/
│   ├── __init__.py
│   ├── progress_display.py
│   └── messages.py
└── errors/
    ├── __init__.py
    └── error_handler.py
```

## Module: src/terminal_interface/main.py

**Purpose**: Main script entry point that orchestrates terminal interface workflow  
**Libraries**: Standard Python only (sys, os, signal)  
**Implements**: SCRIPT_EXEC_T1A2  
**Dependencies**: None

### Functions

#### `main() -> None`
```python
def main() -> None:
    """Main entry point for receipt processing script.
    
    Handles script execution with proper exception handling and exit codes.
    Provides clean entry point following if __name__ == "__main__" pattern.
    
    Returns:
        None
        
    Raises:
        SystemExit: With code 0 for success, 1 for errors
    """
```

**Implementation Notes**:
- Use `if __name__ == "__main__":` pattern as specified
- Implement top-level exception handling to catch all unhandled exceptions
- Return exit code 0 for successful completion
- Return exit code 1 for any errors
- Handle keyboard interrupts (Ctrl+C) gracefully
- Ensure script can be executed from any directory

#### `setup_signal_handlers() -> None`
```python
def setup_signal_handlers() -> None:
    """Configure signal handlers for graceful shutdown.
    
    Sets up handlers for SIGINT (Ctrl+C) and SIGTERM to allow clean exit.
    """
```

**Implementation Notes**:
- Handle SIGINT (Ctrl+C) gracefully
- Print clean exit message when interrupted
- Ensure proper cleanup before exit

### Error Scenarios Implementation
- **Python interpreter issues**: Handle ImportError, SyntaxError at module level
- **Script file permissions**: Handle PermissionError when accessing files
- **Missing dependencies**: Handle ImportError for required modules

### Usage Example
```python
# Execute script
python main.py

# Expected behavior:
# - Shows startup message
# - Displays progress for each file
# - Shows errors for failed files
# - Displays final summary
# - Exits with code 0 (success) or 1 (error)
```

## Module: src/terminal_interface/display/messages.py

**Purpose**: Handles startup messages and static text display  
**Libraries**: Standard Python only  
**Implements**: STARTUP_MSG_T3B4  
**Dependencies**: None

### Functions

#### `display_startup_message() -> None`
```python
def display_startup_message() -> None:
    """Display startup message about receipt processing operation.
    
    Shows informational message before processing begins.
    Message indicates processing is about to start and mentions input folder scanning.
    """
```

**Implementation Notes**:
- Display message before any processing starts
- Message should be brief and informative
- Mention receipt processing operation
- Indicate input folder scanning will begin
- Use simple print statement for output

### Message Content
- Clear indication of receipt processing operation
- Brief description of what will happen
- Reference to input folder scanning
- Keep message concise and user-friendly

### Error Scenarios Implementation
- **Terminal output issues**: Handle sys.stdout errors gracefully
- **Encoding problems**: Use UTF-8 encoding for text output

## Module: src/terminal_interface/display/progress_display.py

**Purpose**: Manages real-time progress display during file processing  
**Libraries**: Standard Python only  
**Implements**: PROGRESS_DISP_T5C6  
**Dependencies**: None

### Class: ProgressDisplay

#### `__init__(self, total_files: int) -> None`
```python
def __init__(self, total_files: int) -> None:
    """Initialize progress display with total file count.
    
    Args:
        total_files: Total number of files to process
    """
```

#### `display_file_progress(self, current_file: int, filename: str) -> None`
```python
def display_file_progress(self, current_file: int, filename: str) -> None:
    """Display progress for current file being processed.
    
    Args:
        current_file: Current file number (1-based)
        filename: Name of file being processed
        
    Format: "Processing file X of Y: filename"
    """
```

**Implementation Notes**:
- Display current file number (1-based counting)
- Show total file count
- Display filename being processed
- Maintain consistent format across all files
- Use real-time output (print statements)
- Handle very long filenames by truncating if necessary

### Data Requirements
- File list from input folder (for total count)
- Current processing index (maintained externally)
- Current filename being processed

### Error Scenarios Implementation
- **Terminal output buffering**: Use flush=True for immediate output
- **Very long filenames**: Truncate filenames longer than 80 characters
- **Special characters in filenames**: Handle Unicode characters properly

## Module: src/terminal_interface/errors/error_handler.py

**Purpose**: Handles error display and logging to console  
**Libraries**: Standard Python only  
**Implements**: ERROR_DISP_T7D8  
**Dependencies**: None

### Class: ErrorHandler

#### `__init__(self) -> None`
```python
def __init__(self) -> None:
    """Initialize error handler with error counter."""
```

#### `display_error(self, filename: str, error_description: str) -> None`
```python
def display_error(self, filename: str, error_description: str) -> None:
    """Display error message for failed file processing.
    
    Args:
        filename: Name of file that failed processing
        error_description: Description of the error that occurred
        
    Shows clear error message and increments error counter.
    """
```

#### `get_error_count(self) -> int`
```python
def get_error_count(self) -> int:
    """Get current error count.
    
    Returns:
        Number of errors encountered
    """
```

**Implementation Notes**:
- Display error messages immediately when they occur
- Show filename and error description clearly
- Maintain error counter for summary reporting
- Use try-catch blocks around file processing operations
- Continue processing after errors (don't halt execution)

### Data Requirements
- Error messages from processing operations
- Failed file names
- Error count tracking (internal counter)

### Error Scenarios Implementation
- **Multiple cascading errors**: Handle and display each error independently
- **Terminal output during error states**: Ensure error messages display properly
- **Error message formatting**: Handle special characters in error messages

## Module: src/terminal_interface/display/summary_display.py

**Purpose**: Displays comprehensive processing summary at completion  
**Libraries**: Standard Python only  
**Implements**: SUMMARY_DISP_T9E0  
**Dependencies**: None

### Class: SummaryDisplay

#### `display_final_summary(self, total_processed: int, error_count: int, duplicates_skipped: int) -> None`
```python
def display_final_summary(self, total_processed: int, error_count: int, duplicates_skipped: int) -> None:
    """Display comprehensive summary after all processing completes.
    
    Args:
        total_processed: Number of files processed successfully
        error_count: Number of errors encountered
        duplicates_skipped: Number of duplicate files skipped
        
    Shows summary with clear formatting and statistics.
    """
```

**Implementation Notes**:
- Display summary after all processing completes
- Show total files processed successfully
- Display count of errors encountered
- Display count of duplicates skipped
- Format numbers clearly and consistently
- Call before script exit

### Data Requirements
- Processing counters from main workflow:
  - Success count
  - Error count  
  - Duplicate count
- Summary statistics accumulated during processing

### Error Scenarios Implementation
- **Counter overflow**: Handle large numbers gracefully
- **Summary display formatting**: Ensure proper formatting of statistics

## Integration Points

### Main Workflow Integration
```python
# Example integration in main processing loop
from terminal_interface.display.messages import display_startup_message
from terminal_interface.display.progress_display import ProgressDisplay
from terminal_interface.errors.error_handler import ErrorHandler
from terminal_interface.display.summary_display import SummaryDisplay

def main():
    # Display startup message
    display_startup_message()
    
    # Initialize displays
    progress = ProgressDisplay(total_files)
    error_handler = ErrorHandler()
    summary = SummaryDisplay()
    
    # Processing loop
    for i, file in enumerate(files, 1):
        progress.display_file_progress(i, file.name)
        try:
            # Process file
            process_file(file)
            success_count += 1
        except Exception as e:
            error_handler.display_error(file.name, str(e))
    
    # Display final summary
    summary.display_final_summary(success_count, error_handler.get_error_count(), duplicates_skipped)
```

### Interface Dependencies
- **Input**: File lists from file processing components
- **Output**: Console display only (no file output)
- **Error Communication**: Exception handling and error message passing

## Configuration

### Fixed Parameters
- **Console Output**: Standard output (sys.stdout)
- **Progress Format**: "Processing file X of Y: filename"
- **Error Format**: Clear error messages with filename and description
- **Summary Format**: Structured statistics display

### Environment Requirements
- **Terminal Support**: Standard terminal with UTF-8 encoding
- **Python Version**: Compatible with Python 3.8+
- **Platform**: Cross-platform (Windows, Linux, macOS)

## Testing Requirements

### Test Scenarios for SCRIPT_EXEC_T1A2
```python
def test_main_successful_execution():
    """Test main function completes successfully and returns exit code 0."""
    
def test_main_handles_exceptions():
    """Test main function catches exceptions and returns exit code 1."""
    
def test_main_handles_keyboard_interrupt():
    """Test main function handles Ctrl+C gracefully."""
```

### Test Scenarios for STARTUP_MSG_T3B4
```python
def test_display_startup_message():
    """Test startup message displays correctly."""
    
def test_startup_message_appears_before_processing():
    """Test startup message appears before any processing begins."""
```

### Test Scenarios for PROGRESS_DISP_T5C6
```python
def test_progress_display_format():
    """Test progress display shows correct format: 'Processing file X of Y: filename'."""
    
def test_progress_display_handles_long_filenames():
    """Test progress display handles very long filenames properly."""
```

### Test Scenarios for ERROR_DISP_T7D8
```python
def test_error_display_shows_filename_and_description():
    """Test error display shows both filename and error description."""
    
def test_error_counter_increments():
    """Test error counter increments properly for each error."""
```

### Test Scenarios for SUMMARY_DISP_T9E0
```python
def test_summary_display_shows_all_counters():
    """Test summary displays total processed, errors, and duplicates skipped."""
    
def test_summary_display_formatting():
    """Test summary displays numbers in clear, readable format."""
```

### Mock Requirements
- **File system operations**: Mock file reading for testing
- **Console output**: Capture print statements for verification
- **Exception scenarios**: Mock exceptions for error handling tests

### Test Data
- **Sample filenames**: Various filename lengths and character sets
- **Error scenarios**: Common processing errors for testing
- **Counter values**: Various combinations of success/error/duplicate counts

## User Story Implementation References

### SCRIPT_EXEC_T1A2: Script Execution Entry Point
- **Implements**: main.py module with main() function
- **Depends on**: None
- **Used by**: All other terminal interface components

### STARTUP_MSG_T3B4: Startup Message Display  
- **Implements**: messages.py module with display_startup_message()
- **Depends on**: SCRIPT_EXEC_T1A2
- **Used by**: Main processing workflow

### PROGRESS_DISP_T5C6: Progress Display During Processing
- **Implements**: progress_display.py module with ProgressDisplay class
- **Depends on**: SCRIPT_EXEC_T1A2
- **Used by**: Main processing workflow

### ERROR_DISP_T7D8: Error Display and Logging
- **Implements**: error_handler.py module with ErrorHandler class
- **Depends on**: SCRIPT_EXEC_T1A2
- **Used by**: Main processing workflow

### SUMMARY_DISP_T9E0: Final Summary Display
- **Implements**: summary_display.py module with SummaryDisplay class
- **Depends on**: SCRIPT_EXEC_T1A2
- **Used by**: Main processing workflow

## Implementation Notes

### KISS Principle Adherence
- All output uses simple text-based display
- Standard Python print statements for console output
- No external dependencies beyond Python standard library
- Simple, straightforward implementation approaches

### Cross-Platform Compatibility
- Uses standard Python library functions only
- Handles different terminal environments
- Proper encoding handling for different systems
- Path handling compatible across platforms

### Error Handling Strategy
- Graceful handling of terminal output issues
- Continue processing after individual errors
- Clear error messages for debugging
- Proper exception propagation to main handler

### Performance Considerations
- Minimal memory usage for display operations
- Efficient string formatting for progress display
- No unnecessary file I/O operations
- Real-time output without significant delays