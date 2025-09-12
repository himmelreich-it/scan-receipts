"""Receipt Scanner TUI Application.

A terminal user interface for processing receipts from scanned documents.
Validates configuration, manages folders, and provides an interactive menu.

This package provides backward compatibility while the new hexagonal architecture
is located in the src/ root level.
"""

from scan_receipts.config import AppConfig
from scan_receipts.main import main

__version__ = "0.1.0"
__all__ = ["AppConfig", "main"]