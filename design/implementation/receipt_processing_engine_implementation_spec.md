# Receipt Processing Engine Implementation Specification

## Package: receipt_processing_engine
**Path**: `src/receipt_processing_engine/`  
**Purpose**: Core automated receipt processing system with AI-powered data extraction using hexagonal architecture  
**User Stories**: RECEIPT_ANALYSIS_A1B2, FILE_VALIDATION_C3D4, DUPLICATE_DETECTION_E5F6  
**Dependencies**: anthropic, hashlib, pathlib, logging, json, os  
**Design Decisions**: Hexagonal architecture with domain/application/infrastructure layers, error classification system, SHA-256 file hashing, Claude Sonnet 4 API integration

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

This specification provides sufficient technical guidance for implementing the Receipt Processing Engine while maintaining clear separation between domain logic and infrastructure concerns.