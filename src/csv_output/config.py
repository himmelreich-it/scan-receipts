"""Configuration constants for CSV output operations."""

# CSV Configuration
CSV_FILENAME = "receipts.csv"
CSV_HEADERS = [
    "ID",
    "Amount",
    "Tax",
    "TaxPercentage",
    "Description",
    "Currency",
    "Date",
    "Confidence",
    "Hash",
    "DoneFilename",
]
CSV_ENCODING = "utf-8"

# Error Types
ERROR_API = "ERROR-API"
ERROR_FILE = "ERROR-FILE"
ERROR_PARSE = "ERROR-PARSE"
ERROR_UNKNOWN = "ERROR-UNKNOWN"
