# User Stories: CSV Data Output Feature

**Feature Code**: CSV_OUTPUT_I9J0  
**Feature Description**: Converts AI-extracted data into CSV format with fields: ID, Amount, Tax, TaxPercentage, Description, Currency, Date, Confidence, Hash, DoneFilename. Manages CSV file creation, header addition, and append operations with auto-incrementing ID generation.  
**Dependencies**: Hard - AI Data Extraction [AI_EXTRACT_G7H8]  

---

## Story 1: CSV File Creation and Management
**Story Title**: Create and Manage CSV Output File with Proper Headers  
**Code**: CSV_CREATE_K1L2  
**Functional Description**: Creates receipts.csv file with proper headers and manages file lifecycle including creation when missing, header validation, and append mode operations for continuous data accumulation.

**Acceptance Criteria**:
- When receipts.csv file does not exist, create new file with headers: "ID,Amount,Tax,TaxPercentage,Description,Currency,Date,Confidence,Hash,DoneFilename"
- When receipts.csv file exists, validate headers match expected format exactly
- When headers are incorrect or missing, recreate file with correct headers and log warning to console
- When file is created successfully, log "Created receipts.csv with headers" to console
- When file already exists with correct headers, log "Using existing receipts.csv file" to console
- When file cannot be created due to permissions, log error "Cannot create receipts.csv: [error details]" and exit with code 1
- When file is corrupted or unreadable, log error "CSV file corrupted: [error details]" and exit with code 1

**Technical Notes**:
- Use Python's csv module for file operations
- Implement file existence checking before creation
- Validate CSV structure and headers on startup
- Handle file permission and corruption scenarios
- Use UTF-8 encoding for international character support

**Dependencies**: None (creates foundation for other CSV operations)

**Data Requirements**:
- CSV Headers: ID, Amount, Tax, TaxPercentage, Description, Currency, Date, Confidence, Hash, DoneFilename
- File Location: Root directory (same level as script)
- File Format: CSV with comma separation
- Encoding: UTF-8

**Error Scenarios**: File permission denied, disk space full, file corruption, invalid headers

---

## Story 2: Data Record Appending with Auto-Incrementing IDs
**Story Title**: Append Extracted Data to CSV with Sequential ID Generation  
**Code**: CSV_APPEND_M3N4  
**Functional Description**: Appends AI-extracted receipt data to CSV file with auto-incrementing ID numbers, ensuring data consistency and proper formatting for all field types including error entries.

**Acceptance Criteria**:
- When first record is added to new CSV file, assign ID = 1
- When records already exist, read last ID from CSV and increment by 1 for new record
- When extracted data is provided, format and append record with fields: ID, Amount, Tax, TaxPercentage, Description, Currency, Date, Confidence, Hash, DoneFilename
- When amount field is float, format to 2 decimal places (e.g., "15.50")
- When tax field is float, format to 2 decimal places (e.g., "2.50")
- When tax_percentage field is float, format to 2 decimal places (e.g., "16.00")
- When description contains commas or quotes, properly escape for CSV format
- When date is in dd-MM-YYYY format, preserve exact format in CSV
- When confidence is integer, store as-is (e.g., "85")
- When hash is provided, store as-is (e.g., "abc123def456")
- When done filename is provided, store full filename with timestamp (e.g., "1-20240315-142530123456-receipt.pdf")
- When record is successfully appended, log "Added record ID [ID] for file [original_filename]" to console
- When CSV write fails, log error "Failed to write record: [error details]" and continue processing

**Technical Notes**:
- Read existing CSV to determine next ID number
- Handle concurrent access protection if needed
- Format numeric fields consistently (2 decimal places for currency)
- Implement proper CSV escaping for text fields
- Ensure atomic write operations to prevent corruption
- Handle large files efficiently for ID determination

**Dependencies**: CSV_CREATE_K1L2 (must have valid CSV file structure)

**Data Requirements**:
- Input: Extracted data object with all required fields
- ID Generation: Auto-incrementing integer starting at 1
- Field Formatting: Specific format requirements for each field type
- File Output: Properly formatted CSV record appended to file

**Error Scenarios**: File write failures, ID determination failures, data formatting errors

---

## Story 3: Error Entry Recording and Data Validation
**Story Title**: Record Error Entries and Validate Data Consistency  
**Code**: CSV_ERROR_O5P6  
**Functional Description**: Handles recording of error entries from failed AI extractions, validates data consistency, and ensures all CSV records maintain proper format regardless of source (successful extraction or error).

**Acceptance Criteria**:
- When error data is provided (confidence = 0, description starts with "ERROR"), create CSV record with all fields populated
- When error entry amount is 0, format as "0.00" in CSV
- When error entry tax is 0, format as "0.00" in CSV  
- When error entry tax_percentage is 0, format as "0.00" in CSV
- When error entry description is "ERROR-API", "ERROR-FILE", "ERROR-PARSE", or "ERROR-UNKNOWN", store exactly as provided
- When error entry currency is empty string, store as empty field in CSV
- When error entry date is empty string, store as empty field in CSV
- When error entry confidence is 0, store as "0" in CSV
- When hash is provided for error entry, store hash value as-is
- When done filename is provided for error entry, store with same timestamp format as successful entries
- When data validation fails for any field, log warning "Data validation warning for ID [ID]: [field] = [value]" but continue processing
- When all error entry fields are recorded, log "Added error record ID [ID] for file [original_filename]: [error_type]"

**Technical Notes**:
- Ensure error entries follow same CSV structure as successful entries
- Validate all field types before writing to CSV
- Handle empty fields appropriately (empty strings vs zeros)
- Maintain data consistency across all record types
- Implement field validation without blocking processing

**Dependencies**: CSV_APPEND_M3N4 (uses same append mechanism)

**Data Requirements**:
- Error Entry Fields: Same structure as successful extraction but with error values
- Field Validation: Type checking and format validation for each field
- Consistency Rules: Ensure error entries match expected CSV format
- Logging: Record error entry creation with appropriate detail

**Error Scenarios**: Data validation failures, inconsistent field formats, CSV structure violations

---

## Implementation Notes

### CSV Structure
```
ID,Amount,Tax,TaxPercentage,Description,Currency,Date,Confidence,Hash,DoneFilename
1,15.50,2.50,16.00,Coffee Shop ABC,EUR,15-03-2024,95,abc123def456,1-20240315-142530123456-receipt.pdf
2,0.00,0.00,0.00,ERROR-FILE,,,,def789ghi012,2-20240315-142645789012-corrupted.jpg
```

### Field Formatting Requirements
- **ID**: Integer, auto-incrementing from 1
- **Amount**: Float formatted to 2 decimal places (e.g., "15.50")
- **Tax**: Float formatted to 2 decimal places (e.g., "2.50") 
- **TaxPercentage**: Float formatted to 2 decimal places (e.g., "16.00")
- **Description**: String, CSV-escaped if contains commas/quotes
- **Currency**: String, standard currency codes (EUR, USD, etc.)
- **Date**: String in dd-MM-YYYY format (e.g., "15-03-2024")
- **Confidence**: Integer 0-100 (e.g., "95")
- **Hash**: String, file hash for duplicate detection
- **DoneFilename**: String, timestamped filename in done folder

### Error Handling Strategy
- Continue processing if individual record write fails
- Log all errors and warnings to console
- Maintain data consistency across all record types
- Handle file corruption and permission issues gracefully
- Never halt processing due to CSV-related failures

### ID Management
- Read last record from existing CSV to determine next ID
- Handle empty CSV files (start with ID = 1)
- Ensure sequential numbering across all record types
- Protect against ID conflicts in concurrent scenarios

---