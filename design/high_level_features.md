# High-Level Features for Receipt Processor

## Feature: Receipt Processing Engine
**Code**: RECEIPT_PROCESS_A8F5  
**Status**: OUTDATED
**Description**: Core automated receipt processing system that handles file intake, AI-powered data extraction using Anthropic's Claude API, and structured data output. Now includes duplicate detection against imported folder and current session cache, date extraction validation, and enhanced error handling with confidence scoring.
**Implementation Scope**:
- File format support (PDF, JPG, PNG)
- Integration with Anthropic Claude API for data extraction
- Required field extraction (Amount, Currency, Date) with validation
- Optional field extraction (Tax, Tax Percentage, Description)
- Hash-based duplicate detection against imported folder (using FILE_MGMT_B7C4 hash service)
- Session-based duplicate prevention during current processing run
- Date extraction validation with failure handling for invalid dates
- Confidence scoring (0-100) for extraction quality
- Error handling for unreadable files, API failures, and corrupted files
- Success criteria enforcement for required fields

**Dependencies**: Hard - File Management System [FILE_MGMT_B7C4] for file hash generation

**User Stories**: design/user_stories/receipt_processing_engine.md

## Feature: File Management System
**Code**: FILE_MGMT_B7C4  
**Status**: IMPLEMENTED
**Description**: Complete file organization system managing the four-folder structure (incoming, scanned, imported, failed) with proper naming conventions and persistence rules. Handles file movement through the processing pipeline while maintaining data integrity and supporting manual file management.
**Implementation Scope**:
- Incoming folder management (never cleared, allows re-processing)
- Scanned folder management (cleared at start of analysis, populated during processing)
- Imported folder management (persistent, never cleared, sequential naming)
- Failed folder management (persistent, with error logs, allows manual retry)
- Naming conventions: scanned uses {yyyyMMdd}-{description}.{ext}, imported uses {number}-{yyyyMMdd}-{description}.{ext}
- File hash generation for duplicate detection
- Automatic folder creation if missing
- Support for manual file organization by users

**Dependencies**: None

**User Stories**: design/user_stories/file_management_system.md

## Feature: CSV Data Staging
**Code**: CSV_STAGING_C9D3  
**Status**: NEW
**Description**: Structured data staging system that converts extracted receipt information into CSV format for review before final import. Provides data organization, validation, and preview functionality with date-based sorting and proper field mapping.
**Implementation Scope**:
- CSV file creation with proper headers (Amount, Tax, TaxPercentage, Description, Currency, Date, Confidence, Hash, DoneFilename)
- Date-based sorting (ascending by date, then time, then description)
- Date formatting in dd-MM-YYYY format
- DoneFilename generation for imported folder target naming
- CSV clearing/recreation on each analysis run
- Data validation and integrity checks
- Only successful extractions included (no failed or duplicate entries)

**Dependencies**: Hard - Receipt Processing Engine [RECEIPT_PROCESS_A8F5]

## Feature: XLSX Integration System
**Code**: XLSX_INTEGRATION_X1Y2  
**Status**: NEW
**Description**: Complete XLSX file management system that handles import validation, sequential numbering, and data persistence to the business source of truth. Manages the final import stage with proper validation, formatting, and append-only behavior.
**Implementation Scope**:
- XLSX structure management with data starting from row 11
- Column mapping (A: Numbering, B: Purchase Date, C: Description, J: Total amount, K: VAT Amount, S: Notes)
- Sequential numbering starting from last XLSX entry + 1 (or 1 if empty)
- Date formatting conversion from dd-MM-YYYY to d-MMM-yy format
- Currency handling with non-EUR notes in column S
- Validation checks ensuring no XLSX entries without corresponding files in imported folder
- Append-only import behavior preserving existing data
- File synchronization between XLSX entries and imported folder

**Dependencies**: Hard - CSV Data Staging [CSV_STAGING_C9D3], File Management System [FILE_MGMT_B7C4]

## Feature: Terminal User Interface and Workflow Control
**Code**: TUI_WORKFLOW_T3U4  
**Status**: NEW
**Description**: Complete terminal-based user interface providing menu-driven interaction, step-by-step workflow control, and comprehensive status monitoring. Manages the entire receipt processing workflow with user control at each stage and clear feedback on system state.
**Implementation Scope**:
- Startup screen showing file counts (incoming, failed) and staging status
- Configuration validation on startup
- Automatic folder creation for missing directories
- Fixed menu with four options: Run Analysis, Import to XLSX, View Staging Table, Exit
- Three main workflow options with appropriate error messages when unavailable
- Real-time progress display during AI analysis with file-by-file updates
- Staging table display with formatted data preview
- Validation status display for staging readiness
- User confirmation for destructive actions (clearing scanned folder)
- Error handling with user-friendly messages and recovery options
- Progress tracking with counts and statistics

**Dependencies**: Soft - Receipt Processing Engine [RECEIPT_PROCESS_A8F5], File Management System [FILE_MGMT_B7C4], CSV Data Staging [CSV_STAGING_C9D3], XLSX Integration System [XLSX_INTEGRATION_X1Y2]

## Feature: Configuration Management
**Code**: CONFIG_MGMT_F5G6  
**Status**: NEW
**Description**: Environment-based configuration system managing all file paths and system settings through .env file configuration. Provides flexible deployment options and proper error handling for missing or invalid configurations.
**Implementation Scope**:
- Environment variable management for all folder paths
- INCOMING_RECEIPTS_FOLDER, SCANNED_FOLDER, IMPORTED_FOLDER, FAILED_FOLDER configuration
- XLSX_OUTPUT_FILE and CSV_STAGING_FILE path management
- Error handling for invalid paths or permission issues
- Default value handling where appropriate

**Dependencies**: None

**User Stories**: design/user_stories/configuration_management.md

## Feature: Data Validation and Quality Assurance
**Code**: DATA_VALIDATION_V7W8  
**Status**: NEW
**Description**: Comprehensive validation system ensuring data integrity throughout the processing workflow. Provides multi-stage validation checks, quality scoring, and consistency verification between staging and final import with detailed error reporting.
**Implementation Scope**:
- Required field validation (Amount, Currency, Date) with extraction failure handling
- Date validation ensuring reasonable ranges and proper extraction
- Sequential numbering validation for XLSX import consistency
- Hash verification for duplicate prevention across imported folder
- Staging validation comparing receipts.csv entries with scanned folder files
- Confidence score integration for quality assessment
- File count validation ensuring staging accuracy
- Data integrity checks between CSV staging and XLSX import

**Dependencies**: Hard - Receipt Processing Engine [RECEIPT_PROCESS_A8F5], CSV Data Staging [CSV_STAGING_C9D3], XLSX Integration System [XLSX_INTEGRATION_X1Y2]

## Feature: Error Handling and Recovery System
**Code**: ERROR_HANDLING_E6F8  
**Status**: NEW
**Description**: Comprehensive error management system handling various failure scenarios while maintaining processing continuity. Provides detailed error logging, recovery options, and user guidance for failed processing with persistent error tracking.
**Implementation Scope**:
- Failed file management with detailed error logs (.log files)
- AI processing failure handling (API errors, extraction failures)
- File system error management (permissions, disk space, corruption)
- XLSX import error handling (file locks, validation failures, structure issues)
- Date extraction failure handling with detailed error messages
- Workflow recovery options (re-analysis, manual file movement)
- User-friendly error messages with actionable guidance
- Persistent error tracking in failed folder with overwrite behavior for retries

**Dependencies**: Hard - Receipt Processing Engine [RECEIPT_PROCESS_A8F5], File Management System [FILE_MGMT_B7C4], CSV Data Staging [CSV_STAGING_C9D3], XLSX Integration System [XLSX_INTEGRATION_X1Y2]