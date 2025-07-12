"""Tests for extraction result value objects."""

import pytest
from decimal import Decimal
from datetime import datetime
from pathlib import Path

from ai_extraction.domain.models.extraction_result import (
    ReceiptData, ErrorReceiptData, ExtractionResult
)


class TestReceiptData:
    """Test ReceiptData value object."""
    
    def test_valid_receipt_data_creation(self):
        """Test: When valid receipt data is provided, create ReceiptData object successfully."""
        receipt_data = ReceiptData(
            amount=Decimal('45.67'),
            tax=Decimal('5.67'),
            description="Test Store",
            currency="EUR",
            date="15-03-2024",
            confidence=85
        )
        
        assert receipt_data.amount == Decimal('45.67')
        assert receipt_data.tax == Decimal('5.67')
        assert receipt_data.description == "Test Store"
        assert receipt_data.currency == "EUR"
        assert receipt_data.date == "15-03-2024"
        assert receipt_data.confidence == 85
    
    def test_currency_code_validation_uppercase(self):
        """Test: When currency is provided in lowercase, convert to uppercase."""
        receipt_data = ReceiptData(
            amount=Decimal('45.67'),
            description="Test Store",
            currency="eur",
            date="15-03-2024",
            confidence=85
        )
        
        assert receipt_data.currency == "EUR"
    
    def test_invalid_currency_code_length(self):
        """Test: When currency code is not 3 letters, raise validation error."""
        with pytest.raises(ValueError, match="String should have at most 3 characters"):
            ReceiptData(
                amount=Decimal('45.67'),
                description="Test Store",
                currency="EURO",
                date="15-03-2024",
                confidence=85
            )
    
    def test_invalid_date_format(self):
        """Test: When date is not in dd-MM-YYYY format, raise validation error."""
        with pytest.raises(ValueError, match="Date must be in dd-MM-YYYY format"):
            ReceiptData(
                amount=Decimal('45.67'),
                description="Test Store",
                currency="EUR",
                date="2024-03-15",
                confidence=85
            )
    
    def test_confidence_score_validation_range(self):
        """Test: When confidence score is outside 0-100 range, raise validation error."""
        with pytest.raises(ValueError):
            ReceiptData(
                amount=Decimal('45.67'),
                description="Test Store",
                currency="EUR",
                date="15-03-2024",
                confidence=150
            )


class TestErrorReceiptData:
    """Test ErrorReceiptData value object."""
    
    def test_valid_error_data_creation(self):
        """Test: When valid error data is provided, create ErrorReceiptData object successfully."""
        error_data = ErrorReceiptData(description="ERROR-API")
        
        assert error_data.amount == Decimal('0')
        assert error_data.tax == Decimal('0')
        assert error_data.description == "ERROR-API"
        assert error_data.currency == ""
        assert error_data.date == ""
        assert error_data.confidence == 0
    
    def test_invalid_error_description(self):
        """Test: When error description is not valid error type, raise validation error."""
        with pytest.raises(ValueError, match="Error description must be one of"):
            ErrorReceiptData(description="INVALID-ERROR")


class TestExtractionResult:
    """Test ExtractionResult container."""
    
    def test_successful_extraction_result(self):
        """Test: When extraction succeeds, create result with success=True and receipt data."""
        receipt_data = ReceiptData(
            amount=Decimal('45.67'),
            description="Test Store",
            currency="EUR",
            date="15-03-2024",
            confidence=85
        )
        
        result = ExtractionResult(
            success=True,
            data=receipt_data,
            filename="test_receipt.jpg"
        )
        
        assert result.success is True
        assert result.data == receipt_data
        assert result.error_data is None
        assert result.filename == "test_receipt.jpg"
        assert isinstance(result.processing_timestamp, datetime)
    
    def test_failed_extraction_result(self):
        """Test: When extraction fails, create result with success=False and error data."""
        error_data = ErrorReceiptData(description="ERROR-API")
        
        result = ExtractionResult(
            success=False,
            error_data=error_data,
            filename="test_receipt.jpg"
        )
        
        assert result.success is False
        assert result.data is None
        assert result.error_data == error_data
        assert result.filename == "test_receipt.jpg"
    
    def test_get_data_success(self):
        """Test: When result is successful, get_data returns receipt data."""
        receipt_data = ReceiptData(
            amount=Decimal('45.67'),
            description="Test Store",
            currency="EUR",
            date="15-03-2024",
            confidence=85
        )
        
        result = ExtractionResult(
            success=True,
            data=receipt_data,
            filename="test_receipt.jpg"
        )
        
        assert result.get_data() == receipt_data
    
    def test_get_data_error(self):
        """Test: When result is error, get_data returns error data."""
        error_data = ErrorReceiptData(description="ERROR-API")
        
        result = ExtractionResult(
            success=False,
            error_data=error_data,
            filename="test_receipt.jpg"
        )
        
        assert result.get_data() == error_data