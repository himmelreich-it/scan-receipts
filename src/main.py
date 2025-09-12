"""Main entry point with hexagonal architecture dependency injection."""

import logging
import sys
from typing import Never

from rich import print as rprint
from rich.text import Text

from adapters import (
    AnthropicAdapter,
    CSVAdapter,
    EnvConfigAdapter,
    FileSystemAdapter,
    TerminalUI,
    XLSXAdapter,
)
from core.use_cases import ImportToXLSXUseCase, ProcessReceiptUseCase, ViewStagingDataUseCase
from scan_receipts.config import AppConfig
from scan_receipts.folders import create_folders

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def create_application() -> TerminalUI:
    """Create and wire the application components using dependency injection.
    
    Returns:
        Configured TerminalUI instance.
        
    Raises:
        SystemExit: If configuration or setup fails.
    """
    try:
        # Load configuration
        config = AppConfig.from_env()
    except ValueError as e:
        rprint(Text(str(e), style="red"))
        sys.exit(1)
    
    try:
        # Create folders using legacy function
        create_folders(config)
    except OSError as e:
        rprint(Text(str(e), style="red"))
        sys.exit(1)
    
    # Create secondary adapters (outbound)
    file_system_adapter = FileSystemAdapter()
    config_adapter = EnvConfigAdapter(config)
    csv_adapter = CSVAdapter()
    ai_adapter = AnthropicAdapter()
    xlsx_adapter = XLSXAdapter()
    
    # Create use cases with injected dependencies
    process_receipt_use_case = ProcessReceiptUseCase(
        file_system_port=file_system_adapter,
        ai_extraction_port=ai_adapter,
        csv_port=csv_adapter,
    )
    
    import_xlsx_use_case = ImportToXLSXUseCase(
        csv_port=csv_adapter,
        xlsx_port=xlsx_adapter,
        file_system_port=file_system_adapter,
    )
    
    view_staging_use_case = ViewStagingDataUseCase(
        csv_port=csv_adapter,
    )
    
    # Create primary adapter (inbound) with injected use cases
    terminal_ui = TerminalUI(
        config=config_adapter,
        process_receipt_use_case=process_receipt_use_case,
        import_xlsx_use_case=import_xlsx_use_case,
        view_staging_use_case=view_staging_use_case,
    )
    
    return terminal_ui


def main() -> Never:
    """Main entry point for the hexagonal architecture application."""
    app = create_application()
    app.run()


if __name__ == "__main__":
    main()