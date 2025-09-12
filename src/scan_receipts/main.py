"""Main entry point for the receipt scanner TUI application."""

import signal
import sys
from typing import Any, Never

from rich import print as rprint
from rich.panel import Panel
from rich.text import Text

from scan_receipts.config import AppConfig
from scan_receipts.folders import count_receipt_files, create_folders, get_staging_info


def signal_handler(sig: int, frame: Any) -> None:
    """Handle Ctrl+C gracefully."""
    print("\nGoodbye")
    sys.exit(0)


def display_header() -> None:
    """Display the application header."""
    rprint(Panel.fit("Receipt Processor", border_style="cyan"))


def display_status(config: AppConfig) -> None:
    """Display system status information.
    
    Args:
        config: Application configuration.
    """
    input_count = count_receipt_files(config.incoming_folder)
    failed_count = count_receipt_files(config.failed_folder)
    staging_info = get_staging_info(config.csv_staging_file)
    
    rprint(f"Input Folder: {input_count} files")
    rprint(f"Failed Folder: {failed_count} files")
    
    if staging_info:
        rprint(f"Staging: {staging_info}")
    else:
        rprint("Staging: No staging data")
    
    rprint()


def display_menu() -> None:
    """Display the main menu options."""
    rprint("Available Actions:")
    rprint()
    rprint("[1] Run Analysis")
    rprint("[2] Import to XLSX")
    rprint("[3] View Staging Table")
    rprint("[4] Exit")
    rprint()


def handle_menu_choice(choice: str) -> bool:
    """Handle user menu selection.
    
    Args:
        choice: User's menu choice.
        
    Returns:
        True to continue, False to exit.
    """
    if choice == "1":
        rprint("Not yet implemented...")
        return True
    elif choice == "2":
        rprint("Not yet implemented...")
        return True
    elif choice == "3":
        rprint("Not yet implemented...")
        return True
    elif choice == "4":
        rprint("Goodbye")
        return False
    else:
        rprint(Text("Invalid choice. Please enter 1-4.", style="red"))
        return True


def main() -> Never:
    """Main entry point for the TUI application."""
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        config = AppConfig.from_env()
    except ValueError as e:
        rprint(Text(str(e), style="red"))
        sys.exit(1)
    
    try:
        create_folders(config)
    except OSError as e:
        rprint(Text(str(e), style="red"))
        sys.exit(1)
    
    display_header()
    
    while True:
        display_status(config)
        display_menu()
        
        try:
            choice = input("Enter your choice (1-4): ").strip()
        except EOFError:
            rprint("\nGoodbye")
            sys.exit(0)
        
        if not handle_menu_choice(choice):
            sys.exit(0)


if __name__ == "__main__":
    main()