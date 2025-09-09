# Architecture Decision Record

## Decision 1: Hexagonal Architecture with Layered Component Structure
**Status**: Accepted
**Context**: The receipt processing system requires clear separation between business logic and external dependencies to ensure testability, maintainability, and flexibility for future changes.
**Decision**: Implement hexagonal architecture with distinct Domain, Application, and Infrastructure layers, using ports and adapters pattern for external integrations.
**Consequences**: Higher initial complexity but significantly improved testability, easier to swap external dependencies, and clearer separation of concerns.

## Decision 2: Terminal User Interface (TUI) Architecture
**Status**: Accepted
**Context**: Requirements specify sophisticated user interaction with menu systems, tables, progress monitoring, and step-by-step workflow control, beyond simple CLI execution.
**Decision**: Create dedicated TUI container with specialized components for menu management, table display, progress monitoring, and user interaction handling.
**Consequences**: More complex UI architecture but provides required user experience with proper separation from business logic.

## Decision 3: Four-Folder File Management System
**Status**: Accepted
**Context**: Requirements specify complex file lifecycle management with incoming, scanned, imported, and failed folders, each with different persistence and clearing rules.
**Decision**: Implement dedicated File Management System with separate adapters for each folder type and their specific behaviors.
**Consequences**: More complex file handling but provides required workflow control and data integrity guarantees.

## Decision 4: Dual Data Pipeline (CSV Staging + XLSX Integration)
**Status**: Accepted
**Context**: Requirements specify two-stage data processing: CSV for staging/review and XLSX as source of truth with specific formatting requirements.
**Decision**: Create separate components for CSV staging operations and XLSX integration with dedicated validation and transformation logic.
**Consequences**: Additional complexity in data handling but provides required user control and data validation capabilities.

## Decision 5: Configuration Management Through Environment Variables
**Status**: Accepted
**Context**: System requires flexible deployment with configurable folder paths and file locations while maintaining simple setup process.
**Decision**: Implement environment-based configuration system with .env file support and automatic folder creation.
**Consequences**: Requires configuration setup but provides deployment flexibility and clear separation of environment-specific settings.

## Decision 6: Comprehensive Error Handling and Recovery System
**Status**: Accepted
**Context**: Requirements specify detailed error handling with persistent error logs, recovery options, and user-friendly error reporting across multiple failure scenarios.
**Decision**: Create dedicated error handling components with file-based error persistence and recovery strategy management.
**Consequences**: Increased system complexity but provides required reliability and user experience for production use.

## Decision 7: Application Layer Use Case Segregation
**Status**: Accepted
**Context**: System has distinct operational phases (Analysis, Staging, Import) with different validation requirements and user interactions.
**Decision**: Create separate use cases for each major operation with dedicated validation and orchestration logic.
**Consequences**: More application layer components but clearer workflow separation and easier testing of individual operations.

## Decision 8: Consolidated Receipt Processing Use Case
**Status**: Accepted
**Context**: Original architecture had redundant orchestration between Process Receipt and Extract Data use cases, creating unnecessary complexity.
**Decision**: Merge Process Receipt and Extract Data use cases into single ProcessReceiptUseCase handling complete workflow including AI extraction, validation, and file management.
**Consequences**: Simplified application layer with clearer responsibility boundaries and reduced component complexity.

## Decision 9: Advanced Terminal User Interface Architecture
**Status**: Accepted
**Context**: Requirements specify sophisticated TUI with menu systems, data tables, progress monitoring, and interactive validation displays beyond basic CLI.
**Decision**: Implement comprehensive TUI container with specialized components for startup screens, menu navigation, table rendering, validation display, and progress monitoring.
**Consequences**: More complex UI architecture but provides required user experience with proper separation between presentation and business logic.

## Decision 10: Dual-Stage Import Workflow (CSV + XLSX)
**Status**: Accepted
**Context**: Requirements specify CSV for staging/review and XLSX as authoritative source of truth with specific column mapping and sequential numbering.
**Decision**: Implement separate use cases for staging validation and XLSX import with dedicated XLSX integration port and adapter.
**Consequences**: Additional workflow complexity but provides required data governance and user control over final import process.

## Decision 11: Configuration Management Through Port/Adapter Pattern
**Status**: Accepted
**Context**: System requires .env file configuration with path validation, folder creation, and startup configuration loading following hexagonal architecture principles.
**Decision**: Implement Configuration Port in application layer with Configuration Adapter in infrastructure layer for .env file handling.
**Consequences**: Maintains architectural consistency, enables configuration testing, and supports future configuration sources while providing required startup validation.

## Decision 12: Simplified Error Handling Architecture
**Status**: Accepted
**Context**: Original architecture had separate Error Handling Adapter creating unnecessary complexity for what are distinct concerns: file logging vs user notifications.
**Decision**: Eliminate Error Handling Adapter; consolidate error logging into File System Adapter and user error display into TUI Error Reporter.
**Consequences**: Reduced component count, clearer responsibility boundaries, and simpler error flow while maintaining all required error handling capabilities.

## Decision 13: Consolidated File Operations Strategy
**Status**: Accepted
**Context**: Multiple infrastructure adapters were handling file-related operations (File System, CSV Export, Duplicate Detection) creating fragmented responsibilities.
**Decision**: Consolidate duplicate detection into File System Adapter and merge CSV Export into CSV Staging Adapter, creating cohesive file operation components.
**Consequences**: Reduced component count, clearer separation of concerns, and more maintainable file handling while preserving all required functionality.