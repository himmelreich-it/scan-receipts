"""Core cleanup functionality for one-off processing mode."""

import shutil
import sys
from pathlib import Path


class CleanupManager:
    """Manages cleanup operations with proper error handling.

    This class implements the One-Off Processing Mode feature by clearing
    the done folder and removing the receipts.csv file at the start of
    each script execution.

    Attributes:
        _done_folder_path: Path to the done folder
        _csv_file_path: Path to the CSV file
    """

    def __init__(self, done_folder_path: str, csv_file_path: str) -> None:
        """Initialize CleanupManager with paths to clean up.

        Args:
            done_folder_path: Path to the done folder (typically "done")
            csv_file_path: Path to the CSV file (typically "receipts.csv")
        """
        self._done_folder_path = done_folder_path
        self._csv_file_path = csv_file_path

    def execute_cleanup(self) -> None:
        """Main entry point for cleanup operations.

        Performs cleanup operations in the specified order:
        1. Clear done folder first
        2. Remove CSV file second

        If any operation fails, terminates execution immediately.
        Operations are performed silently unless errors occur.

        Raises:
            SystemExit: If cleanup operations fail due to files being in use
        """
        # Clear done folder first
        self._clear_done_folder()

        # Remove CSV file second
        self._remove_csv_file()

    def _clear_done_folder(self) -> None:
        """Clear all files and subdirectories from done folder.

        Implements Story 1: Done Folder Cleanup (DONE_FOLDER_CLEANUP_X1Y2)

        Acceptance Criteria:
        - Clears all files and subdirectories from done folder
        - Silent success if folder doesn't exist
        - All file types are removed (images, PDFs, etc.)
        - Subdirectories within done folder are also removed

        Raises:
            SystemExit: If files are in use by other processes
        """
        done_path = Path(self._done_folder_path)

        # Silent success if folder doesn't exist
        if not done_path.exists():
            return

        try:
            # Remove all contents of the directory
            for item in done_path.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
        except (PermissionError, OSError) as e:
            self._handle_cleanup_error(str(done_path), str(e))

    def _remove_csv_file(self) -> None:
        """Remove the receipts.csv file.

        Implements Story 2: CSV File Removal (CSV_FILE_REMOVAL_Z3A4)

        Acceptance Criteria:
        - Removes receipts.csv file at start of execution
        - Silent success if file doesn't exist
        - Only removes receipts.csv, not other CSV files

        Raises:
            SystemExit: If file is in use by other processes
        """
        csv_path = Path(self._csv_file_path)

        # Silent success if file doesn't exist
        if not csv_path.exists():
            return

        try:
            csv_path.unlink()
        except (PermissionError, OSError) as e:
            self._handle_cleanup_error(str(csv_path), str(e))

    def _handle_cleanup_error(self, file_path: str, error_message: str) -> None:
        """Handle cleanup errors by displaying message and terminating.

        Implements Story 3: Cleanup Error Handling (CLEANUP_ERROR_HANDLE_B5C6)

        Acceptance Criteria:
        - Detects when files are in use by other processes
        - Displays clear error message indicating which file(s) are in use
        - Terminates script execution immediately when cleanup fails
        - Error message format: "Error: [filename] is currently in use by another process"

        Args:
            file_path: Path of the file/folder that caused the error
            error_message: Original error message from the exception

        Raises:
            SystemExit: Always terminates script execution with exit code 1
        """
        print(f"Error: {file_path} is currently in use by another process")
        sys.exit(1)
