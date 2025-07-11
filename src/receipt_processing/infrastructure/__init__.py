"""Infrastructure layer for receipt processing."""

from .config import FileProcessingConfig
from .adapters import LocalFileRepository

__all__ = [
    "FileProcessingConfig",
    "LocalFileRepository",
]