# Receipt Processor - High-Level Documentation

## Overview
An automated receipt processing tool that extracts financial information from receipt images and organizes the data for business expense tracking. The system uses Anthropic's Claude API to analyze receipts, processes them into CSV format for review, and imports approved data into an XLSX file which serves as the source of truth. Features an advanced Terminal User Interface (TUI) for better user control and status monitoring.

## Purpose
- **Primary Goal**: Streamline business expense tracking by automating receipt data extraction with user control
- **Target User**: Tech-savvy business owners preparing expense data for accountants
- **Usage Pattern**: Manual execution with step-by-step workflow control
- **Source of Truth**: XLSX file containing all finalized expense entries, it should only receive new entries

## System Architecture

### Core Components
1. **Receipt Scanner**: Processes images from configurable incoming folder
2. **AI Analysis Engine**: Uses Anthropic's Claude API for data extraction
3. **Data Processor**: Converts API responses to structured CSV format for review
4. **XLSX Manager**: Imports approved data to XLSX source of truth
5. **TUI Controller**: Advanced terminal interface with tables and user interactions
6. **File Manager**: Handles file organization across multiple folders

### Technology Stack
- **Language**: Python
- **Package Manager**: uv (for dependency management and execution)
- **AI Service**: Anthropic Claude API via `anthropic` Python library
- **Input Formats**: PDF, JPG, PNG
- **Output Formats**: CSV (staging), XLSX (source of truth)
- **Interface**: TUI (Text User Interface) with tables and menus
- **Configuration**: .env file for folder paths
- **Architecture**: Clean separation of AI processing and data import

## Configuration

### Environment Variables (.env)
- **INCOMING_RECEIPTS_FOLDER**: Path to folder containing new receipts to process
- **SCANNED_FOLDER**: Path to folder containing successfully processed receipts
- **IMPORTED_FOLDER**: Path to folder containing successfully processed receipts
- **FAILED_FOLDER**: Path to folder containing failed receipts with error logs
- **XLSX_OUTPUT_FILE**: Path to XLSX file (source of truth)
- **CSV_STAGING_FILE**: Path to receipts.csv (staging file, defaults to receipts.csv)

### Project Structure
```
project/
├── src/
│   ├── main.py         # Entry point script
│   └── [other modules] # Supporting code modules
├── .env                # Configuration file
├── content
│   ├── incoming/       # New receipts folder (configurable)
│   ├── scanned/        # Processed receipts (configurable)
│   ├── imported/       # Processed receipts (configurable, persistent)
│   ├── failed/         # Failed receipts (configurable, persistent)
│   ├── receipts.csv    # Staging data (created/cleared during analysis)
│   └── expenses.xlsx   # Source of truth (configured path)
└── pyproject.toml      # uv configuration
```

## Functional Requirements

### User Interface & Execution
- **Execution Method**: `uv run main.py` from the src folder
- **Interface Type**: TUI (Text User Interface) with tables, menus, and status updates
- **User Type**: Tech-savvy user comfortable with terminal commands
- **Workflow Control**: Step-by-step process with user decisions at each stage
- **Data Display**: Tables showing file counts, processing results, and validation status

### Startup Behavior
The application starts by displaying:
1. **File Counts**: Number of files in input folder and failed folder
2. **Staging Status**: If receipts.csv exists, show modified date and entry count
3. **Action Options**: Available actions based on current state

### Main Workflow Options

#### Option 1: AI Analysis (Import from Input Folder)
- **Trigger**: User selects "Run Analysis" or "Re-run Analysis"
- **Behavior**: 
  - If no files in incoming folder: display 'No files in {incoming} folder' and go back to menu.
  - Clears/removes existing receipts.csv
  - Clears scanned folder (only when re-running analysis)
  - Does NOT clear imported or failed folders (persistent)
  - Processes all files in incoming folder sequentially using LLM such as Claude
  - For each file: first check for duplicates against imported folder, then against already processed files in current session (scanned folder cache)
  - Successfully scanned files are placed in scanned folder and get a line in receipts.csv
  - Shows progress with TUI updates
  - Go back to menu.

#### Option 2: Import to XLSX
- **Trigger**: User selects "Import to XLSX" (only available if receipts.csv exists)
- **Validation**: For each succesful item in receipts.csv there is a file in scanned folder
- **Behavior**:
  - If no receipts.csv: display 'No receipts.csv' and go back to menu
  - Each item in receipts.csv is added to XLSX and file added to imported folder
    - Sequential number taken from last item in XSLX + 1
    - File is renamed to {sequential-number}-{yyyyMMdd of receipt}-{description:20}.{original-extension}
  - Appends receipts.csv entries to XLSX file
  - Go back to menu
- **Post-Import**: receipts.csv remains until next analysis

#### Option 3: View Staging Table
- **Trigger**: User selects "View Staging Table"
- **Behavior**: 
  - Verify if the number if items in receipts.csv is equal to items in scanned folder
  - Verify whether the names of files in receipts.csv are equal to items in scanned folder
  - Verify whether the hashes in the receipts.csv do not correspond to any hashes from the imported folder
  - Displays 'receipts.csv is ready to be imported' or which items are wrong
    - Count mismatch if applicable
    - Name mismatches if applicable
    - List duplicates if any
  - Go back to menu

## Data Processing Workflow

### AI Analysis Phase

#### Input Processing
- **Source**: Configurable incoming folder containing receipt files
- **Supported Formats**: PDF, JPG, PNG files
- **Processing Order**: Sequential processing of all files
- **Persistence**: Input files remain unchanged for re-processing

#### Duplicate Detection
- **Method**: Hash comparison against files in imported folder and against other files in current processing session (cache)
- **Behavior**: Skip processing, log duplicate detection
- **Failed Folder**: Not checked for duplicates (allows retry of previously failed files)
- **Session Deduplication**: Prevent processing duplicate files within the same analysis run

#### Data Extraction
The system extracts the following information from each receipt:
- **Amount**: Total purchase amount (required)
- **Tax**: VAT amount (if separately listed)
- **Tax Percentage**: VAT percentage (if separately listed)
- **Description**: Business name or transaction description, if not found, use the original filename
- **Currency**: Currency code (e.g., EUR, USD) (required)
- **Date**: Transaction date (required - must be extractable)
- **Confidence**: AI confidence score of proper extraction (0-100)

#### Success Criteria
- **Valid Data**: All required fields successfully extracted
- **Valid Date**: Date must be extractable and reasonable
- **File Processing**: File successfully analyzed by AI

#### Failure Handling
Files are moved to failed folder if:
- AI cannot extract valid date
- AI analysis fails completely
- File is corrupted or unreadable
- Required fields cannot be extracted

### Staging Phase (receipts.csv)

#### Data Organization
- **Format**: CSV file for staging approved extractions
- **Ordering**: Entries sorted by date, then time (if extractable), ascending, then description
- **Content**: Only successful extractions (no failed or duplicate items)

#### Scan behavior (per file processing)
- Pick each file from the incoming folder sequentially
- Check for duplicates against hashes from imported folder (persistent duplicates)
- Check for duplicates against hashes from files already processed in current session (session cache in scanned folder)
- Only perform AI analysis when file is not a duplicate
- Successfully analyzed files are copied to the scanned folder with proper naming
- Each successful analysis adds one entry to receipts.csv

#### CSV Structure
```
Amount, Tax, TaxPercentage, Description, Currency, Date, Confidence, Hash, DoneFilename
```

#### Field Specifications
- **Date Format**: dd-MM-YYYY
- **DoneFilename**: Target filename for done folder
- **Hash**: File hash for duplicate detection

#### Display After Analysis
- **TUI Table**: Shows all entries
- **Summary**: Total processed, failed, duplicates skipped
- **Preview**: What will be imported to XLSX

### XLSX Import Phase

#### Validation Requirements
- **Empty Handling**: If XLSX empty (no entries from row 11), start numbering at 1
- **No XLSX entries without files**: There should be no entries in the XLSX without a file in the imported folder

#### XLSX Structure
- **Data Range**: Entries start from row 11 downward
- **Column Mapping**:
  - **A**: Numbering (sequential)
  - **B**: Purchase Date (format: d-MMM-yy, e.g., 22-Mar-25)
  - **F**: Description
  - **J**: Total amount
  - **K**: VAT Amount
  - **S**: Notes (currency info for non-EUR: "USD 150.00")

#### Import Behavior
- **Append Only**: Only adds new entries, never overwrites existing
- **Order Preservation**: Same order as receipts.csv
- **Currency Handling**: Non-EUR currencies noted in column S
- **Post-Import**: receipts.csv remains until next analysis run

## File Management

### Scanned Folder Management
- **Clearing**: Cleared automatically only at the start of each analysis run (not after completion)
- **Population**: Populated during analysis as each file is successfully processed
- **Validation**: After analysis completion, contains exactly the files referenced in receipts.csv
- **Naming Convention**: `{yyyyMMdd}-{description}.{ext}`
  - `{yyyyMMdd}`: Purchase date from receipt
  - `{description}`: Cleaned description (special chars removed, max 15 chars)
  - `{ext}`: Original file extension

### Imported Folder Management
- **Persistence**: Never cleared automatically
- **Naming Convention**: `{number}-{yyyyMMdd}-{description}.{ext}`
  - `{number}`: Sequential ID from XLSX
  - `{yyyyMMdd}`: Purchase date from receipt
  - `{description}`: Cleaned description (special chars removed, max 15 chars)
  - `{ext}`: Original file extension
- **Accumulation**: Contains all successfully processed receipts over time

### Failed Folder Management
- **Persistence**: Never cleared automatically
- **Naming Convention**: Original filename preserved
- **Overwrite Behavior**: If same filename fails again, overwrite with new error log
- **Metadata**: Include error logs/reasons for failure
- **Manual Review**: Users can inspect and potentially move back to input folder
- **Error Log**: Each failed file has a logfile {original-filename}.{original-extension}.log

### Incoming Folder Management
- **Persistence**: Files never removed automatically
- **Re-processing**: Allows multiple analysis runs until satisfied
- **User Control**: Manual cleanup when ready

## TUI (Text User Interface) Requirements

### Startup Screen
```
Receipt Processor
================
Input Folder: 15 files
Failed Folder: 2 files
Staging: receipts.csv (modified: 2025-01-15 14:30, 8 entries)

Available Actions:
[1] Run Analysis
[2] Import to XLSX
[3] View Staging Table
[4] Exit
```

### Analysis Progress
- **Real-time Updates**: Processing status for each file
- **Progress Bar**: Overall completion percentage
- **Error Logging**: Failed files with reasons
- **Success Summary**: Counts and statistics

### Data Tables
- **Staging Review**: Display receipts.csv content in formatted table
- **Validation Results**: Show numbering validation status
- **Import Preview**: What will be added to XLSX

### Menu System
- **Navigation**: Number-based menu selection
- **Confirmation**: User confirmation for destructive actions

## Error Handling Strategy

### AI Processing Failures
- **Unreadable Files**: Move to failed folder with error log
- **API Failures**: Move to failed folder with API error details
- **Invalid Data**: Move to failed folder if required fields missing
- **Date Extraction**: Move to failed folder if date cannot be determined
- **Continuation**: Continue processing remaining files after errors

### XLSX Import Failures
- **Numbering Mismatch**: Show warning, block import until resolved
- **File Lock**: Handle XLSX file being open, show user-friendly error
- **Corruption**: Validate XLSX structure before import

### File System Errors
- **Folder Creation**: Auto-create configured folders if missing
- **Permission Issues**: Clear error messages for file access problems
- **Disk Space**: Handle insufficient disk space gracefully

### Recovery Options
- **Re-analysis**: Clear staging and restart AI processing
- **Manual Review**: Users can move files between folders manually
- **Staging Reset**: Option to clear receipts.csv without processing

## Data Consistency

### Source of Truth
- **Primary**: XLSX file contains authoritative data
- **Staging**: receipts.csv is temporary staging area
- **Validation**: Numbering sequence ensures consistency

### Validation Checks
- **Sequential Numbering**: Ensure no gaps in XLSX numbering
- **File Synchronization**: imported folder files match XLSX entries
- **Hash Verification**: Prevent duplicate processing

### User Modifications
- **XLSX Changes**: User can manually edit XLSX (system respects changes)
- **File Management**: User can manually organize folders
- **System Adaptation**: Application works around user modifications

## Quality Assurance

### Data Validation
- **Required Fields**: Enforce extraction of essential data
- **Confidence Scores**: Built-in quality indicator for manual review
- **Date Validation**: Ensure reasonable date ranges
- **Currency Recognition**: Proper currency code extraction

### Error Tracking
- **Failed Processing**: Clear marking and logging of failures
- **Error Logs**: Detailed failure reasons in failed folder

### Human Review Points
- **Staging Review**: Manual verification of receipts.csv before XLSX import
- **Low Confidence**: Manual verification recommended for low confidence scores
- **Failed Items**: Human processing required for failed extractions

## Operational Workflow

### Typical Usage Session
1. **Startup**: Launch application, review current state
2. **Analysis**: Run AI processing on input folder receipts
3. **Review**: Examine staging results in TUI table
4. **Import**: Approve import to XLSX source of truth
5. **Cleanup**: Manually organize incoming folder when satisfied
6. **Handoff**: Provide XLSX file to accountant

### Batch Processing Pattern
- **Accumulation**: Collect receipts in incoming folder over time
- **Periodic Processing**: Run analysis when convenient
- **Incremental Import**: Add to existing XLSX data
- **Archive Management**: Manage failed and done folders periodically

### Quality Control Workflow
- **Confidence Review**: Check low confidence scores in staging
- **Error Investigation**: Review failed folder for patterns
- **Data Verification**: Spot-check XLSX entries against original receipts
- **System Maintenance**: Periodic cleanup of processed files