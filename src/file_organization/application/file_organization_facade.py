"""File organization facade providing simplified interface for file operations."""

from pathlib import Path
from typing import Optional

from file_organization.domain.models import ArchiveResult
from file_organization.infrastructure.services import FolderManager, FileArchiver


class FileOrganizationFacade:
    """Facade for file organization operations.

    This facade provides a simplified interface for file organization operations,
    coordinating between folder management and file archiving services. It serves
    as the primary integration point for other system components.
    """

    def __init__(self, project_root: Optional[Path] = None) -> None:
        """Initialize file organization facade.

        Args:
            project_root: Root directory for the project. If None, uses current directory.
        """
        if project_root is None:
            project_root = Path.cwd()

        self.project_root = project_root
        self.folder_manager = FolderManager(project_root)
        self.file_archiver = FileArchiver(project_root / "done")

    def initialize_folder_structure(self) -> None:
        """Initializes required folder structure.

        This method ensures that both input/ and done/ folders exist in the
        project root, creating them if necessary. It coordinates with the
        folder manager service to handle the actual creation and validation.

        Raises:
            FolderCreationError: If folder creation fails due to permissions,
                                disk space, or other file system issues
        """
        self.folder_manager.ensure_folder_structure()

    def archive_processed_file(self, source_path: Path, file_id: int) -> ArchiveResult:
        """Archives a processed file with proper naming.

        This method coordinates the complete file archiving workflow, including
        validation, copying with timestamp naming, and returning structured
        results for CSV integration.

        Args:
            source_path: Path to file to archive (relative to input folder or absolute)
            file_id: Unique ID for the file (used in filename generation)

        Returns:
            ArchiveResult containing archive details for CSV recording

        Raises:
            FileAccessError: If source file cannot be accessed for reading
            FileCopyError: If copy operation fails due to permissions, disk space, etc.

        Example:
            >>> facade = FileOrganizationFacade()
            >>> result = facade.archive_processed_file(Path("input/receipt.jpg"), 1)
            >>> result.get_done_filename()
            "1-20240315-143052123456-receipt.jpg"
        """
        # Resolve source path - handle both relative and absolute paths
        if not source_path.is_absolute():
            # Assume relative to project root if not absolute
            resolved_source_path = self.project_root / source_path
        else:
            resolved_source_path = source_path

        # Delegate to file archiver service
        return self.file_archiver.archive_file(resolved_source_path, file_id)
