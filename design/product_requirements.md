# Receipt Processor - High-Level Documentation

## Overview
An automated receipt processing tool that extracts financial information from receipt images and organizes the data for business expense tracking. The system uses Anthropic's Claude API to analyze receipts and outputs structured data in CSV format, simplifying expense preparation for accounting purposes.

## Purpose
- **Primary Goal**: Streamline business expense tracking by automating receipt data extraction
- **Target User**: Business owners preparing expense data for accountants
- **Usage Pattern**: Manual execution on batches of receipts as needed

## System Architecture

### Core Components
1. **Receipt Scanner**: Processes images from input folder
2. **AI Analysis Engine**: Uses Anthropic's Claude API for data extraction
3. **Data Processor**: Converts API responses to structured CSV format
4. **File Manager**: Handles file organization and naming conventions

### Technology Stack
- **Language**: Python
- **AI Service**: Anthropic Claude API via `anthropic` Python library
- **Input Formats**: PDF, JPG, PNG
- **Output Format**: CSV

## Functional Requirements

### User Interface
- User will use a terminal to run a python script
- User will see be updated by the terminal on progress and errors
- User will run this script once in a while on all the receipts available
- Each run, the `done` folder will be cleared and `receipts.csv` removed, one off run
- The input folder stays intact, the user can re-run

### Input Processing
- **Source**: `input/` folder containing receipt files
- **Supported Formats**: PDF, JPG, PNG files
- **Processing**: Sequential processing of all files in folder

### Data Extraction
The system extracts the following information from each receipt:
- **Amount**: Total purchase amount
- **Tax**: Tax amount (if separately listed)
- **Tax Percentage**: Tax percentage amount (if separately listed)
- **Description**: Business name or transaction description
- **Currency**: Currency code (e.g., EUR, USD)
- **Date**: Transaction date
- **Confidence**: AI confidence score (0-100)

### Output Specification
- **Format**: CSV file with append functionality
- **Fields**: `ID, Amount, Tax, TaxPercetage, Description, Currency, Date, Confidence, Hash, DoneFilename`
- **ID Field**: Auto-incrementing number for each processed receipt
- **Date Format**: dd-MM-YYYY
- **Hash Field**: File hash for duplicate detection
- **File Location**: Root directory alongside script

### File Management
- **Folder Structure**:
  ```
  project/
  ├── input/          # Receipts to process
  ├── done/           # Processed receipts
  └── receipts.csv    # Output data
  ```
- **Auto-Creation**: System creates folders if they don't exist
- **Processed Files**: Moved to `done/` folder with naming convention:
  `{ID}-{processing-timestamp}-{original-filename}`
- **Timestamp Format**: %Y%m%d-%H%M%S%f

## AI Integration

### Anthropic Claude API
- **Library**: `anthropic` Python library
- **Output Format**: Structured JSON response
- **Confidence Scoring**: Each extraction includes confidence assessment
- **Error Handling**: Graceful handling of API failures

### Structured Output Schema
```json
{
  "amount": "float",
  "tax": "float", 
  "tax_percentage": "float", 
  "description": "string",
  "currency": "string",
  "date": "string",
  "confidence": "integer (0-100)",
  "hash": "string"
}
```

## Error Handling Strategy

### Processing Failures
- **Unreadable Files**: Create CSV entry with confidence 0, description "ERROR", log error to console
- **API Failures**: Same error handling as unreadable files, log API error to console
- **Corrupted Files**: Process as error, move to done folder with "ERROR-" prefix, log to console
- **CSV Corruption**: Throw error and display message to console, halt execution
- **Error Handling**: Continue processing remaining files after errors, all errors logged to console

### Low Confidence Results
- **Threshold**: No minimum confidence threshold
- **Handling**: All results processed regardless of confidence level
- **User Decision**: Human review based on confidence scores

### Duplicate Handling
- **Strategy**: Skip duplicate files based on hash comparison
- **Detection**: Use file hash stored in CSV to identify duplicates
- **Feedback**: Log skipped duplicates to console

## Workflow

### Processing Steps
1. **Initialize**: Check/create folder structure
2. **Scan**: Read all files from `input/` folder
3. **Process**: For each file:
   - Display progress to console
   - Send to Anthropic API for analysis
   - Parse structured JSON response
   - Generate incremental ID
   - Append to CSV file
   - Log results to console
   - Copy file to `done/` folder with new naming
4. **Complete**: Display summary (total processed, errors encountered)

### CSV Output Management
- **Append Mode**: New data added to existing CSV
- **ID Continuation**: IDs continue from last processed receipt
- **Header Management**: Headers added only if file is new

## Configuration

### Fixed Parameters
- **Input Folder**: `input/`
- **Output Folder**: `done/`
- **CSV Filename**: `receipts.csv`
- **Date Format**: dd-MM-YYYY
- **Processing**: Manual execution only
- **Timestamp Format**: %Y%m%d-%H%M%S%f
- **Console Logging**: Progress and results displayed during execution

### Flexible Elements
- **File Formats**: Currently PDF, JPG, PNG (expandable)
- **API Parameters**: Adjustable in implementation

## Usage Pattern

### Typical Workflow
1. **Preparation**: Place receipt files in `input/` folder
2. **Execution**: Run script manually
3. **Monitor**: Watch console output for progress and results
4. **Review**: Check CSV output and confidence scores
5. **Summary**: View final processing summary (total files, errors)
6. **Handoff**: Provide organized data to accountant

### Maintenance
- **Frequency**: Run as needed (weekly/monthly)
- **Monitoring**: Review confidence scores for data quality
- **Error Review**: Check console output for processing issues
- **Cleanup**: Archive processed receipts periodically

## Quality Assurance

### Data Validation
- **Confidence Scores**: Built-in quality indicator
- **Error Tracking**: Clear marking of processing failures
- **Audit Trail**: Original filenames preserved in done folder

### Human Review Points
- **Low Confidence**: Manual verification recommended
- **Error Entries**: Require human processing
- **Duplicate Detection**: Manual review during accounting preparation

## Future Considerations

### Scalability Notes
- **Volume**: Designed for small to medium business volumes
- **Performance**: Sequential processing suitable for current needs
- **Storage**: Local file system adequate for typical usage