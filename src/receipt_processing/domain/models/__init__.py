"""Domain models for receipt processing."""

from .file_path import FilePath
from .file_extension import FileExtension
from .file_content import FileContent
from .processable_file import ProcessableFile

__all__ = [
    "FilePath",
    "FileExtension", 
    "FileContent",
    "ProcessableFile",
]