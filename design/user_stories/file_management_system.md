# User Stories: File Management System

**Feature Code**: FILE_MGMT_B7C4  
**Feature Description**: Complete file organization system managing the four-folder structure (incoming, scanned, imported, failed) with proper naming conventions and persistence rules.

## Story 1: Four-Folder Structure Management and Validation
**Code**: FOLDER_MGMT_A8D2  
**Status**: NEW  
**Functional Description**: Manages the complete four-folder structure with automatic creation, validation, and persistence rules enforcement for the receipt processing workflow.

**Acceptance Criteria**:
- When system starts, automatically create missing folders (incoming, scanned, imported, failed) if they don't exist
- When analysis begins, clear scanned folder completely while preserving other folders
- When system checks folder structure, validate all four folders exist and are writable
- When folder creation fails due to permissions, return error code FOLDER_PERMISSION_DENIED with folder path
- When folder is not writable, return error code FOLDER_NOT_WRITABLE with folder path
- When incoming folder is missing files, system continues without error
- When imported folder contains files, preserve all files permanently
- When failed folder contains files, preserve all files permanently

**Technical Notes**: Use pathlib for cross-platform compatibility, implement folder validation before any file operations, handle permission and disk space errors gracefully

**Dependencies**: None  

**Data Requirements**: Folder paths from configuration, folder existence and permission validation

**Error Scenarios**: FOLDER_PERMISSION_DENIED, DISK_SPACE_FULL, INVALID_PATH, FOLDER_CREATION_FAILED

## Story 2: File Movement and Naming Convention Pipeline  
**Code**: FILE_MOVEMENT_B9E3  
**Status**: NEW  
**Functional Description**: Handles file movement between folders during processing with proper naming conventions and copying vs moving rules based on folder persistence requirements.

**Acceptance Criteria**:
- When moving file from incoming to scanned, copy file (preserve original) and apply naming "{yyyyMMdd}-{description}.{ext}"
- When moving file from scanned to imported, move file (remove from source) and apply naming "{number}-{yyyyMMdd}-{description}.{ext}"
- When moving file to failed folder, copy file (preserve original) with original filename
- When description contains non-latin characters, convert to closest latin equivalents or remove
- When description exceeds 15 characters, truncate to 15 characters
- When description contains filesystem-unsafe characters, replace with underscores
- When file move/copy fails due to file lock, return error code FILE_LOCKED with filename
- When target file already exists, return error code FILE_EXISTS with target filename
- When source file doesn't exist, return error code FILE_NOT_FOUND with source filename

**Technical Notes**: Implement character transliteration for non-latin characters, use shutil for file operations, validate target paths before operations

**Dependencies**: FOLDER_MGMT_A8D2

**Data Requirements**: Source and target file paths, date extraction from filenames or metadata, sequential numbering for imported files

**Error Scenarios**: FILE_LOCKED, FILE_PERMISSION_DENIED, DISK_SPACE_FULL, FILE_EXISTS, FILE_NOT_FOUND

## Story 3: File Hash Generation and Duplicate Detection Support
**Code**: FILE_HASH_C7F4  
**Status**: NEW  
**Functional Description**: Provides on-demand SHA-256 hash generation for files to support duplicate detection across folders and sessions, with error handling for corrupted files.

**Acceptance Criteria**:
- When hash is requested for a file, generate SHA-256 hash and return as hexadecimal string
- When file is unreadable, return error code FILE_UNREADABLE with filename and system error details
- When file is corrupted during reading, return error code FILE_CORRUPTED with filename
- When file doesn't exist, return error code FILE_NOT_FOUND with filename
- When multiple hash requests for same file, generate fresh hash each time (no caching)
- When hash generation succeeds, return 64-character hexadecimal string
- When file has zero bytes, return hash of empty content
- When file is very large, process in chunks without memory overflow

**Technical Notes**: Use hashlib.sha256(), read files in chunks to handle large files, don't cache hashes to ensure current file state

**Dependencies**: None

**Data Requirements**: File paths, binary file content reading capability

**Error Scenarios**: FILE_NOT_FOUND, FILE_PERMISSION_DENIED, FILE_CORRUPTED, DISK_IO_ERROR, MEMORY_INSUFFICIENT

## Story 4: Description Cleaning and Filesystem Safety
**Code**: DESC_CLEAN_D5G6  
**Status**: NEW  
**Functional Description**: Cleans and formats file descriptions for use in filenames, ensuring filesystem compatibility and proper length constraints while preserving readability.

**Acceptance Criteria**:
- When description contains non-latin characters (ñ, ü, é, etc.), convert to latin equivalents (n, u, e, etc.)
- When description contains unsafe filesystem characters (/, \, :, *, ?, ", <, >, |), replace with underscores
- When description exceeds 15 characters, truncate to exactly 15 characters
- When description has leading/trailing whitespace, trim whitespace before processing  
- When description is empty or only whitespace, use "unknown" as default
- When description contains multiple consecutive spaces or underscores, collapse to single underscore
- When description ends up as only underscores after cleaning, use "document" as fallback
- When processing succeeds, return cleaned description exactly as it will appear in filename

**Technical Notes**: Implement character mapping table for common non-latin characters, use regex for unsafe character detection, ensure consistent behavior across platforms

**Dependencies**: None

**Data Requirements**: Raw description strings, character mapping rules, filesystem safety rules

**Error Scenarios**: None expected - function should always return a valid description

## Implementation Notes

### Folder Structure Rules
- **Incoming**: Never cleared automatically, allows reprocessing
- **Scanned**: Cleared at start of analysis, populated during processing  
- **Imported**: Persistent storage, never cleared automatically
- **Failed**: Persistent storage with error logs, never cleared automatically

### File Operation Patterns
- **Incoming → Scanned**: Copy (preserve original)
- **Scanned → Imported**: Move (final destination)
- **Any → Failed**: Copy (preserve original for retry)

### Naming Conventions
- **Scanned**: `{yyyyMMdd}-{description}.{ext}`
- **Imported**: `{number}-{yyyyMMdd}-{description}.{ext}`
- **Failed**: Original filename preserved

### Error Reporting Strategy
All file operations should return structured error codes with relevant context data that dependent components can interpret and convert to appropriate user feedback.

### Error Code Definitions
- **FOLDER_PERMISSION_DENIED**: Cannot create or access folder due to permissions
- **FOLDER_NOT_WRITABLE**: Folder exists but is not writable
- **FOLDER_CREATION_FAILED**: General folder creation failure
- **FILE_LOCKED**: File is locked by another process
- **FILE_EXISTS**: Target file already exists
- **FILE_NOT_FOUND**: Source file does not exist
- **FILE_UNREADABLE**: File exists but cannot be read
- **FILE_CORRUPTED**: File corruption detected during operation
- **FILE_PERMISSION_DENIED**: Permission denied for file operation
- **DISK_SPACE_FULL**: Insufficient disk space for operation
- **DISK_IO_ERROR**: General disk I/O error
- **INVALID_PATH**: Invalid file or folder path
- **MEMORY_INSUFFICIENT**: Insufficient memory for operation