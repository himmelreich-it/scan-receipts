"""Unit tests for domain value objects."""

import pytest
from decimal import Decimal
from datetime import datetime
from receipt_processing_engine.domain.value_objects import (
    Amount, Tax, TaxPercentage, Currency, Description, ReceiptDate, 
    Confidence, ExtractionData
)


class TestAmount:
    """Test Amount value object."""
    
    def test_valid_amount(self):
        """Test: Amount accepts valid positive values."""
        amount = Amount(Decimal('45.67'))
        assert amount.value == Decimal('45.67')
    
    def test_zero_amount(self):
        """Test: Amount accepts zero value."""
        amount = Amount(Decimal('0'))
        assert amount.value == Decimal('0')
    
    def test_negative_amount_raises_error(self):
        """Test: Amount raises error for negative values."""
        with pytest.raises(ValueError, match="Amount must be non-negative"):
            Amount(Decimal('-10.50'))


class TestCurrency:
    """Test Currency value object."""
    
    def test_valid_currency_codes(self):
        """Test: Currency accepts valid 3-letter codes."""
        eur = Currency("EUR")
        usd = Currency("USD")
        gbp = Currency("GBP")
        
        assert eur.code == "EUR"
        assert usd.code == "USD"
        assert gbp.code == "GBP"
    
    def test_invalid_currency_codes(self):
        """Test: Currency rejects invalid codes."""
        with pytest.raises(ValueError, match="Currency code must be 3 uppercase letters"):
            Currency("eur")  # lowercase
        
        with pytest.raises(ValueError, match="Currency code must be 3 uppercase letters"):
            Currency("EURO")  # too long
        
        with pytest.raises(ValueError, match="Currency code must be 3 uppercase letters"):
            Currency("US")  # too short


class TestConfidence:
    """Test Confidence value object."""
    
    def test_valid_confidence_scores(self):
        """Test: Confidence accepts valid scores 0-100."""
        conf_0 = Confidence(0)
        conf_50 = Confidence(50)
        conf_100 = Confidence(100)
        
        assert conf_0.score == 0
        assert conf_50.score == 50
        assert conf_100.score == 100
    
    def test_invalid_confidence_scores(self):
        """Test: Confidence rejects invalid scores."""
        with pytest.raises(ValueError, match="Confidence score must be between 0 and 100"):
            Confidence(-1)
        
        with pytest.raises(ValueError, match="Confidence score must be between 0 and 100"):
            Confidence(101)


class TestDescription:
    """Test Description value object."""
    
    def test_valid_descriptions(self):
        """Test: Description accepts valid text."""
        desc = Description("Test Store")
        assert desc.text == "Test Store"
    
    def test_empty_description_raises_error(self):
        """Test: Description rejects empty text."""
        with pytest.raises(ValueError, match="Description cannot be empty"):
            Description("")
        
        with pytest.raises(ValueError, match="Description cannot be empty"):
            Description("   ")  # whitespace only


class TestReceiptDate:
    """Test ReceiptDate value object."""
    
    def test_valid_dates(self):
        """Test: ReceiptDate accepts valid past dates."""
        past_date = datetime(2023, 1, 15)
        receipt_date = ReceiptDate(past_date)
        assert receipt_date.date == past_date
    
    def test_future_date_raises_error(self):
        """Test: ReceiptDate rejects future dates."""
        future_date = datetime(2050, 1, 1)
        with pytest.raises(ValueError, match="Receipt date cannot be in the future"):
            ReceiptDate(future_date)
    
    def test_to_string_format(self):
        """Test: ReceiptDate formats correctly as dd-MM-YYYY."""
        date = datetime(2023, 1, 15)
        receipt_date = ReceiptDate(date)
        assert receipt_date.to_string() == "15-01-2023"


class TestExtractionData:
    """Test ExtractionData value object."""
    
    def test_extraction_data_creation(self):
        """Test: ExtractionData can be created with all fields."""
        extraction_data = ExtractionData(
            amount=Amount(Decimal('45.67')),
            tax=Tax(Decimal('5.67')),
            tax_percentage=TaxPercentage(Decimal('12.5')),
            description=Description("Test Store"),
            currency=Currency("EUR"),
            date=ReceiptDate(datetime(2023, 1, 15)),
            confidence=Confidence(85)
        )
        
        assert extraction_data.amount.value == Decimal('45.67')
        assert extraction_data.tax.value == Decimal('5.67')
        assert extraction_data.description.text == "Test Store"
        assert extraction_data.currency.code == "EUR"
        assert extraction_data.confidence.score == 85
    
    def test_from_api_response_valid(self):
        """Test: ExtractionData can be created from valid API response."""
        api_response = {
            "amount": 45.67,
            "tax": 5.67,
            "tax_percentage": 12.5,
            "description": "Test Store",
            "currency": "EUR",
            "date": "15-01-2023",
            "confidence": 85
        }
        
        extraction_data = ExtractionData.from_api_response(api_response)
        
        assert extraction_data.amount.value == Decimal('45.67')
        assert extraction_data.tax.value == Decimal('5.67')
        assert extraction_data.description.text == "Test Store"
        assert extraction_data.currency.code == "EUR"
        assert extraction_data.confidence.score == 85
        assert extraction_data.date.to_string() == "15-01-2023"
    
    def test_from_api_response_optional_fields(self):
        """Test: ExtractionData handles optional tax fields."""
        api_response = {
            "amount": 45.67,
            "tax": None,
            "tax_percentage": None,
            "description": "Test Store",
            "currency": "EUR",
            "date": "15-01-2023",
            "confidence": 85
        }
        
        extraction_data = ExtractionData.from_api_response(api_response)
        
        assert extraction_data.amount.value == Decimal('45.67')
        assert extraction_data.tax is None
        assert extraction_data.tax_percentage is None
        assert extraction_data.description.text == "Test Store"
    
    def test_from_api_response_invalid_data(self):
        """Test: ExtractionData raises error for invalid API response."""
        api_response = {
            "amount": "invalid",  # Should be number
            "description": "Test Store",
            "currency": "EUR",
            "date": "15-01-2023",
            "confidence": 85
        }
        
        with pytest.raises(ValueError, match="Invalid API response data"):
            ExtractionData.from_api_response(api_response)
    
    def test_from_api_response_missing_fields(self):
        """Test: ExtractionData raises error for missing required fields."""
        api_response = {
            "amount": 45.67,
            # Missing description, currency, date, confidence
        }
        
        with pytest.raises(ValueError, match="Invalid API response data"):
            ExtractionData.from_api_response(api_response)