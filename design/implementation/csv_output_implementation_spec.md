# CSV Data Output - Implementation Specification

**Feature Code**: CSV_OUTPUT_I9J0  
**User Stories**: design/user_stories/csv_data_output_stories.md  
**Implementation Date**: 2025-07-12  

## Overview

**Purpose**: Simple service-based implementation for CSV file creation and management with auto-incrementing IDs, proper field formatting, and error handling.  
**Current State**: CSV file is removed at start of each run (one-off processing mode)  
**Required Changes**: Create new CSV functionality with all required fields  

## Implementation Strategy

### Simple Service Approach
- Single service class to handle all CSV operations
- Fresh CSV file created each run (no existing data to consider)
- Read entire CSV file for ID management during processing (small files)
- No concurrency handling needed
- Standard Python csv module

## Package: csv_output

**Path**: `src/csv_output/`  
**Dependencies**: csv (stdlib), os (stdlib), logging (stdlib)  
**Integration Point**: Standalone CSV creation and management service

### Package Structure
```
src/csv_output/
├── __init__.py
├── csv_service.py           # Main CSV operations service
└── config.py               # Simple configuration constants
```

## Interface Specifications

### 1. CSV Service

#### File: `src/csv_output/csv_service.py`
**Purpose**: Main service for CSV file operations with ID management
**Libraries**: csv, os, logging, typing

**Interface Contract:**

```python
class CsvService:
    """Service for managing CSV output file operations."""
    
    def __init__(self, csv_file_path: str = "receipts.csv"):
        """
        Initialize CSV service.
        
        Args:
            csv_file_path: Path to CSV file (default: receipts.csv)
        """
    
    def ensure_csv_exists(self) -> None:
        """
        Create new CSV file with correct headers.
        
        Always creates fresh file (assumes existing file removed by cleanup).
        
        Logs:
            - "Created receipts.csv with headers" on success
        
        Raises:
            SystemExit(1): If file cannot be created due to permissions
        """
    
    def get_next_id(self) -> int:
        """
        Get next auto-incrementing ID for new record.
        
        Returns:
            Next ID number (1 for new file, last_id + 1 for records added during current run)
        """
    
    def append_record(self, 
                     amount: float, 
                     tax: float, 
                     tax_percentage: float,
                     description: str, 
                     currency: str, 
                     date: str, 
                     confidence: int, 
                     hash_value: str, 
                     done_filename: str) -> int:
        """
        Append new record to CSV file with auto-generated ID.
        
        Args:
            amount: Purchase amount (formatted to 2 decimal places)
            tax: Tax amount (formatted to 2 decimal places)
            tax_percentage: Tax percentage (formatted to 2 decimal places)
            description: Business description (CSV-escaped if needed)
            currency: Currency code (e.g., EUR, USD)
            date: Date in dd-MM-YYYY format
            confidence: Confidence score 0-100
            hash_value: File hash for duplicate detection
            done_filename: Timestamped filename in done folder
        
        Returns:
            ID of the appended record
            
        Logs:
            - "Added record ID {id} for file {original_filename}" on success
            - "Failed to write record: {error}" on failure (continues processing)
        """
    
    def append_error_record(self, 
                           error_type: str, 
                           hash_value: str, 
                           done_filename: str) -> int:
        """
        Append error record to CSV file.
        
        Args:
            error_type: One of ERROR-API, ERROR-FILE, ERROR-PARSE, ERROR-UNKNOWN
            hash_value: File hash
            done_filename: Timestamped filename in done folder
        
        Returns:
            ID of the appended error record
            
        Creates record with:
            - amount: 0.00
            - tax: 0.00  
            - tax_percentage: 0.00
            - description: error_type
            - currency: "" (empty)
            - date: "" (empty)
            - confidence: 0
        """
    
    def _format_currency_field(self, value: float) -> str:
        """Format currency fields to 2 decimal places."""
    
    def _escape_csv_field(self, field: str) -> str:
        """Escape CSV field if contains commas or quotes."""
    
    def _validate_headers(self, existing_headers: list) -> bool:
        """Validate that existing headers match expected format."""
```

### 2. Configuration

#### File: `src/csv_output/config.py`
**Purpose**: Configuration constants for CSV operations

```python
# CSV Configuration
CSV_FILENAME = "receipts.csv"
CSV_HEADERS = [
    "ID", "Amount", "Tax", "TaxPercentage", "Description", 
    "Currency", "Date", "Confidence", "Hash", "DoneFilename"
]
CSV_ENCODING = "utf-8"

# Error Types
ERROR_API = "ERROR-API"
ERROR_FILE = "ERROR-FILE"
ERROR_PARSE = "ERROR-PARSE"
ERROR_UNKNOWN = "ERROR-UNKNOWN"
```

## Data Format Specifications

### CSV Headers
```
ID,Amount,Tax,TaxPercentage,Description,Currency,Date,Confidence,Hash,DoneFilename
```

### Field Formatting Rules
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

### Example Records
```csv
ID,Amount,Tax,TaxPercentage,Description,Currency,Date,Confidence,Hash,DoneFilename
1,15.50,2.50,16.00,Coffee Shop ABC,EUR,15-03-2024,95,abc123def456,1-20240315-142530123456-receipt.pdf
2,0.00,0.00,0.00,ERROR-FILE,,,,def789ghi012,2-20240315-142645789012-corrupted.jpg
```

## Integration Requirements

### Fresh CSV Creation
Each processing run starts with a clean CSV file:
```
Headers: ID,Amount,Tax,TaxPercentage,Description,Currency,Date,Confidence,Hash,DoneFilename
```

**Creation Strategy:**
1. CSV file removed by cleanup before processing starts
2. `ensure_csv_exists()` creates fresh file with correct headers
3. No migration needed - always starting fresh

### Integration with AI Extraction
**Data Source**: AI extraction provides ReceiptData/ErrorReceiptData  
**Missing Fields to Calculate:**
- `TaxPercentage`: Calculate from amount and tax (tax/amount * 100)
- `DoneFilename`: Provided by file organization system

**Integration Points:**
```python
# From AI extraction result
extraction_result = extraction_facade.extract_from_image(request)
receipt_data = extraction_result.get_data()

# Calculate missing fields
tax_percentage = (receipt_data.tax / receipt_data.amount * 100) if receipt_data.amount > 0 else 0.0

# Append to CSV
csv_service = CsvService()
record_id = csv_service.append_record(
    amount=receipt_data.amount,
    tax=receipt_data.tax,
    tax_percentage=tax_percentage,
    description=receipt_data.description,
    currency=receipt_data.currency,
    date=receipt_data.date,
    confidence=receipt_data.confidence,
    hash_value=file_hash,
    done_filename=done_filename
)
```

### Error Handling Strategy
- **File Permission Errors**: Log error and exit with code 1
- **CSV Write Failures**: Log error but continue processing other files
- **Data Validation Warnings**: Log warnings but continue processing
- **Header Validation**: Recreate file if headers incorrect

### User Story Implementation

**Story CSV_CREATE_K1L2**: CSV File Creation and Management
- `ensure_csv_exists()` method creates fresh file with headers
- Proper header creation (no validation needed for fresh files)
- Error handling for permissions
- UTF-8 encoding support

**Story CSV_APPEND_M3N4**: Data Record Appending with Auto-Incrementing IDs  
- `get_next_id()` reads file to determine next ID (starts at 1 for fresh file)
- `append_record()` handles proper field formatting
- Currency formatting to 2 decimal places
- CSV escaping for text fields

**Story CSV_ERROR_O5P6**: Error Entry Recording and Data Validation
- `append_error_record()` creates consistent error entries
- Field validation with warnings (non-blocking)
- Error type validation

## Testing Requirements

### Unit Tests
```
tests/unit/test_csv_output/
├── test_csv_service.py        # Test all service methods
└── test_config.py            # Test configuration constants
```

### Key Test Scenarios
- CSV file creation with correct headers
- ID auto-increment logic (fresh file, records added during run)
- Record formatting (currency fields, CSV escaping)
- Error record creation
- File permission handling
- Invalid data handling (warnings, not failures)

### Integration Tests
- Integration with AI extraction output
- End-to-end record creation workflow
- File system interaction tests

## Implementation Validation

### User Story Coverage
**CSV_CREATE_K1L2**: ✓ Fresh file creation with headers, error handling  
**CSV_APPEND_M3N4**: ✓ Auto-incrementing IDs, field formatting, append operations  
**CSV_ERROR_O5P6**: ✓ Error entries, data validation, consistency

### Technical Requirements Met
- ✓ Simple service-based approach (not DDD)
- ✓ Fresh CSV creation each run (no existing data)
- ✓ Reads entire file for ID management during processing
- ✓ No concurrency handling
- ✓ Standard Python csv module
- ✓ Standalone CSV service
- ✓ Proper field formatting and validation

This specification provides a simple, focused implementation for fresh CSV creation and management while meeting all user story requirements.