"""Immutable value objects for financial data validation."""

from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any, Optional
import re


@dataclass(frozen=True)
class Amount:
    """Value object for monetary amounts."""

    value: Decimal

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Amount must be non-negative")


@dataclass(frozen=True)
class Tax:
    """Value object for tax amounts."""

    value: Decimal

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Tax must be non-negative")


@dataclass(frozen=True)
class TaxPercentage:
    """Value object for tax percentage."""

    value: Decimal

    def __post_init__(self):
        if self.value < 0 or self.value > 100:
            raise ValueError("Tax percentage must be between 0 and 100")


@dataclass(frozen=True)
class Currency:
    """Value object for currency codes."""

    code: str

    def __post_init__(self):
        if not re.match(r"^[A-Z]{3}$", self.code):
            raise ValueError("Currency code must be 3 uppercase letters")


@dataclass(frozen=True)
class Description:
    """Value object for receipt descriptions."""

    text: str

    def __post_init__(self):
        if not self.text or len(self.text.strip()) == 0:
            raise ValueError("Description cannot be empty")


@dataclass(frozen=True)
class ReceiptDate:
    """Value object for receipt dates."""

    date: datetime

    def __post_init__(self):
        if self.date > datetime.now():
            raise ValueError("Receipt date cannot be in the future")

    def to_string(self) -> str:
        """Format date as dd-MM-YYYY."""
        return self.date.strftime("%d-%m-%Y")


@dataclass(frozen=True)
class Confidence:
    """Value object for confidence scores."""

    score: int

    def __post_init__(self):
        if not 0 <= self.score <= 100:
            raise ValueError("Confidence score must be between 0 and 100")


@dataclass(frozen=True)
class ExtractionData:
    """Complete extraction data from receipt analysis."""

    amount: Amount
    tax: Optional[Tax]
    tax_percentage: Optional[TaxPercentage]
    description: Description
    currency: Currency
    date: ReceiptDate
    confidence: Confidence

    @classmethod
    def from_api_response(cls, response_data: Dict[str, Any]) -> "ExtractionData":
        """Create ExtractionData from API response."""
        try:
            amount = Amount(Decimal(str(response_data["amount"])))

            tax = None
            if response_data.get("tax") is not None:
                tax = Tax(Decimal(str(response_data["tax"])))

            tax_percentage = None
            if response_data.get("tax_percentage") is not None:
                tax_percentage = TaxPercentage(
                    Decimal(str(response_data["tax_percentage"]))
                )

            description = Description(response_data["description"])
            currency = Currency(response_data["currency"])

            date_str = response_data["date"]
            if isinstance(date_str, str):
                try:
                    date_obj = datetime.strptime(date_str, "%d-%m-%Y")
                except ValueError:
                    try:
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    except ValueError:
                        date_obj = datetime.strptime(date_str, "%d/%m/%Y")
            else:
                date_obj = date_str

            receipt_date = ReceiptDate(date_obj)
            confidence = Confidence(int(response_data["confidence"]))

            return cls(
                amount=amount,
                tax=tax,
                tax_percentage=tax_percentage,
                description=description,
                currency=currency,
                date=receipt_date,
                confidence=confidence,
            )
        except (KeyError, ValueError, TypeError) as e:
            raise ValueError(f"Invalid API response data: {e}")
