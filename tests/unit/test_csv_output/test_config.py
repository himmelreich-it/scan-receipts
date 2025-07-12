"""Unit tests for CSV configuration constants."""

from src.csv_output.config import (
    CSV_FILENAME, CSV_HEADERS, CSV_ENCODING,
    ERROR_API, ERROR_FILE, ERROR_PARSE, ERROR_UNKNOWN
)


def test_csv_filename_is_correct():
    """Test that CSV filename is set correctly."""
    assert CSV_FILENAME == "receipts.csv"


def test_csv_headers_are_complete():
    """Test that CSV headers contain all required fields."""
    expected_headers = [
        "ID", "Amount", "Tax", "TaxPercentage", "Description", 
        "Currency", "Date", "Confidence", "Hash", "DoneFilename"
    ]
    assert CSV_HEADERS == expected_headers


def test_csv_encoding_is_utf8():
    """Test that CSV encoding is UTF-8."""
    assert CSV_ENCODING == "utf-8"


def test_error_types_are_defined():
    """Test that all error types are properly defined."""
    assert ERROR_API == "ERROR-API"
    assert ERROR_FILE == "ERROR-FILE"
    assert ERROR_PARSE == "ERROR-PARSE"
    assert ERROR_UNKNOWN == "ERROR-UNKNOWN"


def test_headers_count():
    """Test that we have exactly 10 headers as specified."""
    assert len(CSV_HEADERS) == 10


def test_headers_have_no_duplicates():
    """Test that all header names are unique."""
    assert len(CSV_HEADERS) == len(set(CSV_HEADERS))