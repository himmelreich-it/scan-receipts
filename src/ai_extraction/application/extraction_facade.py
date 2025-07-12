"""Application facade for AI receipt data extraction operations."""

import logging
from typing import List

from ..domain.models import ExtractionResult, ImageExtractionRequest
from ..domain.services import ExtractionService
from ..infrastructure.api import ClaudeApiClient

logger = logging.getLogger(__name__)


class ExtractionFacade:
    """Application facade for AI receipt data extraction operations."""
    
    def __init__(self):
        self.api_client = ClaudeApiClient()
        self.extraction_service = ExtractionService(self.api_client)
    
    def extract_from_image(self, request: ImageExtractionRequest) -> ExtractionResult:
        """
        Extract receipt data from a single image.
        
        Args:
            request: Image extraction request
            
        Returns:
            ExtractionResult with success/failure indication and data
        """
        logger.debug(f"Starting extraction for {request.filename}")
        result = self.extraction_service.extract_receipt_data(request)
        logger.debug(f"Completed extraction for {request.filename} - Success: {result.success}")
        return result
    
    def extract_from_images(self, requests: List[ImageExtractionRequest]) -> List[ExtractionResult]:
        """
        Extract receipt data from multiple images sequentially.
        
        Args:
            requests: List of image extraction requests
            
        Returns:
            List of ExtractionResults maintaining input order
        """
        logger.info(f"Starting batch extraction for {len(requests)} images")
        results = []
        
        for request in requests:
            result = self.extract_from_image(request)
            results.append(result)
        
        successful_count = sum(1 for r in results if r.success)
        error_count = len(results) - successful_count
        
        logger.info(f"Batch extraction completed - {successful_count} successful, {error_count} errors")
        return results