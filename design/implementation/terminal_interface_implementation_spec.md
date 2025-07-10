# Terminal Interface Implementation Specification

## Package: terminal_interface
**Path**: `src/terminal_interface/`  
**Purpose**: Provides command-line interface for the receipt processing script with progress display and error handling  
**User Stories**: SCRIPT_EXEC_T1A2, STARTUP_MSG_T3B4, PROGRESS_DISP_T5C6, ERROR_DISP_T7D8, SUMMARY_DISP_T9E0  
**Dependencies**: None (uses only Python standard library)

## Module: terminal_interface.main

### Module Details
- **Module location**: `src/terminal_interface/main.py`
- **Libraries used**: 
  - `sys` - for exit codes and command-line argument access
  - `os` - for working directory management
  - `typing` - for type hints
- **Module-level functions**: `main()` - entry point orchestrating terminal interface workflow
- **Module-level properties**: None

### Function: main()
**Signature**: `def main() -> None`
**Purpose**: Main entry point that orchestrates the terminal interface workflow
**Implementation Notes**:
- Uses `if __name__ == "__main__":` pattern for script execution
- Implements top-level exception handling with clean exit codes
- Ensures script can be executed from any directory
- Handles keyboard interrupts gracefully (Ctrl+C)

**Error Handling**:
- Catches all exceptions and provides clean error messages
- Uses `sys.exit(1)` for error conditions, `sys.exit(0)` for success
- Logs errors to console before exiting

**Code Structure**:
```python
def main() -> None:
    """Main entry point for receipt processing terminal interface."""
    try:
        # Initialize display components
        display = TerminalDisplay()
        
        # Show startup message
        display.show_startup_message()
        
        # Process receipts with progress display
        processor = ReceiptProcessor(display)
        results = processor.process_all()
        
        # Display final summary
        display.show_summary(results)
        
    except KeyboardInterrupt:
        print("\nProcessing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    else:
        sys.exit(0)
```

## Module: terminal_interface.display

### Module Details
- **Module location**: `src/terminal_interface/display.py`
- **Libraries used**:
  - `typing` - for type hints
  - `dataclasses` - for ProcessingResults structure
- **Module-level functions**: None
- **Module-level properties**: Static message templates

### Class: TerminalDisplay
**Purpose**: Handles all terminal output including startup messages, progress, errors, and summary
**Methods**:
- `show_startup_message() -> None`
- `show_progress(current: int, total: int, filename: str) -> None`
- `show_error(filename: str, error_message: str) -> None`
- `show_summary(results: ProcessingResults) -> None`

#### Method: show_startup_message()
**Signature**: `def show_startup_message(self) -> None`
**Purpose**: Displays brief informational message about receipt processing operation
**Implementation Notes**:
- Simple print statement with static message
- Displays before any processing starts
- Mentions input folder scanning

**Implementation**:
```python
def show_startup_message(self) -> None:
    """Display startup message indicating processing is about to begin."""
    print("Receipt Processing Tool")
    print("Scanning input folder for receipt files...")
    print()
```

#### Method: show_progress()
**Signature**: `def show_progress(self, current: int, total: int, filename: str) -> None`
**Purpose**: Shows real-time progress in format "Processing file X of Y: filename"
**Implementation Notes**:
- Displays current file number, total file count, and filename
- Updates for each file in sequence
- Maintains consistent format
- Handles long filenames by truncating if necessary

**Implementation**:
```python
def show_progress(self, current: int, total: int, filename: str) -> None:
    """Display current processing progress."""
    # Truncate filename if too long for terminal display
    display_filename = filename[:50] + "..." if len(filename) > 50 else filename
    print(f"Processing file {current} of {total}: {display_filename}")
```

#### Method: show_error()
**Signature**: `def show_error(self, filename: str, error_message: str) -> None`
**Purpose**: Displays error messages to console for individual file processing failures
**Implementation Notes**:
- Shows clear error messages for failed files
- Displays filename with error description
- Prints error messages immediately when they occur

**Implementation**:
```python
def show_error(self, filename: str, error_message: str) -> None:
    """Display error message for failed file processing."""
    print(f"ERROR processing {filename}: {error_message}")
```

#### Method: show_summary()
**Signature**: `def show_summary(self, results: ProcessingResults) -> None`
**Purpose**: Shows comprehensive summary at completion
**Implementation Notes**:
- Displays total files processed successfully
- Shows count of errors encountered
- Shows count of duplicates skipped
- Displays summary after all processing completes

**Implementation**:
```python
def show_summary(self, results: ProcessingResults) -> None:
    """Display final processing summary."""
    print("\n" + "="*50)
    print("PROCESSING SUMMARY")
    print("="*50)
    print(f"Total files processed: {results.successful_count}")
    print(f"Errors encountered: {results.error_count}")
    print(f"Duplicates skipped: {results.duplicate_count}")
    print(f"Total files scanned: {results.total_files}")
    print("="*50)
```

### Data Structure: ProcessingResults
**Purpose**: Container for processing statistics
**Implementation**:
```python
@dataclass
class ProcessingResults:
    """Results of receipt processing operation."""
    successful_count: int
    error_count: int
    duplicate_count: int
    total_files: int
```

## Module: terminal_interface.processor

### Module Details
- **Module location**: `src/terminal_interface/processor.py`
- **Libraries used**:
  - `typing` - for type hints
  - `pathlib` - for file path operations
- **Module-level functions**: None
- **Module-level properties**: None

### Class: ReceiptProcessor
**Purpose**: Orchestrates receipt processing with terminal display integration
**Properties**:
- `_display: TerminalDisplay` - Terminal display handler
- `_current_file: int` - Current file counter
- `_total_files: int` - Total files to process
- `_results: ProcessingResults` - Processing statistics

#### Method: __init__()
**Signature**: `def __init__(self, display: TerminalDisplay) -> None`
**Purpose**: Initialize processor with display handler
**Implementation Notes**:
- Stores display handler for progress reporting
- Initializes counters

#### Method: process_all()
**Signature**: `def process_all(self) -> ProcessingResults`
**Purpose**: Main processing loop that handles file iteration and progress display
**Implementation Notes**:
- Calculates total files upfront for progress display
- Maintains counter during processing
- Handles errors for individual files while continuing processing
- Updates display for each file processed

**Implementation**:
```python
def process_all(self) -> ProcessingResults:
    """Process all receipt files with progress display."""
    # Initialize results tracking
    results = ProcessingResults(
        successful_count=0,
        error_count=0,
        duplicate_count=0,
        total_files=0
    )
    
    # Get list of files to process
    input_files = self._get_input_files()
    results.total_files = len(input_files)
    
    # Process each file
    for index, file_path in enumerate(input_files, 1):
        try:
            # Display progress
            self._display.show_progress(index, results.total_files, file_path.name)
            
            # Process individual file
            success = self._process_file(file_path)
            if success:
                results.successful_count += 1
            else:
                results.duplicate_count += 1
                
        except Exception as e:
            # Display error and continue processing
            self._display.show_error(file_path.name, str(e))
            results.error_count += 1
    
    return results
```

#### Method: _get_input_files()
**Signature**: `def _get_input_files(self) -> List[Path]`
**Purpose**: Get list of receipt files from input directory
**Implementation Notes**:
- Returns list of Path objects for supported file types
- Handles empty directory gracefully

#### Method: _process_file()
**Signature**: `def _process_file(self, file_path: Path) -> bool`
**Purpose**: Process individual receipt file
**Implementation Notes**:
- Returns True if processed successfully, False if duplicate
- Raises exceptions for processing errors
- Integrates with other system components for actual processing

## Entry Point Configuration

### Module: main.py (root level)
**Purpose**: Script entry point for `python main.py` execution
**Implementation**:
```python
#!/usr/bin/env python3
"""Receipt processing script entry point."""

if __name__ == "__main__":
    from src.terminal_interface.main import main
    main()
```

## Integration Points

### Interface with Other Components
- **Receipt Processing Core**: `ReceiptProcessor._process_file()` calls core processing logic
- **File Management**: Terminal interface triggers file organization after processing
- **Error Handling**: Terminal interface catches and displays errors from all components

### Error Scenarios Handled
1. **Python interpreter issues**: Handled by shell/OS, not application code
2. **Script file permissions**: Handled by shell/OS, not application code
3. **Missing dependencies**: Handled by Python import system
4. **Terminal output issues**: Basic print statements, no special handling required
5. **Encoding problems**: Use default UTF-8 encoding, no special handling
6. **Terminal output buffering**: Use immediate print statements
7. **Very long filenames**: Truncate for display purposes
8. **Special characters in filenames**: Use Path objects for proper handling
9. **Multiple cascading errors**: Continue processing after individual file errors
10. **Keyboard interrupts**: Graceful handling with try/catch in main()

## Usage Examples

### Basic Execution
```bash
python main.py
```

### Expected Output Flow
```
Receipt Processing Tool
Scanning input folder for receipt files...

Processing file 1 of 5: receipt_001.pdf
Processing file 2 of 5: grocery_store_receipt.jpg
ERROR processing damaged_file.pdf: File format not supported
Processing file 3 of 5: restaurant_bill.png
Processing file 4 of 5: gas_station.pdf
Processing file 5 of 5: office_supplies.jpg

==================================================
PROCESSING SUMMARY
==================================================
Total files processed: 4
Errors encountered: 1
Duplicates skipped: 0
Total files scanned: 5
==================================================
```

## Testing Requirements

### Test Scenarios
1. **Script execution**: Test that `python main.py` executes without import errors
2. **Startup message display**: Verify message appears before processing
3. **Progress display format**: Check "Processing file X of Y: filename" format
4. **Error display**: Verify error messages for failed files
5. **Summary display**: Check all summary components are shown
6. **Exit codes**: Verify 0 for success, 1 for errors
7. **Keyboard interrupt handling**: Test Ctrl+C behavior

### Mock Requirements
- Mock file system operations for testing
- Mock processing components to simulate success/failure scenarios
- Mock print statements to capture output for verification

### Test Data
- Create temporary directories with sample files
- Use various filename lengths and character sets
- Simulate different processing outcomes (success, error, duplicate)

## User Story References

### Implements
- **SCRIPT_EXEC_T1A2**: Main entry point with `if __name__ == "__main__":` pattern
- **STARTUP_MSG_T3B4**: `TerminalDisplay.show_startup_message()` 
- **PROGRESS_DISP_T5C6**: `TerminalDisplay.show_progress()` with file counter
- **ERROR_DISP_T7D8**: `TerminalDisplay.show_error()` with error logging
- **SUMMARY_DISP_T9E0**: `TerminalDisplay.show_summary()` with processing statistics

### Dependencies
- No external dependencies (all user stories are independent)

### Used by
- This terminal interface will be used by all other processing components for user feedback and error reporting