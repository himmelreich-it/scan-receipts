"""Custom exception hierarchy for AI extraction failures."""


class ExtractionError(Exception):
    """Base exception for AI extraction failures."""
    
    def __init__(self, message: str, filename: str = "", original_error: Exception = None):
        super().__init__(message)
        self.filename = filename
        self.original_error = original_error


class ApiExtractionError(ExtractionError):
    """API-related failures (rate limits, auth, network)."""
    pass


class FileExtractionError(ExtractionError):
    """File processing failures (corrupted, unsupported)."""
    pass


class ParseExtractionError(ExtractionError):
    """Response parsing failures (malformed JSON, missing fields)."""
    pass


class UnknownExtractionError(ExtractionError):
    """Unexpected failures not covered by other categories."""
    pass