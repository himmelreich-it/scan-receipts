"""Value objects representing extracted receipt data and results."""

from decimal import Decimal
from typing import Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class ReceiptData(BaseModel):
    """Value object for successfully extracted receipt data."""
    
    amount: Decimal = Field(..., description="Total purchase amount")
    tax: Decimal = Field(default=Decimal('0'), description="Tax amount")
    tax_percentage: Decimal = Field(default=Decimal('0'), description="Tax percentage")
    description: str = Field(..., max_length=500, description="Business name or transaction description")
    currency: str = Field(..., max_length=3, description="Currency code (EUR, USD, etc.)")
    date: str = Field(..., description="Transaction date in dd-MM-YYYY format")
    confidence: int = Field(..., ge=0, le=100, description="AI confidence score")
    
    @field_validator('date')
    def validate_date_format(cls, v):
        """Ensure date is in dd-MM-YYYY format."""
        try:
            datetime.strptime(v, '%d-%m-%Y')
            return v
        except ValueError:
            raise ValueError('Date must be in dd-MM-YYYY format (e.g., "15-03-2024")')
    
    @field_validator('currency')
    def validate_currency_code(cls, v):
        """Ensure currency is uppercase 3-letter code."""
        if len(v) != 3 or not v.isalpha():
            raise ValueError('Currency must be 3-letter code (e.g., "EUR", "USD")')
        return v.upper()


class ErrorReceiptData(BaseModel):
    """Value object for failed extraction with error categorization."""
    
    amount: Decimal = Field(default=Decimal('0'))
    tax: Decimal = Field(default=Decimal('0'))
    tax_percentage: Decimal = Field(default=Decimal('0'))
    description: str  # ERROR-API, ERROR-FILE, ERROR-PARSE, ERROR-UNKNOWN
    currency: str = Field(default="")
    date: str = Field(default="")
    confidence: int = Field(default=0)
    
    @field_validator('description')
    def validate_error_description(cls, v):
        """Ensure description is valid error type."""
        valid_errors = {'ERROR-API', 'ERROR-FILE', 'ERROR-PARSE', 'ERROR-UNKNOWN'}
        if v not in valid_errors:
            raise ValueError(f'Error description must be one of: {valid_errors}')
        return v


class ExtractionResult(BaseModel):
    """Container for extraction results with success/failure indication."""
    
    success: bool
    data: Optional[ReceiptData] = None
    error_data: Optional[ErrorReceiptData] = None
    filename: str
    processing_timestamp: datetime = Field(default_factory=datetime.now)
    
    def get_data(self) -> Union[ReceiptData, ErrorReceiptData]:
        """Get the appropriate data object based on success status."""
        if self.success and self.data is not None:
            return self.data
        elif not self.success and self.error_data is not None:
            return self.error_data
        else:
            raise ValueError("ExtractionResult is in invalid state - no data available")