# Hexagonal Architecture Instructions for Coding Agents

## Overview
You are a coding agent that follows Hexagonal Architecture (Ports and Adapters) principles. Your primary goal is to create maintainable, testable, and loosely coupled code by isolating business logic from external dependencies.

## Core Principles to Follow

### 1. Domain-Driven Structure
- **Always start with the domain layer** - create entities, value objects, and domain services first
- **Keep business logic pure** - no external dependencies in domain code
- **Use ubiquitous language** - match code terminology with business terminology
- **Aggregate roots** should encapsulate business invariants

### 2. Dependency Direction Rules
- **Dependencies flow inward** - outer layers depend on inner layers, never the reverse
- **Application layer** orchestrates domain operations but contains no business logic
- **Infrastructure layer** implements interfaces defined by inner layers
- **Domain layer** has no dependencies on external libraries or frameworks

### 3. Port and Adapter Pattern
- **Define ports as interfaces** in the application or domain layer
- **Implement adapters** in the infrastructure layer
- **Primary ports** (driving): interfaces for use cases
- **Secondary ports** (driven): interfaces for external systems

## Layer Structure Guidelines

### Domain Layer (Core)
**Contains:** Core business objects, value objects, domain services, repository interfaces, business events, domain exceptions

**Rules:**
- No external dependencies
- Pure business logic only
- Entities contain behavior, not just data
- Value objects are immutable
- Use domain events for decoupling

### Application Layer (Use Cases)
**Contains:** Application services/use cases, primary ports, data transfer objects, command/query objects

**Rules:**
- Orchestrate domain operations
- Handle cross-cutting concerns (transactions, security)
- Convert between DTOs and domain objects
- No business logic - delegate to domain
- Define interfaces for external dependencies

### Infrastructure Layer (Adapters)
**Contains:** Database implementations, external service clients, message queue implementations, web controllers, CLI interfaces, configuration

**Rules:**
- Implement interfaces defined by inner layers
- Handle technical concerns (persistence, networking)
- Convert between external formats and internal DTOs
- Contain framework-specific code

## Implementation Guidelines

### 1. Starting a New Feature
1. **Identify the use case** - what business operation needs to be performed?
2. **Define domain entities** - what business concepts are involved?
3. **Create use case interface** - define the primary port
4. **Implement domain logic** - create entities and domain services
5. **Define external dependencies** - create repository/service interfaces
6. **Implement use case** - orchestrate domain operations
7. **Create adapters** - implement external interfaces
8. **Add controllers/entry points** - create primary adapters

### 2. Repository Pattern
```
# Domain layer - define interface
interface OrderRepository:
    save(order)
    find_by_id(order_id)
    find_by_customer_id(customer_id)

# Infrastructure layer - implement interface
class DatabaseOrderRepository implements OrderRepository:
    # Database-specific implementation
```

### 3. Use Case Implementation
```
# Application layer
class PlaceOrderUseCase:
    constructor(order_repository, payment_service)
    
    execute(place_order_command):
        # 1. Validate input
        # 2. Load domain objects
        # 3. Execute business logic
        # 4. Save results
        # 5. Return response
```

### 4. Dependency Injection
- **Configure DI container** in the infrastructure layer
- **Wire interfaces to implementations** at application startup
- **Use constructor injection** for required dependencies
- **Avoid service locator pattern**

## Testing Strategy

### Unit Tests
- **Test domain logic in isolation** - no external dependencies
- **Mock secondary ports** when testing application layer
- **Use test doubles** for external services
- **Focus on behavior, not implementation**

### Integration Tests
- **Test adapter implementations** against real external systems
- **Use appropriate test infrastructure** for your technology stack
- **Test complete use case flows** with minimal mocking

### Architecture Tests
- **Verify dependency rules** - ensure no violations of layer boundaries
- **Check interface compliance** - verify adapters implement ports correctly
- **Validate module structure** - ensure proper layer organization

## Code Quality Guidelines

### 1. Naming Conventions
- **Use business terminology** throughout the codebase
- **Ports describe their role** (OrderRepository, EmailService)
- **Adapters include technology** (PostgresOrderRepository, SmtpEmailService)
- **Use cases are verbs** (PlaceOrderUseCase, CancelOrderUseCase)

### 2. Error Handling
- **Domain exceptions** for business rule violations
- **Application exceptions** for use case failures
- **Infrastructure exceptions** for technical failures
- **Convert exceptions at boundaries** - don't leak implementation details

### 3. Data Flow
- **DTOs at boundaries** - convert to/from domain objects
- **Domain objects internally** - use rich domain models
- **Avoid anemic models** - entities should contain behavior
- **Immutable value objects** - reduce state mutation

## Common Patterns to Implement

### 1. CQRS (Command Query Responsibility Segregation)
- **Separate read and write models** when complexity warrants
- **Commands modify state** - return void or simple results
- **Queries return data** - no side effects

### 2. Domain Events
- **Publish events** when important business events occur
- **Decouple side effects** from main business logic
- **Eventual consistency** between bounded contexts

### 3. Specification Pattern
- **Encapsulate business rules** in specification objects
- **Compose complex queries** from simple specifications
- **Reuse business logic** across different contexts

## Red Flags to Avoid

### ❌ Architecture Violations
- Domain objects depending on infrastructure
- Controllers containing business logic
- Direct database access from domain layer
- Tight coupling between layers

### ❌ Common Anti-patterns
- Anemic domain models (just data holders)
- God objects that do everything
- Circular dependencies between layers
- Leaking implementation details through interfaces

### ❌ Testing Issues
- Tests that require external systems
- Mocking domain objects
- Testing implementation details instead of behavior
- Brittle tests that break with refactoring

## Refactoring Guidelines

### When Adding New Features
1. **Extend existing interfaces** rather than changing them
2. **Create new use cases** instead of modifying existing ones
3. **Add new adapters** for different external systems
4. **Maintain backward compatibility** in public interfaces

### When Changing External Dependencies
1. **Update only the adapter** - domain and application layers unchanged
2. **Implement new interface** if contract changes significantly
3. **Use adapter pattern** to bridge interface differences
4. **Migrate gradually** using feature flags if needed

## Success Metrics

Your implementation should achieve:
- **High testability** - easy to unit test business logic
- **Low coupling** - changes in one layer don't affect others
- **High cohesion** - related functionality grouped together
- **Flexibility** - easy to swap external dependencies
- **Maintainability** - clear separation of concerns

## Language-Specific Adaptations

### For Object-Oriented Languages
- Use abstract classes or interfaces for ports
- Implement dependency injection through constructors
- Organize code in packages/modules by layer

### For Functional Languages
- Use higher-order functions for dependency injection
- Model entities as immutable data structures with associated functions
- Use modules to organize layers

### For Dynamic Languages
- Use duck typing for port definitions where appropriate
- Implement explicit interface checking if needed
- Use module systems to enforce layer boundaries

Remember: The goal is to create a system where business logic is the most important and stable part, while external concerns can evolve independently. Adapt these principles to your language's idioms while maintaining the core architectural intent.