"""Application orchestration and workflow management."""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from ..domain.entities import Receipt, ProcessingStatus
from ..domain.value_objects import ExtractionData
from ..domain.exceptions import ReceiptProcessingError
from .ports import (
    AIExtractionPort,
    FileSystemPort,
    DuplicateDetectionPort,
)


logger = logging.getLogger(__name__)


class ValidationResult:
    """Result of validation with any issues found."""

    def __init__(self, is_valid: bool, issues: Optional[List[str]] = None):
        self.is_valid = is_valid
        self.issues = issues or []


class ProcessReceiptUseCase:
    """Main orchestrator for receipt processing workflow."""

    def __init__(
        self,
        ai_extraction: AIExtractionPort,
        file_system: FileSystemPort,
        duplicate_detection: DuplicateDetectionPort,
    ):
        self.ai_extraction = ai_extraction
        self.file_system = file_system
        self.duplicate_detection = duplicate_detection

    async def process_receipts(
        self, input_folder: Path, done_folder: Path
    ) -> List[Receipt]:
        """Process all receipts in input folder.

        Workflow:
        1. Initialize duplicate detection with done folder
        2. Get list of input files
        3. Process each file through validation pipeline
        4. Return list of processed receipts
        """
        try:
            # Initialize duplicate detection with done folder
            self.duplicate_detection.initialize_done_folder_hashes(done_folder)

            # Get list of input files
            input_files = self.file_system.get_input_files(input_folder)

            results = []
            for file_path in input_files:
                receipt = await self._process_single_receipt(file_path)
                results.append(receipt)

            return results

        except Exception as error:
            logger.error(f"Failed to process receipts from {input_folder}: {error}")
            raise ReceiptProcessingError(f"Processing failed: {error}")

    async def _process_single_receipt(self, file_path: Path) -> Receipt:
        """Process a single receipt file through complete workflow."""
        try:
            logger.info(f"Processing {file_path}")

            # Generate file hash
            file_hash = self.duplicate_detection.generate_file_hash(file_path)

            # Create receipt entity
            receipt = Receipt(
                file_path=str(file_path),
                file_hash=file_hash,
                original_filename=file_path.name,
                processing_status=ProcessingStatus.PROCESSING,
            )

            # Check for duplicates
            if self.duplicate_detection.is_duplicate(file_hash):
                receipt.mark_as_duplicate()
                logger.info(f"Duplicate file skipped: {file_path}")
                return receipt

            # Add to session tracking
            self.duplicate_detection.add_to_session(file_hash, file_path.name)

            # Check file format
            if not self.ai_extraction.supports_file_format(file_path):
                self.file_system.move_file_to_failed(
                    file_path, "Unsupported file format"
                )
                receipt.mark_as_failed("Unsupported file format", "UNSUPPORTED_FORMAT")
                return receipt

            # Extract data using AI
            try:
                api_response = await self.ai_extraction.extract_data(file_path)
                extraction_data = ExtractionData.from_api_response(api_response)

                # Mark as processed
                receipt.mark_as_processed(extraction_data)
                logger.info(
                    f"Successfully processed {file_path} with confidence {extraction_data.confidence.score}"
                )

            except ValueError as e:
                # Handle date validation errors specifically
                if "Date validation failed" in str(e):
                    self.file_system.move_file_to_failed(file_path, str(e))
                    receipt.mark_as_failed(str(e), "VALIDATION_ERROR")
                else:
                    # Handle other validation errors
                    self.file_system.move_file_to_failed(
                        file_path, f"JSON parsing failed: {str(e)}"
                    )
                    receipt.mark_as_failed(f"JSON parsing failed: {str(e)}", "VALIDATION_ERROR")

            except Exception as e:
                # Handle API failures
                self.file_system.move_file_to_failed(
                    file_path, f"API failure: {str(e)}"
                )
                receipt.mark_as_failed(f"API failure: {str(e)}", "API_FAILURE")

            return receipt

        except Exception as error:
            logger.error(f"Unexpected error processing {file_path}: {error}")
            # Create a failed receipt for unexpected errors
            try:
                file_hash = self.duplicate_detection.generate_file_hash(file_path)
            except Exception:
                file_hash = "unknown"

            receipt = Receipt(
                file_path=str(file_path),
                file_hash=file_hash,
                original_filename=file_path.name,
            )
            receipt.mark_as_failed(f"File unreadable or corrupted: {str(error)}", "FILE_CORRUPT")

            try:
                self.file_system.move_file_to_failed(
                    file_path, f"File unreadable or corrupted: {str(error)}"
                )
            except Exception:
                pass  # Continue even if we can't move to failed folder

            return receipt


class ExtractDataUseCase:
    """Manages AI-powered data extraction from receipt files."""

    def __init__(self, ai_extraction: AIExtractionPort):
        self.ai_extraction = ai_extraction

    async def extract_and_validate(self, file_path: Path) -> ExtractionData:
        """Extract data from receipt and validate business rules.

        Process:
        1. Extract data using AI service
        2. Validate date using business rules
        3. Validate required fields
        4. Return validated extraction result
        """
        try:
            # Extract data using AI
            api_response = await self.ai_extraction.extract_data(file_path)

            # Validate API response
            self._validate_api_response(api_response)

            # Create extraction data (this will trigger date validation)
            extraction_data = ExtractionData.from_api_response(api_response)

            return extraction_data

        except ValueError as e:
            # Re-raise validation errors (including date validation)
            raise e
        except Exception as e:
            logger.error(f"Data extraction failed for {file_path}: {e}")
            raise ReceiptProcessingError(f"Failed to extract data: {e}")

    def _validate_api_response(self, response: Dict[str, Any]) -> None:
        """Validate API response contains required fields."""
        required_fields = ["amount", "description", "currency", "date", "confidence"]
        missing_fields = [field for field in required_fields if field not in response]

        if missing_fields:
            raise ReceiptProcessingError(f"Missing required fields: {missing_fields}")

        try:
            confidence = int(response["confidence"])
            if not 0 <= confidence <= 100:
                raise ReceiptProcessingError(f"Invalid confidence score: {confidence}")
        except (ValueError, TypeError):
            raise ReceiptProcessingError(
                "Confidence must be an integer between 0 and 100"
            )
