"""CSV operations port."""

from abc import ABC, abstractmethod
from typing import Any, List


class CSVPort(ABC):
    """Interface for CSV operations."""
    
    @abstractmethod
    def read_staging_data(self, csv_path: str) -> List[Any]:
        """Read staging data from CSV.
        
        Args:
            csv_path: Path to CSV file.
            
        Returns:
            List of staging data records.
        """
        pass
    
    @abstractmethod  
    def write_staging_data(self, csv_path: str, data: List[Any]) -> None:
        """Write staging data to CSV.
        
        Args:
            csv_path: Path to CSV file.
            data: Data to write.
        """
        pass