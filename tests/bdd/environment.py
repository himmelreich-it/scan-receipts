"""BDD test environment configuration."""

from typing import Any


def before_scenario(context: Any, scenario: Any) -> None:
    """Initialize context attributes before each scenario."""
    # Initialize _record to track available attributes for behave context
    context._record = {
        "config": ("", 1, "", ""),
        "tmpdir": ("", 1, "", ""),
        "startup_success": ("", 1, "", ""),
        "startup_error": ("", 1, "", ""),
        "input_count": ("", 1, "", ""),
        "failed_count": ("", 1, "", ""),
        "staging_info": ("", 1, "", ""),
        "menu_result": ("", 1, "", ""),
        "selected_option": ("", 1, "", ""),
        "invalid_input": ("", 1, "", ""),
        "exit_called": ("", 1, "", ""),
        "env_patch": ("", 1, "", ""),
        "env_vars": ("", 1, "", ""),
        "tags": ("", 1, "", ""),  # Required by behave runner
        "text": ("", 1, "", ""),  # Required by behave runner
        "table": ("", 1, "", ""),  # Required by behave runner
        "feature": ("", 1, "", ""),  # Required by behave runner
        # Duplicate detection test attributes
        "temp_dir": ("", 1, "", ""),
        "incoming": ("", 1, "", ""),
        "scanned": ("", 1, "", ""),
        "imported": ("", 1, "", ""),
        "failed": ("", 1, "", ""),
        "csv_file": ("", 1, "", ""),
        "file_system": ("", 1, "", ""),
        "duplicate_detection": ("", 1, "", ""),
        "mock_ai_extraction": ("", 1, "", ""),
        "mock_csv": ("", 1, "", ""),
        "use_case": ("", 1, "", ""),
        "file_contents": ("", 1, "", ""),
        "output": ("", 1, "", ""),
        "execution_error": ("", 1, "", ""),
        # View staging table test attributes
        "csv_path": ("", 1, "", ""),
        "csv_table": ("", 1, "", ""),
    }

    # Initialize _origin to track attribute origins for behave context
    # Use string literals instead of ContextMode to avoid type issues
    context._origin = {
        "config": "USER",
        "tmpdir": "USER",
        "startup_success": "USER",
        "startup_error": "USER",
        "input_count": "USER",
        "failed_count": "USER",
        "staging_info": "USER",
        "menu_result": "USER",
        "selected_option": "USER",
        "invalid_input": "USER",
        "exit_called": "USER",
        "env_patch": "USER",
        "env_vars": "USER",
        "tags": "BEHAVE",  # Required by behave runner
        "text": "BEHAVE",  # Required by behave runner
        "table": "BEHAVE",  # Required by behave runner
        "feature": "BEHAVE",  # Required by behave runner
        # Duplicate detection test attributes
        "temp_dir": "USER",
        "incoming": "USER",
        "scanned": "USER",
        "imported": "USER",
        "failed": "USER",
        "csv_file": "USER",
        "file_system": "USER",
        "duplicate_detection": "USER",
        "mock_ai_extraction": "USER",
        "mock_csv": "USER",
        "use_case": "USER",
        "file_contents": "USER",
        "output": "USER",
        "execution_error": "USER",
        # View staging table test attributes
        "csv_path": "USER",
        "csv_table": "USER",
    }


def after_scenario(context: Any, scenario: Any) -> None:
    """Clean up after each scenario."""
    # Stop any environment patching
    try:
        if (
            hasattr(context, "env_patch")
            and context.env_patch
            and hasattr(context.env_patch, "stop")
        ):
            context.env_patch.stop()
    except Exception:
        pass  # Ignore cleanup errors

    # Clean up temporary directories
    try:
        if hasattr(context, "tmpdir") and context.tmpdir:
            import shutil
            from pathlib import Path

            tmpdir_path = Path(context.tmpdir)
            if tmpdir_path.exists():
                shutil.rmtree(tmpdir_path)
    except Exception:
        pass  # Ignore cleanup errors

    # Clean up duplicate detection test temporary directories
    try:
        if hasattr(context, "temp_dir") and context.temp_dir:
            import shutil
            from pathlib import Path

            temp_dir_path = Path(context.temp_dir)
            if temp_dir_path.exists():
                shutil.rmtree(temp_dir_path)
    except Exception:
        pass  # Ignore cleanup errors

    # Clean up CSV files created for view staging table tests
    try:
        if hasattr(context, "csv_path") and context.csv_path:
            from pathlib import Path

            csv_path = Path(context.csv_path)
            if csv_path.exists():
                csv_path.unlink()
    except Exception:
        pass  # Ignore cleanup errors
