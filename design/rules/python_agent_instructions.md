# Python Coding Best Practices for AI Agents

## Code Style and Formatting

### PEP 8 Compliance
- Follow PEP 8 guidelines for code formatting
- Use 4 spaces for indentation (no tabs)
- Line length should not exceed 79 characters for code, 72 for comments
- Use snake_case for variables and functions, PascalCase for classes

### Import Organization
```python
# Standard library imports
import os
import sys
from pathlib import Path

# Third-party imports
import requests
import pandas as pd

# Local application imports (use absolute paths)
from mypackage.utils import helper_function
from mypackage.core import Receipt
```

## Package and Module Organization

### Module Design Principles
- **Consolidate related functionality**: Use `models.py` for data classes, `exceptions.py` for custom exceptions, `utils.py` for utilities
- **Avoid one-class-per-file**: Group related classes/functions in the same module unless >500 lines or distinct responsibilities
- **Use descriptive module names**: `parser.py`, `validators.py`, `handlers.py` over generic names

### Package Structure
```
myproject/
├── src/
│   └── mypackage/
│       ├── __init__.py          # Public API definition
│       ├── models.py            # Data models and domain objects
│       ├── core.py              # Main business logic
│       ├── utils.py             # Utility functions
│       ├── exceptions.py        # Custom exceptions
│       └── config.py            # Configuration
├── tests/
│   ├── test_models.py
│   ├── test_core.py
│   └── test_utils.py
└── pyproject.toml
```

### Public API Design
- Define package's public interface in `__init__.py`
- Keep internal modules private unless explicitly exported
- Use `__all__` to control exports
```python
# src/mypackage/__init__.py
from models import Receipt, Transaction, User
from core import process_receipt
from exceptions import ParseError, ValidationError

__all__ = ['Receipt', 'Transaction', 'User', 'process_receipt', 'ParseError', 'ValidationError']
```

### Import Strategy
- **External users**: Import from package level only
```python
# Good: Clean public API usage
from mypackage import Receipt, process_receipt

# Avoid: Direct internal module imports
from mypackage.models import Receipt
```
- **Internal modules**: Use absolute imports within the same package
```python
# Good: Internal module imports with absolute paths
from mypackage.models import Receipt
from mypackage.utils import validate_input
from mypackage.exceptions import ValidationError

# Avoid: Relative imports
from .models import Receipt
from .utils import validate_input
```
- **Subpackages**: Create only when >7-10 modules or distinct functional areas
- **Absolute local imports** Always assume we run from the src folder, base absolute import paths on this assumption

## Agent Decision Making
- When multiple approaches are valid, prioritize readability over performance unless specified
- Default to more explicit code over clever shortcuts
- If requirements are ambiguous, ask for clarification rather than assuming
- Always explain significant architectural decisions in comments
- Generate complete, runnable code blocks with necessary imports

## Type Hints
- Use type hints for all function parameters and return types
- Import types from `typing` module when needed
- Include type information even for obvious cases to aid code clarity
```python
from typing import List, Dict, Optional, Union

def process_receipts(receipts: List[Receipt]) -> Dict[str, float]:
    return {}
```

## Error Handling
- Use specific exception types rather than bare `except:`
- Include meaningful error messages
- Use context managers for resource management
- Validate inputs at function boundaries, not just external inputs
- Default to conservative error handling (fail fast)
- Add recovery strategies for common failure modes specified in requirements
```python
try:
    with open(file_path, 'r') as f:
        data = f.read()
except FileNotFoundError:
    logger.error(f"File not found: {file_path}")
    raise
except PermissionError:
    logger.error(f"Permission denied: {file_path}")
    raise
```

## Documentation
- Use docstrings for all modules, classes, and functions
- Follow Google or NumPy docstring format
- Include usage examples in docstrings
- Document assumptions and limitations
- Add performance considerations for data processing code
- Link related functions and classes in docstrings
```python
def extract_total(receipt_text: str) -> Optional[float]:
    """Extract total amount from receipt text.
    
    Args:
        receipt_text: Raw text extracted from receipt image
        
    Returns:
        Total amount as float, or None if not found
        
    Raises:
        ValueError: If text format is invalid
        
    Example:
        >>> extract_total("Total: $45.67")
        45.67
        >>> extract_total("No total here")
        None
    """
    pass
```

## Testing Strategy
- Generate tests that validate the functional specification requirements
- Test only the error conditions explicitly mentioned in the spec
- Test the happy path and one level of error handling (e.g., file not found, invalid input format)
- Avoid testing implementation details or hypothetical edge cases
- If the spec doesn't mention an error case, don't test for it
- Use pytest as the testing framework
- Use meaningful test names that describe the scenario being tested
- Generate tests alongside implementation code
- Provide realistic test data fixtures when needed
- Configure pytest settings in pytest.ini
- Do NOT add src in imports, the pythonpath is set in the pytest.ini

```python
# Good: Tests what the spec requires
def test_extract_total_found():
    assert extract_total("Total: $45.67") == 45.67

def test_extract_total_not_found():
    assert extract_total("No total here") is None

# Avoid: Testing hypothetical edge cases not in spec
```

## Logging
- Use the `logging` module instead of print statements
- Configure appropriate log levels
- Include context in log messages
- Add inline comments explaining complex logic
```python
import logging

logger = logging.getLogger(__name__)

def process_image(image_path: str) -> None:
    logger.info(f"Processing image: {image_path}")
    try:
        # processing logic
        logger.debug("Image processed successfully")
    except Exception as e:
        logger.error(f"Failed to process {image_path}: {e}")
        raise
```

## Dependencies (uv)
- Use `uv` for dependency management
- Pin dependency versions in pyproject.toml
- Use virtual environments with `uv venv`
- Keep dependencies minimal and well-justified
- Regular security updates with `uv sync`

## Performance
- Use list comprehensions for simple transformations
- Prefer generators for memory efficiency with large datasets
- Profile code when performance is critical
- Use appropriate data structures (sets for membership tests, etc.)

## Progressive Implementation
- Start with minimal viable implementation that meets the spec
- Add features incrementally with clear boundaries
- Use TODO/FIXME comments for known improvements mentioned in requirements
- Validate each increment before proceeding
- Include assertions for internal consistency checks that help debugging

## Security
- Validate all inputs according to specification requirements
- Use environment variables for sensitive configuration
- Never commit secrets to version control
- Sanitize file paths to prevent directory traversal when file handling is specified