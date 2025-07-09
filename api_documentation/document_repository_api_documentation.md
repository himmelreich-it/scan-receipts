# Document Repository API Documentation

## Package: document_repository
**Package Path**: `document_repository/`
**Purpose**: Data access layer for document persistence and CSV management

**Modules**:
- document_repository.interfaces (Repository interfaces)
- document_repository.csv_impl (CSV-based repository implementation)
- document_repository.models (Data transfer objects)

**Dependencies**: 
- receipt_document_processing (for domain models)
- Standard library: `csv`, `pathlib`, `typing`

**User Stories Served**: Story 2 (Sequential ID Generation), Story 3 (File Hash Calculation and Duplicate Detection)

## class DocumentRepository
**Module**: document_repository.interfaces
**Purpose**: Repository interface for document persistence

**Methods**:
- `find_by_id(self, document_id: DocumentId) -> Optional[ReceiptDocument]`
- `save(self, document: ReceiptDocument) -> None`
- `find_all_processed(self) -> List[ReceiptDocument]`
- `get_last_id(self) -> int`
- `get_existing_hashes(self) -> Set[str]`

**Usage**:
```python
from document_repository.interfaces import DocumentRepository

# Interface to be implemented by concrete repositories
```

**Serves User Stories**: Story 2 (Sequential ID Generation), Story 3 (File Hash Calculation and Duplicate Detection)

## class CsvDocumentRepository
**Module**: document_repository.csv_impl
**Purpose**: CSV-based implementation of document repository

**Methods**:
- `__init__(self, csv_file_path: Path)`
- `find_by_id(self, document_id: DocumentId) -> Optional[ReceiptDocument]`
- `save(self, document: ReceiptDocument) -> None`
- `find_all_processed(self) -> List[ReceiptDocument]`
- `get_last_id(self) -> int`
- `get_existing_hashes(self) -> Set[str]`

**Usage**:
```python
from document_repository.csv_impl import CsvDocumentRepository

repo = CsvDocumentRepository(Path("receipts.csv"))
last_id = repo.get_last_id()
existing_hashes = repo.get_existing_hashes()
```

**CSV Schema**:
- Fields: `['ID', 'Amount', 'Tax', 'Description', 'Currency', 'Date', 'Confidence', 'Hash']`
- ID field used for sequential ID generation
- Hash field used for duplicate detection

**Serves User Stories**: Story 2 (Sequential ID Generation), Story 3 (File Hash Calculation and Duplicate Detection)

## class DocumentRecord
**Module**: document_repository.models
**Purpose**: Data transfer object for CSV document records

**Properties**:
- `id: int`
- `amount: Optional[float]`
- `tax: Optional[float]`
- `description: Optional[str]`
- `currency: Optional[str]`
- `date: Optional[str]`
- `confidence: Optional[int]`
- `hash: str`

**Methods**:
- `__init__(self, id: int, hash: str, amount: Optional[float] = None, tax: Optional[float] = None, description: Optional[str] = None, currency: Optional[str] = None, date: Optional[str] = None, confidence: Optional[int] = None)`
- `to_dict(self) -> Dict[str, Any]`
- `from_dict(cls, data: Dict[str, Any]) -> DocumentRecord`

**Usage**:
```python
from document_repository.models import DocumentRecord

record = DocumentRecord(id=1, hash="abc123", amount=45.67)
record_dict = record.to_dict()
```

**Serves User Stories**: Story 2 (Sequential ID Generation), Story 3 (File Hash Calculation and Duplicate Detection)

## class CsvCorruptionError
**Module**: document_repository.csv_impl
**Purpose**: Exception for CSV file corruption issues

**Properties**:
- `message: str`
- `csv_file_path: Path`

**Methods**:
- `__init__(self, message: str, csv_file_path: Path)`

**Usage**:
```python
from document_repository.csv_impl import CsvCorruptionError

try:
    # CSV operations
    pass
except CsvCorruptionError as e:
    print(f"CSV corruption: {e.message}")
```

**Serves User Stories**: Story 2 (Sequential ID Generation), Story 7 (Error Handling and Recovery)

## class CsvReader
**Module**: document_repository.csv_impl
**Purpose**: Utility for reading CSV files with error handling

**Methods**:
- `__init__(self, csv_file_path: Path)`
- `read_all_records(self) -> List[DocumentRecord]`
- `get_max_id(self) -> int`
- `get_all_hashes(self) -> Set[str]`

**Usage**:
```python
from document_repository.csv_impl import CsvReader

reader = CsvReader(Path("receipts.csv"))
max_id = reader.get_max_id()
all_hashes = reader.get_all_hashes()
```

**Error Handling**:
- Raises CsvCorruptionError for unreadable files
- Handles missing files gracefully
- Validates CSV structure

**Serves User Stories**: Story 2 (Sequential ID Generation), Story 3 (File Hash Calculation and Duplicate Detection)

## class CsvWriter
**Module**: document_repository.csv_impl
**Purpose**: Utility for writing CSV files with proper headers

**Methods**:
- `__init__(self, csv_file_path: Path)`
- `write_header(self) -> None`
- `append_record(self, record: DocumentRecord) -> None`
- `file_exists(self) -> bool`

**Usage**:
```python
from document_repository.csv_impl import CsvWriter

writer = CsvWriter(Path("receipts.csv"))
if not writer.file_exists():
    writer.write_header()
writer.append_record(record)
```

**Serves User Stories**: Story 2 (Sequential ID Generation), Story 3 (File Hash Calculation and Duplicate Detection)

## Test Instructions

**Test Scenarios**:
- CSV file reading with valid data
- CSV file reading with missing file
- CSV file reading with corrupted data
- Sequential ID generation from existing records
- Hash extraction from existing records
- Record creation and serialization
- Error handling for CSV corruption

**Expected Behaviors**:
- CsvDocumentRepository returns 0 for get_last_id() when file doesn't exist
- CsvDocumentRepository returns empty set for get_existing_hashes() when file doesn't exist
- CsvDocumentRepository raises CsvCorruptionError for unreadable files
- DocumentRecord properly serializes to/from dictionary format

**Mock Requirements**:
- Mock CSV file content for various test scenarios
- Mock file system operations for file existence checks
- Mock CSV corruption scenarios

## Dependencies and Integration

**Package Dependencies**:
- receipt_document_processing: DocumentId, ReceiptDocument domain models
- Standard library: `csv`, `pathlib`, `typing`, `logging`

**Integration Points**:
- Used by: SequentialIdService, DuplicateDetectionService from receipt_document_processing
- Provides: Data access layer for document metadata and duplicate detection

**User Story Cross-References**:
- Story 2: DocumentRepository interface, CsvDocumentRepository.get_last_id()
- Story 3: CsvDocumentRepository.get_existing_hashes(), DocumentRecord
- Story 7: CsvCorruptionError and error handling patterns