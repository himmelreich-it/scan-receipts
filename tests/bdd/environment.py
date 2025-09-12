"""BDD test environment configuration."""

from typing import Any


def before_scenario(context: Any, scenario: Any) -> None:
    """Initialize context attributes before each scenario."""
    # Initialize _record to track available attributes for behave context
    context._record = {
        'config': ("", 1, "", ""),
        'tmpdir': ("", 1, "", ""),
        'startup_success': ("", 1, "", ""),
        'startup_error': ("", 1, "", ""),
        'input_count': ("", 1, "", ""),
        'failed_count': ("", 1, "", ""),
        'staging_info': ("", 1, "", ""),
        'menu_result': ("", 1, "", ""),
        'selected_option': ("", 1, "", ""),
        'invalid_input': ("", 1, "", ""),
        'exit_called': ("", 1, "", ""),
        'env_patch': ("", 1, "", ""),
        'env_vars': ("", 1, "", ""),
        'tags': ("", 1, "", ""),  # Required by behave runner
        'text': ("", 1, "", ""),  # Required by behave runner
        'table': ("", 1, "", ""),  # Required by behave runner
    }
    
    # Initialize _origin to track attribute origins for behave context
    from behave.runner import ContextMode  # type: ignore
    context._origin = {
        'config': ContextMode.USER,
        'tmpdir': ContextMode.USER,
        'startup_success': ContextMode.USER,
        'startup_error': ContextMode.USER,
        'input_count': ContextMode.USER,
        'failed_count': ContextMode.USER,
        'staging_info': ContextMode.USER,
        'menu_result': ContextMode.USER,
        'selected_option': ContextMode.USER,
        'invalid_input': ContextMode.USER,
        'exit_called': ContextMode.USER,
        'env_patch': ContextMode.USER,
        'env_vars': ContextMode.USER,
        'tags': ContextMode.BEHAVE,  # Required by behave runner
        'text': ContextMode.BEHAVE,  # Required by behave runner
        'table': ContextMode.BEHAVE,  # Required by behave runner
    }


def after_scenario(context: Any, scenario: Any) -> None:
    """Clean up after each scenario."""
    # Stop any environment patching
    if hasattr(context, 'env_patch') and context.env_patch:
        context.env_patch.stop()