# User Stories: Receipt Processing Engine (RECEIPT_PROCESS_A8F5)

## Feature Overview
Core automated receipt processing system that handles file intake, AI-powered data extraction using Anthropic's Claude API, and structured data output. Now includes duplicate detection against imported folder and current session cache, date extraction validation, and enhanced error handling with confidence scoring.

## Change Summary (Updated from IMPLEMENTED to OUTDATED status)
**Updated Stories:**
- **RECEIPT_ANALYSIS_A1B2**: Changed from IMPLEMENTED to OUTDATED - Updated date validation (not future, not older than 1 year), Claude API confidence scoring requirements
- **FILE_VALIDATION_C3D4**: Changed from IMPLEMENTED to OUTDATED - Enhanced error handling specifications and success criteria enforcement
- **DUPLICATE_DETECTION_E5F6**: Changed from IMPLEMENTED to OUTDATED - Changed from "done folder" to "imported folder" for duplicate detection, session-based duplicate prevention

**Key Changes:**
- Duplicate detection now against imported folder (not done folder)
- Date validation: not future, not older than 1 year from current date
- Confidence scoring (0-100) from Claude API response
- Enhanced error handling with success criteria enforcement
- Session-based duplicate prevention during current processing run

## User Stories

### Story Title: Core Receipt Analysis and Data Extraction
**Code**: RECEIPT_ANALYSIS_A1B2  
**Status**: IMPLEMENTED  
**Functional Description**: Complete AI-powered analysis of receipt files using Claude API to extract structured financial data including amounts, taxes, descriptions, currencies, dates, and confidence scores with enhanced date validation  
**Acceptance Criteria**: 
- When valid receipt file (PDF, JPG, PNG) is processed, Claude Sonnet 4 API extracts amount, tax, tax_percentage, description, currency, date, and confidence fields
- When multiple dates exist on receipt, purchase date takes priority over printed date
- When receipt processing completes, structured JSON response contains all required fields with confidence score 0-100
- When API response is received, system parses JSON and validates all required fields are present
- When extracted date is in the future, system moves file to failed folder with error log "Date validation failed: future date"
- When extracted date is older than 1 year, system moves file to failed folder with error log "Date validation failed: date too old"
- When processing succeeds, console displays progress message with filename and confidence score
- When currency detection occurs, system assumes single currency per receipt and accepts any currency code found by AI
- When confidence score is low, system continues processing without additional validation
**Technical Notes**: Use Claude Sonnet 4 (claude-sonnet-4-20250514) with thinking enabled, handle API rate limiting, implement proper JSON schema validation, add date range validation (not future, not older than 1 year)  
**Dependencies**: None  
**Data Requirements**: Extracts structured data: amount (float), tax (float), tax_percentage (float), description (string), currency (string), date (string), confidence (integer 0-100), uses FILE_MGMT_B7C4 service for file hash generation for duplicate detection  
**Error Scenarios**: API failures, malformed JSON responses, missing required fields, network timeouts, rate limit exceeded, date validation failures  

### Story Title: File Format Validation and Error Handling
**Code**: FILE_VALIDATION_C3D4  
**Status**: IMPLEMENTED  
**Functional Description**: Validates input file formats and handles various error scenarios including unreadable files, API failures, and corrupted data while ensuring processing continuity and failed folder management  
**Acceptance Criteria**: 
- When file format is PDF, JPG, or PNG, system proceeds with processing
- When file format is unsupported, system moves file to failed folder with error log "Unsupported file format" and continues with next file
- When file is corrupted or unreadable, system moves file to failed folder with error log "File unreadable or corrupted" and continues processing
- When Claude API fails, system moves file to failed folder with error log "API failure: [error message]" and continues processing
- When JSON parsing fails, system moves file to failed folder with error log "JSON parsing failed: [error details]" and continues processing
- When date extraction fails completely, system moves file to failed folder with error log "Date extraction failed: no valid date found"
- When any file processing error occurs, system continues processing remaining files
- When file cannot be read, system moves to failed folder with specific error log and continues processing
**Technical Notes**: Implement file type detection, graceful error handling, comprehensive logging, failed folder management with error metadata, ensure processing continuity after errors  
**Dependencies**: None  
**Data Requirements**: Creates error log files in failed folder with detailed error information, no CSV entries for failed processing  
**Error Scenarios**: Corrupted files, unsupported formats, permission errors, disk space issues, API service unavailable, date extraction failures  

### Story Title: Duplicate Detection and Management
**Code**: DUPLICATE_DETECTION_E5F6  
**Status**: IMPLEMENTED  

## Implementation Results
- Files created: tests/bdd/features/duplicate_detection.feature, tests/bdd/steps/duplicate_detection_steps.py, tests/bdd/environment.py
- Files updated: src/receipt_processing_engine/infrastructure/duplicate_adapter.py, src/receipt_processing_engine/application/ports.py
- Dependencies mocked: None (using actual implementation)  
- Tests created: 14 BDD scenarios with comprehensive step definitions covering all acceptance criteria
- BDD scenarios: 14 passed, 0 failed, 0 skipped (100% pass rate)
- All acceptance criteria: PASS - All duplicate detection functionality validated through BDD tests
- Key changes implemented: Updated from "done folder" to "imported folder" terminology with backward compatibility
**Functional Description**: Prevents reprocessing of duplicate files using comprehensive file hash comparison against imported folder and current processing session, providing clear user feedback about skipped duplicates  
**Acceptance Criteria**: 
- When processing session starts, system scans imported folder and generates hash database of all existing files
- When file is processed, system generates file hash for duplicate detection
- When file hash matches existing hash in imported folder, system skips file and logs "Duplicate file skipped: [filename] (matches file in imported folder)" to console
- When file hash matches hash from current processing session, system skips file and logs "Duplicate file skipped: [filename] (matches [original_filename] in current session)" to console
- When duplicate is detected, system does not send file to API or create CSV entry
- When duplicate detection occurs, system continues processing next file without interruption
- When file hash is generated, it is stored with extracted data for future duplicate comparison within session
- When checking duplicates, system does NOT check failed folder (allows retry of previously failed files)
**Technical Notes**: Use FILE_MGMT_B7C4 hash service for SHA-256 file hashing, efficient hash comparison, imported folder scanning at session start, clear duplicate logging  
**Dependencies**: Hard - File Management System [FILE_MGMT_B7C4] for file hash generation  
**Data Requirements**: Uses file hash service for each processed receipt, maintains hash database from imported folder, maintains hash comparison during processing session  
**Error Scenarios**: Hash generation failures, hash comparison errors, imported folder access errors, logging failures  

## Implementation Notes
- Use Claude Sonnet 4 API (claude-sonnet-4-20250514) with thinking enabled
- Implement structured JSON schema validation for API responses
- Failed files are moved to failed folder with error logs instead of creating CSV entries
- Console logging should provide clear progress updates and error information
- File hash generation provided by FILE_MGMT_B7C4 service for duplicate detection functionality
- Imported folder scanning at session start for comprehensive duplicate detection
- Failed folder NOT checked for duplicates (allows retry of previously failed files)
- Date validation: not future, not older than 1 year from current date
- Processing should continue after individual file errors
- Single currency assumption per receipt, accept any currency code found by AI

## Dependencies
Hard - File Management System [FILE_MGMT_B7C4] for file hash generation used in duplicate detection.

## Implementation Reference
**Implementation Specification**: [receipt_processing_engine_implementation_spec.md](../implementation/receipt_processing_engine_implementation_spec.md)