"""Validation rules for receipt data."""

from datetime import datetime
from pathlib import Path
from typing import Final

from scan_receipts.folders import RECEIPT_EXTENSIONS

# Business rules
MIN_TOTAL_AMOUNT: Final[float] = 0.01
MAX_TOTAL_AMOUNT: Final[float] = 999999.99
MIN_CONFIDENCE_SCORE: Final[float] = 0.0
MAX_CONFIDENCE_SCORE: Final[float] = 1.0


def is_valid_receipt_file(file_path: Path) -> bool:
    """Validate if file is a supported receipt format.
    
    Args:
        file_path: Path to the file to validate.
        
    Returns:
        True if file is a supported receipt format.
    """
    return (
        file_path.exists() 
        and file_path.is_file() 
        and file_path.suffix.lower() in RECEIPT_EXTENSIONS
    )


def is_valid_amount(amount: float) -> bool:
    """Validate receipt amount.
    
    Args:
        amount: Amount to validate.
        
    Returns:
        True if amount is within valid range.
    """
    return MIN_TOTAL_AMOUNT <= amount <= MAX_TOTAL_AMOUNT


def is_valid_confidence(confidence: float) -> bool:
    """Validate confidence score.
    
    Args:
        confidence: Confidence score to validate.
        
    Returns:
        True if confidence is within valid range.
    """
    return MIN_CONFIDENCE_SCORE <= confidence <= MAX_CONFIDENCE_SCORE


def is_valid_vendor(vendor: str) -> bool:
    """Validate vendor name.
    
    Args:
        vendor: Vendor name to validate.
        
    Returns:
        True if vendor name is valid.
    """
    return bool(vendor and vendor.strip())


def is_recent_date(date: datetime, max_days_ago: int = 365) -> bool:
    """Check if date is recent (within specified days).
    
    Args:
        date: Date to check.
        max_days_ago: Maximum days in the past to consider recent.
        
    Returns:
        True if date is recent.
    """
    now = datetime.now()
    days_diff = (now - date).days
    return 0 <= days_diff <= max_days_ago