"""Unit tests for ViewStagingUseCase."""

from pathlib import Path
from unittest.mock import Mock


from core.domain.configuration import AppConfig
from core.domain.receipt import ReceiptData, StagingTableData
from core.use_cases.view_staging import ViewStagingUseCase


class TestViewStagingUseCase:
    """Test ViewStagingUseCase functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_file_system = Mock()
        self.mock_csv_adapter = Mock()
        self.use_case = ViewStagingUseCase(self.mock_file_system, self.mock_csv_adapter)
        
        # Create mock config
        self.config = Mock(spec=AppConfig)
        self.config.csv_staging_file = Path("/tmp/receipts.csv")
    
    def test_get_full_table_file_not_exists(self):
        """Test getting full table when file doesn't exist."""
        staging_data = StagingTableData(
            file_path=Path("/tmp/receipts.csv"),
            headers=[],
            receipts=[]
        )
        self.mock_csv_adapter.read_staging_table.return_value = staging_data
        
        result = self.use_case.get_full_table(self.config)
        
        assert result is not None
        assert result.file_path == Path("/tmp/receipts.csv")
        assert result.headers == []
        assert result.receipts == []
        assert result.is_empty
        self.mock_csv_adapter.read_staging_table.assert_called_once_with(self.config.csv_staging_file)
    
    def test_get_full_table_with_data(self):
        """Test getting full table with data."""
        receipt1 = ReceiptData(
            amount="100.00",
            tax="10.00",
            tax_percentage="10",
            description="Test Receipt 1",
            currency="USD",
            date="2024-01-01",
            confidence="0.95",
            hash="abc123",
            done_filename="receipt_001.pdf"
        )
        receipt2 = ReceiptData(
            amount="200.00",
            tax="20.00",
            tax_percentage="10",
            description="Test Receipt 2",
            currency="EUR",
            date="2024-01-02",
            confidence="0.90",
            hash="def456",
            done_filename="receipt_002.pdf"
        )
        
        staging_data = StagingTableData(
            file_path=Path("/tmp/receipts.csv"),
            headers=['Amount', 'Tax', 'TaxPercentage', 'Description', 
                    'Currency', 'Date', 'Confidence', 'Hash', 'DoneFilename'],
            receipts=[receipt1, receipt2]
        )
        self.mock_csv_adapter.read_staging_table.return_value = staging_data
        
        result = self.use_case.get_full_table(self.config)
        
        assert result is not None
        assert len(result.receipts) == 2
        assert not result.is_empty
        assert result.receipts[0].amount == "100.00"
        assert result.receipts[1].amount == "200.00"
        self.mock_csv_adapter.read_staging_table.assert_called_once_with(self.config.csv_staging_file)
    
    def test_get_full_table_error_handling(self):
        """Test error handling when reading CSV fails."""
        self.mock_csv_adapter.read_staging_table.return_value = None
        
        result = self.use_case.get_full_table(self.config)
        
        assert result is None
        self.mock_csv_adapter.read_staging_table.assert_called_once_with(self.config.csv_staging_file)