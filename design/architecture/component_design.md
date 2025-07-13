# Component Architecture Design

## Overview
This document describes the component-level architecture for the Receipt Processor system, following hexagonal architecture principles. The design emphasizes separation of concerns, testability, and maintainability.

## Architecture Layers

### Domain Layer (Core Business Logic)
The domain layer contains the core business concepts and rules, with no external dependencies:

- **Receipt Aggregate**: Central domain entity that encapsulates receipt business logic and invariants
- **Extraction Value Objects**: Immutable objects for Amount, Tax, Currency, and Date with built-in validation
- **Processing Policies**: Domain services that implement business rules for confidence scoring and data validation

### Application Layer (Use Cases)
The application layer orchestrates domain operations and defines ports for external dependencies:

- **Process Receipt Use Case**: Main orchestrator that coordinates the entire receipt processing workflow
- **Extract Data Use Case**: Manages AI-powered data extraction from receipt images
- **Validate Results Use Case**: Applies business rules and validation to extracted data

#### Ports (Interfaces)
- **Receipt Repository Port**: Interface for receipt data persistence operations
- **AI Extraction Port**: Interface for AI-powered data extraction services
- **File System Port**: Interface for file operations and management

### Infrastructure Layer (Adapters)
The infrastructure layer implements the ports and handles all external concerns:

#### File Management
- **File System Adapter**: Handles file scanning, copying, and organization
- **CSV Export Adapter**: Manages CSV file generation and formatting
- **Duplicate Detection Adapter**: Implements file hash-based duplicate detection

#### External Services
- **Anthropic API Adapter**: Integrates with Claude API for receipt analysis
- **CSV Repository Adapter**: Implements data persistence using CSV format

#### Cross-cutting Concerns
- **Error Handling Adapter**: Manages error scenarios and recovery strategies

## Key Design Decisions

### Hexagonal Architecture Benefits
1. **Testability**: Domain logic can be tested in isolation without external dependencies
2. **Flexibility**: External systems can be swapped without affecting core business logic
3. **Maintainability**: Clear separation of concerns makes the system easier to understand and modify

### Component Organization
- **Domain components** contain only business logic and have no external dependencies
- **Application components** orchestrate domain operations and define interfaces for external needs
- **Infrastructure components** implement the interfaces and handle all technical concerns

### Data Flow
1. CLI Interface receives user commands
2. Use Cases in Application Layer orchestrate the workflow
3. Domain objects enforce business rules
4. Infrastructure adapters handle external system interactions

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
Concentrates on the core business logic components, showing how domain entities and value objects interact with application use cases.

### Infrastructure Focus
Emphasizes the adapter implementations and their connections to external systems, demonstrating how technical concerns are isolated from business logic.

## References
- [Hexagonal Architecture Guide](../rules/hexagonal_architecture_guide.md)
- [Product Requirements](../product_requirements.md)
- [High Level Features](../high_level_features.md)
- [Python Coding Standards](../rules/python_agent_instructions.md)