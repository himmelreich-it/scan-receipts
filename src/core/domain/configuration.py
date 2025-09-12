"""Configuration domain entity."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Final, List

from dotenv import load_dotenv  # type: ignore

REQUIRED_ENV_VARS: Final[List[str]] = [
    "INCOMING_RECEIPTS_FOLDER",
    "SCANNED_FOLDER", 
    "IMPORTED_FOLDER",
    "FAILED_FOLDER",
    "CSV_STAGING_FILE",
    "XLSX_OUTPUT_FILE",
]


@dataclass(frozen=True)
class AppConfig:
    """Application configuration loaded from environment variables."""
    
    incoming_folder: Path
    scanned_folder: Path
    imported_folder: Path
    failed_folder: Path
    csv_staging_file: Path
    xlsx_output_file: Path
    
    @classmethod
    def from_env(cls, load_dotenv_file: bool = True) -> "AppConfig":
        """Load configuration from environment variables.
        
        Args:
            load_dotenv_file: Whether to load .env file. Set to False in tests.
        
        Returns:
            AppConfig instance with validated paths.
            
        Raises:
            ValueError: If required environment variables are missing.
        """
        if load_dotenv_file:
            load_dotenv()
        
        missing_vars: List[str] = []
        for var in REQUIRED_ENV_VARS:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")
        
        return cls(
            incoming_folder=Path(os.getenv("INCOMING_RECEIPTS_FOLDER")),  # type: ignore
            scanned_folder=Path(os.getenv("SCANNED_FOLDER")),  # type: ignore
            imported_folder=Path(os.getenv("IMPORTED_FOLDER")),  # type: ignore
            failed_folder=Path(os.getenv("FAILED_FOLDER")),  # type: ignore
            csv_staging_file=Path(os.getenv("CSV_STAGING_FILE")),  # type: ignore
            xlsx_output_file=Path(os.getenv("XLSX_OUTPUT_FILE")),  # type: ignore
        )