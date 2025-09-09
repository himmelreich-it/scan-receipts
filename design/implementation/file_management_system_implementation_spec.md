# Implementation Specification: File Management System

**Feature Code**: FILE_MGMT_B7C4  
**User Stories**: design/user_stories/file_management_system.md  
**Architecture Reference**: design/architecture/component_design.c4 (File System Port & Adapter)

## Package Structure

### Package: file_management
**Path**: `src/file_management/`  
**Purpose**: Complete file organization system managing four-folder structure with proper naming conventions and persistence rules  
**User Stories**: FOLDER_MGMT_A8D2, FILE_MOVEMENT_B9E3, FILE_HASH_C7F4, DESC_CLEAN_D5G6  
**Dependencies**: `pathlib`, `hashlib`, `shutil`, `re`, `unicodedata`  
**Design Decisions**: Result objects for error handling, low-level port operations, loose coupling with folder paths as parameters

## Component Architecture

Following hexagonal architecture from design/architecture/component_design.c4:

### Domain Layer Components
- **File Operation Results**: Value objects representing operation outcomes
- **File Validation Rules**: Business rules for naming conventions and filesystem safety

### Application Layer Interface  
- **File System Port**: Abstract interface defining file operations contract

### Infrastructure Layer Implementation
- **File System Adapter**: Concrete implementation of file operations using pathlib and system APIs

## Technical Specifications

### File System Port Interface

**File Location**: `src/file_management/ports.py`  
**Purpose**: Abstract interface for file system operations supporting hexagonal architecture  
**Libraries**: `abc`, `pathlib`, `typing`  
**Design Pattern**: Port/Adapter pattern with Result objects

**Interface Definition**:
```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union
from file_management.models import FileOperationResult, HashResult, FolderValidationResult

class FileSystemPort(ABC):
    
    @abstractmethod
    def ensure_folder_exists(self, folder_path: Path) -> FolderValidationResult:
        """Create folder if missing, validate permissions."""
        
    @abstractmethod
    def clear_folder(self, folder_path: Path) -> FileOperationResult:
        """Remove all contents from folder."""
        
    @abstractmethod 
    def copy_file(self, source_path: Path, target_path: Path) -> FileOperationResult:
        """Copy file from source to target location."""
        
    @abstractmethod
    def move_file(self, source_path: Path, target_path: Path) -> FileOperationResult:
        """Move file from source to target location."""
        
    @abstractmethod
    def generate_file_hash(self, file_path: Path) -> HashResult:
        """Generate SHA-256 hash for file content."""
        
    @abstractmethod
    def list_files(self, folder_path: Path, pattern: str = "*") -> list[Path]:
        """List files in folder matching optional pattern."""
```

### Domain Models and Results

**File Location**: `src/file_management/models.py`  
**Purpose**: Data models and result objects for file operations  
**Libraries**: `dataclasses`, `pathlib`, `typing`, `enum`  
**Design Pattern**: Value objects with immutable data and built-in validation

**Result Types**:
```python
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from enum import Enum

class FileErrorCode(Enum):
    # Folder errors
    FOLDER_PERMISSION_DENIED = "FOLDER_PERMISSION_DENIED"
    FOLDER_NOT_WRITABLE = "FOLDER_NOT_WRITABLE" 
    FOLDER_CREATION_FAILED = "FOLDER_CREATION_FAILED"
    
    # File errors
    FILE_LOCKED = "FILE_LOCKED"
    FILE_EXISTS = "FILE_EXISTS"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_UNREADABLE = "FILE_UNREADABLE"
    FILE_CORRUPTED = "FILE_CORRUPTED"
    FILE_PERMISSION_DENIED = "FILE_PERMISSION_DENIED"
    
    # System errors
    DISK_SPACE_FULL = "DISK_SPACE_FULL"
    DISK_IO_ERROR = "DISK_IO_ERROR"
    INVALID_PATH = "INVALID_PATH"
    MEMORY_INSUFFICIENT = "MEMORY_INSUFFICIENT"

@dataclass(frozen=True)
class FileOperationResult:
    success: bool
    error_code: Optional[FileErrorCode] = None
    error_message: Optional[str] = None
    file_path: Optional[Path] = None

@dataclass(frozen=True) 
class HashResult:
    success: bool
    hash_value: Optional[str] = None
    error_code: Optional[FileErrorCode] = None
    error_message: Optional[str] = None
    file_path: Optional[Path] = None

@dataclass(frozen=True)
class FolderValidationResult:
    success: bool
    folder_path: Path
    exists: bool = False
    is_writable: bool = False
    error_code: Optional[FileErrorCode] = None
    error_message: Optional[str] = None
```

### File Description Utilities

**File Location**: `src/file_management/utils.py`  
**Purpose**: Utility functions for filename cleaning and validation  
**Libraries**: `re`, `unicodedata`  
**User Story**: DESC_CLEAN_D5G6

**Key Functions**:
```python
def clean_description(description: str) -> str:
    """Clean description for filesystem compatibility.
    
    Implements business rules:
    - Convert non-latin characters to latin equivalents
    - Replace unsafe filesystem characters with underscores
    - Truncate to 15 characters maximum
    - Handle whitespace and provide fallbacks
    
    Args:
        description: Raw description string
        
    Returns:
        Cleaned description ready for filename use
    """

def is_valid_filename_character(char: str) -> bool:
    """Check if character is safe for filesystem usage."""
    
def transliterate_unicode(text: str) -> str:
    """Convert unicode characters to closest latin equivalents."""
```

### File System Adapter Implementation

**File Location**: `src/file_management/adapters.py`  
**Purpose**: Concrete implementation of File System Port using pathlib and system APIs  
**Libraries**: `pathlib`, `hashlib`, `shutil`, `logging`, `os`  
**Design Pattern**: Adapter pattern implementing port interface  
**User Stories**: FOLDER_MGMT_A8D2, FILE_MOVEMENT_B9E3, FILE_HASH_C7F4

**Key Implementation Aspects**:
- **Chunk-based hash generation**: Process large files in 64KB chunks to prevent memory issues
- **Comprehensive error mapping**: Map system exceptions to domain error codes
- **Atomic operations**: Ensure file operations are completed successfully or rolled back
- **Permission validation**: Check folder permissions before attempting operations

**Error Handling Strategy**: 
- Catch specific filesystem exceptions (PermissionError, FileNotFoundError, OSError)
- Map to domain error codes for consistent handling across use cases
- Include system error details in error messages for debugging
- Never raise exceptions - always return Result objects

### Integration with Configuration System

**Configuration Dependency**: Loose coupling through dependency injection  
**Integration Point**: Use cases receive folder paths from Configuration Port and pass to File System Port methods  
**No direct configuration dependency**: File System Adapter remains testable and flexible

## BDD Test Scenarios

### Feature Files Created

**tests/bdd/features/file_management_folder_structure.feature**
```gherkin
Feature: Four-Folder Structure Management and Validation
  As a receipt processing system
  I want to manage a complete four-folder structure 
  So that files are properly organized through the processing workflow

  Background:
    Given the system is configured with test folder paths
    And I have file system permissions

  Scenario: Create missing folders automatically
    Given the folders "incoming", "scanned", "imported", "failed" do not exist
    When I ensure folder structure exists
    Then all four folders should be created successfully
    And each folder should be writable

  Scenario: Clear scanned folder while preserving others
    Given all folders exist with test files
    When I begin analysis workflow
    Then the scanned folder should be empty
    And the "incoming", "imported", "failed" folders should retain their files

  Scenario Outline: Handle folder permission errors
    Given folder "<folder_name>" cannot be created due to permissions
    When I try to ensure folder structure
    Then I should receive error code "FOLDER_PERMISSION_DENIED"
    And the error should include the folder path

    Examples:
      | folder_name |
      | incoming    |
      | scanned     |
      | imported    |
      | failed      |
```

**tests/bdd/features/file_management_operations.feature**  
```gherkin
Feature: File Movement and Naming Convention Pipeline
  As a receipt processing system
  I want to move files between folders with proper naming
  So that files follow the correct workflow and naming conventions

  Background:
    Given all folders exist and are writable
    And I have a test receipt file "test_receipt.pdf"

  Scenario: Copy file from incoming to scanned
    Given a file exists in incoming folder
    When I copy the file to scanned folder with name "20231215-grocery_store.pdf"
    Then the file should exist in both incoming and scanned folders
    And the scanned file should have the exact name "20231215-grocery_store.pdf"

  Scenario: Move file from scanned to imported  
    Given a file exists in scanned folder named "20231215-grocery_store.pdf"
    When I move the file to imported folder with name "001-20231215-grocery_store.pdf"
    Then the file should exist only in imported folder
    And the imported file should have the exact name "001-20231215-grocery_store.pdf"

  Scenario Outline: Handle file operation errors
    Given a file operation encounters "<error_condition>"
    When I attempt the file operation
    Then I should receive error code "<error_code>"
    
    Examples:
      | error_condition | error_code           |
      | file locked     | FILE_LOCKED          |
      | target exists   | FILE_EXISTS          |
      | source missing  | FILE_NOT_FOUND       |
      | no permission   | FILE_PERMISSION_DENIED |
```

**tests/bdd/features/file_management_hash_generation.feature**
```gherkin
Feature: File Hash Generation and Duplicate Detection Support
  As a receipt processing system
  I want to generate SHA-256 hashes for files
  So that duplicate detection can be performed across folders and sessions

  Background:
    Given I have test files with known content

  Scenario: Generate hash for normal file
    Given a file "test_receipt.pdf" with known content
    When I generate a hash for the file
    Then I should receive a 64-character hexadecimal string
    And the hash should match the expected SHA-256 value

  Scenario: Generate hash for empty file
    Given an empty file "empty.txt"
    When I generate a hash for the file
    Then I should receive the SHA-256 hash of empty content
    And the operation should succeed

  Scenario Outline: Handle hash generation errors
    Given a file with "<error_condition>"
    When I try to generate a hash
    Then I should receive error code "<error_code>"
    
    Examples:
      | error_condition | error_code        |
      | file not found  | FILE_NOT_FOUND    |
      | file unreadable | FILE_UNREADABLE   |
      | file corrupted  | FILE_CORRUPTED    |
      | no permission   | FILE_PERMISSION_DENIED |
```

**tests/bdd/features/file_management_description_cleaning.feature**
```gherkin  
Feature: Description Cleaning and Filesystem Safety
  As a receipt processing system
  I want to clean file descriptions for filesystem compatibility
  So that filenames are safe across different operating systems

  Scenario Outline: Convert non-latin characters
    Given a description with text "<input_text>"
    When I clean the description
    Then the result should be "<expected_output>"
    
    Examples:
      | input_text        | expected_output |
      | Café André        | Cafe Andre      |
      | Müller & Söhne    | Muller & Sohne  |
      | Niño's Restaurant | Nino's Restaurant |

  Scenario Outline: Replace unsafe filesystem characters
    Given a description with text "<input_text>"  
    When I clean the description
    Then the result should be "<expected_output>"
    
    Examples:
      | input_text    | expected_output |
      | File/Name     | File_Name      |
      | Test:File     | Test_File      |
      | Name<>File    | Name__File     |

  Scenario: Truncate long descriptions
    Given a description "This is a very long description that exceeds fifteen characters"
    When I clean the description
    Then the result should be exactly 15 characters long
    And it should be "This is a very "

  Scenario Outline: Handle edge cases
    Given a description with text "<input_text>"
    When I clean the description  
    Then the result should be "<expected_output>"
    
    Examples:
      | input_text | expected_output |
      | ""         | unknown         |
      | "   "      | unknown         |
      | "  test  " | test            |
```

### BDD Test Data Requirements
- **Test files**: Various file formats (PDF, JPG, PNG) with different sizes
- **Folder structures**: Temporary test directories for each scenario
- **Unicode test data**: Non-latin characters for description cleaning tests
- **Error simulation**: Mock filesystem conditions for error scenarios

### Step Definition Interfaces
```python
# Expected step definition signatures for implementation

@given("the system is configured with test folder paths")
def step_given_test_folder_paths(context):
    """Setup test folder configuration"""

@when("I ensure folder structure exists")  
def step_when_ensure_folder_structure(context):
    """Call folder validation through File System Port"""

@then("all four folders should be created successfully")
def step_then_folders_created(context):
    """Verify folder creation success"""

@when("I copy the file to scanned folder with name {filename}")
def step_when_copy_file_to_scanned(context, filename):
    """Execute file copy operation"""

@when("I generate a hash for the file")
def step_when_generate_hash(context):
    """Execute hash generation through port"""
```

## Integration Specifications

### Main Application Entry Point Integration
- **Configuration Loading**: File System Adapter receives folder paths from Configuration Adapter during dependency injection
- **Use Case Wiring**: File System Port injected into use cases that require file operations
- **Error Propagation**: File operation errors flow through use cases to TUI Error Reporter

### CLI Integration Points  
- **No direct CLI integration**: File management operations are triggered by application use cases
- **Status Reporting**: File counts and folder states reported through use cases to TUI Interface

### Initialization Sequence
1. Configuration Adapter loads folder paths from .env
2. File System Adapter created with dependencies
3. File System Port interface injected into relevant use cases
4. Folder structure validation performed at system startup

### Dependency Injection Setup
```python
# Expected wiring in main application
def create_file_system_adapter() -> FileSystemPort:
    return FileSystemAdapter()

def create_process_receipt_use_case(
    file_system: FileSystemPort,
    # ... other dependencies
) -> ProcessReceiptUseCase:
    return ProcessReceiptUseCase(file_system_port=file_system)
```

## Quality Requirements

### Traceability to User Stories
- **FOLDER_MGMT_A8D2**: Implemented by folder validation methods and error handling
- **FILE_MOVEMENT_B9E3**: Implemented by copy/move operations with naming support  
- **FILE_HASH_C7F4**: Implemented by hash generation with chunk processing
- **DESC_CLEAN_D5G6**: Implemented by description cleaning utilities

### Backward Compatibility
- File System Port interface designed for extension without breaking existing use cases
- Result objects provide forward-compatible error handling
- No breaking changes to existing components

### Technical Choices Validation
- **Result objects**: Confirmed for clean error handling without exceptions
- **Low-level operations**: Confirmed for maximum use case control
- **Loose coupling**: Confirmed through dependency injection and parameter passing
- **Complete filename parameters**: Confirmed for simplicity and flexibility

## Implementation Boundaries

### Included in Specification
- **Port interface contracts** with method signatures and Result object types
- **Domain model structure** for file operations and error codes  
- **Adapter architecture** with key implementation approaches
- **Integration patterns** with configuration and use case layers
- **BDD scenarios** covering all acceptance criteria from user stories

### Excluded from Specification  
- **Complete method implementations** (interface contracts provided)
- **Detailed business logic code** (approach described, not implemented)
- **Production-ready error messages** (error structure defined)
- **Full configuration integration code** (dependency injection pattern shown)
- **Complete BDD step implementations** (interfaces and expectations provided)

The specification provides clear guidance for implementing the File Management System while maintaining hexagonal architecture principles and satisfying all user story acceptance criteria.