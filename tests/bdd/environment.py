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
