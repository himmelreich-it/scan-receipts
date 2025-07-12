"""Archive result value object for file organization operations."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ArchiveResult:
    """Result of file archiving operation.

    This value object represents the outcome of successfully archiving a file
    to the done folder with timestamp naming. It provides all the information
    needed for CSV recording and audit trails.

    Attributes:
        source_filename: Original filename from input folder
        archived_filename: New filename in done folder (with timestamp)
        archive_timestamp: When the archiving operation was performed
        file_id: Unique ID used in the filename generation
    """

    source_filename: str
    archived_filename: str
    archive_timestamp: datetime
    file_id: int

    def get_done_filename(self) -> str:
        """Returns filename for CSV DoneFilename field.

        This method provides the filename (without path) that should be
        recorded in the CSV file's DoneFilename field for audit purposes.

        Returns:
            The archived filename without path prefix

        Example:
            >>> result = ArchiveResult(
            ...     source_filename="receipt.jpg",
            ...     archived_filename="1-20240315-143052123456-receipt.jpg",
            ...     archive_timestamp=datetime.now(),
            ...     file_id=1
            ... )
            >>> result.get_done_filename()
            "1-20240315-143052123456-receipt.jpg"
        """
        return self.archived_filename
