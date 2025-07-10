# High-Level Features - Receipt Processor

## Feature: Terminal Script Interface
**Code**: TERMINAL_UI_A1B2  
**Description**: Provides a command-line interface for users to execute the receipt processing script from terminal. Displays progress updates and errors to the user during execution, supporting manual script execution on batches of receipts.  
**Dependencies**: None  
**User Stories**: design/user_stories/terminal_script_interface_stories.md  

## Feature: One-Off Processing Mode
**Code**: ONEOFF_PROC_C3D4  
**Description**: Implements one-off processing runs that clear the done folder and remove receipts.csv at the start of each execution. Keeps the input folder intact, allowing users to re-run the script multiple times on the same receipt files.  
**Dependencies**: Hard - Terminal Script Interface [TERMINAL_UI_A1B2]  
**User Stories**: design/user_stories/one_off_processing_mode_stories.md  

## Feature: Receipt Image Processing
**Code**: RECEIPT_IMG_E5F6  
**Description**: Processes receipt images and PDF files from the input folder, supporting PDF, JPG, and PNG formats. Handles sequential processing of all files in the input directory and manages file reading operations for AI analysis.  
**Dependencies**: None  

## Feature: AI Data Extraction
**Code**: AI_EXTRACT_G7H8  
**Description**: Integrates with Anthropic's Claude API to extract structured financial data from receipt images. Extracts amount, tax, description, currency, date, and generates confidence scores for each processed receipt using the anthropic Python library.  
**Dependencies**: Hard - Receipt Image Processing [RECEIPT_IMG_E5F6]  

## Feature: CSV Data Output
**Code**: CSV_OUTPUT_I9J0  
**Description**: Converts AI-extracted data into CSV format with fields: ID, Amount, Tax, Description, Currency, Date, Confidence, Hash. Manages CSV file creation, header addition, and append operations with auto-incrementing ID generation.  
**Dependencies**: Hard - AI Data Extraction [AI_EXTRACT_G7H8]  

## Feature: File Organization System
**Code**: FILE_ORG_K1L2  
**Description**: Creates and manages folder structure (input/, done/, receipts.csv), moves processed files to done folder with timestamp naming convention, and maintains original filename preservation in the archive structure.  
**Dependencies**: Hard - Receipt Image Processing [RECEIPT_IMG_E5F6]  

## Feature: Duplicate Detection
**Code**: DUPLICATE_DET_M3N4  
**Description**: Implements hash-based duplicate detection using file hash comparison against existing CSV records. Skips processing of duplicate files and provides console feedback when duplicates are detected.  
**Dependencies**: Hard - CSV Data Output [CSV_OUTPUT_I9J0]  

## Feature: Error Handling
**Code**: ERROR_HANDLE_O5P6  
**Description**: Handles processing failures for unreadable files, API failures, and corrupted files by creating error entries in CSV with confidence 0 and "ERROR" description. Continues processing remaining files and logs all errors to console.  
**Dependencies**: Hard - AI Data Extraction [AI_EXTRACT_G7H8], Hard - CSV Data Output [CSV_OUTPUT_I9J0]  

## Feature: Processing Progress Display
**Code**: PROGRESS_DISP_Q7R8  
**Description**: Displays real-time processing progress to console including individual file processing status, results logging, and final summary showing total processed files and errors encountered.  
**Dependencies**: Hard - Terminal Script Interface [TERMINAL_UI_A1B2]  

## Feature: Batch Processing Workflow
**Code**: BATCH_PROC_S9T0  
**Description**: Orchestrates the complete workflow from folder initialization through file processing completion. Manages sequential processing of all files in input folder and coordinates between all system components.  
**Dependencies**: Hard - Receipt Image Processing [RECEIPT_IMG_E5F6], Hard - File Organization System [FILE_ORG_K1L2], Hard - AI Data Extraction [AI_EXTRACT_G7H8], Hard - One-Off Processing Mode [ONEOFF_PROC_C3D4]  

---

**Consolidation Note**: The PRD explicitly describes 10 distinct functional areas including the newly added User Interface requirements. The Terminal Script Interface and One-Off Processing Mode were extracted as separate features based on the explicit UI requirements. All extracted features are directly traceable to explicit descriptions in the PRD document.