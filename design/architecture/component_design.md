# Component Architecture Design

## Overview
This document describes the component-level architecture for the Receipt Processor system, following hexagonal architecture principles. The design emphasizes separation of concerns, testability, and maintainability.

## Architecture Layers

### Domain Layer (Core Business Logic)
The domain layer contains the core business concepts and rules, with no external dependencies:

- **Receipt Entity**: Central domain entity that encapsulates receipt business logic and validation
- **Extraction Value Objects**: Immutable objects for Amount, Tax, Currency, and Date with built-in validation
- **Processing Policies**: Domain services that implement business rules for confidence scoring and data validation

### Application Layer (Use Cases)
The application layer orchestrates domain operations and defines ports for external dependencies:

- **Process Receipt Use Case**: Complete receipt processing workflow including AI extraction, validation, and file management
- **Validate Staging Use Case**: Validates CSV staging data and file synchronization before import
- **Import to XLSX Use Case**: Imports validated CSV data to XLSX with sequential numbering and proper formatting
- **Validate Results Use Case**: Applies business rules and validation to extracted data

#### Ports (Interfaces)
- **Receipt Repository Port**: Interface for receipt data persistence operations
- **AI Extraction Port**: Interface for AI-powered data extraction services
- **File System Port**: Interface for file operations and management
- **XLSX Integration Port**: Interface for XLSX file operations and data import
- **Configuration Port**: Interface for system configuration access and validation

### Infrastructure Layer (Adapters)
The infrastructure layer implements the ports and handles all external concerns:

#### File Management
- **File System Adapter**: Handles file scanning, copying, organization, error logging, and duplicate detection across all four folders
- **Configuration Adapter**: Loads configuration from .env file with validation and automatic folder creation
- **XLSX Integration Adapter**: Handles XLSX import with sequential numbering and validation

#### External Services
- **Anthropic API Adapter**: Integrates with Claude API for receipt analysis
- **CSV Staging Adapter**: Handles CSV staging operations including read/write for receipt data

#### Cross-cutting Concerns
- Error handling is managed through File System Adapter (for error logging) and TUI Error Reporter (for user notifications)

## Key Design Decisions

### Hexagonal Architecture Benefits
1. **Testability**: Domain logic can be tested in isolation without external dependencies
2. **Flexibility**: External systems can be swapped without affecting core business logic
3. **Maintainability**: Clear separation of concerns makes the system easier to understand and modify

### Component Organization
- **Domain components** contain only business logic and have no external dependencies
- **Application components** orchestrate domain operations and define interfaces for external needs
- **Infrastructure components** implement the interfaces and handle all technical concerns
- **Configuration management** follows port/adapter pattern for testability and flexibility

### Data Flow
1. Configuration is loaded at startup and distributed to infrastructure adapters
2. TUI Interface displays system status and receives user menu selections
3. Use Cases in Application Layer orchestrate the workflows (processing, validation, import)
4. Domain objects enforce business rules and data validation
5. Infrastructure adapters handle external system interactions (AI, file system, XLSX)
6. Error handling flows through File System Adapter (logging) and TUI Error Reporter (user display)

## Technology Mapping

### Domain Layer
- Pure Python classes with no external dependencies
- Value objects implemented as immutable dataclasses
- Domain services as stateless classes

### Application Layer
- Python abstract base classes (ABC) for port definitions
- Application services as coordinating classes
- Dependency injection through constructor parameters

### Infrastructure Layer
- Concrete implementations of port interfaces
- Integration with external libraries (anthropic, csv, pathlib)
- Framework-specific code isolated to this layer

## Views and Perspectives

### Component Overview
Shows the complete component structure with all layers and their relationships, highlighting the hexagonal architecture pattern.

### Domain Focus
Concentrates on the core business logic components, showing how the Receipt Entity and value objects interact with application use cases.

### Infrastructure Focus
Emphasizes the adapter implementations and their connections to external systems, demonstrating how technical concerns are isolated from business logic.

## References
- [Hexagonal Architecture Guide](../rules/hexagonal_architecture_guide.md)
- [Product Requirements](../product_requirements.md)
- [High Level Features](../high_level_features.md)
- [Python Coding Standards](../rules/python_agent_instructions.md)