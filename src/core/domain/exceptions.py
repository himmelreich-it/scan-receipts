"""Domain exceptions for the receipt processing system."""


class ReceiptProcessingError(Exception):
    """Base exception for receipt processing errors."""
    pass


class ConfigurationError(ReceiptProcessingError):
    """Error in application configuration."""
    pass


class FolderCreationError(ReceiptProcessingError):
    """Error creating required folders.""" 
    pass