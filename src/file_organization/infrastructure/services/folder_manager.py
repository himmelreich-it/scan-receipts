"""Folder management service for file organization operations."""

import os
from pathlib import Path
from typing import Optional

from file_organization.domain.exceptions import FolderCreationError, FileAccessError
from file_organization.infrastructure.config import (
    INPUT_FOLDER_NAME,
    DONE_FOLDER_NAME,
)


class FolderManager:
    """Manages folder creation and validation for file organization.

    This service handles the creation of required folder structure (input/ and done/)
    and validates folder permissions. It implements proper error handling with
    specific error messages as required by the user stories.
    """

    def __init__(self, project_root: Optional[Path] = None) -> None:
        """Initialize folder manager.

        Args:
            project_root: Root directory for the project. If None, uses current directory.
        """
        if project_root is None:
            project_root = Path.cwd()

        self.project_root = project_root
        self.input_folder = project_root / INPUT_FOLDER_NAME
        self.done_folder = project_root / DONE_FOLDER_NAME

    def ensure_folder_structure(self) -> None:
        """Ensures input/ and done/ folders exist, creates if missing.

        This method checks for the existence of both input/ and done/ folders
        in the project root and creates them if they are missing. It implements
        specific error handling for different failure scenarios.

        Raises:
            FolderCreationError: If folder creation fails due to permissions,
                                disk space, or other file system issues
        """
        self._create_folder_if_missing(self.input_folder, INPUT_FOLDER_NAME)
        self._create_folder_if_missing(self.done_folder, DONE_FOLDER_NAME)

    def validate_folder_permissions(self, folder_path: Path) -> None:
        """Validates write permissions on folder.

        Args:
            folder_path: Path to folder to validate

        Raises:
            FileAccessError: If folder is not writable
        """
        if not folder_path.exists():
            raise FileAccessError(str(folder_path), "access", "Folder does not exist")

        if not os.access(folder_path, os.W_OK):
            raise FileAccessError(str(folder_path), "write to", "Permission denied")

    def _create_folder_if_missing(self, folder_path: Path, folder_name: str) -> None:
        """Creates folder if it doesn't exist with proper error handling.

        Args:
            folder_path: Path to the folder to create
            folder_name: Human-readable name for error messages

        Raises:
            FolderCreationError: If folder creation fails
        """
        if folder_path.exists():
            return

        try:
            # Use exist_ok=True to handle race conditions
            folder_path.mkdir(parents=True, exist_ok=True)

            # Validate the folder was created and is writable
            self.validate_folder_permissions(folder_path)

        except PermissionError:
            raise FolderCreationError(folder_name, "Permission denied")
        except OSError as e:
            # Handle various OS-level errors
            error_msg = str(e).lower()
            if (
                "no space left on device" in error_msg
                or "insufficient disk space" in error_msg
            ):
                raise FolderCreationError(folder_name, "Insufficient disk space")
            else:
                raise FolderCreationError(folder_name, str(e))
        except FileAccessError:
            # Re-raise permission errors from validation
            raise FolderCreationError(folder_name, "Permission denied")
