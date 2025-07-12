# File Organization System Implementation Specification

## Package: file_organization
**Path**: `src/file_organization/`
**Purpose**: Shared infrastructure for file system operations including folder management and file archiving
**User Stories**: [FOLDER_MGMT_F1A2], [FILE_ARCHIVE_G3B4], [FS_ERROR_HANDLE_H5C6]
**Dependencies**: Standard library (os, shutil, pathlib, datetime), existing domain exception patterns
**Design Decisions**: Shared infrastructure package providing utilities for file operations with domain exceptions that bubble up to terminal interface

## Architecture Overview

```
src/file_organization/
├── __init__.py
├── domain/
│   ├── __init__.py
│   ├── exceptions/
│   │   ├── __init__.py
│   │   └── file_organization_errors.py
│   └── models/
│       ├── __init__.py
│       └── archive_result.py
├── infrastructure/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── file_organization_config.py
│   └── services/
│       ├── __init__.py
│       ├── folder_manager.py
│       └── file_archiver.py
└── application/
    ├── __init__.py
    └── file_organization_facade.py
```

## Component Details

### Domain Layer

#### Exception Definitions
**File**: `src/file_organization/domain/exceptions/file_organization_errors.py`
**Purpose**: Domain-specific exceptions for file organization operations
**Libraries**: Standard library only
**Design Pattern**: Domain exception hierarchy extending from base domain exception

**Interface Contracts**:
```python
class FileOrganizationError(Exception):
    """Base exception for file organization operations."""
    def __init__(self, message: str, operation: str = None)

class FolderCreationError(FileOrganizationError):
    """Raised when folder creation fails."""
    def __init__(self, folder_path: str, reason: str)

class FileCopyError(FileOrganizationError):
    """Raised when file copy operation fails."""
    def __init__(self, source_path: str, target_path: str, reason: str)

class FileAccessError(FileOrganizationError):
    """Raised when file access validation fails."""
    def __init__(self, file_path: str, operation: str, reason: str)
```

**Error Handling Strategy**: Each exception includes specific context (paths, operations, reasons) for detailed error reporting
**User Story References**: [FS_ERROR_HANDLE_H5C6]

#### Archive Result Model
**File**: `src/file_organization/domain/models/archive_result.py`
**Purpose**: Value object representing the result of file archiving operation
**Libraries**: dataclasses, datetime
**Design Pattern**: Value object with immutable properties

**Interface Contracts**:
```python
@dataclass(frozen=True)
class ArchiveResult:
    """Result of file archiving operation."""
    source_filename: str
    archived_filename: str
    archive_timestamp: datetime
    file_id: int
    
    def get_done_filename(self) -> str:
        """Returns filename for CSV DoneFilename field."""
```

**User Story References**: [FILE_ARCHIVE_G3B4]

### Infrastructure Layer

#### Configuration
**File**: `src/file_organization/infrastructure/config/file_organization_config.py`
**Purpose**: Configuration constants and paths for file organization operations
**Libraries**: pathlib
**Design Pattern**: Configuration module following existing project pattern

**Interface Contracts**:
```python
# Folder paths
DEFAULT_INPUT_FOLDER: Path
DEFAULT_DONE_FOLDER: Path
PROJECT_ROOT: Path

# Timestamp format
ARCHIVE_TIMESTAMP_FORMAT: str = "%Y%m%d-%H%M%S%f"

# Error message templates
FOLDER_CREATION_ERROR_TEMPLATE: str
FILE_COPY_ERROR_TEMPLATE: str
FILE_ACCESS_ERROR_TEMPLATE: str
```

**Configuration Structure**: Follows existing config pattern with constants for paths and error message templates
**User Story References**: [FOLDER_MGMT_F1A2], [FILE_ARCHIVE_G3B4], [FS_ERROR_HANDLE_H5C6]

#### Folder Manager Service
**File**: `src/file_organization/infrastructure/services/folder_manager.py`
**Purpose**: Handles folder creation and validation operations
**Libraries**: os, pathlib
**Design Pattern**: Service class with single responsibility for folder operations

**Interface Contracts**:
```python
class FolderManager:
    """Manages folder creation and validation for file organization."""
    
    def __init__(self, project_root: Path = None)
    
    def ensure_folder_structure(self) -> None:
        """Ensures input/ and done/ folders exist, creates if missing.
        
        Raises:
            FolderCreationError: If folder creation fails for any reason
        """
    
    def validate_folder_permissions(self, folder_path: Path) -> None:
        """Validates write permissions on folder.
        
        Args:
            folder_path: Path to folder to validate
            
        Raises:
            FileAccessError: If folder is not writable
        """
    
    def _create_folder_if_missing(self, folder_path: Path) -> None:
        """Creates folder if it doesn't exist with proper error handling."""
```

**Key Algorithms**: Uses os.makedirs() with exist_ok=True, comprehensive exception handling for OSError subtypes
**Error Handling**: Catches specific exceptions (PermissionError, OSError) and converts to domain exceptions
**User Story References**: [FOLDER_MGMT_F1A2]

#### File Archiver Service
**File**: `src/file_organization/infrastructure/services/file_archiver.py`
**Purpose**: Handles file copying operations with timestamp naming
**Libraries**: shutil, datetime, pathlib
**Design Pattern**: Service class responsible for file archiving operations

**Interface Contracts**:
```python
class FileArchiver:
    """Handles file archiving operations with timestamp naming."""
    
    def __init__(self, done_folder: Path = None)
    
    def archive_file(self, source_path: Path, file_id: int) -> ArchiveResult:
        """Copies file to done folder with timestamp naming.
        
        Args:
            source_path: Path to source file
            file_id: Unique ID for filename generation
            
        Returns:
            ArchiveResult with archiving details
            
        Raises:
            FileAccessError: If source file is not readable
            FileCopyError: If copy operation fails
        """
    
    def _generate_archive_filename(self, original_filename: str, file_id: int, timestamp: datetime) -> str:
        """Generates archive filename with format: {ID}-{timestamp}-{original}."""
    
    def _validate_source_file(self, source_path: Path) -> None:
        """Validates source file exists and is readable."""
    
    def _perform_copy_operation(self, source_path: Path, target_path: Path) -> None:
        """Performs atomic copy operation with error handling."""
```

**Key Algorithms**: 
- Timestamp generation using datetime.now() with microsecond precision
- shutil.copy2() for metadata preservation
- Atomic copy operations with validation

**Performance Considerations**: Sequential operations to maintain ID sequence, timestamp precision prevents filename conflicts
**User Story References**: [FILE_ARCHIVE_G3B4]

### Application Layer

#### File Organization Facade
**File**: `src/file_organization/application/file_organization_facade.py`
**Purpose**: Coordinating facade providing simplified interface for file organization operations
**Libraries**: Internal domain and infrastructure components
**Design Pattern**: Facade pattern for simplified external interface

**Interface Contracts**:
```python
class FileOrganizationFacade:
    """Facade for file organization operations."""
    
    def __init__(self, project_root: Path = None)
    
    def initialize_folder_structure(self) -> None:
        """Initializes required folder structure.
        
        Raises:
            FolderCreationError: If folder creation fails
        """
    
    def archive_processed_file(self, source_path: Path, file_id: int) -> ArchiveResult:
        """Archives a processed file with proper naming.
        
        Args:
            source_path: Path to file to archive
            file_id: Unique ID for the file
            
        Returns:
            ArchiveResult containing archive details
            
        Raises:
            FileAccessError: If source file cannot be accessed
            FileCopyError: If copy operation fails
        """
```

**Integration Points**: 
- Used by batch processing workflow for file archiving
- Integrates with CSV service for DoneFilename recording
- Error handling bubbles up to terminal interface

**User Story References**: All stories - provides unified interface

## Technical Specifications

### Exception Flow Architecture
```
File Organization Services
    ↓ (Domain Exceptions)
File Organization Facade  
    ↓ (Domain Exceptions)
Terminal Interface
    ↓ (Error Display + Exit)
System Exit with Code 1
```

### Integration with Existing Services

#### CSV Output Integration
- FileOrganizationFacade.archive_processed_file() returns ArchiveResult
- ArchiveResult.get_done_filename() provides value for CSV DoneFilename field
- CSV service calls file organization after successful AI extraction

#### Terminal Interface Integration
- Terminal interface catches FileOrganizationError exceptions
- Error handler displays formatted error messages
- System exits with code 1 on any file organization error

#### Batch Processing Integration
- Workflow calls initialize_folder_structure() before processing begins
- For each file: calls archive_processed_file() after successful processing
- File organization operations are sequential to maintain ID sequence

### Configuration Integration
- Inherits project root detection from existing config patterns
- Uses consistent error message formatting with existing services
- Folder paths configurable but default to project standard

### Security Measures
- Path validation to prevent directory traversal
- Permission checking before operations
- Atomic copy operations to prevent partial states
- Input validation for file paths and IDs

### Performance Considerations
- Sequential operations maintain ID sequence requirements
- Timestamp precision (microseconds) ensures unique filenames
- Minimal memory footprint with Path objects
- Early validation reduces partial operation failures

## Testing Requirements

### Unit Testing Strategy
- Test each service class independently with mocked file system
- Test exception scenarios for all error conditions in acceptance criteria
- Test filename generation with various inputs and edge cases
- Test configuration loading and path resolution

### Integration Testing Requirements
- Test complete folder structure creation with real file system
- Test file copying with actual files of different sizes
- Test error scenarios with permission restrictions
- Test integration with existing CSV and terminal services

### Test Data Requirements
- Mock file system structures for unit tests
- Sample receipt files for integration tests
- Error simulation utilities for exception testing
- Temporary directory fixtures for safe testing

## Implementation Priority

1. **Domain Exceptions** - Foundation for error handling
2. **Configuration** - Required by all other components  
3. **Folder Manager** - Prerequisite for file operations
4. **File Archiver** - Core file copying functionality
5. **Application Facade** - Integration interface
6. **Integration Tests** - Validate complete workflow

## Dependencies and Integration Points

### Internal Dependencies
- Existing domain exception patterns
- Terminal interface error handling
- CSV output service integration
- Batch processing workflow coordination

### External Dependencies
- Standard library only (os, shutil, pathlib, datetime)
- No third-party dependencies required

### Integration Sequence
1. Create file organization package structure
2. Implement domain exceptions and models
3. Implement infrastructure services
4. Implement application facade
5. Update batch processing workflow to use facade
6. Update CSV service to use ArchiveResult
7. Update terminal interface error handling