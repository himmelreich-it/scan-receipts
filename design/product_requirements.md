# Receipt Processor - High-Level Documentation

## Overview
An automated receipt processing tool that extracts financial information from receipt images and organizes the data for business expense tracking. The system uses Anthropic's Claude API to analyze receipts, processes them into CSV format for review, and imports approved data into an XLSX file which serves as the source of truth. Features an advanced Terminal User Interface (TUI) for better user control and status monitoring.

## Purpose
- **Primary Goal**: Streamline business expense tracking by automating receipt data extraction with user control
- **Target User**: Tech-savvy business owners preparing expense data for accountants
- **Usage Pattern**: Manual execution with step-by-step workflow control
- **Source of Truth**: XLSX file containing all finalized expense entries

## System Architecture

### Core Components
1. **Receipt Scanner**: Processes images from configurable input folder
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
- **INPUT_RECEIPTS_FOLDER**: Path to folder containing new receipts to process
- **DONE_FOLDER**: Path to folder containing successfully processed receipts
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
├── receipts.csv        # Staging data (created/cleared during analysis)
├── expenses.xlsx       # Source of truth (configured path)
├── input/              # New receipts folder (configurable)
├── done/               # Processed receipts (configurable, persistent)
├── failed/             # Failed receipts (configurable, persistent)
└── pyproject.toml      # uv configuration
```

## Functional Requirements

### User Interface & Execution
- **Execution Method**: `uv run main.py` from the root folder
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
  - Clears/removes existing receipts.csv
  - Does NOT clear done or failed folders (persistent)
  - Processes all files in input folder using AI
  - Shows progress with TUI updates

#### Option 2: Import to XLSX
- **Trigger**: User selects "Import to XLSX" (only available if receipts.csv exists)
- **Validation**: First number in receipts.csv must equal max XLSX number + 1
- **Behavior**: Appends receipts.csv entries to XLSX file
- **Post-Import**: receipts.csv remains until next analysis

## Data Processing Workflow

### AI Analysis Phase

#### Input Processing
- **Source**: Configurable input folder containing receipt files
- **Supported Formats**: PDF, JPG, PNG files
- **Processing Order**: Sequential processing of all files
- **Persistence**: Input files remain unchanged for re-processing

#### Duplicate Detection
- **Method**: Hash comparison against files in done folder and against other files in current processing session
- **Behavior**: Skip processing, log duplicate detection
- **Failed Folder**: Not checked for duplicates (allows retry of previously failed files)
- **Session Deduplication**: Prevent processing duplicate files within the same analysis run

#### Data Extraction
The system extracts the following information from each receipt:
- **Amount**: Total purchase amount (required)
- **Tax**: VAT amount (if separately listed)
- **Tax Percentage**: VAT percentage (if separately listed)
- **Description**: Business name or transaction description (required)
- **Currency**: Currency code (e.g., EUR, USD) (required)
- **Date**: Transaction date (required - must be extractable)
- **Confidence**: AI confidence score (0-100)

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
- **Ordering**: Entries sorted by date, then time (if extractable), then description
- **Numbering**: Sequential numbers starting from max XLSX number + 1
- **Content**: Only successful extractions (no failed or duplicate items)

#### CSV Structure
```
ID, Amount, Tax, TaxPercentage, Description, Currency, Date, Confidence, Hash, DoneFilename
```

#### Field Specifications
- **ID**: Sequential number for XLSX import
- **Date Format**: dd-MM-YYYY
- **DoneFilename**: Target filename for done folder
- **Hash**: File hash for duplicate detection

#### Display After Analysis
- **TUI Table**: Shows all entries with assigned numbers
- **Summary**: Total processed, failed, duplicates skipped
- **Preview**: What will be imported to XLSX

### XLSX Import Phase

#### Validation Requirements
- **Sequential Check**: First receipts.csv number = max XLSX number + 1
- **Empty Handling**: If XLSX empty (no entries from row 11), start numbering at 1
- **User Warning**: Alert if manual XLSX edits broke sequential numbering

#### XLSX Structure
- **Data Range**: Entries start from row 11 downward
- **Column Mapping**:
  - **A**: Numbering (sequential)
  - **B**: Purchase Date (format: d-MMM-yy, e.g., 22-Mar-25)
  - **C**: Description
  - **J**: Total amount
  - **K**: VAT Amount
  - **S**: Notes (currency info for non-EUR: "USD 150.00")

#### Import Behavior
- **Append Only**: Only adds new entries, never overwrites existing
- **Order Preservation**: Same order as receipts.csv
- **Currency Handling**: Non-EUR currencies noted in column S
- **Post-Import**: receipts.csv remains until next analysis run

## File Management

### Done Folder Management
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

### Input Folder Management
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
- **Context-Sensitive**: Available options based on current state
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
- **File Synchronization**: done folder files match XLSX entries
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
- **Audit Trail**: Original filenames preserved in done folder
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
5. **Cleanup**: Manually organize input folder when satisfied
6. **Handoff**: Provide XLSX file to accountant

### Batch Processing Pattern
- **Accumulation**: Collect receipts in input folder over time
- **Periodic Processing**: Run analysis when convenient
- **Incremental Import**: Add to existing XLSX data
- **Archive Management**: Manage failed and done folders periodically

### Quality Control Workflow
- **Confidence Review**: Check low confidence scores in staging
- **Error Investigation**: Review failed folder for patterns
- **Data Verification**: Spot-check XLSX entries against original receipts
- **System Maintenance**: Periodic cleanup of processed files