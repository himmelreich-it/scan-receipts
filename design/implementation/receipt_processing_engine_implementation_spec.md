# Receipt Processing Engine Implementation Specification

## Feature Overview
Core automated receipt processing system that handles file intake, AI-powered data extraction using Anthropic's Claude API, and structured data output. Includes advanced duplicate detection, date validation, and enhanced error handling with failed folder management.

## User Stories Implemented
- **RECEIPT_ANALYSIS_A1B2**: Core Receipt Analysis and Data Extraction
- **FILE_VALIDATION_C3D4**: File Format Validation and Error Handling  
- **DUPLICATE_DETECTION_E5F6**: Duplicate Detection and Management

## Architecture Overview

Following hexagonal architecture principles, the implementation is structured in three layers:

### Domain Layer (Core Business Logic)
- **Receipt Aggregate**: Central domain entity with business rules
- **Extraction Value Objects**: Immutable data structures for extracted information
- **Validation Policies**: Business rules for date validation and data integrity

### Application Layer (Use Cases)
- **Process Receipt Use Case**: Main orchestrator for receipt processing workflow
- **Extract Data Use Case**: Manages AI-powered data extraction
- **Validate Results Use Case**: Applies business rules and validation

### Infrastructure Layer (Adapters)
- **Anthropic AI Adapter**: Handles API integration and PDF conversion
- **File System Adapter**: Manages file operations and folder organization
- **Duplicate Detection Adapter**: Implements hash-based duplicate detection

## Package Structure

```
src/
└── receipt_processing_engine/
    ├── __init__.py                 # Public API exports
    ├── domain/
    │   ├── __init__.py
    │   ├── models.py              # Receipt aggregate and value objects
    │   ├── policies.py            # Date validation and business rules
    │   └── exceptions.py          # Domain-specific exceptions
    ├── application/
    │   ├── __init__.py
    │   ├── use_cases.py           # Main use case implementations
    │   └── ports.py               # Interface definitions (ports)
    └── infrastructure/
        ├── __init__.py
        ├── ai_adapter.py          # Anthropic API integration
        ├── file_adapter.py        # File system operations
        ├── duplicate_adapter.py   # Hash-based duplicate detection
        └── config.py              # Configuration and constants
```

## Implementation Specifications

### Package: receipt_processing_engine
**Path**: `src/receipt_processing_engine/`
**Purpose**: Core receipt processing functionality with AI-powered data extraction
**User Stories**: RECEIPT_ANALYSIS_A1B2, FILE_VALIDATION_C3D4, DUPLICATE_DETECTION_E5F6
**Dependencies**: anthropic, pdf2image, pathlib, hashlib, json, logging, datetime
**Design Decisions**: Hexagonal architecture, PDF-to-image conversion, SHA-256 hashing, hard-coded 1-year date validation
## Domain Layer Components

### File: `domain/models.py`
**Purpose**: Core domain entities and value objects

#### Receipt Aggregate
```python
@dataclass
class Receipt:
    """Central domain entity representing a receipt and its processing state."""
    
    file_path: Path
    original_filename: str
    file_hash: str
    extraction_result: Optional[ExtractionResult]
    processing_status: ProcessingStatus
    error_message: Optional[str]
    
    def mark_as_processed(self, result: ExtractionResult) -> None:
        """Mark receipt as successfully processed with extraction result."""
        
    def mark_as_failed(self, error_message: str) -> None:
        """Mark receipt as failed with error details."""
        
    def is_duplicate(self) -> bool:
        """Check if this receipt is marked as a duplicate."""
```

#### ExtractionResult Value Object
```python
@dataclass(frozen=True)
class ExtractionResult:
    """Immutable value object containing extracted receipt data."""
    
    amount: float
    tax: Optional[float]
    tax_percentage: Optional[float]
    description: str
    currency: str
    date: datetime.date
    confidence: int
    
    def __post_init__(self) -> None:
        """Validate extraction result data on creation."""
```

#### ProcessingStatus Enum
```python
class ProcessingStatus(Enum):
    """Receipt processing status enumeration."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DUPLICATE = "duplicate"
```

### File: `domain/policies.py`
**Purpose**: Business rules and validation policies

#### DateValidationPolicy
```python
class DateValidationPolicy:
    """Domain service for date validation business rules."""
    
    @staticmethod
    def validate_date(date: datetime.date) -> ValidationResult:
        """Validate date is not future and not older than 1 year.
        
        Business Rules:
        - Date must not be in the future
        - Date must not be older than 1 year from current date
        """
        
    @staticmethod
    def is_date_in_future(date: datetime.date) -> bool:
        """Check if date is in the future."""
        
    @staticmethod
    def is_date_too_old(date: datetime.date) -> bool:
        """Check if date is older than 1 year."""
```

#### ValidationResult
```python
@dataclass(frozen=True)
class ValidationResult:
    """Result of validation operations."""
    
    is_valid: bool
    error_message: Optional[str]
```

### File: `domain/exceptions.py`
**Purpose**: Domain-specific exceptions

```python
class ReceiptProcessingError(Exception):
    """Base exception for receipt processing errors."""

class DateValidationError(ReceiptProcessingError):
    """Exception for date validation failures."""

class ExtractionValidationError(ReceiptProcessingError):
    """Exception for data extraction validation failures."""

class DuplicateReceiptError(ReceiptProcessingError):
    """Exception for duplicate receipt detection."""
```

## Application Layer Components

### File: `application/ports.py`
**Purpose**: Interface definitions (ports) for external dependencies

#### AI Extraction Port
```python
class AIExtractionPort(ABC):
    """Port for AI-powered data extraction services."""
    
    @abstractmethod
    async def extract_data(self, file_path: Path) -> ExtractionResult:
        """Extract structured data from receipt file."""
        
    @abstractmethod
    def supports_file_format(self, file_path: Path) -> bool:
        """Check if file format is supported for extraction."""
```

#### File System Port
```python
class FileSystemPort(ABC):
    """Port for file system operations."""
    
    @abstractmethod
    def ensure_folders_exist(self, folders: List[Path]) -> None:
        """Create folder structure if it doesn't exist."""
        
    @abstractmethod
    def move_file_to_failed(self, file_path: Path, error_message: str) -> None:
        """Move file to failed folder with error log."""
        
    @abstractmethod
    def get_input_files(self, input_folder: Path) -> List[Path]:
        """Get list of receipt files from input folder."""
```

#### Duplicate Detection Port
```python
class DuplicateDetectionPort(ABC):
    """Port for duplicate detection services."""
    
    @abstractmethod
    def initialize_imported_folder_hashes(self, imported_folder: Path) -> None:
        """Scan imported folder and build hash database."""
        
    @abstractmethod
    def is_duplicate(self, file_hash: str) -> bool:
        """Check if file hash is a duplicate."""
        
    @abstractmethod
    def add_to_session(self, file_hash: str, filename: str) -> None:
        """Add file hash to current session tracking."""
```

### File: `application/use_cases.py`
**Purpose**: Main use case implementations

#### ProcessReceiptUseCase
```python
class ProcessReceiptUseCase:
    """Main orchestrator for receipt processing workflow."""
    
    def __init__(
        self,
        ai_extraction: AIExtractionPort,
        file_system: FileSystemPort,
        duplicate_detection: DuplicateDetectionPort
    ):
        """Initialize use case with required dependencies."""
        
    async def process_receipts(self, input_folder: Path) -> List[Receipt]:
        """Process all receipts in input folder.
        
        Workflow:
        1. Initialize duplicate detection with imported folder using FILE_MGMT_B7C4
        2. Get list of input files
        3. Process each file through validation pipeline with confidence scoring
        4. Apply enhanced date validation (not future, not older than 1 year)
        5. Return list of processed receipts
        """
        
    async def _process_single_receipt(self, file_path: Path) -> Receipt:
        """Process a single receipt file through complete workflow."""
```

#### ExtractDataUseCase
```python
class ExtractDataUseCase:
    """Manages AI-powered data extraction from receipt files."""
    
    def __init__(self, ai_extraction: AIExtractionPort):
        """Initialize with AI extraction service."""
        
    async def extract_and_validate(self, file_path: Path) -> ExtractionResult:
        """Extract data from receipt and validate business rules.
        
        Process:
        1. Extract data using AI service with confidence scoring
        2. Validate date using enhanced business rules (not future, not older than 1 year)
        3. Validate required fields are present
        4. Return validated extraction result with confidence score
        """
```

## Infrastructure Layer Components

### File: `infrastructure/ai_adapter.py`
**Purpose**: Anthropic API integration with PDF conversion

#### AnthropicAIAdapter
```python
class AnthropicAIAdapter(AIExtractionPort):
    """Adapter for Anthropic Claude API with PDF conversion support."""
    
    def __init__(self, api_key: str):
        """Initialize with Anthropic API key."""
        
    async def extract_data(self, file_path: Path) -> ExtractionResult:
        """Extract structured data from receipt file.
        
        Process:
        1. Check file format (PDF, JPG, PNG)
        2. Convert PDF to image if needed
        3. Send image to Claude API
        4. Parse JSON response
        5. Create ExtractionResult object
        """
        
    def _convert_pdf_to_image(self, pdf_path: Path) -> Path:
        """Convert PDF first page to PNG image.
        
        Uses pdf2image library to convert PDF to image format
        that can be sent to Anthropic API.
        """
        
    def _send_to_claude_api(self, image_path: Path) -> dict:
        """Send image to Claude API and get structured response."""
        
    def _parse_extraction_response(self, response: dict) -> ExtractionResult:
        """Parse Claude API response into ExtractionResult object."""
        
    def supports_file_format(self, file_path: Path) -> bool:
        """Check if file format is supported (PDF, JPG, PNG)."""
```

### File: `infrastructure/file_adapter.py`
**Purpose**: File system operations and folder management

#### FileSystemAdapter
```python
class FileSystemAdapter(FileSystemPort):
    """Adapter for file system operations."""
    
    def __init__(self, imported_folder: Path, failed_folder: Path):
        """Initialize with folder paths."""
        
    def ensure_folders_exist(self, folders: List[Path]) -> None:
        """Create folder structure if it doesn't exist."""
        
    def move_file_to_failed(self, file_path: Path, error_message: str) -> None:
        """Move file to failed folder with error log.
        
        Process:
        1. Copy file to failed folder
        2. Create text error log with same name + .error extension
        3. Log error details to console
        """
        
    def get_input_files(self, input_folder: Path) -> List[Path]:
        """Get list of receipt files from input folder.
        
        Filters for supported formats: PDF, JPG, PNG
        """
        
    def _create_error_log(self, failed_file_path: Path, error_message: str) -> None:
        """Create simple text error log file."""
```

### File: `infrastructure/duplicate_adapter.py`
**Purpose**: Hash-based duplicate detection

#### DuplicateDetectionAdapter
```python
class DuplicateDetectionAdapter(DuplicateDetectionPort):
    """Adapter for SHA-256 hash-based duplicate detection."""
    
    def __init__(self):
        """Initialize with empty hash databases."""
        
    def initialize_imported_folder_hashes(self, imported_folder: Path) -> None:
        """Scan imported folder and build hash database.
        
        Process:
        1. Scan all files in imported folder
        2. Generate SHA-256 hash for each file
        3. Store in hash database for duplicate checking
        """
        
    def is_duplicate(self, file_hash: str) -> bool:
        """Check if file hash is a duplicate.
        
        Checks against:
        1. Imported folder hash database
        2. Current session hash database
        """
        
    def add_to_session(self, file_hash: str, filename: str) -> None:
        """Add file hash to current session tracking."""
        
    def _generate_file_hash(self, file_path: Path) -> str:
        """Generate SHA-256 hash for file."""
```

### File: `infrastructure/config.py`
**Purpose**: Configuration and constants

```python
class ProcessingConfig:
    """Configuration constants for receipt processing."""
    
    # Date validation
    MAX_DATE_AGE_DAYS = 365  # 1 year
    
    # Supported file formats
    SUPPORTED_FORMATS = {'.pdf', '.jpg', '.jpeg', '.png'}
    
    # API configuration
    CLAUDE_MODEL = "claude-sonnet-4-20250514"
    
    # Error messages
    ERROR_MESSAGES = {
        'date_future': 'Date validation failed: future date',
        'date_too_old': 'Date validation failed: date too old',
        'unsupported_format': 'Unsupported file format',
        'api_failure': 'API failure',
        'json_parsing': 'JSON parsing failed',
        'date_extraction': 'Date extraction failed: no valid date found',
        'file_unreadable': 'File unreadable or corrupted'
    }
```

## Integration Specifications

### Main Application Entry Point
```python
# Integration with main application
from receipt_processing_engine import ProcessReceiptUseCase, create_receipt_processor

async def main():
    # Initialize receipt processor with configuration
    processor = create_receipt_processor(
        api_key=os.getenv('ANTHROPIC_API_KEY'),
        imported_folder=Path(os.getenv('IMPORTED_FOLDER')),
        failed_folder=Path(os.getenv('FAILED_FOLDER'))
    )
    
    # Process receipts
    results = await processor.process_receipts(
        input_folder=Path(os.getenv('INPUT_RECEIPTS_FOLDER'))
    )
    
    return results
```

### Public API (Package `__init__.py`)
```python
# src/receipt_processing_engine/__init__.py
from .application.use_cases import ProcessReceiptUseCase
from .domain.models import Receipt, ExtractionResult, ProcessingStatus
from .domain.exceptions import ReceiptProcessingError
from .infrastructure.ai_adapter import AnthropicAIAdapter
from .infrastructure.file_adapter import FileSystemAdapter
from .infrastructure.duplicate_adapter import DuplicateDetectionAdapter

def create_receipt_processor(
    api_key: str,
    imported_folder: Path,
    failed_folder: Path
) -> ProcessReceiptUseCase:
    """Factory function to create configured receipt processor."""

__all__ = [
    'ProcessReceiptUseCase',
    'Receipt',
    'ExtractionResult',
    'ProcessingStatus',
    'ReceiptProcessingError',
    'create_receipt_processor'
]
```

## Configuration Requirements

### Environment Variables
```bash
ANTHROPIC_API_KEY=your_api_key_here
IMPORTED_FOLDER=/path/to/imported/folder
FAILED_FOLDER=/path/to/failed/folder
INPUT_RECEIPTS_FOLDER=/path/to/input/folder
```

### Dependencies (pyproject.toml)
```toml
[project]
dependencies = [
    "anthropic",
    "pdf2image",
    "pillow",
    "python-dateutil"
]
```

## Error Handling Strategy

### Error Categories
1. **File System Errors**: Permission issues, disk space, folder access
2. **PDF Conversion Errors**: Corrupted PDFs, conversion failures
3. **API Errors**: Network failures, rate limiting, authentication
4. **Data Validation Errors**: Date validation, required field validation
5. **Duplicate Detection Errors**: Hash generation failures

### Error Handling Approach
- **Fail Fast**: Stop processing individual file on error, continue with next
- **Error Logging**: Create detailed error logs in failed folder
- **Recovery**: Allow retry by moving files back to input folder
- **Continuation**: Continue processing other files when one fails

## Performance Considerations

### Optimization Strategies
1. **Async Processing**: Use asyncio for AI API calls
2. **Lazy Loading**: Load done folder hashes only when needed
3. **Memory Management**: Process files one at a time to avoid memory issues
4. **Caching**: Cache file hashes to avoid recalculation

### Scalability Constraints
- **API Rate Limits**: Anthropic API has rate limiting
- **Memory Usage**: PDF conversion requires temporary image storage
- **Disk Space**: Failed folder accumulates files over time

This implementation specification provides comprehensive guidance for developing the Receipt Processing Engine while maintaining clean architecture principles and meeting all user story requirements.

## Architecture Overview

### Domain Layer Components

#### File: `src/receipt_processing_engine/domain/entities.py`
**Purpose**: Core business entities and aggregates  
**Libraries**: dataclasses, datetime, hashlib  
**Design Patterns**: Aggregate Root, Entity pattern  

**Receipt Aggregate Root**
```python
@dataclass
class Receipt:
    file_path: str
    file_hash: str
    extraction_data: Optional[ExtractionData]
    processing_status: ProcessingStatus
    error_type: Optional[str]
    
    def mark_as_processed(self, data: ExtractionData) -> None
    def mark_as_failed(self, error_type: str) -> None
    def is_duplicate(self, other_hash: str) -> bool
    def to_csv_row(self) -> Dict[str, Any]
```

**Processing Status Enum**
```python
class ProcessingStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"
    DUPLICATE = "duplicate"
```

#### File: `src/receipt_processing_engine/domain/value_objects.py`
**Purpose**: Immutable value objects for financial data validation  
**Libraries**: dataclasses, decimal, datetime, re  
**Design Patterns**: Value Object pattern  

**ExtractionData Value Object**
```python
@dataclass(frozen=True)
class ExtractionData:
    amount: Amount
    tax: Optional[Tax]
    tax_percentage: Optional[TaxPercentage]
    description: Description
    currency: Currency
    date: ReceiptDate
    confidence: Confidence
    
    @classmethod
    def from_api_response(cls, response_data: Dict[str, Any]) -> 'ExtractionData'
```

**Financial Value Objects**
```python
@dataclass(frozen=True)
class Amount:
    value: Decimal
    def __post_init__(self): # Validate positive amount

@dataclass(frozen=True) 
class Currency:
    code: str
    def __post_init__(self): # Validate ISO currency code

@dataclass(frozen=True)
class Confidence:
    score: int
    def __post_init__(self): # Validate 0-100 range
```

#### File: `src/receipt_processing_engine/domain/policies.py`
**Purpose**: Business rules and domain services  
**Libraries**: typing, logging  
**Design Patterns**: Domain Service pattern  

**Processing Policies**
```python
class ProcessingPolicies:
    @staticmethod
    def should_process_file(file_path: str, known_hashes: Set[str]) -> bool
    
    @staticmethod
    def classify_processing_error(exception: Exception) -> str
    
    @staticmethod
    def is_confidence_acceptable(confidence: int) -> bool
```

#### File: `src/receipt_processing_engine/domain/exceptions.py`
**Purpose**: Domain-specific exceptions  
**Libraries**: None  

**Custom Exceptions**
```python
class ReceiptProcessingError(Exception)
class InvalidFileFormatError(ReceiptProcessingError)
class DuplicateFileError(ReceiptProcessingError)
class ExtractionValidationError(ReceiptProcessingError)
```

### Application Layer Components

#### File: `src/receipt_processing_engine/application/use_cases.py`
**Purpose**: Application orchestration and workflow management  
**Libraries**: typing, logging  
**Design Patterns**: Use Case pattern, Command pattern  

**Process Receipt Use Case**
```python
class ProcessReceiptUseCase:
    def __init__(self, 
                 ai_extraction_port: AIExtractionPort,
                 file_system_port: FileSystemPort,
                 receipt_repository_port: ReceiptRepositoryPort,
                 duplicate_detector_port: DuplicateDetectionPort)
    
    async def execute(self, file_path: str) -> Receipt
    def _handle_processing_error(self, error: Exception, file_path: str) -> Receipt
```

**Extract Data Use Case** 
```python
class ExtractDataUseCase:
    def __init__(self, ai_extraction_port: AIExtractionPort)
    
    async def execute(self, file_path: str) -> ExtractionData
    def _validate_api_response(self, response: Dict[str, Any]) -> None
```

**Validate Results Use Case**
```python
class ValidateResultsUseCase:
    def __init__(self, processing_policies: ProcessingPolicies)
    
    def execute(self, extraction_data: ExtractionData) -> ValidationResult
    def _apply_business_rules(self, data: ExtractionData) -> List[str]
```

#### File: `src/receipt_processing_engine/application/ports.py`
**Purpose**: Interface definitions for external dependencies  
**Libraries**: abc, typing  
**Design Patterns**: Port/Adapter pattern, Interface Segregation  

**Port Interfaces**
```python
class AIExtractionPort(ABC):
    @abstractmethod
    async def extract_receipt_data(self, file_path: str) -> Dict[str, Any]

class FileSystemPort(ABC):
    @abstractmethod
    def validate_file_format(self, file_path: str) -> bool
    @abstractmethod
    def read_file_content(self, file_path: str) -> bytes

class DuplicateDetectionPort(ABC):
    @abstractmethod
    def generate_file_hash(self, file_path: str) -> str
    @abstractmethod
    def is_duplicate(self, file_hash: str, known_hashes: Set[str]) -> bool

class ReceiptRepositoryPort(ABC):
    @abstractmethod
    def save_receipt(self, receipt: Receipt) -> None
    @abstractmethod
    def get_processed_hashes(self) -> Set[str]
```

### Infrastructure Layer Components

#### File: `src/receipt_processing_engine/infrastructure/anthropic_adapter.py`
**Purpose**: Claude API integration for receipt data extraction  
**Libraries**: anthropic, json, logging, asyncio  
**Design Patterns**: Adapter pattern, Template Method  

**Anthropic API Adapter**
```python
class AnthropicAdapter(AIExtractionPort):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514")
    
    async def extract_receipt_data(self, file_path: str) -> Dict[str, Any]
    def _build_extraction_prompt(self, file_content: bytes) -> str
    def _parse_response(self, response: str) -> Dict[str, Any]
    def _handle_api_error(self, error: Exception) -> Dict[str, Any]
```

**JSON Schema Validation**
```python
EXTRACTION_SCHEMA = {
    "type": "object",
    "required": ["amount", "description", "currency", "date", "confidence"],
    "properties": {
        "amount": {"type": "number"},
        "tax": {"type": ["number", "null"]},
        "tax_percentage": {"type": ["number", "null"]},
        "description": {"type": "string"},
        "currency": {"type": "string"},
        "date": {"type": "string"},
        "confidence": {"type": "integer", "minimum": 0, "maximum": 100}
    }
}
```

#### File: `src/receipt_processing_engine/infrastructure/file_system_adapter.py`
**Purpose**: File operations and format validation  
**Libraries**: pathlib, mimetypes, os  
**Design Patterns**: Adapter pattern  

**File System Adapter**
```python
class FileSystemAdapter(FileSystemPort):
    SUPPORTED_FORMATS = {'.pdf', '.jpg', '.jpeg', '.png'}
    
    def validate_file_format(self, file_path: str) -> bool
    def read_file_content(self, file_path: str) -> bytes
    def _detect_file_type(self, file_path: str) -> str
    def _handle_file_access_error(self, error: Exception) -> None
```

#### File: `src/receipt_processing_engine/infrastructure/duplicate_detection_adapter.py`
**Purpose**: SHA-256 file hashing for duplicate detection  
**Libraries**: hashlib, pathlib  
**Design Patterns**: Adapter pattern  

**Duplicate Detection Adapter**
```python
class DuplicateDetectionAdapter(DuplicateDetectionPort):
    def generate_file_hash(self, file_path: str) -> str
    def is_duplicate(self, file_hash: str, known_hashes: Set[str]) -> bool
    def _calculate_sha256(self, file_content: bytes) -> str
```

#### File: `src/receipt_processing_engine/infrastructure/console_logger.py`
**Purpose**: Console progress reporting and error logging  
**Libraries**: logging, sys  
**Design Patterns**: Observer pattern  

**Console Logger**
```python
class ConsoleLogger:
    def __init__(self, level: str = "INFO")
    
    def log_processing_start(self, filename: str) -> None
    def log_processing_success(self, filename: str, confidence: int) -> None
    def log_processing_error(self, filename: str, error_type: str, message: str) -> None
    def log_duplicate_skipped(self, filename: str, original_filename: str) -> None
```

## Technical Specifications

### Error Handling Strategy
**Error Classification System**:
- `API_FAILURE`: Claude API errors, network timeouts, rate limits
- `FILE_CORRUPT`: Unreadable files, permission errors, corrupted data  
- `UNSUPPORTED_FORMAT`: Non-PDF/JPG/PNG files, invalid file types

**Error Recovery**:
- Continue processing remaining files after individual failures
- Create CSV entries with confidence 0 and error type in description
- Log specific error details to console with filename context

### Data Models and Relationships
**Receipt Aggregate Structure**:
- Central aggregate containing file metadata and extraction results
- Encapsulates business logic for status transitions and validation
- Provides CSV export interface following specified field mapping

**Value Object Hierarchy**:
- ExtractionData contains validated financial value objects
- Immutable objects ensure data integrity throughout processing
- Built-in validation prevents invalid business data states

### Integration Points
**Claude API Integration**:
- Asynchronous API calls to handle potential rate limiting
- Structured prompt engineering for consistent JSON responses
- Response validation against defined schema before domain object creation

**File System Integration**:
- Path validation and file access error handling
- MIME type detection for format validation
- Binary file reading for hash generation and API submission

### Performance Considerations
**Memory Management**:
- Stream file reading for large receipt images
- Avoid loading all files into memory simultaneously
- Use generators for batch processing when possible

**API Rate Limiting**:
- Implement exponential backoff for API failures
- Consider async processing queue for large file batches
- Monitor and log API usage patterns

### Security Measures
**Input Validation**:
- File path sanitization to prevent directory traversal
- File size limits to prevent resource exhaustion
- MIME type validation beyond file extension checking

**API Key Management**:
- Environment variable configuration for API credentials
- No hardcoded secrets in source code
- Error messages that don't expose sensitive information

## Configuration Requirements

### Environment Configuration
```python
# Required environment variables
ANTHROPIC_API_KEY: str
CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
LOG_LEVEL: str = "INFO"
MAX_FILE_SIZE_MB: int = 10
```

### Dependencies Configuration
```toml
# pyproject.toml additions
[project]
dependencies = [
    "anthropic>=0.25.0",
    "python-dotenv>=1.0.0",
]
```

## Testing Requirements

### Unit Testing Strategy
**Domain Layer Tests**:
- Receipt aggregate business logic validation
- Value object validation and immutability
- Processing policies business rule verification

**Application Layer Tests**:
- Use case orchestration with mocked ports
- Error handling workflow validation
- Input validation and boundary conditions

**Infrastructure Layer Tests**:
- Adapter contract compliance testing
- External service integration testing with mocks
- File system operation error scenarios

### Test Data Requirements
**Mock API Responses**:
- Valid extraction responses with all required fields
- Invalid responses missing required fields
- Malformed JSON responses for error testing

**Test Receipt Files**:
- Valid PDF/JPG/PNG files for format testing
- Corrupted files for error handling testing
- Various file sizes for performance testing

## BDD Test Scenarios

### Feature Files
- **duplicate_detection.feature**: Comprehensive duplicate detection and management scenarios in `tests/bdd/features/`

### Scenario Coverage
**DUPLICATE_DETECTION_E5F6 Acceptance Criteria Mapping**:
- `Initialize imported folder hash database at session start` → "When processing session starts, system scans imported folder and generates hash database"
- `Skip duplicate file that matches imported folder` → "When file hash matches existing hash in imported folder, system skips file and logs message"
- `Skip duplicate file that matches current session` → "When file hash matches hash from current processing session, system skips file and logs message"
- `Process file from failed folder (no duplicate check)` → "When checking duplicates, system does NOT check failed folder"
- `Generate and store file hash` → "When file is processed, system generates file hash" and "When file hash is generated, it is stored"
- `Continue processing after duplicate detection` → "When duplicate detection occurs, system continues processing next file"
- `Hash generation for different file types` → Parameterized testing for PDF/JPG/PNG formats
- `Handle hash generation failure` → "Hash generation failures" error scenario
- `Handle hash comparison error` → "Hash comparison errors" error scenario  
- `Handle imported folder access error` → "Imported folder access errors" error scenario
- `Handle logging failure` → "Logging failures" error scenario

### Test Data Requirements
**File System Test Data**:
- Sample receipt files (PDF, JPG, PNG) with known binary content for hash generation
- Corrupted files for error testing
- Files with identical content for duplicate detection testing
- Folder structure with done/failed/input directories

**Hash Test Data**:
- Pre-calculated SHA-256 hashes for test files
- Hash collision scenarios for edge case testing
- Invalid hash formats for error condition testing

**Session State Test Data**:
- Current session hash tracking with filename mappings
- Imported folder hash database with existing file hashes
- Failed folder files excluded from duplicate checking

### Step Definition Interfaces
**Expected step definition signatures for behave implementation**:

```python
# Background and setup steps
@given('a receipt processing system is initialized')
def step_system_initialized(context): pass

@given('an imported folder exists with processed receipts')  
def step_imported_folder_exists(context): pass

@given('the imported folder contains existing processed receipt files')
def step_imported_folder_contains_files(context): pass

# Hash database initialization steps
@when('the processing session starts')
def step_processing_session_starts(context): pass

@then('the system scans the imported folder')
def step_system_scans_imported_folder(context): pass

@then('generates SHA-256 hashes for all existing files')
def step_generates_hashes(context): pass

# Duplicate detection steps
@given('the imported folder contains a file "{filename}" with hash "{hash_value}"')
def step_imported_folder_file_with_hash(context, filename, hash_value): pass

@when('processing a file "{filename}" with the same hash "{hash_value}"')
def step_processing_file_with_hash(context, filename, hash_value): pass

@then('the system detects the file as a duplicate')
def step_detects_duplicate(context): pass

@then('skips processing without sending to API')
def step_skips_processing(context): pass

@then('logs "{message}"')
def step_logs_message(context, message): pass

@then('continues processing the next file')
def step_continues_processing(context): pass

@then('does not create a CSV entry for the duplicate')
def step_no_csv_entry(context): pass

# Session duplicate detection steps  
@given('the current processing session has already processed "{filename}" with hash "{hash_value}"')
def step_session_processed_file(context, filename, hash_value): pass

# Failed folder exclusion steps
@given('the failed folder contains a file "{filename}" with hash "{hash_value}"')
def step_failed_folder_contains_file(context, filename, hash_value): pass

@then('the system does not check the failed folder for duplicates')
def step_no_failed_folder_check(context): pass

@then('processes the file normally')
def step_processes_normally(context): pass

# Hash generation steps
@given('a file "{filename}" is being processed')
def step_file_being_processed(context, filename): pass

@when('the system generates the file hash')
def step_generates_file_hash(context): pass

@then('it calculates SHA-256 hash of the binary file content')
def step_calculates_sha256(context): pass

@then('stores the hash with the extracted data')
def step_stores_hash(context): pass

# Batch processing steps
@given('multiple files in the input folder')
def step_multiple_files(context): pass

@when('the system processes the files in sequence')
def step_processes_sequence(context): pass

@then('it processes {filename} normally')
def step_processes_file_normally(context, filename): pass

@then('skips {filename} as duplicate without interruption')
def step_skips_duplicate(context, filename): pass

# Error handling steps
@given('a file "{filename}" that cannot be read properly')
def step_unreadable_file(context, filename): pass

@when('the system attempts to generate the file hash')
def step_attempts_hash_generation(context): pass

@then('hash generation fails with an error')
def step_hash_generation_fails(context): pass

@then('moves the file to failed folder with error log "{error_message}"')
def step_moves_to_failed_folder(context, error_message): pass

@given('the hash database is corrupted or inaccessible')
def step_hash_database_corrupted(context): pass

@when('the system attempts to compare a file hash for duplicate detection')
def step_attempts_hash_comparison(context): pass

@then('hash comparison fails with an error')
def step_hash_comparison_fails(context): pass

@then('continues processing the file as non-duplicate')
def step_processes_as_non_duplicate(context): pass

@given('the imported folder is inaccessible due to permissions or missing directory')
def step_imported_folder_inaccessible(context): pass

@then('initializes with empty hash database')
def step_initializes_empty_database(context): pass

@given('the logging system is unavailable or failing')
def step_logging_unavailable(context): pass

@then('logging fails but duplicate detection continues')
def step_logging_fails_continues(context): pass
```

## Implementation Tracking

### Story Implementation Mapping
- **RECEIPT_ANALYSIS_A1B2**: ProcessReceiptUseCase, ExtractDataUseCase, AnthropicAdapter
- **FILE_VALIDATION_C3D4**: FileSystemAdapter, error classification system
- **DUPLICATE_DETECTION_E5F6**: DuplicateDetectionAdapter, hash-based duplicate logic

### Interface Contracts
**Critical Interfaces**:
- AIExtractionPort defines Claude API contract
- FileSystemPort ensures consistent file operations
- DuplicateDetectionPort provides hash-based duplicate detection
- All ports return domain objects, not infrastructure primitives

### Key Algorithms
**File Hash Generation**: SHA-256 calculation of binary file content for duplicate detection
**Error Classification**: Exception type mapping to business error categories
**API Response Validation**: JSON schema validation before domain object creation
**Processing Workflow**: Sequential file processing with error isolation and continuation

## Update Summary

This implementation specification has been updated to reflect the OUTDATED user story requirements:

### Key Changes Made:
1. **FILE_MGMT_B7C4 Integration**: Updated duplicate detection to use FILE_MGMT_B7C4 hash service instead of internal hash generation
2. **Enhanced Date Validation**: Added specific date validation rules (not future, not older than 1 year) with exact error messages 
3. **Confidence Scoring**: Integrated Claude API confidence scoring (0-100) throughout extraction workflow
4. **Improved Error Messages**: Added specific error message formats matching user story requirements
5. **Session-based Duplicate Logging**: Enhanced duplicate detection to distinguish between imported folder and session-based duplicates
6. **Dependency Updates**: Added file_management package dependency and updated factory functions

### Architecture Changes:
- **FileSystemAdapter**: Now delegates hash generation to FILE_MGMT_B7C4 service
- **DuplicateDetectionAdapter**: Uses FILE_MGMT_B7C4 for hash generation, enhanced duplicate detection return values
- **DateValidationPolicy**: Enhanced with specific error message requirements
- **ProcessingConfig**: Added confidence score constants and configurable date validation
- **AnthropicAIAdapter**: Enhanced to handle confidence scoring from Claude API

### User Story Alignment:
- **RECEIPT_ANALYSIS_A1B2**: Enhanced with confidence scoring, specific date validation, and Claude Sonnet 4 requirements
- **FILE_VALIDATION_C3D4**: Updated with enhanced error handling and success criteria enforcement  
- **DUPLICATE_DETECTION_E5F6**: Updated to use FILE_MGMT_B7C4 and enhanced session-based duplicate prevention

### Status Update:
All three OUTDATED user stories are now updated to meet the enhanced requirements with FILE_MGMT_B7C4 integration, confidence scoring, and improved date validation.

This specification provides comprehensive technical guidance for implementing the Receipt Processing Engine with all required enhancements while maintaining hexagonal architecture principles.