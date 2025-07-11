"""Integration tests for Receipt Image Processing feature."""

import tempfile
import os
from pathlib import Path

from src.receipt_processing.infrastructure.config.file_processing_config import FileProcessingConfig
from src.receipt_processing.infrastructure.adapters.local_file_repository import LocalFileRepository
from src.receipt_processing.domain.services.file_filtering_service import FileFilteringService
from src.receipt_processing.domain.services.file_content_reader import FileContentReader
from src.receipt_processing.domain.specifications.supported_file_spec import SupportedFileExtensionSpecification
from src.receipt_processing.application.workflows.sequential_processing_workflow import SequentialProcessingWorkflow


class TestReceiptProcessingIntegration:
    """Integration tests for the complete Receipt Image Processing feature."""
    
    def test_complete_workflow_with_supported_files(self):
        """Test the complete workflow with actual file system operations."""
        # Create temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = os.path.join(temp_dir, "input")
            os.makedirs(input_dir)
            
            # Create test files
            test_files = {
                "receipt1.pdf": b"PDF content here",
                "receipt2.jpg": b"JPG content here", 
                "receipt3.png": b"PNG content here",
                "document.txt": b"Text content here"  # unsupported
            }
            
            for filename, content in test_files.items():
                with open(os.path.join(input_dir, filename), 'wb') as f:
                    f.write(content)
            
            # Setup the complete workflow
            config = FileProcessingConfig()
            repository = LocalFileRepository()
            spec = SupportedFileExtensionSpecification(config.get_supported_extensions())
            filtering_service = FileFilteringService(spec)
            content_reader = FileContentReader()
            
            workflow = SequentialProcessingWorkflow(
                repository,
                filtering_service,
                content_reader
            )
            
            # Execute the workflow
            result = workflow.process_input_directory(input_dir)
            
            # Verify results
            assert result.total_processed == 3  # Only supported files
            assert result.success_count == 3
            assert result.error_count == 0
            
            # Verify file contents were read correctly
            for processed_file in result.successful_files:
                assert processed_file.content is not None
                assert processed_file.content.data  # base64 content
                assert processed_file.content.size_bytes > 0
                assert processed_file.processing_status == "processed"
                assert processed_file.processed_at is not None
    
    def test_workflow_with_empty_directory(self):
        """Test workflow behavior with empty input directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = os.path.join(temp_dir, "input")
            
            # Setup workflow
            config = FileProcessingConfig()
            repository = LocalFileRepository()
            spec = SupportedFileExtensionSpecification(config.get_supported_extensions())
            filtering_service = FileFilteringService(spec)
            content_reader = FileContentReader()
            
            workflow = SequentialProcessingWorkflow(
                repository,
                filtering_service,
                content_reader
            )
            
            # Execute workflow - directory will be created automatically
            result = workflow.process_input_directory(input_dir)
            
            # Verify results
            assert result.total_processed == 0
            assert result.success_count == 0
            assert result.error_count == 0
            assert os.path.exists(input_dir)  # Directory was created
    
    def test_workflow_with_unsupported_files_only(self):
        """Test workflow with only unsupported file types."""
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = os.path.join(temp_dir, "input")
            os.makedirs(input_dir)
            
            # Create only unsupported files
            unsupported_files = {
                "document.txt": b"Text content",
                "data.csv": b"CSV content",
                "script.py": b"Python content"
            }
            
            for filename, content in unsupported_files.items():
                with open(os.path.join(input_dir, filename), 'wb') as f:
                    f.write(content)
            
            # Setup workflow
            config = FileProcessingConfig()
            repository = LocalFileRepository()
            spec = SupportedFileExtensionSpecification(config.get_supported_extensions())
            filtering_service = FileFilteringService(spec)
            content_reader = FileContentReader()
            
            workflow = SequentialProcessingWorkflow(
                repository,
                filtering_service,
                content_reader
            )
            
            # Execute workflow
            result = workflow.process_input_directory(input_dir)
            
            # Verify results - no files should be processed
            assert result.total_processed == 0
            assert result.success_count == 0
            assert result.error_count == 0