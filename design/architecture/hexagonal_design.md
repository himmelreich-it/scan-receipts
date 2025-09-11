# Hexagonal Architecture Design

## Overview
Simple hexagonal (ports & adapters) architecture for the receipt processing system, focusing on clear separation between business logic and external dependencies.

## Core Domain (Hexagon Center)

### 1. Receipt Processing Core
**Responsibility**: Business logic for receipt data extraction and processing
- Receipt entity management
- Extraction result validation
- Business rules for required/optional fields
- Confidence scoring logic
- Duplicate detection logic

### 2. Validation Core
**Responsibility**: Data quality and integrity rules
- Field validation rules (Amount, Currency, Date)
- Date range validation
- Sequential numbering logic
- Data consistency rules
- Quality scoring algorithms

## Ports (Interfaces)

### Input Ports (Use Cases)
```
- ProcessReceiptUseCase
- ImportToXLSXUseCase
- ViewStagingDataUseCase
- ValidateDataUseCase
```

### Output Ports (Dependencies)
```
- AIExtractionPort (for receipt data extraction)
- FileSystemPort (for file operations)
- XLSXPort (for Excel operations)
- CSVPort (for staging data)
- ConfigurationPort (for settings)
```

## Adapters (Implementations)

### Primary Adapters (Driving)
1. **TUI Adapter**
   - Terminal user interface
   - Menu system
   - Progress display
   - User input handling
   - Orchestrates use case workflows

2. **Main (Application Startup)**
   - Dependency injection setup
   - Component wiring
   - Application initialization

### Secondary Adapters (Driven)

1. **AI Extraction Adapter**
   - Implements: AIExtractionPort
   - Anthropic Claude API integration
   - Request/response handling
   - Error recovery

2. **File System Adapter**
   - Implements: FileSystemPort
   - Folder management (incoming/scanned/imported/failed)
   - File operations (move, copy, delete)
   - Hash generation
   - File validation

3. **XLSX Integration Adapter**
   - Implements: XLSXPort
   - Excel file reading/writing
   - Sequential numbering
   - Date formatting
   - Data append operations

4. **CSV Adapter**
   - Implements: CSVPort
   - Staging file management
   - Data serialization
   - Sort operations

5. **Configuration Adapter**
   - Implements: ConfigurationPort
   - Environment variable reading
   - Path validation
   - Default value handling

## Data Flow

### Receipt Processing Flow
```
TUI Adapter 
    → ProcessReceiptUseCase 
        → FileSystemPort (read files)
        → AIExtractionPort (extract data)
        → ValidationCore (validate)
        → CSVPort (stage data)
        → FileSystemPort (move files)
```

### Import Flow
```
TUI Adapter 
    → ImportToXLSXUseCase
        → CSVPort (read staging)
        → ValidationCore (validate)
        → XLSXPort (read existing)
        → XLSXPort (append data)
        → FileSystemPort (move to imported)
```

## Directory Structure
```
src/
├── main.py                          # Application startup
├── core/
│   ├── domain/
│   │   ├── receipt.py               # Receipt entity
│   │   ├── validation.py            # Validation rules
│   │   └── exceptions.py            # Domain exceptions
│   └── use_cases/
│       ├── process_receipt.py       # Process receipt use case
│       ├── import_to_xlsx.py        # Import use case
│       └── view_staging.py          # View staging use case
├── ports/
│   ├── ai_extraction.py             # AI extraction port
│   ├── file_system.py               # File system port
│   ├── xlsx.py                      # XLSX port
│   ├── csv.py                       # CSV port
│   └── configuration.py             # Configuration port
└── adapters/
    ├── primary/
    │   └── tui/
    │       ├── terminal_ui.py       # TUI adapter
    │       └── workflows.py         # Workflow orchestration
    └── secondary/
        ├── anthropic_adapter.py     # AI extraction adapter
        ├── file_system_adapter.py   # File system adapter
        ├── xlsx_adapter.py          # XLSX adapter
        ├── csv_adapter.py           # CSV adapter
        └── env_config_adapter.py    # Configuration adapter
```

## Implementation Order

1. Define ports (interfaces)
2. Implement core domain logic
3. Implement use cases
4. Create adapters
5. Wire components in main
6. Add TUI adapter last