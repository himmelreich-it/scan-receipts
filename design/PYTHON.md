# Python Coding Best Practices

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

# Local application imports
from .utils import helper_function
from .core import Receipt
```

## Type Hints
- Use type hints for all function parameters and return types
- Import types from `typing` module when needed
```python
from typing import List, Dict, Optional, Union

def process_receipts(receipts: List[Receipt]) -> Dict[str, float]:
    return {}
```

## Error Handling
- Use specific exception types rather than bare `except:`
- Include meaningful error messages
- Use context managers for resource management
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
```python
def extract_total(receipt_text: str) -> Optional[float]:
    """Extract total amount from receipt text.
    
    Args:
        receipt_text: Raw text extracted from receipt image
        
    Returns:
        Total amount as float, or None if not found
        
    Raises:
        ValueError: If text format is invalid
    """
    pass
```

## Testing
- Write unit tests for all functions
- Use pytest as the testing framework
- Aim for high test coverage
- Use meaningful test names that describe the scenario
- Configure pytest settings in pytest.ini

## Logging
- Use the `logging` module instead of print statements
- Configure appropriate log levels
- Include context in log messages
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

## Project Structure
```
scan-receipts/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── ocr.py
│   │   └── parser.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_core/
│   │   └── test_utils/
│   └── integration/
│       ├── __init__.py
│       └── test_e2e/
├── pytest.ini
├── pyproject.toml
└── README.md
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

## Security
- Validate all inputs
- Use environment variables for sensitive configuration
- Never commit secrets to version control
- Sanitize file paths to prevent directory traversal