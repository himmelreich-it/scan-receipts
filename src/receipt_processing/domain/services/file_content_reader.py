"""Service for reading file content for Claude API."""

import base64
from receipt_processing.domain.models.file_content import FileContent
from receipt_processing.domain.models.file_extension import FileExtension
from receipt_processing.domain.models.processable_file import ProcessableFile


class FileContentReader:
    """Domain service for reading file content in Claude API format."""
    
    def read_file_content(self, processable_file: ProcessableFile) -> None:
        """Read file content and populate the processable_file's content."""
        try:
            with open(processable_file.file_path.path, 'rb') as file:
                file_data = file.read()
                base64_content = base64.b64encode(file_data).decode('utf-8')
                mime_type = self._determine_mime_type(processable_file.extension)
                
                content = FileContent(
                    data=base64_content,
                    mime_type=mime_type,
                    size_bytes=len(file_data)
                )
                processable_file.content = content
                
        except FileNotFoundError:
            processable_file.mark_as_error(f"File no longer accessible: {processable_file.file_path.name}")
        except PermissionError:
            processable_file.mark_as_error(f"Permission denied: {processable_file.file_path.name}")
        except (IOError, OSError):
            processable_file.mark_as_error(f"Failed to read file: {processable_file.file_path.name}")
        except MemoryError:
            processable_file.mark_as_error(f"File too large: {processable_file.file_path.name}")
        except Exception as e:
            processable_file.mark_as_error(f"Unexpected error: {str(e)}")
    
    def _determine_mime_type(self, extension: FileExtension) -> str:
        """Determine MIME type based on file extension."""
        mime_mapping = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png'
        }
        return mime_mapping.get(extension.extension, 'application/octet-stream')