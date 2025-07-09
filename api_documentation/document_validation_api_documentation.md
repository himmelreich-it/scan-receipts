# Document Validation API Documentation

## Package: document_validation
**Package Path**: `document_validation/`
**Purpose**: Document validation and format checking for receipt documents

**Modules**:
- document_validation.services (Document validation services)
- document_validation.validators (Specific validation implementations)

**Dependencies**: 
- receipt_document_processing (for ReceiptDocument entity)
- Standard library: `pathlib`, `logging`

**User Stories Served**: Story 4 (Document File Reading and Validation), Story 7 (Error Handling and Recovery)

## class DocumentValidationService
**Module**: document_validation.services
**Purpose**: Service for validating receipt documents before processing

**Methods**:
- `__init__(self)`
- `validate_document(self, document: ReceiptDocument) -> bool`

**Usage**:
```python
from document_validation.services import DocumentValidationService

service = DocumentValidationService()
if service.validate_document(document):
    # Document is valid for processing
else:
    # Handle validation failure
```

**Validation Checks**:
- Supported file format (PDF, JPG, JPEG, PNG)
- File exists and is readable
- File can be opened without corruption

**Serves User Stories**: Story 4 (Document File Reading and Validation)

## class FormatValidator
**Module**: document_validation.validators
**Purpose**: Validates document file format

**Methods**:
- `__init__(self, supported_extensions: frozenset[str])`
- `is_supported_format(self, file_path: Path) -> bool`

**Usage**:
```python
from document_validation.validators import FormatValidator

validator = FormatValidator({'.pdf', '.jpg', '.jpeg', '.png'})
if validator.is_supported_format(Path("receipt.pdf")):
    # Format is supported
```

**Serves User Stories**: Story 4 (Document File Reading and Validation)

## class FileAccessValidator
**Module**: document_validation.validators
**Purpose**: Validates file accessibility and readability

**Methods**:
- `__init__(self)`
- `can_read_file(self, file_path: Path) -> bool`
- `file_exists(self, file_path: Path) -> bool`

**Usage**:
```python
from document_validation.validators import FileAccessValidator

validator = FileAccessValidator()
if validator.can_read_file(Path("receipt.pdf")):
    # File is readable
```

**Serves User Stories**: Story 4 (Document File Reading and Validation)

## class DocumentContentValidator
**Module**: document_validation.validators
**Purpose**: Validates document content can be read

**Methods**:
- `__init__(self)`
- `can_read_content(self, file_path: Path) -> bool`

**Usage**:
```python
from document_validation.validators import DocumentContentValidator

validator = DocumentContentValidator()
if validator.can_read_content(Path("receipt.pdf")):
    # Content is readable
```

**Serves User Stories**: Story 4 (Document File Reading and Validation)

## class ValidationError
**Module**: document_validation.services
**Purpose**: Exception for validation failures

**Properties**:
- `message: str`
- `file_path: Optional[Path]`

**Methods**:
- `__init__(self, message: str, file_path: Optional[Path] = None)`

**Usage**:
```python
from document_validation.services import ValidationError

try:
    # Validation logic
    pass
except ValidationError as e:
    print(f"Validation failed: {e.message}")
```

**Serves User Stories**: Story 7 (Error Handling and Recovery)

## Test Instructions

**Test Scenarios**:
- Supported format validation for PDF, JPG, JPEG, PNG files
- Unsupported format rejection
- File existence checking
- File readability validation
- Content accessibility testing
- Error handling for corrupted files
- Error handling for permission issues

**Expected Behaviors**:
- DocumentValidationService returns True for valid documents
- DocumentValidationService returns False for invalid documents
- FormatValidator correctly identifies supported formats
- FileAccessValidator handles permission errors gracefully
- DocumentContentValidator detects corrupted files

**Mock Requirements**:
- Mock file system operations for existence checks
- Mock file reading operations for content validation
- Mock permission errors for error handling tests

## Dependencies and Integration

**Package Dependencies**:
- receipt_document_processing: ReceiptDocument entity
- Standard library: `pathlib`, `logging`, `typing`

**Integration Points**:
- Used by: DocumentProcessingService from document_discovery
- Provides: Validation services for document processing workflow

**User Story Cross-References**:
- Story 4: DocumentValidationService, FormatValidator, FileAccessValidator, DocumentContentValidator
- Story 7: ValidationError and error handling patterns