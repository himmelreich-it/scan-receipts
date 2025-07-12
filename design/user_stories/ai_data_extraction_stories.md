# User Stories: AI Data Extraction Feature

**Feature Code**: AI_EXTRACT_G7H8  
**Feature Description**: Integrates with Anthropic's Claude API to extract structured financial data from receipt images. Extracts amount, tax, description, currency, date, and generates confidence scores for each processed receipt using the anthropic Python library.  
**Dependencies**: Hard - Receipt Image Processing [RECEIPT_IMG_E5F6]  
**Implementation Specification**: design/implementation/ai_extraction_implementation_spec.md

---

## Story 1: Core Receipt Data Extraction
**Status**: IMPLEMENTED

**Story Title**: Extract Financial Data from Receipt Images Using Claude API  
**Code**: EXTRACT_DATA_A1B2  
**Functional Description**: Sends receipt images to Anthropic's Claude API for analysis and extracts structured financial data including amount, tax, description, currency, date, and confidence scores. Uses claude-sonnet-4-20250514 model with thinking for high-quality extraction.

**Acceptance Criteria**:
- When a valid receipt image (PDF, JPG, PNG) is processed, send image to Claude API using claude-sonnet-4-20250514 model with thinking enabled
- When Claude API returns successful response, extract exactly these fields: amount (float), tax (float), description (string), currency (string), date (string in dd-MM-YYYY format), confidence (integer 0-100)
- When extracted data is valid, return structured data object with all required fields populated
- When date extraction succeeds, format date as dd-MM-YYYY (e.g., "15-03-2024")
- When currency is detected, return standard currency code (EUR, USD, GBP, etc.)
- When tax amount is not separately listed on receipt, return 0 for tax field
- When confidence score is generated, ensure it's integer between 0-100
- When API call completes successfully, log extraction results to console showing confidence score and key extracted values

**Technical Notes**:
- Use `anthropic` Python library for API integration
- Configure with claude-sonnet-4-20250514 model and enable thinking mode
- Convert PDFs to PNG format (first page only) before API submission using pdf2image
- Implement proper image encoding for API submission (base64 for images)
- Structure prompt to request specific JSON schema output
- Handle different image formats (JPG, PNG) and PDF conversion appropriately
- Implement retry logic for transient API failures (3 attempts with exponential backoff)

**Dependencies**: Receipt Image Processing [RECEIPT_IMG_E5F6] must provide valid image data

**Data Requirements**:
- Input: Image file data (bytes) and file metadata
- Output: Structured data object with fields: amount, tax, description, currency, date, confidence
- API Configuration: Model name, API key, timeout settings
- Logging: Extraction results and confidence scores

**Error Scenarios**: API failures, malformed responses, missing required fields in API response

---

## Story 2: Comprehensive Error Handling for AI Extraction
**Status**: IMPLEMENTED

**Story Title**: Handle AI Extraction Failures with Specific Error Categorization  
**Code**: EXTRACT_ERROR_C3D4  
**Functional Description**: Provides robust error handling for AI extraction failures, categorizing different types of errors for troubleshooting and creating appropriate error entries with confidence 0 and specific error descriptions.

**Acceptance Criteria**:
- When Claude API returns rate limit error (429), create error entry with description "ERROR-API", confidence 0, and log "Rate limit exceeded for file [filename]"
- When Claude API returns authentication error (401/403), create error entry with description "ERROR-API", confidence 0, and log "Authentication failed for file [filename]"
- When Claude API returns network/connection error, create error entry with description "ERROR-API", confidence 0, and log "Network error for file [filename]: [error details]"
- When image file is corrupted or unreadable, create error entry with description "ERROR-FILE", confidence 0, and log "Corrupted file: [filename]"
- When image file format is unsupported, create error entry with description "ERROR-FILE", confidence 0, and log "Unsupported format: [filename]"
- When Claude API returns malformed JSON response, create error entry with description "ERROR-PARSE", confidence 0, and log "Invalid API response for file [filename]"
- When Claude API response missing required fields, create error entry with description "ERROR-PARSE", confidence 0, and log "Incomplete extraction data for file [filename]"
- When unexpected error occurs not covered above, create error entry with description "ERROR-UNKNOWN", confidence 0, and log "Unexpected error for file [filename]: [error details]"
- When any error occurs, continue processing remaining files without stopping execution
- When error entry is created, populate amount=0, tax=0, currency="", date="" for consistency

**Technical Notes**:
- Implement comprehensive exception handling around API calls
- Distinguish between different HTTP error codes from Claude API
- Use try-catch blocks to categorize unexpected errors
- Ensure error entries follow same data structure as successful extractions
- Log all errors to console with sufficient detail for troubleshooting
- Maintain processing flow continuation after errors

**Dependencies**: Receipt Image Processing [RECEIPT_IMG_E5F6] for file validation

**Data Requirements**:
- Error Entry Structure: same fields as successful extraction but with error values
- Error Logging: Error type, filename, error details, timestamp
- Error Categories: ERROR-API, ERROR-FILE, ERROR-PARSE, ERROR-UNKNOWN

**Error Scenarios**: All error scenarios are the primary focus of this story - API failures, file corruption, parsing failures, unexpected errors

---

## Implementation Notes

### API Integration Requirements
- Library: `anthropic` Python library
- Model: claude-sonnet-4-20250514 with thinking enabled
- Authentication: API key configuration
- Rate Limiting: Implement backoff strategy for 429 errors
- Timeout: Configure appropriate API timeout (30 seconds recommended)

### Data Schema
```json
{
  "amount": "float",
  "tax": "float", 
  "description": "string",
  "currency": "string",
  "date": "string (dd-MM-YYYY format)",
  "confidence": "integer (0-100)"
}
```

### Error Handling Matrix
| Error Type | Description Value | Use Case |
|------------|------------------|----------|
| ERROR-API | Rate limits, auth, network failures | API-related issues |
| ERROR-FILE | Corrupted, unreadable, unsupported files | File processing issues |
| ERROR-PARSE | Malformed JSON, missing fields | Response parsing issues |
| ERROR-UNKNOWN | Unexpected failures | Catch-all for unforeseen errors |

### Console Logging Requirements
- Successful extractions: Log confidence score and key extracted values
- Error cases: Log specific error type, filename, and error details
- Continue processing: Never halt execution due to individual file failures

---

## Complete Feature Implementation Results

- **Feature Name**: AI Data Extraction
- **Stories Implemented**: EXTRACT_DATA_A1B2, EXTRACT_ERROR_C3D4
- **Files Created**: 
  - Domain: `src/ai_extraction/domain/{models,services,exceptions}/`
  - Infrastructure: `src/ai_extraction/infrastructure/{api,config}/`
  - Application: `src/ai_extraction/application/`
  - Tests: `tests/unit/test_ai_extraction/` and `tests/integration/test_ai_extraction/`
- **Architecture**: DDD-based with clean separation of domain, infrastructure, and application layers
- **Public APIs**: `ExtractionFacade.extract_from_image()`, `ExtractionFacade.extract_from_images()`
- **Integration Points**: Value objects for data exchange, no exceptions thrown (error as data pattern)
- **Test Coverage**: Unit: 25 tests, Integration: 4 tests, End-to-End: Full workflow validation
- **All Acceptance Criteria**: PASS - Both user stories fully implemented and tested
- **Feature Validation**: PASS - Complete feature ready for integration with other components