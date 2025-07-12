# One-Off Processing Mode User Stories

## Feature Overview
**Feature**: One-Off Processing Mode  
**Code**: ONEOFF_PROC_C3D4  
**Description**: Implements one-off processing runs that clear the done folder and remove receipts.csv at the start of each execution. Keeps the input folder intact, allowing users to re-run the script multiple times on the same receipt files.  
**Dependencies**: Hard - Terminal Script Interface [TERMINAL_UI_A1B2]

## User Stories

### Story 1: Done Folder Cleanup
**Status**: IMPLEMENTED
**Code**: DONE_FOLDER_CLEANUP_X1Y2  
**Functional Description**: Automatically clears all files from the done folder at the beginning of script execution to ensure clean processing runs without accumulating previously processed files.  
**Acceptance Criteria**:
- Script clears all files and subdirectories from done folder at start of execution
- If done folder doesn't exist, operation silently succeeds (no error)
- Cleanup happens before any receipt processing begins
- Operation is silent - no console output about cleanup activities
- All file types are removed from done folder (images, PDFs, etc.)
- Subdirectories within done folder are also removed

**Technical Notes**: Use Python's shutil.rmtree() for directory cleanup, handle FileNotFoundError gracefully  
**Dependencies**: None  
**Data Requirements**: Access to done folder path, ability to delete files and directories  
**Error Scenarios**: Files in use by other processes (handled in Story 3), permission errors, disk full scenarios

### Story 2: CSV File Removal
**Status**: IMPLEMENTED
**Code**: CSV_FILE_REMOVAL_Z3A4  
**Functional Description**: Removes the receipts.csv file at the beginning of script execution to start with a clean CSV output file for each processing run.  
**Acceptance Criteria**:
- Script removes receipts.csv file at start of execution
- If receipts.csv doesn't exist, operation silently succeeds (no error)
- Removal happens before any receipt processing begins
- Operation is silent - no console output about file removal
- Only removes receipts.csv, not other CSV files that might exist

**Technical Notes**: Use Python's os.remove() with proper exception handling for FileNotFoundError  
**Dependencies**: None  
**Data Requirements**: Access to receipts.csv file path  
**Error Scenarios**: File in use by other processes (handled in Story 3), permission errors

### Story 3: Cleanup Error Handling
**Status**: IMPLEMENTED
**Code**: CLEANUP_ERROR_HANDLE_B5C6  
**Functional Description**: Handles file-in-use errors during cleanup operations and terminates script execution gracefully with appropriate error messages when files cannot be cleaned up.  
**Acceptance Criteria**:
- Detects when files in done folder are in use by other processes
- Detects when receipts.csv is in use by other processes  
- Displays clear error message indicating which file(s) are in use
- Terminates script execution immediately when cleanup fails
- Does not proceed with receipt processing if cleanup fails
- Error message format: "Error: [filename] is currently in use by another process"

**Technical Notes**: Catch PermissionError and OSError exceptions, provide specific error messages, use sys.exit() for termination  
**Dependencies**: Done Folder Cleanup [DONE_FOLDER_CLEANUP_X1Y2], CSV File Removal [CSV_FILE_REMOVAL_Z3A4]  
**Data Requirements**: Exception handling for file operations  
**Error Scenarios**: Multiple files in use simultaneously, partial cleanup success before failure, permission denied errors

### Story 4: Main Script Integration
**Status**: IMPLEMENTED
**Code**: CLEANUP_MAIN_INTEGRATION_M7N8  
**Functional Description**: Integrates cleanup functionality into the main script execution flow to ensure cleanup operations run automatically when the script starts.  
**Acceptance Criteria**:
- CleanupManager is instantiated in main.py at script startup
- Cleanup operations execute immediately after startup message display
- Cleanup operations complete before any receipt processing begins
- Uses standard folder paths: "done" folder and "receipts.csv" file
- Integration follows existing main.py structure and patterns
- No console output during successful cleanup operations

**Technical Notes**: Import CleanupManager, instantiate with default paths, call execute_cleanup() in main() function  
**Dependencies**: Done Folder Cleanup [DONE_FOLDER_CLEANUP_X1Y2], CSV File Removal [CSV_FILE_REMOVAL_Z3A4], Cleanup Error Handling [CLEANUP_ERROR_HANDLE_B5C6]  
**Data Requirements**: Access to main.py execution flow  
**Error Scenarios**: Import errors, initialization failures, cleanup operation failures

## Implementation Notes
- All cleanup operations must complete successfully before any receipt processing begins
- Operations are performed silently unless errors occur
- The input folder is never modified by this feature
- Cleanup order: done folder first, then receipts.csv
- Script termination on error prevents incomplete processing states

## Integration Points
- Must integrate with Terminal Script Interface for error display
- Must execute before any other processing components start
- Must not interfere with folder creation logic in File Organization System

## Implementation Design Index
| User Story | Package | Implementation File | Status |
|------------|---------|-------------------|--------|
| DONE_FOLDER_CLEANUP_X1Y2 | cleanup | cleanup_implementation_spec.md | **IMPLEMENTED** |
| CSV_FILE_REMOVAL_Z3A4 | cleanup | cleanup_implementation_spec.md | **IMPLEMENTED** |
| CLEANUP_ERROR_HANDLE_B5C6 | cleanup | cleanup_implementation_spec.md | **IMPLEMENTED** |
| CLEANUP_MAIN_INTEGRATION_M7N8 | terminal_interface | terminal_interface_implementation_spec.md | **IMPLEMENTED** |

## User Story Implementation References

### Story 1: Done Folder Cleanup
**Implementation Design**: 
- Package: cleanup (see cleanup_implementation_spec.md)
- Modules: cleanup.cleaner.CleanupManager._clear_done_folder()
- Dependencies: None
- Dependents: CLEANUP_ERROR_HANDLE_B5C6

### Story 2: CSV File Removal
**Implementation Design**: 
- Package: cleanup (see cleanup_implementation_spec.md)
- Modules: cleanup.cleaner.CleanupManager._remove_csv_file()
- Dependencies: None
- Dependents: CLEANUP_ERROR_HANDLE_B5C6

### Story 3: Cleanup Error Handling
**Implementation Design**: 
- Package: cleanup (see cleanup_implementation_spec.md)
- Modules: cleanup.cleaner.CleanupManager._handle_cleanup_error()
- Dependencies: DONE_FOLDER_CLEANUP_X1Y2, CSV_FILE_REMOVAL_Z3A4
- Dependents: CLEANUP_MAIN_INTEGRATION_M7N8

### Story 4: Main Script Integration
**Implementation Design**: 
- Package: terminal_interface (see terminal_interface_implementation_spec.md)
- Modules: terminal_interface.main.main()
- Dependencies: DONE_FOLDER_CLEANUP_X1Y2, CSV_FILE_REMOVAL_Z3A4, CLEANUP_ERROR_HANDLE_B5C6
- Dependents: None

## Complete Feature Implementation Results

### Feature Summary
- **Feature Name**: One-Off Processing Mode
- **Feature Code**: ONEOFF_PROC_C3D4
- **Stories Implemented**: DONE_FOLDER_CLEANUP_X1Y2, CSV_FILE_REMOVAL_Z3A4, CLEANUP_ERROR_HANDLE_B5C6, CLEANUP_MAIN_INTEGRATION_M7N8
- **Implementation Status**: **COMPLETED**

### Files Created
```
src/cleanup/
├── __init__.py                # Package initialization and public API
├── cleaner.py                 # Core CleanupManager class implementation
└── config.py                  # Configuration constants

tests/unit/test_cleanup/
├── __init__.py                # Test package initialization
└── test_cleaner.py            # Comprehensive unit tests

tests/integration/
├── __init__.py                # Integration test package initialization
└── test_cleanup_integration.py # End-to-end integration tests
```

### Architecture
The cleanup package implements a simple, focused approach using the CleanupManager class:
- **CleanupManager**: Main orchestration class
  - `execute_cleanup()`: Entry point that coordinates all cleanup operations
  - `_clear_done_folder()`: Implements done folder cleanup (Story 1)
  - `_remove_csv_file()`: Implements CSV file removal (Story 2)
  - `_handle_cleanup_error()`: Implements error handling (Story 3)

### Public APIs
```python
from cleanup import CleanupManager

# Main public interface
cleanup_manager = CleanupManager(done_folder_path="done", csv_file_path="receipts.csv")
cleanup_manager.execute_cleanup()  # Executes complete cleanup or terminates on error
```

### Integration Points
- **Terminal Script Interface**: Used for error display and script termination
- **Batch Processing Workflow**: Must execute before any processing begins
- **File Organization System**: Does not interfere with folder creation logic

### Test Coverage
- **Unit Tests**: 14 tests covering all acceptance criteria
- **Integration Tests**: 6 tests covering end-to-end workflows
- **Test Categories**: Happy path, error handling, edge cases, silent operation, integration

### All Acceptance Criteria Validation
**Story 1 (DONE_FOLDER_CLEANUP_X1Y2)**: ✅ ALL PASS
- Clears all files and subdirectories from done folder at start
- Silent success if folder doesn't exist
- Silent operation (no console output)
- Removes all file types and subdirectories

**Story 2 (CSV_FILE_REMOVAL_Z3A4)**: ✅ ALL PASS
- Removes receipts.csv file at start of execution
- Silent success if file doesn't exist
- Silent operation (no console output)
- Only removes receipts.csv, not other CSV files

**Story 3 (CLEANUP_ERROR_HANDLE_B5C6)**: ✅ ALL PASS
- Detects files in use in done folder and CSV file
- Displays clear error message with exact format
- Terminates script immediately on cleanup failure
- Does not proceed with processing if cleanup fails

### Feature Validation: ✅ PASS
- **Complete Feature Works**: End-to-end functionality verified through integration tests
- **All Stories Integrated**: Stories work together seamlessly in realistic scenarios
- **Error Handling**: Proper error detection, reporting, and script termination
- **Silent Operation**: No console output during successful operations
- **Cleanup Order**: Done folder first, then CSV file
- **Input Preservation**: Input folder never modified
- **Multiple Runs**: Feature supports repeated execution (one-off runs)

### Implementation Quality
- **Code Standards**: Follows Python coding guidelines and PEP 8
- **Documentation**: Comprehensive docstrings and comments
- **Type Hints**: Full type annotation for all methods
- **Error Handling**: Specific exception handling with clear messages
- **Testing**: 100% acceptance criteria coverage with unit and integration tests
- **Dependencies**: Uses only standard library (no external dependencies)