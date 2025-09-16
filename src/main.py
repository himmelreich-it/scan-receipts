"""Main entry point with hexagonal architecture dependency injection."""

import sys
from typing import Never

from rich import print as rprint
from rich.text import Text

from adapters.primary.tui.terminal_ui import TerminalUI
from adapters.secondary.anthropic_adapter import AnthropicAdapter
from adapters.secondary.csv_adapter import CSVAdapter
from adapters.secondary.duplicate_detection_adapter import DuplicateDetectionAdapter
from adapters.secondary.env_config_adapter import EnvConfigAdapter
from adapters.secondary.file_system_adapter import FileSystemAdapter
from adapters.secondary.xlsx_adapter import XLSXAdapter
from core.use_cases.import_to_xlsx import ImportToXLSXUseCase
from core.use_cases.process_receipt import ProcessReceiptUseCase
from core.use_cases.view_staging import ViewStagingUseCase


def main() -> Never:
    """Main entry point with dependency injection."""
    # Load configuration
    config_adapter = EnvConfigAdapter()
    try:
        config = config_adapter.load_config()
    except ValueError as e:
        rprint(Text(str(e), style="red"))
        sys.exit(1)

    # Create adapters
    file_system = FileSystemAdapter()
    ai_extraction = AnthropicAdapter()
    csv = CSVAdapter()
    xlsx = XLSXAdapter()
    duplicate_detection = DuplicateDetectionAdapter(file_system)

    # Create use cases
    process_receipt_use_case = ProcessReceiptUseCase(
        file_system, ai_extraction, csv, duplicate_detection
    )
    import_to_xlsx_use_case = ImportToXLSXUseCase(csv, xlsx, file_system)
    view_staging_use_case = ViewStagingUseCase(file_system, csv)

    # Create and run TUI
    tui = TerminalUI(
        file_system,
        process_receipt_use_case,
        import_to_xlsx_use_case,
        view_staging_use_case,
    )

    tui.run(config)


if __name__ == "__main__":
    main()
