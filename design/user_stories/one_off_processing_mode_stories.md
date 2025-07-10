# One-Off Processing Mode User Stories

## Feature Overview
**Feature**: One-Off Processing Mode  
**Code**: ONEOFF_PROC_C3D4  
**Description**: Implements one-off processing runs that clear the done folder and remove receipts.csv at the start of each execution. Keeps the input folder intact, allowing users to re-run the script multiple times on the same receipt files.  
**Dependencies**: Hard - Terminal Script Interface [TERMINAL_UI_A1B2]

## User Stories

### Story 1: Done Folder Cleanup
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