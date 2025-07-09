# Domain-Driven Design (DDD) Instructions for Code Agents

## Core DDD Principles

### 1. Domain-First Approach
- **Always start with domain understanding** before writing any code
- Ask clarifying questions about business rules, constraints, and processes
- Identify the core domain vs supporting subdomains vs generic subdomains
- Focus on business value and domain experts' language

### 2. Ubiquitous Language
- **Use domain terminology consistently** across all code, comments, and documentation
- Avoid technical jargon in domain models
- When encountering ambiguous terms, ask for clarification
- Code should read like domain expert conversations

## Strategic DDD Patterns

### Bounded Contexts
- **Identify context boundaries** by looking for:
  - Different meanings of the same term (e.g., "Customer" in Sales vs Support)
  - Different business rules for similar concepts
  - Natural team/organizational boundaries
  - Data consistency requirements

- **Each bounded context should have:**
  - Its own domain model
  - Its own ubiquitous language
  - Clear boundaries and interfaces

### Context Mapping
- **Define relationships between bounded contexts:**
  - **Shared Kernel**: Common domain models between contexts
  - **Customer-Supplier**: Upstream context serves downstream
  - **Conformist**: Downstream conforms to upstream model
  - **Anti-corruption Layer**: Protect domain from external systems
  - **Open Host Service**: Context exposes public API
  - **Published Language**: Well-documented shared protocol

### Subdomain Classification
- **Core Domain**: Main business differentiator, invest most effort
- **Supporting Subdomain**: Important but not core, can be built in-house
- **Generic Subdomain**: Solved problems, prefer off-the-shelf solutions

## Tactical DDD Patterns

### Entities
- **Create entities when objects have:**
  - Unique identity that persists over time
  - Lifecycle and state changes
  - Business behavior, not just data

```python
from dataclasses import dataclass
from typing import List
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"

@dataclass(frozen=True)
class OrderId:
    value: str

class Order:  # Entity
    def __init__(self, order_id: OrderId, customer_id: CustomerId):
        self._id = order_id
        self._customer_id = customer_id
        self._status = OrderStatus.PENDING
        self._line_items: List[LineItem] = []
    
    @property
    def id(self) -> OrderId:
        return self._id
    
    def confirm(self) -> None:
        if self._status != OrderStatus.PENDING:
            raise DomainError("Can only confirm pending orders")
        self._status = OrderStatus.CONFIRMED
    
    def ship(self) -> None:
        if self._status != OrderStatus.CONFIRMED:
            raise DomainError("Can only ship confirmed orders")
        self._status = OrderStatus.SHIPPED
```

### Value Objects
- **Use value objects for:**
  - Concepts without identity
  - Immutable data with business meaning
  - Encapsulating business rules and validations

```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")
        if not self.currency:
            raise ValueError("Currency is required")
    
    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def multiply(self, factor: Decimal) -> 'Money':
        return Money(self.amount * factor, self.currency)

@dataclass(frozen=True)
class Email:
    address: str
    
    def __post_init__(self):
        if '@' not in self.address:
            raise ValueError("Invalid email address")
```

### Aggregates
- **Design aggregates to:**
  - Enforce business invariants
  - Define transaction boundaries
  - Control access to entities within the boundary

```python
class OrderAggregate:
    def __init__(self, order_id: OrderId, customer_id: CustomerId):
        self._order = Order(order_id, customer_id)
        self._line_items: List[LineItem] = []
        self._domain_events: List[DomainEvent] = []
    
    def add_line_item(self, product_id: ProductId, quantity: int, unit_price: Money) -> None:
        # Business invariant: Cannot add items to shipped orders
        if self._order.status == OrderStatus.SHIPPED:
            raise DomainError("Cannot modify shipped orders")
        
        line_item = LineItem(product_id, quantity, unit_price)
        self._line_items.append(line_item)
        
        # Raise domain event
        self._domain_events.append(LineItemAdded(self._order.id, product_id, quantity))
    
    def get_total(self) -> Money:
        if not self._line_items:
            return Money(Decimal('0'), 'USD')
        
        total = self._line_items[0].total()
        for item in self._line_items[1:]:
            total = total.add(item.total())
        return total
    
    def get_domain_events(self) -> List[DomainEvent]:
        return self._domain_events.copy()
    
    def clear_domain_events(self) -> None:
        self._domain_events.clear()
```

### Domain Services
- **Create domain services for:**
  - Operations that don't naturally belong to an entity or value object
  - Business processes involving multiple aggregates
  - Complex domain calculations

```python
class PricingService:
    def __init__(self, discount_repository: DiscountRepository):
        self._discount_repository = discount_repository
    
    def calculate_order_total(self, order: OrderAggregate, customer: Customer) -> Money:
        base_total = order.get_total()
        
        # Complex pricing logic that doesn't belong in Order
        applicable_discounts = self._discount_repository.find_applicable_discounts(
            customer.customer_type, 
            order.get_line_items()
        )
        
        for discount in applicable_discounts:
            base_total = discount.apply(base_total)
        
        return base_total
```

### Specifications
- **Use specifications for:**
  - Complex business rules
  - Reusable business logic
  - Querying with business meaning

```python
from abc import ABC, abstractmethod

class Specification(ABC):
    @abstractmethod
    def is_satisfied_by(self, candidate) -> bool:
        pass
    
    def and_(self, other: 'Specification') -> 'Specification':
        return AndSpecification(self, other)

class CustomerEligibleForDiscountSpec(Specification):
    def __init__(self, minimum_order_value: Money):
        self._minimum_order_value = minimum_order_value
    
    def is_satisfied_by(self, customer: Customer) -> bool:
        return (customer.is_premium_member() and 
                customer.total_orders_value() >= self._minimum_order_value)

class AndSpecification(Specification):
    def __init__(self, left: Specification, right: Specification):
        self._left = left
        self._right = right
    
    def is_satisfied_by(self, candidate) -> bool:
        return self._left.is_satisfied_by(candidate) and self._right.is_satisfied_by(candidate)
```

### Factories
- **Use factories for:**
  - Complex aggregate creation
  - Encapsulating creation logic
  - Ensuring invariants during creation

```python
class OrderFactory:
    def __init__(self, product_catalog: ProductCatalog):
        self._product_catalog = product_catalog
    
    def create_order(self, customer_id: CustomerId, items: List[OrderItemRequest]) -> OrderAggregate:
        order_id = OrderId(str(uuid.uuid4()))
        order = OrderAggregate(order_id, customer_id)
        
        for item_request in items:
            product = self._product_catalog.find_by_id(item_request.product_id)
            if not product:
                raise DomainError(f"Product {item_request.product_id} not found")
            
            if not product.is_available():
                raise DomainError(f"Product {item_request.product_id} is not available")
            
            order.add_line_item(
                item_request.product_id,
                item_request.quantity,
                product.price
            )
        
        return order
```

### Domain Events
- **Use domain events for:**
  - Decoupling within bounded contexts
  - Eventual consistency between aggregates
  - Integration between bounded contexts

```python
from abc import ABC
from datetime import datetime
from dataclasses import dataclass

class DomainEvent(ABC):
    pass

@dataclass(frozen=True)
class OrderConfirmed(DomainEvent):
    order_id: OrderId
    customer_id: CustomerId
    total_amount: Money
    occurred_at: datetime

@dataclass(frozen=True)
class PaymentProcessed(DomainEvent):
    order_id: OrderId
    payment_amount: Money
    occurred_at: datetime

class OrderAggregate:
    def confirm(self) -> None:
        if self._status != OrderStatus.PENDING:
            raise DomainError("Can only confirm pending orders")
        
        self._status = OrderStatus.CONFIRMED
        
        # Raise domain event
        self._domain_events.append(OrderConfirmed(
            self._order.id,
            self._order.customer_id,
            self.get_total(),
            datetime.now()
        ))
```

### Repositories (Domain Interfaces)
- **Define repository interfaces in domain layer:**
  - Focus on domain needs, not persistence details
  - Use domain language
  - Return domain objects

```python
from abc import ABC, abstractmethod

class OrderRepository(ABC):
    @abstractmethod
    def find_by_id(self, order_id: OrderId) -> Optional[OrderAggregate]:
        pass
    
    @abstractmethod
    def find_by_customer(self, customer_id: CustomerId) -> List[OrderAggregate]:
        pass
    
    @abstractmethod
    def save(self, order: OrderAggregate) -> None:
        pass
    
    @abstractmethod
    def find_orders_awaiting_shipment(self) -> List[OrderAggregate]:
        pass
```

### Anti-Corruption Layer
- **Protect domain from external systems:**
  - Translate between domain and external models
  - Isolate domain from external changes
  - Maintain domain integrity

```python
class PaymentGatewayACL:
    def __init__(self, external_payment_service: ExternalPaymentService):
        self._external_service = external_payment_service
    
    def process_payment(self, order: OrderAggregate) -> PaymentResult:
        # Translate domain model to external format
        external_request = self._translate_to_external(order)
        
        # Call external service
        external_response = self._external_service.charge_payment(external_request)
        
        # Translate back to domain model
        return self._translate_to_domain(external_response)
    
    def _translate_to_external(self, order: OrderAggregate) -> ExternalPaymentRequest:
        return ExternalPaymentRequest(
            amount=float(order.get_total().amount),
            currency=order.get_total().currency,
            reference=order.id.value
        )
    
    def _translate_to_domain(self, response: ExternalPaymentResponse) -> PaymentResult:
        if response.status == "success":
            return PaymentResult.success(PaymentId(response.transaction_id))
        else:
            return PaymentResult.failure(response.error_message)
```

## DDD-Specific Implementation Rules

### Aggregate Design Rules
- **Keep aggregates small**: Only include what's needed for consistency
- **One aggregate per transaction**: Don't modify multiple aggregates in one transaction
- **Reference by ID**: Aggregates reference other aggregates by ID only
- **Eventual consistency**: Use domain events for cross-aggregate consistency

### Domain Event Guidelines
- **Events are facts**: Use past tense naming (OrderConfirmed, not ConfirmOrder)
- **Events are immutable**: Once created, they cannot be changed
- **Events contain relevant data**: Include what subscribers need
- **Events enable loose coupling**: Aggregates don't know about subscribers

### Ubiquitous Language Enforcement
- **Class names reflect domain concepts**: Order, Customer, Product (not OrderEntity)
- **Method names use domain verbs**: confirm(), ship(), cancel()
- **Exception names are domain-specific**: InsufficientInventoryError, InvalidOrderStateError
- **Comments explain business rules**: Why, not what

### Bounded Context Integration
- **Published Language**: Define shared schemas for integration
- **Shared Kernel**: Share common domain models (use sparingly)
- **Customer-Supplier**: Upstream provides what downstream needs
- **Conformist**: Downstream adapts to upstream model

## Domain Model Evolution

### Refactoring Guidelines
- **Listen to domain experts**: Model should match their mental model
- **Evolve ubiquitous language**: Update code when language changes
- **Respect context boundaries**: Don't leak concepts between contexts
- **Preserve business invariants**: Ensure rules remain enforced

### Context Mapping Evolution
- **Monitor context relationships**: Detect when boundaries need adjustment
- **Manage shared concepts**: Decide when to split or merge contexts
- **Version published languages**: Handle breaking changes gracefully

## Common DDD Mistakes to Avoid

### Domain Layer Violations
- **Don't put infrastructure concerns in domain**: No database, UI, or external service dependencies
- **Avoid anemic domain models**: Entities should have behavior, not just data
- **Don't expose aggregate internals**: Only aggregate root should be publicly accessible

### Aggregate Mistakes
- **Don't create large aggregates**: Keep them focused on single business concept
- **Don't navigate associations**: Use repositories to load related aggregates
- **Don't ignore eventual consistency**: Accept that some operations will be async

### Context Boundary Violations
- **Don't share domain models**: Each context should have its own models
- **Don't bypass context boundaries**: Always go through defined interfaces
- **Don't mix ubiquitous languages**: Keep each context's language pure

---

*This guide focuses exclusively on DDD concepts and patterns. Use in conjunction with general software design patterns and coding standards.*