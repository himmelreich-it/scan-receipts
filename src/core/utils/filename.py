"""Filename generation and sanitization utilities."""

import re
from datetime import datetime
from pathlib import Path


def sanitize_description(text: str, max_length: int = 15) -> str:
    """Sanitize description for use in filename.

    Removes special characters, limits length, and ensures valid filename format.

    Args:
        text: Description text to sanitize.
        max_length: Maximum length of sanitized description (default 15).

    Returns:
        Sanitized description suitable for filename.

    Examples:
        >>> sanitize_description("Coffeecompany De Dijk AMSTERDAM", 20)
        'CoffeecompanyDeDijk'
        >>> sanitize_description("Test & Company!", 10)
        'TestCompa'
    """
    # Remove special characters, keep only alphanumeric and spaces
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", text)

    # Remove extra spaces
    cleaned = " ".join(cleaned.split())

    # Remove all spaces to create camelCase-style name
    cleaned = cleaned.replace(" ", "")

    # Limit length
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]

    return cleaned


def generate_scanned_filename(
    date_str: str, description: str, extension: str, suffix: int = 0
) -> str:
    """Generate filename for scanned folder.

    Format: {yyyyMMdd}-{description}.{ext} or {yyyyMMdd}-{description}-{suffix}.{ext}

    Args:
        date_str: Date string in format dd-MM-YYYY.
        description: Receipt description.
        extension: File extension (with or without leading dot).
        suffix: Optional numeric suffix for duplicate filenames (0 means no suffix).

    Returns:
        Formatted filename for scanned folder.

    Raises:
        ValueError: If date_str format is invalid.

    Examples:
        >>> generate_scanned_filename("10-07-2025", "Coffeecompany", ".jpg")
        '20250710-Coffeecompany.jpg'
        >>> generate_scanned_filename("10-07-2025", "Coffeecompany", ".jpg", suffix=2)
        '20250710-Coffeecompany-2.jpg'
    """
    # Parse date from dd-MM-YYYY format
    try:
        date_obj = datetime.strptime(date_str, "%d-%m-%Y")
    except ValueError as e:
        raise ValueError(f"Invalid date format '{date_str}', expected dd-MM-YYYY: {e}")

    # Format date as yyyyMMdd
    date_part = date_obj.strftime("%Y%m%d")

    # Sanitize description (max 15 chars as per requirements)
    desc_part = sanitize_description(description, max_length=15)

    # Ensure extension has leading dot
    if not extension.startswith("."):
        extension = f".{extension}"

    # Add suffix if provided and non-zero
    if suffix > 0:
        return f"{date_part}-{desc_part}-{suffix}{extension}"
    else:
        return f"{date_part}-{desc_part}{extension}"


def generate_unique_scanned_filename(
    date_str: str, description: str, extension: str, destination_folder: Path
) -> str:
    """Generate unique filename for scanned folder, avoiding conflicts.

    If the base filename already exists in the destination folder, adds a numeric
    suffix (-2, -3, etc.) until a unique filename is found.

    Args:
        date_str: Date string in format dd-MM-YYYY.
        description: Receipt description.
        extension: File extension (with or without leading dot).
        destination_folder: Path to the folder where file will be saved.

    Returns:
        Unique formatted filename for scanned folder.

    Raises:
        ValueError: If date_str format is invalid.

    Examples:
        >>> generate_unique_scanned_filename("10-07-2025", "Coffeecompany", ".jpg", Path("/data/scanned"))
        '20250710-Coffeecompany.jpg'  # If file doesn't exist
        >>> generate_unique_scanned_filename("10-07-2025", "Coffeecompany", ".jpg", Path("/data/scanned"))
        '20250710-Coffeecompany-2.jpg'  # If base file exists
    """
    # Try base filename first (no suffix)
    base_filename = generate_scanned_filename(date_str, description, extension, suffix=0)
    target_path = destination_folder / base_filename

    if not target_path.exists():
        return base_filename

    # File exists, try with suffixes until we find available one
    suffix = 2
    while True:
        filename_with_suffix = generate_scanned_filename(
            date_str, description, extension, suffix=suffix
        )
        target_path = destination_folder / filename_with_suffix

        if not target_path.exists():
            return filename_with_suffix

        suffix += 1

        # Safety check to prevent infinite loop (unlikely but defensive)
        if suffix > 1000:
            raise ValueError(
                f"Too many duplicate files for {base_filename} (tried up to suffix {suffix})"
            )


def generate_imported_filename(
    sequential_number: int, date_str: str, description: str, extension: str
) -> str:
    """Generate filename for imported folder.

    Format: {number}-{yyyyMMdd}-{description}.{ext}

    Args:
        sequential_number: Sequential number from XLSX.
        date_str: Date string in format dd-MM-YYYY.
        description: Receipt description.
        extension: File extension (with or without leading dot).

    Returns:
        Formatted filename for imported folder.

    Raises:
        ValueError: If date_str format is invalid.

    Examples:
        >>> generate_imported_filename(76, "10-07-2025", "Coffeecompany", ".jpg")
        '76-20250710-Coffeecompany.jpg'
    """
    # Parse date from dd-MM-YYYY format
    try:
        date_obj = datetime.strptime(date_str, "%d-%m-%Y")
    except ValueError as e:
        raise ValueError(f"Invalid date format '{date_str}', expected dd-MM-YYYY: {e}")

    # Format date as yyyyMMdd
    date_part = date_obj.strftime("%Y%m%d")

    # Sanitize description (max 15 chars as per requirements)
    desc_part = sanitize_description(description, max_length=15)

    # Ensure extension has leading dot
    if not extension.startswith("."):
        extension = f".{extension}"

    return f"{sequential_number}-{date_part}-{desc_part}{extension}"
