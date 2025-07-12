"""CSV Data Output package for receipt processing.

This package provides CSV file creation and management functionality
for storing extracted receipt data with auto-incrementing IDs.
"""

from .csv_service import CsvService

__all__ = ["CsvService"]
