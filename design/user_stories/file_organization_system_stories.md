# User Stories: File Organization System

**Feature**: File Organization System [FILE_ORG_K1L2]  
**Status**: IMPLEMENTED - Updated from "moves" to "copies" files  
**Dependencies**: Receipt Image Processing [RECEIPT_IMG_E5F6]

## Story 1: Folder Structure Management
**Code**: FOLDER_MGMT_F1A2  
**Status**: IMPLEMENTED
**Functional Description**: Ensures required folder structure exists before processing begins, creating input/ and done/ folders if missing, and validating folder accessibility  
**Acceptance Criteria**:
- When script starts, check if input/ folder exists in project root
- When input/ folder is missing, create input/ folder and continue execution
- When input/ folder creation fails due to permissions, display error "Cannot create input folder: Permission denied" and halt with exit code 1
- When input/ folder creation fails due to disk space, display error "Cannot create input folder: Insufficient disk space" and halt with exit code 1
- When script starts, check if done/ folder exists in project root
- When done/ folder is missing, create done/ folder and continue execution
- When done/ folder creation fails, display error "Cannot create done folder: [specific error]" and halt with exit code 1
- When both folders exist or are successfully created, proceed to file processing
**Technical Notes**: Use os.makedirs() with exist_ok=True, implement proper exception handling for OSError and PermissionError, validate write permissions on created folders  
**Dependencies**: None  
**Data Requirements**: Creates folder structure in project root directory  
**Error Scenarios**: Permission denied, disk space full, file system errors, read-only directories

## Story 2: Processed File Archiving
**Code**: FILE_ARCHIVE_G3B4  
**Status**: IMPLEMENTED
**Functional Description**: Copies processed receipt files to done/ folder with timestamp naming convention and records new filename in CSV for audit trail  
**Acceptance Criteria**:
- When a receipt file is successfully processed, copy file from input/ to done/ folder
- When copying file, generate new filename using format: {ID}-{timestamp}-{original-filename}
- When generating timestamp, use format %Y%m%d-%H%M%S%f (e.g., 20240315-143052123456)
- When file copy operation completes, record new filename (without path) in CSV DoneFilename field
- When copy operation fails due to permissions, display error "Cannot copy file [filename]: Permission denied" and halt with exit code 1
- When copy operation fails due to disk space, display error "Cannot copy file [filename]: Insufficient disk space" and halt with exit code 1
- When copy operation fails for any reason, halt execution and display specific error message
- When original file becomes inaccessible during copy, display error "Cannot read source file [filename]" and halt with exit code 1
**Technical Notes**: Use shutil.copy2() to preserve file metadata, implement ID counter coordination with CSV processing, handle file path construction properly, validate source file exists before copy attempt  
**Dependencies**: Folder Structure Management [FOLDER_MGMT_F1A2]  
**Data Requirements**: Generates new filenames with timestamp, updates CSV DoneFilename field with just the filename (no path)  
**Error Scenarios**: Source file locked/deleted, target disk full, permission errors, corrupted files, network drive failures

## Story 3: File System Operation Error Handling
**Code**: FS_ERROR_HANDLE_H5C6  
**Status**: IMPLEMENTED
**Functional Description**: Provides comprehensive error handling for all file system operations with clear error messages and graceful failure modes  
**Acceptance Criteria**:
- When any file system operation fails, display specific error message indicating the operation and reason
- When folder creation fails, include folder name and specific error in message format: "Cannot create [folder] folder: [error details]"
- When file copy fails, include source filename and specific error in message format: "Cannot copy file [filename]: [error details]"
- When any critical file system error occurs, halt execution immediately with non-zero exit code
- When error occurs, do not attempt to continue processing remaining files
- When displaying error messages, include enough context for user to understand and resolve the issue
- When file system errors occur, ensure no partial state is left (e.g., partially copied files)
**Technical Notes**: Implement consistent error message formatting, use appropriate exit codes (1 for errors), ensure atomic operations where possible, clean up partial operations on failure  
**Dependencies**: Folder Structure Management [FOLDER_MGMT_F1A2], Processed File Archiving [FILE_ARCHIVE_G3B4]  
**Data Requirements**: No data persistence on errors, maintain clean state  
**Error Scenarios**: Permission changes during execution, disk space exhaustion mid-operation, network drive disconnection, antivirus interference

## Implementation Notes

**Key Changes from Previous Version**:
- Updated from file "moving" to file "copying" operations
- Original files remain in input/ folder for potential re-processing
- All copy operations must complete successfully or halt execution

**Integration Points**:
- Coordinates with CSV processing for ID generation and DoneFilename recording
- Depends on Receipt Image Processing for file identification
- Must complete before next file processing begins

**Performance Considerations**:
- Sequential file copying (not parallel) to maintain ID sequence
- Timestamp precision ensures unique filenames even for rapid processing
- File operations should be atomic to prevent partial states

**Implementation Reference**: design/implementation/file_organization_implementation_spec.md