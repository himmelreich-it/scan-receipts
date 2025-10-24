"""Use case for importing staging data to XLSX."""

import logging
from typing import List

from rich import print as rprint

from core.domain.configuration import AppConfig
from core.utils.filename import generate_imported_filename
from ports.csv import CSVPort
from ports.duplicate_detection import DuplicateDetectionPort
from ports.file_system import FileSystemPort
from ports.xlsx import XLSXPort

logger = logging.getLogger(__name__)


class ImportToXLSXUseCase:
    """Use case for importing staging data to Excel."""

    def __init__(
        self,
        csv: CSVPort,
        xlsx: XLSXPort,
        file_system: FileSystemPort,
        duplicate_detection: DuplicateDetectionPort,
    ):
        self.csv = csv
        self.xlsx = xlsx
        self.file_system = file_system
        self.duplicate_detection = duplicate_detection

    def execute(self, config: AppConfig) -> None:
        """Import staging data to XLSX file.

        Args:
            config: Application configuration.
        """
        logger.info("Starting XLSX import")

        # 1. Check if receipts.csv exists
        if not config.csv_staging_file.exists():
            rprint("❌ No receipts.csv found. Run analysis first.")
            return

        # 2. Read staging CSV data
        staging_data = self.csv.read_staging_table(config.csv_staging_file)
        if not staging_data or staging_data.is_empty:
            rprint("❌ receipts.csv is empty. Nothing to import.")
            return

        rprint(f"📄 Found {len(staging_data.receipts)} entries in receipts.csv")

        # 3. Validate files exist in scanned folder
        validation_errors = self._validate_staging_data(staging_data, config)
        if validation_errors:
            rprint("\n❌ Validation errors:")
            for error in validation_errors:
                rprint(f"  • {error}")
            return

        rprint("✅ Validation passed")

        # 4. Check for duplicate hashes against imported folder
        imported_hashes = self.file_system.get_file_hashes_from_folder(config.imported_folder)
        duplicates = []
        for receipt in staging_data.receipts:
            # Check if hash already exists in imported folder
            if any(h.hash_value == receipt.hash for h in imported_hashes):
                duplicates.append(receipt.description)

        if duplicates:
            rprint("\n❌ Duplicate receipts found (already imported):")
            for dup in duplicates:
                rprint(f"  • {dup}")
            rprint("These receipts appear to have already been imported.")
            return

        # 5. Create backup of XLSX file
        if self.xlsx.xlsx_file_exists(config.xlsx_output_file):
            rprint(f"\n💾 Creating backup of {config.xlsx_output_file.name}...")
            backup_path = self.file_system.create_backup_file(config.xlsx_output_file)
            if backup_path:
                rprint(f"✅ Backup created: {backup_path.name}")
            else:
                rprint("⚠️  No backup created (file doesn't exist)")
        else:
            rprint(f"⚠️  XLSX file does not exist: {config.xlsx_output_file}")
            return

        # 6. Prepare entries for XLSX
        rprint(f"\n📝 Importing {len(staging_data.receipts)} entries...")

        xlsx_entries = []
        for receipt in staging_data.receipts:
            entry = {
                "date": receipt.date,
                "description": receipt.description,
                "amount": receipt.amount,
                "tax": receipt.tax,
                "currency": receipt.currency,
            }
            xlsx_entries.append(entry)

        # 7. Append to XLSX and get sequential numbers used
        try:
            used_numbers = self.xlsx.append_entries(config.xlsx_output_file, xlsx_entries)
            rprint(
                f"✅ Successfully appended entries to XLSX (numbers {used_numbers[0]}-{used_numbers[-1]})"
            )
        except Exception as e:
            rprint(f"❌ Failed to append to XLSX: {e}")
            logger.error(f"Failed to append to XLSX: {e}")
            return

        # 8. Move files from scanned to imported folder with proper naming
        rprint("\n📦 Moving files to imported folder...")
        moved_count = 0
        failed_moves = []

        for idx, receipt in enumerate(staging_data.receipts):
            current_number = used_numbers[idx]
            try:
                # Find source file in scanned folder
                source_file = config.scanned_folder / receipt.done_filename

                if not source_file.exists():
                    failed_moves.append(f"{receipt.done_filename} (not found)")
                    continue

                # Generate imported filename
                extension = source_file.suffix
                imported_filename = generate_imported_filename(
                    current_number, receipt.date, receipt.description, extension
                )

                # Move file to imported folder
                self.file_system.move_file_to_folder(
                    source_file, config.imported_folder, imported_filename
                )

                moved_count += 1

            except Exception as e:
                failed_moves.append(f"{receipt.done_filename} ({str(e)})")
                logger.error(f"Failed to move {receipt.done_filename}: {e}")

        # 9. Show summary
        rprint("\n✅ Import complete!")
        rprint(f"  • Entries added to XLSX: {len(xlsx_entries)}")
        rprint(f"  • Files moved to imported: {moved_count}")

        if failed_moves:
            rprint(f"\n⚠️  Failed to move {len(failed_moves)} files:")
            for failed in failed_moves:
                rprint(f"  • {failed}")

        logger.info(
            f"XLSX import completed - entries: {len(xlsx_entries)}, files moved: {moved_count}"
        )

    def _validate_staging_data(self, staging_data: any, config: AppConfig) -> List[str]:
        """Validate staging data against scanned folder.

        Args:
            staging_data: Staging table data from CSV.
            config: Application configuration.

        Returns:
            List of validation error messages (empty if valid).
        """
        errors = []

        # Get files in scanned folder
        scanned_files = self.file_system.get_supported_files(config.scanned_folder)
        scanned_filenames = {f.name for f in scanned_files}

        # Check count
        if len(staging_data.receipts) != len(scanned_files):
            errors.append(
                f"Count mismatch: receipts.csv has {len(staging_data.receipts)} entries, "
                f"scanned folder has {len(scanned_files)} files"
            )

        # Check each CSV entry has corresponding file
        for receipt in staging_data.receipts:
            if receipt.done_filename not in scanned_filenames:
                errors.append(f"File not found in scanned folder: {receipt.done_filename}")

        return errors
