"""Terminal User Interface adapter for receipt processing."""

import signal
import sys
from typing import Any, Never

from rich import print as rprint
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from core.domain.configuration import AppConfig
from core.use_cases.import_to_xlsx import ImportToXLSXUseCase
from core.use_cases.process_receipt import ProcessReceiptUseCase
from core.use_cases.view_staging import ViewStagingUseCase
from ports.file_system import FileSystemPort


class TerminalUI:
    """Terminal User Interface adapter."""

    def __init__(
        self,
        file_system: FileSystemPort,
        process_receipt_use_case: ProcessReceiptUseCase,
        import_to_xlsx_use_case: ImportToXLSXUseCase,
        view_staging_use_case: ViewStagingUseCase,
    ):
        self.file_system = file_system
        self.process_receipt_use_case = process_receipt_use_case
        self.import_to_xlsx_use_case = import_to_xlsx_use_case
        self.view_staging_use_case = view_staging_use_case

    def signal_handler(self, sig: int, frame: Any) -> None:
        """Handle Ctrl+C gracefully."""
        print("\nGoodbye")
        sys.exit(0)

    def display_header(self) -> None:
        """Display the application header."""
        rprint(Panel.fit("Receipt Processor", border_style="cyan"))

    def display_status(self, config: AppConfig) -> None:
        """Display system status information.

        Args:
            config: Application configuration.
        """
        # Display configured folder and file paths
        rprint("Configured Paths:")
        rprint(f"Incoming: {config.incoming_folder.resolve()}")
        rprint(f"Scanned: {config.scanned_folder.resolve()}")
        rprint(f"Imported: {config.imported_folder.resolve()}")
        rprint(f"Failed: {config.failed_folder.resolve()}")
        rprint(f"XLSX: {config.xlsx_output_file.resolve()}")
        rprint(f"CSV: {config.csv_staging_file.resolve()}")
        rprint()

        input_count = self.file_system.count_receipt_files(config.incoming_folder)
        failed_count = self.file_system.count_receipt_files(config.failed_folder)
        staging_info = self.view_staging_use_case.execute(config)

        rprint(f"Input Folder: {input_count} files")
        rprint(f"Failed Folder: {failed_count} files")

        if staging_info:
            rprint(f"Staging: {staging_info}")
        else:
            rprint("Staging: No staging data")

        rprint()

    def display_menu(self, config: AppConfig) -> None:
        """Display the main menu options.

        Args:
            config: Application configuration.
        """
        rprint()
        rprint("Available Actions:")

        # Dynamic menu option based on receipts.csv existence
        if config.csv_staging_file.exists():
            rprint("[1] Re-run Analysis")
        else:
            rprint("[1] Run Analysis")

        rprint("[2] Import to XLSX")
        rprint("[3] View Staging Table")
        rprint("[4] Exit")
        rprint()

    def display_staging_table(self, config: AppConfig) -> None:
        """Display the staging table contents.

        Args:
            config: Application configuration.
        """
        staging_data = self.view_staging_use_case.get_full_table(config)

        if staging_data is None:
            rprint(Text("Error reading staging table.", style="red"))
            return

        if not staging_data.exists:
            rprint("receipts.csv does not exist")
            return

        if staging_data.is_empty:
            rprint("receipts.csv is empty")
            return

        # Create a rich table
        table = Table(title=f"Staging Table: {staging_data.file_path.name}")

        # Add columns
        table.add_column("Amount", style="cyan")
        table.add_column("Tax", style="cyan")
        table.add_column("TaxPercentage", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Currency", style="yellow")
        table.add_column("Date", style="magenta")
        table.add_column("Confidence", style="blue")
        table.add_column("Hash", style="dim")
        table.add_column("DoneFilename", style="white")

        # Add rows
        for receipt in staging_data.receipts:
            table.add_row(
                receipt.amount,
                receipt.tax,
                receipt.tax_percentage,
                receipt.description,
                receipt.currency,
                receipt.date,
                receipt.confidence,
                receipt.hash[:8] + "..." if len(receipt.hash) > 8 else receipt.hash,
                receipt.done_filename,
            )

        rprint(table)
        rprint(f"\nTotal entries: {len(staging_data.receipts)}")

    def handle_menu_choice(self, choice: str, config: AppConfig) -> bool:
        """Handle user menu selection.

        Args:
            choice: User's menu choice.
            config: Application configuration.

        Returns:
            True to continue, False to exit.
        """
        if choice == "1":
            self.process_receipt_use_case.execute(config)
            rprint("Analysis completed.")
            return True
        elif choice == "2":
            self.import_to_xlsx_use_case.execute(config)
            rprint("Import completed.")
            return True
        elif choice == "3":
            self.display_staging_table(config)
            return True
        elif choice == "4":
            rprint("Goodbye")
            return False
        else:
            rprint(Text("Invalid choice. Please enter 1-4.", style="red"))
            return True

    def run(self, config: AppConfig) -> Never:
        """Run the terminal UI.

        Args:
            config: Application configuration.
        """
        signal.signal(signal.SIGINT, self.signal_handler)

        try:
            self.file_system.create_folders(config)
        except OSError as e:
            rprint(Text(str(e), style="red"))
            sys.exit(1)

        self.display_header()

        while True:
            self.display_status(config)
            self.display_menu(config)

            try:
                choice = input("Enter your choice (1-4): ").strip()
            except EOFError:
                rprint("\nGoodbye")
                sys.exit(0)

            if not self.handle_menu_choice(choice, config):
                sys.exit(0)
