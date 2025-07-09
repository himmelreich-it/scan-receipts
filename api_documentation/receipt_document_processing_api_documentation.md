# Receipt Document Processing API Documentation

## Package: receipt_document_processing
**Package Path**: `receipt_document_processing/`
**Purpose**: Core domain package containing entities, value objects, and services for receipt document lifecycle management

**Modules**:
- receipt_document_processing.entities (Domain entities)
- receipt_document_processing.value_objects (Value objects and identifiers)
- receipt_document_processing.services (Domain services)
- receipt_document_processing.exceptions (Domain exceptions)

**Dependencies**: None (core domain package)
**User Stories Served**: Stories 2, 3, 5, 6, 8

## class DocumentId
**Module**: receipt_document_processing.value_objects
**Purpose**: Unique identifier for receipt documents

**Methods**:
- `__init__(self, value: int)`
- `__str__(self) -> str`
- `from_string(cls, value: str) -> DocumentId`

**Usage**:
```python
from receipt_document_processing.value_objects import DocumentId

doc_id = DocumentId(42)
id_str = str(doc_id)  # "42"
```

**Serves User Stories**: Story 2 (Sequential ID Generation)

## class FileHash
**Module**: receipt_document_processing.value_objects
**Purpose**: File hash for duplicate detection with failure handling

**Methods**:
- `__init__(self, value: str)`
- `calculate(cls, file_path: str) -> FileHash`
- `is_creation_failed(self) -> bool`

**Usage**:
```python
from receipt_document_processing.value_objects import FileHash

file_hash = FileHash.calculate("path/to/file.pdf")
if file_hash.is_creation_failed():
    # Handle failed hash calculation
```

**Serves User Stories**: Story 3 (File Hash Calculation and Duplicate Detection)

## class ProcessingTimestamp
**Module**: receipt_document_processing.value_objects
**Purpose**: Timestamp for document processing with filename formatting

**Methods**:
- `__init__(self, value: datetime)`
- `now(cls) -> ProcessingTimestamp`
- `format_for_filename(self) -> str`

**Usage**:
```python
from receipt_document_processing.value_objects import ProcessingTimestamp

timestamp = ProcessingTimestamp.now()
filename_part = timestamp.format_for_filename()  # "20240101-123456789012"
```

**Serves User Stories**: Story 5 (Document Metadata Collection)

## class DocumentMetadata
**Module**: receipt_document_processing.value_objects
**Purpose**: Essential metadata for receipt documents

**Properties**:
- `document_id: DocumentId`
- `original_filename: str`
- `file_hash: FileHash`
- `processing_timestamp: ProcessingTimestamp`
- `file_path: Path`

**Methods**:
- `__init__(self, document_id: DocumentId, original_filename: str, file_hash: FileHash, processing_timestamp: ProcessingTimestamp, file_path: Path)`
- `get_processed_filename(self) -> str`

**Usage**:
```python
from receipt_document_processing.value_objects import DocumentMetadata

metadata = DocumentMetadata(doc_id, "receipt.pdf", file_hash, timestamp, path)
processed_name = metadata.get_processed_filename()  # "42-20240101-123456789012-receipt.pdf"
```

**Serves User Stories**: Story 5 (Document Metadata Collection)

## class DocumentProcessingState
**Module**: receipt_document_processing.value_objects
**Purpose**: Enumeration of document processing states

**Values**:
- `DISCOVERED = "discovered"`
- `PROCESSING = "processing"`
- `COMPLETED = "completed"`
- `ERROR = "error"`

**Serves User Stories**: Story 6 (Document Processing State Management)

## class ReceiptDocument
**Module**: receipt_document_processing.entities
**Purpose**: Core entity representing a receipt document

**Properties**:
- `id: DocumentId`
- `file_path: Path`
- `state: DocumentProcessingState`
- `metadata: Optional[DocumentMetadata]`
- `error_message: Optional[str]`

**Methods**:
- `__init__(self, file_path: Path, document_id: DocumentId)`
- `start_processing(self) -> None`
- `complete_processing(self, metadata: DocumentMetadata) -> None`
- `mark_error(self, error_message: str) -> None`
- `is_supported_format(self) -> bool`
- `get_file_content(self) -> bytes`

**Usage**:
```python
from receipt_document_processing.entities import ReceiptDocument

document = ReceiptDocument(Path("receipt.pdf"), DocumentId(1))
document.start_processing()
content = document.get_file_content()
document.complete_processing(metadata)
```

**Serves User Stories**: Story 4 (Document File Reading), Story 6 (Document Processing State Management)

## class SequentialIdService
**Module**: receipt_document_processing.services
**Purpose**: Service for generating sequential document IDs

**Methods**:
- `__init__(self, csv_file_path: Path)`
- `get_next_id(self) -> DocumentId`

**Usage**:
```python
from receipt_document_processing.services import SequentialIdService

service = SequentialIdService(Path("receipts.csv"))
next_id = service.get_next_id()  # Returns DocumentId(1) if CSV doesn't exist
```

**Serves User Stories**: Story 2 (Sequential ID Generation)

## class DuplicateDetectionService
**Module**: receipt_document_processing.services  
**Purpose**: Service for detecting duplicate documents by hash

**Methods**:
- `__init__(self, csv_file_path: Path)`
- `is_duplicate(self, file_hash: FileHash) -> bool`

**Usage**:
```python
from receipt_document_processing.services import DuplicateDetectionService

service = DuplicateDetectionService(Path("receipts.csv"))
if service.is_duplicate(file_hash):
    # Skip duplicate file
```

**Serves User Stories**: Story 3 (File Hash Calculation and Duplicate Detection)

## class DocumentProcessingResult
**Module**: receipt_document_processing.services
**Purpose**: Result object for integration with dependent features

**Properties**:
- `document: ReceiptDocument`
- `success: bool`
- `error_message: Optional[str]`

**Methods**:
- `__init__(self, document: ReceiptDocument, success: bool, error_message: Optional[str] = None)`
- `has_metadata(self) -> bool`
- `file_content(self) -> Optional[bytes]`

**Usage**:
```python
from receipt_document_processing.services import DocumentProcessingResult

result = DocumentProcessingResult(document, True, None)
if result.success and result.has_metadata:
    content = result.file_content
```

**Serves User Stories**: Story 8 (Integration Interface for Dependent Features)

## class DocumentProcessingInterface
**Module**: receipt_document_processing.services
**Purpose**: Interface for dependent features to access document processing

**Methods**:
- `process_all_documents(self) -> Iterator[DocumentProcessingResult]`
- `get_document_metadata(self, document_id: DocumentId) -> Optional[DocumentMetadata]`

**Serves User Stories**: Story 8 (Integration Interface for Dependent Features)

## Exception Classes

### DocumentProcessingError
**Module**: receipt_document_processing.exceptions
**Purpose**: Base exception for document processing errors

### FolderCreationError
**Module**: receipt_document_processing.exceptions
**Purpose**: Raised when folders cannot be created
**Inherits**: DocumentProcessingError

### CsvCorruptionError
**Module**: receipt_document_processing.exceptions
**Purpose**: Raised when CSV file is corrupted
**Inherits**: DocumentProcessingError

### FileReadError
**Module**: receipt_document_processing.exceptions
**Purpose**: Raised when file cannot be read
**Inherits**: DocumentProcessingError

## Test Instructions

**Test Scenarios**:
- DocumentId validation and string conversion
- FileHash calculation and failure handling
- ProcessingTimestamp formatting
- DocumentMetadata processed filename generation
- ReceiptDocument state transitions
- SequentialIdService ID generation
- DuplicateDetectionService duplicate checking
- DocumentProcessingResult integration

**Mock Requirements**:
- Mock file system operations for testing
- Mock CSV file content for ID service testing
- Mock hash calculation for predictable results

## Dependencies and Integration

**Package Dependencies**: 
- Standard library: `pathlib`, `datetime`, `hashlib`, `csv`, `enum`, `uuid`

**Integration Points**:
- Consumed by: document_discovery, document_validation, document_repository packages
- Provides: Core domain models and services for document processing

**User Story Cross-References**:
- Story 2: DocumentId, SequentialIdService
- Story 3: FileHash, DuplicateDetectionService  
- Story 5: DocumentMetadata, ProcessingTimestamp
- Story 6: DocumentProcessingState, ReceiptDocument state management
- Story 8: DocumentProcessingResult, DocumentProcessingInterface