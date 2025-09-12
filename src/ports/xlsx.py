"""XLSX operations port."""

from abc import ABC, abstractmethod
from typing import Any, List


class XLSXPort(ABC):
    """Interface for Excel operations."""
    
    @abstractmethod
    def read_xlsx_data(self, xlsx_path: str) -> List[Any]:
        """Read data from XLSX file.
        
        Args:
            xlsx_path: Path to XLSX file.
            
        Returns:
            List of records from XLSX.
        """
        pass
    
    @abstractmethod
    def append_xlsx_data(self, xlsx_path: str, data: List[Any]) -> None:
        """Append data to XLSX file.
        
        Args:
            xlsx_path: Path to XLSX file.
            data: Data to append.
        """
        pass