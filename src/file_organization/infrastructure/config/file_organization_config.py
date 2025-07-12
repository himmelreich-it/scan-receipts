"""Configuration constants and paths for file organization operations."""

from pathlib import Path

# Folder paths - following existing project patterns
PROJECT_ROOT = Path.cwd()
DEFAULT_INPUT_FOLDER = PROJECT_ROOT / "input"
DEFAULT_DONE_FOLDER = PROJECT_ROOT / "done"

# Timestamp format for archived files
# Format: %Y%m%d-%H%M%S%f (e.g., 20240315-143052123456)
ARCHIVE_TIMESTAMP_FORMAT = "%Y%m%d-%H%M%S%f"

# Error message templates for consistent error reporting
FOLDER_CREATION_ERROR_TEMPLATE = "Cannot create {folder_name} folder: {error_details}"
FILE_COPY_ERROR_TEMPLATE = "Cannot copy file {filename}: {error_details}"
FILE_ACCESS_ERROR_TEMPLATE = "Cannot {operation} file {filename}: {error_details}"

# Folder names for error messages
INPUT_FOLDER_NAME = "input"
DONE_FOLDER_NAME = "done"
