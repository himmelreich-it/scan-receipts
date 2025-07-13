"""Application orchestration and workflow management."""

import logging
from typing import Dict, Any, List, Optional
from ..domain.entities import Receipt, ProcessingStatus
from ..domain.value_objects import ExtractionData
from ..domain.policies import ProcessingPolicies
from ..domain.exceptions import ReceiptProcessingError, InvalidFileFormatError
from .ports import (
    AIExtractionPort,
    FileSystemPort,
    DuplicateDetectionPort,
    ReceiptRepositoryPort,
)


logger = logging.getLogger(__name__)


class ValidationResult:
    """Result of validation with any issues found."""

    def __init__(self, is_valid: bool, issues: Optional[List[str]] = None):
        self.is_valid = is_valid
        self.issues = issues or []


class ProcessReceiptUseCase:
    """Main use case for processing receipt files."""

    def __init__(
        self,
        ai_extraction_port: AIExtractionPort,
        file_system_port: FileSystemPort,
        receipt_repository_port: ReceiptRepositoryPort,
        duplicate_detector_port: DuplicateDetectionPort,
    ):
        self.ai_extraction_port = ai_extraction_port
        self.file_system_port = file_system_port
        self.receipt_repository_port = receipt_repository_port
        self.duplicate_detector_port = duplicate_detector_port
        self.extract_data_use_case = ExtractDataUseCase(ai_extraction_port)
        self.validate_results_use_case = ValidateResultsUseCase(ProcessingPolicies())

    async def execute(self, file_path: str) -> Receipt:
        """Execute complete receipt processing workflow.

        Args:
            file_path: Path to receipt file to process

        Returns:
            Processed Receipt entity
        """
        try:
            logger.info(f"Starting processing for {file_path}")

            file_hash = self.duplicate_detector_port.generate_file_hash(file_path)
            receipt = Receipt(file_path=file_path, file_hash=file_hash)
            receipt.processing_status = ProcessingStatus.PROCESSING

            known_hashes = self.receipt_repository_port.get_processed_hashes()
            if self.duplicate_detector_port.is_duplicate(file_hash, known_hashes):
                receipt.mark_as_duplicate()
                logger.info(f"Duplicate file skipped: {file_path}")
                return receipt

            if not self.file_system_port.validate_file_format(file_path):
                raise InvalidFileFormatError(f"Unsupported file format: {file_path}")

            extraction_data = await self.extract_data_use_case.execute(file_path)

            validation_result = self.validate_results_use_case.execute(extraction_data)
            if not validation_result.is_valid:
                logger.warning(
                    f"Validation issues for {file_path}: {validation_result.issues}"
                )

            receipt.mark_as_processed(extraction_data)
            self.receipt_repository_port.save_receipt(receipt)

            logger.info(
                f"Successfully processed {file_path} with confidence {extraction_data.confidence.score}"
            )
            return receipt

        except Exception as error:
            return self._handle_processing_error(
                error, file_path, receipt if "receipt" in locals() else None
            )

    def _handle_processing_error(
        self, error: Exception, file_path: str, receipt: Optional[Receipt] = None
    ) -> Receipt:
        """Handle processing errors and create appropriate receipt."""
        error_type = ProcessingPolicies.classify_processing_error(error)

        if receipt is None:
            try:
                file_hash = self.duplicate_detector_port.generate_file_hash(file_path)
            except Exception:
                file_hash = "unknown"
            receipt = Receipt(file_path=file_path, file_hash=file_hash)

        receipt.mark_as_failed(error_type)

        logger.error(f"{error_type} for {file_path}: {error}")

        try:
            self.receipt_repository_port.save_receipt(receipt)
        except Exception as save_error:
            logger.error(f"Failed to save error receipt for {file_path}: {save_error}")

        return receipt


class ExtractDataUseCase:
    """Use case for AI-powered data extraction."""

    def __init__(self, ai_extraction_port: AIExtractionPort):
        self.ai_extraction_port = ai_extraction_port

    async def execute(self, file_path: str) -> ExtractionData:
        """Extract data from receipt file using AI.

        Args:
            file_path: Path to receipt file

        Returns:
            Extracted and validated data

        Raises:
            ReceiptProcessingError: When extraction or validation fails
        """
        try:
            response_data = await self.ai_extraction_port.extract_receipt_data(
                file_path
            )
            self._validate_api_response(response_data)
            return ExtractionData.from_api_response(response_data)
        except Exception as e:
            logger.error(f"Data extraction failed for {file_path}: {e}")
            raise ReceiptProcessingError(f"Failed to extract data: {e}")

    def _validate_api_response(self, response: Dict[str, Any]) -> None:
        """Validate API response contains required fields.

        Args:
            response: API response dictionary

        Raises:
            ReceiptProcessingError: When response is invalid
        """
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


class ValidateResultsUseCase:
    """Use case for validating extraction results."""

    def __init__(self, processing_policies: ProcessingPolicies):
        self.processing_policies = processing_policies

    def execute(self, extraction_data: ExtractionData) -> ValidationResult:
        """Validate extracted data against business rules.

        Args:
            extraction_data: Data to validate

        Returns:
            ValidationResult with issues if any
        """
        issues = self._apply_business_rules(extraction_data)
        return ValidationResult(is_valid=len(issues) == 0, issues=issues)

    def _apply_business_rules(self, data: ExtractionData) -> List[str]:
        """Apply business rules and return any issues found.

        Args:
            data: Data to validate

        Returns:
            List of validation issues
        """
        issues = []

        if not self.processing_policies.is_confidence_acceptable(data.confidence.score):
            issues.append(
                f"Confidence score {data.confidence.score} outside acceptable range"
            )

        if data.amount.value <= 0:
            issues.append("Amount must be positive")

        if data.tax and data.tax.value < 0:
            issues.append("Tax amount cannot be negative")

        return issues
