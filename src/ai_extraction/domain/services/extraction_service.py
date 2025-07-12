"""Domain service orchestrating extraction logic and error handling."""

import logging

from ..models import ExtractionResult, ReceiptData, ErrorReceiptData, ImageExtractionRequest
from ..exceptions import (
    ApiExtractionError, FileExtractionError, 
    ParseExtractionError
)
from ...infrastructure.api import ClaudeApiClient

logger = logging.getLogger(__name__)


class ExtractionService:
    """Domain service for orchestrating receipt data extraction."""
    
    def __init__(self, api_client: ClaudeApiClient):
        self.api_client = api_client
    
    def extract_receipt_data(self, request: ImageExtractionRequest) -> ExtractionResult:
        """
        Extract receipt data with comprehensive error handling.
        
        Args:
            request: Image extraction request
            
        Returns:
            ExtractionResult with success/failure indication and appropriate data
        """
        try:
            # Validate image data
            self._validate_image_request(request)
            
            # Call API for extraction
            api_response = self.api_client.extract_receipt_data(request)
            
            # Parse and validate response
            receipt_data = self._parse_api_response(api_response, request.filename)
            
            # Log successful extraction
            logger.info(
                f"Successfully extracted data from {request.filename} - "
                f"Amount: {receipt_data.amount} {receipt_data.currency}, "
                f"Confidence: {receipt_data.confidence}%"
            )
            
            return ExtractionResult(
                success=True,
                data=receipt_data,
                filename=request.filename
            )
            
        except FileExtractionError as e:
            return self._create_error_result("ERROR-FILE", e, request.filename)
        except ApiExtractionError as e:
            return self._create_error_result("ERROR-API", e, request.filename)
        except ParseExtractionError as e:
            return self._create_error_result("ERROR-PARSE", e, request.filename)
        except Exception as e:
            logger.error(f"Unexpected error for file {request.filename}: {e}")
            return self._create_error_result("ERROR-UNKNOWN", e, request.filename)
    
    def _validate_image_request(self, request: ImageExtractionRequest) -> None:
        """Validate image request data."""
        if not request.image_data:
            raise FileExtractionError("Empty image data", request.filename)
        
        if len(request.image_data) == 0:
            raise FileExtractionError("Zero-byte image file", request.filename)
        
        # Basic file format validation
        if request.mime_type == 'image/jpeg' and not request.image_data.startswith(b'\xff\xd8'):
            raise FileExtractionError("Corrupted JPEG file", request.filename)
        elif request.mime_type == 'image/png' and not request.image_data.startswith(b'\x89PNG'):
            raise FileExtractionError("Corrupted PNG file", request.filename)
    
    def _parse_api_response(self, api_response: dict, filename: str) -> ReceiptData:
        """Parse and validate API response into ReceiptData."""
        try:
            # Validate required fields
            required_fields = {'amount', 'tax', 'description', 'currency', 'date', 'confidence'}
            missing_fields = required_fields - set(api_response.keys())
            if missing_fields:
                raise ParseExtractionError(
                    f"Missing required fields: {missing_fields}", 
                    filename
                )
            
            # Create and validate ReceiptData
            return ReceiptData(**api_response)
            
        except (ValueError, TypeError) as e:
            raise ParseExtractionError(f"Invalid response data: {str(e)}", filename, e)
    
    def _create_error_result(self, error_type: str, error: Exception, filename: str) -> ExtractionResult:
        """Create error result with appropriate logging."""
        # Map error types to log messages
        error_messages = {
            "ERROR-API": "API-related error",
            "ERROR-FILE": "File processing error", 
            "ERROR-PARSE": "Response parsing error",
            "ERROR-UNKNOWN": "Unexpected error"
        }
        
        log_message = f"{error_messages.get(error_type, 'Error')} for file {filename}: {str(error)}"
        
        if error_type == "ERROR-API":
            if "rate limit" in str(error).lower():
                logger.error(f"Rate limit exceeded for file {filename}")
            elif "authentication" in str(error).lower():
                logger.error(f"Authentication failed for file {filename}")
            else:
                logger.error(f"Network error for file {filename}: {str(error)}")
        elif error_type == "ERROR-FILE":
            if "corrupted" in str(error).lower():
                logger.error(f"Corrupted file: {filename}")
            else:
                logger.error(f"Unsupported format: {filename}")
        elif error_type == "ERROR-PARSE":
            if "json" in str(error).lower() or "malformed" in str(error).lower():
                logger.error(f"Invalid API response for file {filename}")
            else:
                logger.error(f"Incomplete extraction data for file {filename}")
        else:
            logger.error(f"Unexpected error for file {filename}: {str(error)}")
        
        error_data = ErrorReceiptData(description=error_type)
        
        return ExtractionResult(
            success=False,
            error_data=error_data,
            filename=filename
        )