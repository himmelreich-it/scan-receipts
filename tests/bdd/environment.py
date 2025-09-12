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
    try:
        from behave.runner import ContextMode  # type: ignore[import-untyped]
        user_mode = ContextMode.USER  # type: ignore[attr-defined]
        behave_mode = ContextMode.BEHAVE  # type: ignore[attr-defined]
    except ImportError:
        # Fallback for type checking or if behave not available
        user_mode = "USER"  # type: ignore[assignment]
        behave_mode = "BEHAVE"  # type: ignore[assignment]
    
    context._origin = {
        'config': user_mode,
        'tmpdir': user_mode,
        'startup_success': user_mode,
        'startup_error': user_mode,
        'input_count': user_mode,
        'failed_count': user_mode,
        'staging_info': user_mode,
        'menu_result': user_mode,
        'selected_option': user_mode,
        'invalid_input': user_mode,
        'exit_called': user_mode,
        'env_patch': user_mode,
        'env_vars': user_mode,
        'tags': behave_mode,  # Required by behave runner
        'text': behave_mode,  # Required by behave runner
        'table': behave_mode,  # Required by behave runner
    }


def after_scenario(context: Any, scenario: Any) -> None:
    """Clean up after each scenario."""
    # Stop any environment patching
    if hasattr(context, 'env_patch') and context.env_patch:
        context.env_patch.stop()