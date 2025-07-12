# AI Data Extraction - Implementation Specification

**Feature Code**: AI_EXTRACT_G7H8  
**User Stories**: design/user_stories/ai_data_extraction_stories.md  
**Implementation Date**: 2025-07-12  

## Package: ai_extraction

**Path**: `src/ai_extraction/`  
**Purpose**: Domain package for AI-powered receipt data extraction using Anthropic's Claude API  
**User Stories**: EXTRACT_DATA_A1B2, EXTRACT_ERROR_C3D4  
**Dependencies**: anthropic, pydantic, python-dotenv, pdf2image, pillow, receipt_image_processing  
**Design Decisions**: DDD-based architecture with custom exception hierarchy, environment-based configuration, hardcoded retry logic with exponential backoff, PDF-to-PNG conversion in infrastructure layer  

### Package Structure
```
src/ai_extraction/
├── __init__.py
├── domain/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── extraction_result.py     # Value objects for extracted data
│   │   └── extraction_request.py    # Value objects for request data
│   ├── services/
│   │   ├── __init__.py
│   │   └── extraction_service.py    # Domain service for extraction logic
│   └── exceptions/
│       ├── __init__.py
│       └── extraction_errors.py     # Custom exception hierarchy
├── infrastructure/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── claude_client.py         # Anthropic API client wrapper
│   └── config/
│       ├── __init__.py
│       └── settings.py              # Environment configuration
└── application/
    ├── __init__.py
    └── extraction_facade.py         # Application service/facade
```

## Architecture Overview

### Design Patterns Applied
- **Value Object Pattern**: For ReceiptData, ErrorReceiptData, and ImageExtractionRequest
- **Domain Service Pattern**: For ExtractionService orchestrating business logic
- **Facade Pattern**: For ExtractionFacade providing simplified external interface
- **Adapter Pattern**: For ClaudeApiClient wrapping external API
- **Exception Hierarchy Pattern**: For domain-specific error categorization
- **Settings Pattern**: For environment-based configuration management

### Component Relationships
```
ExtractionFacade → ExtractionService → ClaudeApiClient
       ↓                ↓                    ↓
Value Objects ← Domain Exceptions ← Infrastructure Config
```

## Interface Definitions

### 1. Domain Models

#### File: `src/ai_extraction/domain/models/extraction_result.py`
**Purpose**: Value objects representing extracted receipt data and results
**Libraries**: pydantic, typing, decimal, datetime
**Design Pattern**: Value Object pattern

**Interface Contracts:**

```python
class ReceiptData(BaseModel):
    """Value object for successfully extracted receipt data."""
    # Required fields with validation constraints
    amount: Decimal          # Total purchase amount
    tax: Decimal            # Tax amount, defaults to 0
    description: str        # Business name, max 500 chars
    currency: str           # 3-letter currency code
    date: str              # dd-MM-YYYY format
    confidence: int        # 0-100 range
    
    # Validation methods required:
    # - validate_date_format(): Ensure dd-MM-YYYY format
    # - validate_currency_code(): Ensure 3-letter uppercase

class ErrorReceiptData(BaseModel):
    """Value object for failed extraction with error categorization."""
    # Same structure as ReceiptData but with error defaults
    description: str  # Must be: ERROR-API, ERROR-FILE, ERROR-PARSE, ERROR-UNKNOWN
    
    # Validation methods required:
    # - validate_error_description(): Ensure valid error type

class ExtractionResult(BaseModel):
    """Container for extraction results with success/failure indication."""
    success: bool
    data: Optional[ReceiptData]
    error_data: Optional[ErrorReceiptData]
    filename: str
    processing_timestamp: datetime
    
    # Methods required:
    # - get_data() -> ReceiptData | ErrorReceiptData
```

#### File: `src/ai_extraction/domain/models/extraction_request.py`
**Purpose**: Value objects for extraction request data
**Libraries**: pydantic, pathlib

**Interface Contracts:**

```python
class ImageExtractionRequest(BaseModel):
    """Value object for image extraction request."""
    file_path: Path
    image_data: bytes
    mime_type: str  # Must support: image/jpeg, image/png, application/pdf
    
    # Validation methods required:
    # - validate_mime_type(): Ensure supported formats
    
    # Properties required:
    # - filename: str (derived from file_path)
```

### 2. Domain Exceptions

#### File: `src/ai_extraction/domain/exceptions/extraction_errors.py`
**Purpose**: Custom exception hierarchy for domain-specific errors
**Libraries**: Standard library only

**Exception Hierarchy Design:**

```python
ExtractionError (base)
├── ApiExtractionError       # Maps to ERROR-API
├── FileExtractionError      # Maps to ERROR-FILE  
├── ParseExtractionError     # Maps to ERROR-PARSE
└── UnknownExtractionError   # Maps to ERROR-UNKNOWN

# Each exception should support:
# - message: str
# - filename: str (optional)
# - original_error: Exception (optional)
```

### 3. Infrastructure Configuration

#### File: `src/ai_extraction/infrastructure/config/settings.py`
**Purpose**: Environment-based configuration management
**Libraries**: pydantic-settings, python-dotenv
**Design Pattern**: Settings pattern

**Configuration Structure:**

```python
class ClaudeApiSettings(BaseSettings):
    """Configuration for Anthropic Claude API."""
    
    # Required environment variables
    anthropic_api_key: str
    
    # Model configuration with defaults
    model_name: str = "claude-sonnet-4-20250514"
    enable_thinking: bool = True
    max_tokens: int = 2000
    
    # API configuration with defaults
    api_timeout: int = 30
    max_retries: int = 3
    base_backoff_delay: float = 1.0
    max_backoff_delay: float = 60.0
    
    # Configuration requirements:
    # - Use .env file loading
    # - Environment prefix: "CLAUDE_"
    # - Global settings instance available
```

### 4. Infrastructure API Client

#### File: `src/ai_extraction/infrastructure/api/claude_client.py`
**Purpose**: Anthropic API client wrapper with retry logic
**Libraries**: anthropic, base64, time, logging, pdf2image, pillow, io
**Design Pattern**: Adapter pattern with Retry pattern

**Interface Contracts:**

```python
class ClaudeApiClient:
    """Wrapper for Anthropic Claude API with retry logic and error handling."""
    
    def __init__(self):
        # Initialize Anthropic client with API key
        # Build extraction prompt template
    
    def extract_receipt_data(self, request: ImageExtractionRequest) -> Dict[str, Any]:
        """
        Extract receipt data using Claude API with retry logic.
        
        Args:
            request: Image extraction request with file data
            
        Returns:
            Parsed JSON response from Claude API
            
        Raises:
            ApiExtractionError: For API-related failures
            ParseExtractionError: For response parsing failures
            UnknownExtractionError: For unexpected errors
        """
        # Implementation requirements:
        # - 3 retry attempts with exponential backoff
        # - Handle specific HTTP error codes (429, 401, 403)
        # - Convert PDFs to PNG (first page only) before API submission
        # - Base64 encode images for API submission
        # - Use configured model with thinking enabled
        # - Parse and validate JSON response
        # - Map different error types to appropriate exceptions
```

**Key Algorithms:**
- **Retry Logic**: Exponential backoff starting at 1 second, max 60 seconds, 3 total attempts
- **Error Categorization**: Map HTTP status codes and exception types to domain exceptions
- **PDF Conversion**: Convert PDF to PNG using pdf2image (first page only, 300 DPI)
- **Image Encoding**: Base64 encode image data with proper MIME type headers (always image/png for converted PDFs)
- **Response Validation**: Ensure JSON contains required fields before returning

**Extraction Prompt Requirements:**
- Request specific JSON schema with exact field names
- Include guidelines for date formatting (dd-MM-YYYY)
- Specify confidence scoring approach (0-100)
- Handle tax extraction (0 if not separately listed)
- Request standard currency codes

**PDF Processing Requirements:**
- **Conversion Library**: Use pdf2image for PDF to PNG conversion
- **Page Selection**: Process only the first page of multi-page PDFs
- **Image Quality**: Convert at 300 DPI for optimal text recognition
- **Format Standardization**: Always convert to PNG format for consistency
- **Error Handling**: Map PDF conversion failures to FileExtractionError
- **Memory Management**: Convert one page at a time to minimize memory usage
- **Transparency**: Domain layer receives original PDF data, conversion is transparent infrastructure concern

**PDF Conversion Algorithm:**
```python
def convert_pdf_to_png(pdf_data: bytes) -> Tuple[bytes, str]:
    """
    Convert PDF to PNG format for Claude API submission.
    
    Args:
        pdf_data: Raw PDF file bytes
        
    Returns:
        Tuple of (png_bytes, "image/png")
        
    Raises:
        FileExtractionError: If PDF conversion fails
    """
    # Implementation:
    # 1. Use pdf2image.convert_from_bytes() with first_page=1, last_page=1
    # 2. Set DPI to 300 for optimal quality
    # 3. Convert PIL Image to PNG bytes using BytesIO
    # 4. Return PNG bytes and "image/png" MIME type
```

### 5. Domain Service

#### File: `src/ai_extraction/domain/services/extraction_service.py`
**Purpose**: Domain service orchestrating extraction logic and error handling
**Libraries**: logging
**Design Pattern**: Domain Service pattern

**Interface Contracts:**

```python
class ExtractionService:
    """Domain service for orchestrating receipt data extraction."""
    
    def __init__(self, api_client: ClaudeApiClient):
        # Store API client dependency
    
    def extract_receipt_data(self, request: ImageExtractionRequest) -> ExtractionResult:
        """
        Extract receipt data with comprehensive error handling.
        
        Args:
            request: Image extraction request
            
        Returns:
            ExtractionResult with success/failure indication and appropriate data
        """
        # Implementation requirements:
        # - Validate image request before processing
        # - Call API client for extraction
        # - Parse and validate API response into domain models
        # - Handle all exception types and map to error results
        # - Log successful extractions with key data
        # - Log specific error messages by category
        # - Always return ExtractionResult (never throw exceptions)
```

**Error Handling Strategy:**
- **File Validation**: Check for empty data, basic format validation for JPEG/PNG headers
- **API Response Validation**: Ensure all required fields present and valid types
- **Exception Mapping**: Convert infrastructure exceptions to domain exceptions, then to error results
- **Logging Requirements**: Log success with confidence and key values, log errors with specific categorization

### 6. Application Facade

#### File: `src/ai_extraction/application/extraction_facade.py`
**Purpose**: Application service providing simplified interface for extraction operations
**Libraries**: logging
**Design Pattern**: Facade pattern

**Interface Contracts:**

```python
class ExtractionFacade:
    """Application facade for AI receipt data extraction operations."""
    
    def __init__(self):
        # Initialize API client and extraction service
    
    def extract_from_image(self, request: ImageExtractionRequest) -> ExtractionResult:
        """Extract receipt data from a single image."""
        # Delegate to extraction service
        # Add application-level logging
    
    def extract_from_images(self, requests: List[ImageExtractionRequest]) -> List[ExtractionResult]:
        """Extract receipt data from multiple images sequentially."""
        # Process requests in order
        # Log batch processing summary
        # Return results maintaining input order
```

## Integration Specifications

### Main Application Integration Requirements
- **Public Interface**: ExtractionFacade provides main integration point
- **Data Exchange**: Uses ImageExtractionRequest and ExtractionResult value objects
- **Error Handling**: All errors converted to ExtractionResult with error_data, no exceptions thrown
- **Logging**: Application-level logging for batch operations, domain-level logging for individual extractions

### Configuration Requirements

**Environment Variables (.env):**
```env
CLAUDE_ANTHROPIC_API_KEY=your_api_key_here
CLAUDE_MODEL_NAME=claude-sonnet-4-20250514
CLAUDE_ENABLE_THINKING=true
CLAUDE_API_TIMEOUT=30
CLAUDE_MAX_TOKENS=2000
```

**Python Dependencies (pyproject.toml):**
```toml
[project.dependencies]
anthropic = "^0.31.0"
pydantic = "^2.7.0"
pydantic-settings = "^2.3.0"
python-dotenv = "^1.0.0"
pdf2image = "^1.17.0"
pillow = "^10.0.0"
```

### Integration Points

**With Receipt Image Processing:**
- Receives image data and metadata as ImageExtractionRequest
- File path, raw bytes, and MIME type required
- No direct coupling - uses value objects for data exchange

**With CSV Data Output:**
- Provides ReceiptData or ErrorReceiptData via ExtractionResult
- Maintains consistent data structure for both success and error cases
- Error descriptions compatible with CSV error handling requirements

**With Error Handling System:**
- Maps infrastructure errors to domain-specific error categories
- Provides detailed error logging for troubleshooting
- Continues processing after individual file failures

## Testing Requirements

### Unit Test Structure
```
tests/unit/test_ai_extraction/
├── test_domain/
│   ├── test_models/           # Test value object validation
│   ├── test_services/         # Test extraction service logic
│   └── test_exceptions/       # Test exception hierarchy
├── test_infrastructure/
│   ├── test_api/             # Test API client (mocked)
│   └── test_config/          # Test configuration loading
└── test_application/
    └── test_extraction_facade.py  # Test facade operations
```

### Integration Test Requirements
- Test complete extraction workflow with mocked API responses
- Test error handling for each error category
- Test configuration loading from environment variables
- Test retry logic with simulated API failures

### Test Data Requirements
- Valid receipt images for testing (JPEG, PNG, PDF samples)
- Expected API responses in JSON format
- Error response samples for each API failure type
- Environment variable configurations for testing

## Security Considerations

- **API Key Protection**: Store in environment variables, never in code or logs
- **Input Validation**: Validate all image data and request parameters
- **Error Sanitization**: Ensure error messages don't leak sensitive information
- **Rate Limiting**: Built-in retry logic respects API rate limits

## Performance Considerations

- **Sequential Processing**: Process one image at a time to manage memory usage
- **Timeout Handling**: 30-second timeout for API calls with configurable setting
- **Memory Management**: Process image data without storing multiple images in memory
- **API Efficiency**: Use appropriate max_tokens setting (2000) for detailed responses

## Implementation Notes

### User Story Coverage

**Story EXTRACT_DATA_A1B2**: Core Receipt Data Extraction
- Interface contracts for Claude API integration with specified model
- Data structures for all required fields with validation
- Confidence scoring and date formatting requirements
- Console logging specifications for extraction results
- Retry logic architecture (3 attempts, exponential backoff)

**Story EXTRACT_ERROR_C3D4**: Comprehensive Error Handling
- Exception hierarchy mapping to four error categories
- Error logging specifications with filename and context
- Error result creation maintaining consistent data structure
- Continue processing strategy after individual failures

### Key Implementation Decisions
1. **Domain-Driven Design**: Clear separation of concerns across layers
2. **Value Objects**: Immutable data structures with built-in validation
3. **Error as Data**: Convert all errors to result objects rather than exceptions
4. **Configuration Flexibility**: Environment-based settings with sensible defaults
5. **Logging Strategy**: Structured logging for monitoring and debugging
6. **API Integration**: Robust client with retry logic and comprehensive error handling

This specification provides architectural guidance for implementing the AI Data Extraction feature while allowing flexibility in the actual implementation details.