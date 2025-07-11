# Implementation Specification: Receipt Image Processing

**Feature Code**: RECEIPT_IMG_E5F6  
**User Stories**: INPUT_SCAN_FILTER_A1B2, FILE_READ_PROCESS_C3D4, SEQ_PROCESS_WORKFLOW_E5F6  
**Bounded Context**: Receipt Processing (Core Domain)  

## Package Structure

```
src/
├── receipt_processing/
│   ├── __init__.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── file_path.py           # FilePath value object
│   │   │   ├── file_extension.py      # FileExtension value object  
│   │   │   ├── file_content.py        # FileContent value object
│   │   │   └── processable_file.py    # ProcessableFile entity
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── file_filtering_service.py    # Domain service for filtering
│   │   │   └── file_content_reader.py       # Domain service for reading
│   │   ├── specifications/
│   │   │   ├── __init__.py
│   │   │   └── supported_file_spec.py       # File extension specification
│   │   └── repositories/
│   │       ├── __init__.py
│   │       └── file_system_repository.py    # File system abstraction
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   └── file_processing_config.py    # Hardcoded configuration
│   │   └── adapters/
│   │       ├── __init__.py
│   │       └── local_file_repository.py     # Concrete file system implementation
│   └── application/
│       ├── __init__.py
│       ├── workflows/
│       │   ├── __init__.py
│       │   └── sequential_processing_workflow.py  # Main workflow orchestrator
│       └── dtos/
│           ├── __init__.py
│           └── processing_result.py         # Data transfer objects
```

## Component Details

### Domain Layer

#### Value Objects

**FilePath** (`src/receipt_processing/domain/models/file_path.py`)
```python
@dataclass(frozen=True)
class FilePath:
    path: str
    
    def __post_init__(self):
        if not self.path:
            raise ValueError("File path cannot be empty")
        if not isinstance(self.path, str):
            raise TypeError("File path must be a string")
    
    @property
    def name(self) -> str:
        return os.path.basename(self.path)
    
    @property
    def directory(self) -> str:
        return os.path.dirname(self.path)
    
    def exists(self) -> bool:
        return os.path.exists(self.path)
```

**FileExtension** (`src/receipt_processing/domain/models/file_extension.py`)
```python
@dataclass(frozen=True)
class FileExtension:
    extension: str
    
    def __post_init__(self):
        if not self.extension:
            raise ValueError("File extension cannot be empty")
        # Normalize to lowercase with leading dot
        object.__setattr__(self, 'extension', self.extension.lower())
        if not self.extension.startswith('.'):
            object.__setattr__(self, 'extension', f'.{self.extension}')
    
    def matches(self, other: 'FileExtension') -> bool:
        return self.extension == other.extension
```

**FileContent** (`src/receipt_processing/domain/models/file_content.py`)
```python
@dataclass(frozen=True)
class FileContent:
    data: str  # base64 encoded content
    mime_type: str
    size_bytes: int
    
    def __post_init__(self):
        if not self.data:
            raise ValueError("File content cannot be empty")
        if self.size_bytes < 0:
            raise ValueError("File size cannot be negative")
```

#### Entity

**ProcessableFile** (`src/receipt_processing/domain/models/processable_file.py`)
```python
@dataclass
class ProcessableFile:
    file_path: FilePath
    extension: FileExtension
    content: Optional[FileContent] = None
    processing_status: str = "pending"  # pending, processed, error
    error_message: Optional[str] = None
    processed_at: Optional[datetime] = None
    
    def mark_as_processed(self) -> None:
        self.processing_status = "processed"
        self.processed_at = datetime.now()
    
    def mark_as_error(self, error_message: str) -> None:
        self.processing_status = "error"
        self.error_message = error_message
        self.processed_at = datetime.now()
    
    def is_ready_for_processing(self) -> bool:
        return self.content is not None and self.processing_status == "pending"
```

#### Domain Services

**FileFilteringService** (`src/receipt_processing/domain/services/file_filtering_service.py`)
```python
class FileFilteringService:
    def __init__(self, supported_extensions_spec: SupportedFileExtensionSpecification):
        self.supported_extensions_spec = supported_extensions_spec
    
    def filter_supported_files(self, file_paths: List[FilePath]) -> List[ProcessableFile]:
        processable_files = []
        for file_path in file_paths:
            try:
                extension = FileExtension(os.path.splitext(file_path.path)[1])
                if self.supported_extensions_spec.is_satisfied_by(extension):
                    processable_files.append(ProcessableFile(file_path, extension))
            except ValueError:
                # Skip files with invalid extensions (no console output per requirements)
                continue
        return processable_files
```

**FileContentReader** (`src/receipt_processing/domain/services/file_content_reader.py`)
```python
class FileContentReader:
    def read_file_content(self, processable_file: ProcessableFile) -> None:
        try:
            with open(processable_file.file_path.path, 'rb') as file:
                file_data = file.read()
                base64_content = base64.b64encode(file_data).decode('utf-8')
                mime_type = self._determine_mime_type(processable_file.extension)
                
                content = FileContent(
                    data=base64_content,
                    mime_type=mime_type,
                    size_bytes=len(file_data)
                )
                processable_file.content = content
                
        except (IOError, OSError) as e:
            processable_file.mark_as_error(f"Failed to read file: {str(e)}")
        except MemoryError:
            processable_file.mark_as_error("File too large")
        except Exception as e:
            processable_file.mark_as_error(f"Unexpected error: {str(e)}")
    
    def _determine_mime_type(self, extension: FileExtension) -> str:
        mime_mapping = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png'
        }
        return mime_mapping.get(extension.extension, 'application/octet-stream')
```

#### Specification

**SupportedFileExtensionSpecification** (`src/receipt_processing/domain/specifications/supported_file_spec.py`)
```python
class SupportedFileExtensionSpecification:
    def __init__(self, supported_extensions: List[str]):
        self.supported_extensions = [FileExtension(ext) for ext in supported_extensions]
    
    def is_satisfied_by(self, extension: FileExtension) -> bool:
        return any(ext.matches(extension) for ext in self.supported_extensions)
```

#### Repository Interface

**FileSystemRepository** (`src/receipt_processing/domain/repositories/file_system_repository.py`)
```python
from abc import ABC, abstractmethod

class FileSystemRepository(ABC):
    @abstractmethod
    def list_files_in_directory(self, directory_path: str) -> List[FilePath]:
        pass
    
    @abstractmethod
    def ensure_directory_exists(self, directory_path: str) -> None:
        pass
    
    @abstractmethod
    def directory_exists(self, directory_path: str) -> bool:
        pass
```

### Infrastructure Layer

#### Configuration

**FileProcessingConfig** (`src/receipt_processing/infrastructure/config/file_processing_config.py`)
```python
class FileProcessingConfig:
    # Hardcoded configuration as requested
    SUPPORTED_FILE_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png']
    INPUT_DIRECTORY = 'input'
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        return cls.SUPPORTED_FILE_EXTENSIONS.copy()
    
    @classmethod
    def get_input_directory(cls) -> str:
        return cls.INPUT_DIRECTORY
```

#### Repository Implementation

**LocalFileRepository** (`src/receipt_processing/infrastructure/adapters/local_file_repository.py`)
```python
class LocalFileRepository(FileSystemRepository):
    def list_files_in_directory(self, directory_path: str) -> List[FilePath]:
        if not self.directory_exists(directory_path):
            return []
        
        file_paths = []
        try:
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                if os.path.isfile(item_path):
                    file_paths.append(FilePath(item_path))
        except PermissionError:
            raise PermissionError(f"Permission denied: cannot access {directory_path}")
        
        return file_paths
    
    def ensure_directory_exists(self, directory_path: str) -> None:
        if not self.directory_exists(directory_path):
            try:
                os.makedirs(directory_path, exist_ok=True)
                print(f"Created input folder")
            except PermissionError:
                raise PermissionError(f"Permission denied: cannot create {directory_path}")
    
    def directory_exists(self, directory_path: str) -> bool:
        return os.path.exists(directory_path) and os.path.isdir(directory_path)
```

### Application Layer

#### Data Transfer Objects

**ProcessingResult** (`src/receipt_processing/application/dtos/processing_result.py`)
```python
@dataclass
class ProcessingResult:
    successful_files: List[ProcessableFile]
    failed_files: List[ProcessableFile]
    total_processed: int
    
    @property
    def success_count(self) -> int:
        return len(self.successful_files)
    
    @property
    def error_count(self) -> int:
        return len(self.failed_files)
```

#### Workflow Orchestrator

**SequentialProcessingWorkflow** (`src/receipt_processing/application/workflows/sequential_processing_workflow.py`)
```python
class SequentialProcessingWorkflow:
    def __init__(
        self,
        file_repository: FileSystemRepository,
        filtering_service: FileFilteringService,
        content_reader: FileContentReader
    ):
        self.file_repository = file_repository
        self.filtering_service = filtering_service
        self.content_reader = content_reader
    
    def process_input_directory(self, input_directory: str) -> ProcessingResult:
        # User Story 1: Input folder scanning and filtering
        try:
            self.file_repository.ensure_directory_exists(input_directory)
        except PermissionError as e:
            print(f"Permission denied: cannot access input folder")
            sys.exit(1)
        
        file_paths = self.file_repository.list_files_in_directory(input_directory)
        
        if not file_paths:
            print("No files found in input folder")
            return ProcessingResult([], [], 0)
        
        processable_files = self.filtering_service.filter_supported_files(file_paths)
        
        # User Story 2 & 3: Sequential processing
        successful_files = []
        failed_files = []
        
        try:
            for processable_file in processable_files:
                try:
                    # User Story 2: File content reading
                    self.content_reader.read_file_content(processable_file)
                    
                    if processable_file.processing_status == "error":
                        print(f"File corrupted: {processable_file.file_path.name}")
                        failed_files.append(processable_file)
                    else:
                        # File ready for downstream processing
                        processable_file.mark_as_processed()
                        successful_files.append(processable_file)
                        
                except KeyboardInterrupt:
                    print("Processing interrupted by user")
                    sys.exit(0)
                except Exception as e:
                    processable_file.mark_as_error(f"Processing failed: {str(e)}")
                    print(f"Processing failed for {processable_file.file_path.name}: {str(e)}")
                    failed_files.append(processable_file)
        
        except KeyboardInterrupt:
            print("Processing stopped by user")
            sys.exit(0)
        
        return ProcessingResult(successful_files, failed_files, len(processable_files))
    
    def get_processed_files(self) -> List[ProcessableFile]:
        # Interface for downstream components
        # Returns files ready for AI extraction
        pass
```

## Testing Strategy

### Unit Tests Structure
```
tests/
├── unit/
│   └── test_receipt_processing/
│       ├── test_domain/
│       │   ├── test_models/
│       │   │   ├── test_file_path.py
│       │   │   ├── test_file_extension.py
│       │   │   ├── test_file_content.py
│       │   │   └── test_processable_file.py
│       │   ├── test_services/
│       │   │   ├── test_file_filtering_service.py
│       │   │   └── test_file_content_reader.py
│       │   └── test_specifications/
│       │       └── test_supported_file_spec.py
│       ├── test_infrastructure/
│       │   └── test_adapters/
│       │       └── test_local_file_repository.py
│       └── test_application/
│           └── test_workflows/
│               └── test_sequential_processing_workflow.py
```

### Key Test Approaches
- **Mock file system operations** using `unittest.mock` and `pytest-mock`
- **Temporary directories** for integration-style tests that need actual file I/O
- **Property-based testing** for value object validation
- **Exception testing** for all error scenarios defined in user stories

## Implementation Dependencies

### Required Python Packages
- `base64` (built-in) - for file encoding
- `os` (built-in) - for file operations  
- `dataclasses` (built-in) - for value objects and entities
- `datetime` (built-in) - for timestamps
- `typing` (built-in) - for type hints

### Development Dependencies  
- `pytest` - testing framework
- `pytest-mock` - mocking support
- `mypy` - type checking

## Integration Points

### Downstream Interface
The workflow exposes `ProcessingResult` containing:
- `successful_files`: List of ProcessableFile entities with populated content
- `failed_files`: List of ProcessableFile entities with error information
- File metadata: original filename, path, processing timestamp

### Error Integration
Failed files include structured error information for CSV output:
- File corruption errors
- Permission denied errors  
- Memory errors
- Invalid format errors

## Quality Assurance

### Design Validation Checklist
- ✅ All user story acceptance criteria mapped to specific methods
- ✅ DDD tactical patterns properly implemented
- ✅ Error scenarios explicitly handled with required logging
- ✅ Configuration approach matches technical requirements (hardcoded)
- ✅ Simple method call interface for downstream integration
- ✅ Mock-based testing strategy for reliable unit tests
- ✅ Memory management kept simple as requested (no streaming/caching)
- ✅ Sequential processing with continue-on-error behavior
- ✅ Base64 encoding for Claude API compatibility

### Acceptance Criteria Traceability
Each method and class directly implements specific acceptance criteria from the user stories, ensuring complete requirement coverage without over-engineering.