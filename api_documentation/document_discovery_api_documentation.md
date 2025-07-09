# Document Discovery API Documentation

## Package: document_discovery
**Package Path**: `document_discovery/`
**Purpose**: File system discovery and folder management for receipt documents

**Modules**:
- document_discovery.services (Discovery and folder management services)
- document_discovery.config (Configuration for discovery operations)

**Dependencies**: 
- receipt_document_processing (for domain models)
- Standard library: `pathlib`, `logging`

**User Stories Served**: Story 1 (Document Discovery and Folder Management)

## class DocumentDiscoveryService
**Module**: document_discovery.services
**Purpose**: Service for discovering receipt documents in input folder

**Methods**:
- `__init__(self, input_folder: Path, done_folder: Path)`
- `ensure_folder_structure(self) -> None`
- `discover_documents(self) -> Iterator[Path]`

**Usage**:
```python
from document_discovery.services import DocumentDiscoveryService

service = DocumentDiscoveryService(Path("input"), Path("done"))
service.ensure_folder_structure()
for file_path in service.discover_documents():
    # Process each discovered file
```

**Behavior**:
- Creates input/ and done/ folders if they don't exist
- Raises FolderCreationError on permission issues
- Logs empty folder message if no files found
- Filters to supported file extensions only

**Serves User Stories**: Story 1 (Document Discovery and Folder Management)

## class DocumentProcessingService
**Module**: document_discovery.services
**Purpose**: Main orchestration service for document processing workflow

**Methods**:
- `__init__(self, discovery_service: DocumentDiscoveryService, id_service: SequentialIdService, duplicate_service: DuplicateDetectionService, validation_service: DocumentValidationService, input_folder: Path, done_folder: Path)`
- `process_documents(self) -> Iterator[ReceiptDocument]`
- `move_processed_document(self, document: ReceiptDocument) -> None`

**Usage**:
```python
from document_discovery.services import DocumentProcessingService

service = DocumentProcessingService(discovery, id_svc, dup_svc, val_svc, input, done)
for document in service.process_documents():
    if document.state == DocumentProcessingState.COMPLETED:
        service.move_processed_document(document)
```

**Processing Flow**:
1. Ensure folder structure exists
2. Discover documents in input folder
3. For each document:
   - Generate sequential ID
   - Calculate hash and check for duplicates
   - Validate document format and readability
   - Collect metadata
   - Manage state transitions

**Serves User Stories**: Story 1, 2, 3, 4, 5, 6, 7 (Main processing workflow)

## class DocumentProcessingFacade
**Module**: document_discovery.services
**Purpose**: Facade for document processing operations providing clean interface

**Methods**:
- `__init__(self, processing_service: DocumentProcessingService)`
- `process_all_documents(self) -> Iterator[DocumentProcessingResult]`
- `get_document_metadata(self, document_id: DocumentId) -> Optional[DocumentMetadata]`

**Usage**:
```python
from document_discovery.services import DocumentProcessingFacade

facade = DocumentProcessingFacade(processing_service)
for result in facade.process_all_documents():
    if result.success:
        # Pass to Financial Data Extraction
    else:
        # Handle error
```

**Serves User Stories**: Story 8 (Integration Interface for Dependent Features)

## class DocumentProcessingConfig
**Module**: document_discovery.config
**Purpose**: Configuration for document processing operations

**Properties**:
- `input_folder: Path`
- `done_folder: Path`
- `csv_file_path: Path`
- `supported_extensions: frozenset[str]`

**Methods**:
- `__init__(self, input_folder: Path = Path("input"), done_folder: Path = Path("done"), csv_file_path: Path = Path("receipts.csv"))`

**Usage**:
```python
from document_discovery.config import DocumentProcessingConfig

config = DocumentProcessingConfig()
# Use default values: input/, done/, receipts.csv
```

**Default Values**:
- input_folder: `Path("input")`
- done_folder: `Path("done")`
- csv_file_path: `Path("receipts.csv")`
- supported_extensions: `{'.pdf', '.jpg', '.jpeg', '.png'}`

**Serves User Stories**: Story 1 (Document Discovery and Folder Management)

## Test Instructions

**Test Scenarios**:
- Folder creation when folders don't exist
- Permission error handling during folder creation
- Discovery of supported file formats
- Skipping of unsupported file formats
- Empty folder handling
- Document processing workflow integration
- File movement to done folder

**Expected Behaviors**:
- DocumentDiscoveryService creates folders if missing
- DocumentDiscoveryService raises FolderCreationError on permission issues
- DocumentProcessingService processes documents sequentially
- DocumentProcessingFacade provides clean integration interface

**Mock Requirements**:
- Mock file system operations for folder creation
- Mock file discovery for various scenarios
- Mock dependent services for workflow testing

## Dependencies and Integration

**Package Dependencies**:
- receipt_document_processing: Core domain models and services
- document_validation: Document validation service
- Standard library: `pathlib`, `logging`, `typing`

**Integration Points**:
- Uses: SequentialIdService, DuplicateDetectionService from receipt_document_processing
- Uses: DocumentValidationService from document_validation
- Provides: Main processing workflow for dependent features

**User Story Cross-References**:
- Story 1: DocumentDiscoveryService, DocumentProcessingConfig
- Stories 1-7: DocumentProcessingService (main workflow)
- Story 8: DocumentProcessingFacade (integration interface)