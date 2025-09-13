"""Unit tests for file system adapter."""

import csv
import tempfile
from datetime import datetime
from pathlib import Path

import pytest  # type: ignore[import-untyped]
from pytest_mock import MockerFixture  # type: ignore[import-untyped]

from adapters.secondary.file_system_adapter import FileSystemAdapter
from core.domain.configuration import AppConfig
from core.domain.receipt import StagingInfo


class TestCreateFolders:
    """Test folder creation functionality."""

    def test_create_folders_success(self, mocker: MockerFixture) -> None:
        """Test successful creation of all required folders."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = mocker.MagicMock(spec=AppConfig)
            config.incoming_folder = Path(tmpdir) / "incoming"
            config.scanned_folder = Path(tmpdir) / "scanned"
            config.imported_folder = Path(tmpdir) / "imported"
            config.failed_folder = Path(tmpdir) / "failed"

            fs_adapter = FileSystemAdapter()
            fs_adapter.create_folders(config)

            assert config.incoming_folder.exists()
            assert config.scanned_folder.exists()
            assert config.imported_folder.exists()
            assert config.failed_folder.exists()

    def test_create_folders_with_nested_paths(self, mocker: MockerFixture) -> None:
        """Test creation of folders with nested parent paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = mocker.MagicMock(spec=AppConfig)
            config.incoming_folder = Path(tmpdir) / "deep" / "nested" / "incoming"
            config.scanned_folder = Path(tmpdir) / "deep" / "nested" / "scanned"
            config.imported_folder = Path(tmpdir) / "deep" / "nested" / "imported"
            config.failed_folder = Path(tmpdir) / "deep" / "nested" / "failed"

            fs_adapter = FileSystemAdapter()
            fs_adapter.create_folders(config)

            assert config.incoming_folder.exists()
            assert config.scanned_folder.exists()
            assert config.imported_folder.exists()
            assert config.failed_folder.exists()

    def test_create_folders_existing_folders(self, mocker: MockerFixture) -> None:
        """Test that existing folders are not affected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = mocker.MagicMock(spec=AppConfig)
            config.incoming_folder = Path(tmpdir) / "incoming"
            config.scanned_folder = Path(tmpdir) / "scanned"
            config.imported_folder = Path(tmpdir) / "imported"
            config.failed_folder = Path(tmpdir) / "failed"

            config.incoming_folder.mkdir()
            test_file = config.incoming_folder / "test.txt"
            test_file.write_text("test content")

            fs_adapter = FileSystemAdapter()
            fs_adapter.create_folders(config)

            assert test_file.exists()
            assert test_file.read_text() == "test content"

    def test_create_folders_permission_error(self, mocker: MockerFixture) -> None:
        """Test error handling when folder creation fails due to permissions."""
        mock_mkdir = mocker.patch("adapters.secondary.file_system_adapter.Path.mkdir")
        mock_mkdir.side_effect = PermissionError("Permission denied")

        config = mocker.MagicMock(spec=AppConfig)
        config.incoming_folder = Path("/tmp/incoming")
        config.scanned_folder = Path("/tmp/scanned")
        config.imported_folder = Path("/tmp/imported")
        config.failed_folder = Path("/tmp/failed")

        fs_adapter = FileSystemAdapter()
        with pytest.raises(OSError) as exc_info:  # type: ignore[attr-defined]
            fs_adapter.create_folders(config)

        assert "Failed to create folder" in str(exc_info.value)  # type: ignore[attr-defined]


class TestCountReceiptFiles:
    """Test receipt file counting functionality."""

    def test_count_receipt_files_empty_folder(self):
        """Test counting files in an empty folder."""
        with tempfile.TemporaryDirectory() as tmpdir:
            folder = Path(tmpdir)
            fs_adapter = FileSystemAdapter()
            assert fs_adapter.count_receipt_files(folder) == 0

    def test_count_receipt_files_with_receipts(self):
        """Test counting various receipt file types."""
        with tempfile.TemporaryDirectory() as tmpdir:
            folder = Path(tmpdir)

            (folder / "receipt1.pdf").touch()
            (folder / "receipt2.PDF").touch()
            (folder / "image1.jpg").touch()
            (folder / "image2.JPG").touch()
            (folder / "scan.png").touch()
            (folder / "scan2.PNG").touch()
            (folder / "photo.jpeg").touch()
            (folder / "photo2.JPEG").touch()

            fs_adapter = FileSystemAdapter()
            assert fs_adapter.count_receipt_files(folder) == 8

    def test_count_receipt_files_mixed_files(self):
        """Test counting only receipt files, ignoring other types."""
        with tempfile.TemporaryDirectory() as tmpdir:
            folder = Path(tmpdir)

            (folder / "receipt.pdf").touch()
            (folder / "image.jpg").touch()
            (folder / "document.txt").touch()
            (folder / "data.csv").touch()
            (folder / "spreadsheet.xlsx").touch()

            fs_adapter = FileSystemAdapter()
            assert fs_adapter.count_receipt_files(folder) == 2

    def test_count_receipt_files_ignores_subdirectories(self):
        """Test that subdirectories are not counted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            folder = Path(tmpdir)
            subfolder = folder / "subfolder"
            subfolder.mkdir()

            (folder / "receipt1.pdf").touch()
            (subfolder / "receipt2.pdf").touch()
            (folder / "subfolder.pdf").mkdir()

            fs_adapter = FileSystemAdapter()
            assert fs_adapter.count_receipt_files(folder) == 1

    def test_count_receipt_files_nonexistent_folder(self):
        """Test counting files in a non-existent folder."""
        folder = Path("/nonexistent/folder")
        fs_adapter = FileSystemAdapter()
        assert fs_adapter.count_receipt_files(folder) == 0


class TestGetStagingInfo:
    """Test staging CSV information retrieval."""

    def test_get_staging_info_missing_file(self):
        """Test getting info for non-existent CSV file."""
        csv_path = Path("/nonexistent/file.csv")
        fs_adapter = FileSystemAdapter()
        assert fs_adapter.get_staging_info(csv_path) is None

    def test_get_staging_info_empty_csv(self):
        """Test getting info for empty CSV file."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            csv_path = Path(f.name)

        try:
            fs_adapter = FileSystemAdapter()
            info = fs_adapter.get_staging_info(csv_path)
            assert info is not None
            assert info.entry_count == 0
        finally:
            csv_path.unlink()

    def test_get_staging_info_with_header_only(self):
        """Test getting info for CSV with header but no data."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            csv_path = Path(f.name)
            writer = csv.writer(f)
            writer.writerow(["Amount", "Tax", "Description", "Date"])

        try:
            fs_adapter = FileSystemAdapter()
            info = fs_adapter.get_staging_info(csv_path)
            assert info is not None
            assert info.entry_count == 0
        finally:
            csv_path.unlink()

    def test_get_staging_info_with_entries(self):
        """Test getting info for CSV with data entries."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            csv_path = Path(f.name)
            writer = csv.writer(f)
            writer.writerow(["Amount", "Tax", "Description", "Date"])
            writer.writerow(["100.00", "19.00", "Purchase 1", "2025-01-15"])
            writer.writerow(["50.00", "9.50", "Purchase 2", "2025-01-16"])
            writer.writerow(["75.00", "14.25", "Purchase 3", "2025-01-17"])

        try:
            fs_adapter = FileSystemAdapter()
            info = fs_adapter.get_staging_info(csv_path)
            assert info is not None
            assert info.entry_count == 3
            assert info.file_path == csv_path
            assert isinstance(info.modified_time, datetime)
        finally:
            csv_path.unlink()

    def test_staging_info_string_format(self):
        """Test StagingInfo string formatting."""
        staging_info = StagingInfo(
            file_path=Path("receipts.csv"),
            modified_time=datetime(2025, 1, 15, 14, 30),
            entry_count=8,
        )

        result = str(staging_info)
        assert "receipts.csv" in result
        assert "2025-01-15 14:30" in result
        assert "8 entries" in result
