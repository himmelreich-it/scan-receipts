# Python Coding Guidelines for AI Agents

## Core Principles
- **DRY**: Extract common patterns into reusable functions/classes, use constants for repeated values
- **SOLID**: Single responsibility, composition over inheritance, depend on abstractions
- **Fail Fast**: Validate inputs early, use type hints, explicit error handling
- **Immutability**: Use `@dataclass(frozen=True)` for value objects, `Final` for constants

```python
from dataclasses import dataclass
from typing import Final, Protocol

@dataclass(frozen=True)
class Receipt:
    total: float
    vendor: str

MAX_RETRIES: Final[int] = 3

class ImageProcessor(Protocol):
    def process(self, image_path: str) -> str: ...
```

## Code Style (PEP 8)
- 4 spaces indentation, 79 char lines, snake_case/PascalCase
- Import order: standard library → third-party → local (absolute paths)
- Type hints for all parameters/returns, meaningful docstrings

## Package Structure
```
src/mypackage/
├── __init__.py          # Public API only
├── models.py            # Data classes
├── core.py              # Business logic  
├── utils.py             # Utilities
├── exceptions.py        # Custom exceptions
└── config.py            # Configuration
```

**Import Rules:**
- External users: `from mypackage import Receipt` (package level only)
- Internal modules: `from mypackage.models import Receipt` (absolute paths)
- Always assume running from `src/` folder
- Apply "API flattening" or "namespace flattening" pattern

## Configuration & Resources
```python
@dataclass(frozen=True)
class AppConfig:
    api_key: str
    debug: bool = False
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        api_key = os.getenv('API_KEY')
        if not api_key:
            raise ValueError("API_KEY required")
        return cls(api_key=api_key)

# Always use context managers
with open(file_path, 'r') as f:
    data = f.read()
```

## Error Handling & Logging
- Specific exceptions, meaningful messages, validate at function boundaries
- Use `logging` module, include context in messages
- Default to conservative error handling (fail fast)

```python
import logging
logger = logging.getLogger(__name__)

def process_file(path: str) -> None:
    logger.info(f"Processing: {path}")
    try:
        # logic here
    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        raise
```

## Documentation & Testing
- Use `pytest`, not `unittest`
- Use pytest mocks not `unittest.mock`
- Google/NumPy docstring format with examples, assumptions, performance notes
- Test functional spec requirements only (happy path + explicit error cases)
- Use pytest, meaningful test names, realistic fixtures
- Document the API of a package in the ``__init__.py` as part of the API/namespace flattening pattern
- Configure pytest.ini with pythonpath, no `src` in test imports

```python
def extract_total(receipt_text: str) -> Optional[float]:
    """Extract total from receipt text.
    
    Args:
        receipt_text: Raw receipt text
        
    Returns:
        Total amount or None if not found
        
    Example:
        >>> extract_total("Total: $45.67")
        45.67
    """
```

## Agent Decision Making
- Prioritize readability over performance unless specified
- Explicit code over clever shortcuts
- Ask for clarification on ambiguous requirements
- Comment architectural decisions
- Generate complete, runnable code with imports

## Dependencies & Security
- Environment variables for sensitive config
- Validate inputs per specification
- Sanitize file paths when handling files

## Performance & Implementation
- List comprehensions for simple transforms, generators for large data
- Appropriate data structures (sets for membership)
- Progressive implementation: start minimal, add incrementally
- Use TODO/FIXME for known improvements from requirements