"""Value objects for extraction request data."""

from pathlib import Path
from pydantic import BaseModel, Field, field_validator


class ImageExtractionRequest(BaseModel):
    """Value object for image extraction request."""
    
    file_path: Path = Field(..., description="Path to image file")
    image_data: bytes = Field(..., description="Raw image file data")
    mime_type: str = Field(..., description="MIME type of image")
    
    @field_validator('mime_type')
    def validate_mime_type(cls, v):
        """Ensure supported MIME types for AI extraction (images only)."""
        supported_types = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
        if v not in supported_types:
            raise ValueError(f'Unsupported MIME type: {v}. Supported types: {supported_types}')
        return v
    
    @property
    def filename(self) -> str:
        """Get filename from path."""
        return self.file_path.name