"""Terminal user interface adapter."""

import signal
import sys
from typing import Any, Never

from rich import print as rprint
from rich.panel import Panel
from rich.text import Text

from core.use_cases import ImportToXLSXUseCase, ProcessReceiptUseCase, ViewStagingDataUseCase
from ports import ConfigurationPort


class TerminalUI:
    """Terminal user interface for the receipt processor."""

    def __init__(
        self,
        config: ConfigurationPort,
        process_receipt_use_case: ProcessReceiptUseCase,
        import_xlsx_use_case: ImportToXLSXUseCase,
        view_staging_use_case: ViewStagingDataUseCase,
    ):
        self._config = config
        self._process_receipt = process_receipt_use_case
        self._import_xlsx = import_xlsx_use_case
        self._view_staging = view_staging_use_case

    def run(self) -> Never:
        """Run the TUI application."""
        signal.signal(signal.SIGINT, self._signal_handler)
        
        self._display_header()
        
        while True:
            self._display_status()
            self._display_menu()
            
            try:
                choice = input("Enter your choice (1-4): ").strip()
            except EOFError:
                rprint("\nGoodbye")
                sys.exit(0)
            
            if not self._handle_menu_choice(choice):
                sys.exit(0)

    def _signal_handler(self, sig: int, frame: Any) -> None:
        """Handle Ctrl+C gracefully."""
        print("\nGoodbye")
        sys.exit(0)

    def _display_header(self) -> None:
        """Display the application header."""
        rprint(Panel.fit("Receipt Processor", border_style="cyan"))

    def _display_status(self) -> None:
        """Display system status information."""
        from adapters.secondary import FileSystemAdapter
        
        # Use temporary adapter for status display
        # In a complete implementation, this would be injected
        fs_adapter = FileSystemAdapter()
        
        input_count = fs_adapter.count_receipt_files(self._config.get_incoming_folder())
        failed_count = fs_adapter.count_receipt_files(self._config.get_failed_folder())
        staging_info = self._view_staging.get_staging_summary(self._config.get_csv_staging_file())
        
        rprint(f"Input Folder: {input_count} files")
        rprint(f"Failed Folder: {failed_count} files")
        
        if staging_info:
            rprint(f"Staging: {staging_info}")
        else:
            rprint("Staging: No staging data")
        
        rprint()

    def _display_menu(self) -> None:
        """Display the main menu options."""
        rprint()
        rprint("Available Actions:")
        rprint("[1] Run Analysis")
        rprint("[2] Import to XLSX")
        rprint("[3] View Staging Table")
        rprint("[4] Exit")
        rprint()

    def _handle_menu_choice(self, choice: str) -> bool:
        """Handle user menu selection.
        
        Args:
            choice: User's menu choice.
            
        Returns:
            True to continue, False to exit.
        """
        if choice == "1":
            self._run_analysis()
            return True
        elif choice == "2":
            self._import_to_xlsx()
            return True
        elif choice == "3":
            self._view_staging_table()
            return True
        elif choice == "4":
            rprint("Goodbye")
            return False
        else:
            rprint(Text("Invalid choice. Please enter 1-4.", style="red"))
            return True

    def _run_analysis(self) -> None:
        """Execute receipt processing workflow."""
        try:
            rprint("Running receipt analysis...")
            
            receipts = self._process_receipt.execute(
                incoming_folder=self._config.get_incoming_folder(),
                scanned_folder=self._config.get_scanned_folder(),
                failed_folder=self._config.get_failed_folder(),
                staging_csv=self._config.get_csv_staging_file(),
            )
            
            if receipts:
                rprint(f"[green]Successfully processed {len(receipts)} receipts[/green]")
            else:
                rprint("[yellow]No receipts found to process[/yellow]")
                
        except Exception as e:
            rprint(f"[red]Error during analysis: {e}[/red]")

    def _import_to_xlsx(self) -> None:
        """Execute XLSX import workflow."""
        try:
            rprint("Importing to XLSX...")
            
            count = self._import_xlsx.execute(
                staging_csv=self._config.get_csv_staging_file(),
                xlsx_file=self._config.get_xlsx_output_file(),
                imported_folder=self._config.get_imported_folder(),
            )
            
            if count > 0:
                rprint(f"[green]Successfully imported {count} receipts[/green]")
            else:
                rprint("[yellow]No new receipts to import[/yellow]")
                
        except Exception as e:
            rprint(f"[red]Error during import: {e}[/red]")

    def _view_staging_table(self) -> None:
        """Display staging data."""
        try:
            rprint("Loading staging data...")
            
            staging_info = self._view_staging.get_staging_summary(
                self._config.get_csv_staging_file()
            )
            
            if staging_info:
                rprint(f"[green]Staging Data: {staging_info}[/green]")
                
                # Get detailed data
                receipts = self._view_staging.get_staging_data(
                    self._config.get_csv_staging_file()
                )
                
                if receipts:
                    for receipt in receipts:
                        rprint(f"- {receipt.filename}: {receipt.vendor} (${receipt.total})")
                else:
                    rprint("[yellow]Detailed data not yet implemented[/yellow]")
            else:
                rprint("[yellow]No staging data found[/yellow]")
                
        except Exception as e:
            rprint(f"[red]Error viewing staging data: {e}[/red]")