"""BDD test environment configuration."""

from typing import Any


def before_scenario(context: Any, scenario: Any) -> None:
    """Initialize context attributes before each scenario."""
    # Use _record to track available attributes
    context._record = {
        'config': None,
        'tmpdir': None,
        'startup_success': None,
        'startup_error': None,
        'input_count': None,
        'failed_count': None,
        'staging_info': None,
        'menu_result': None,
        'selected_option': None,
        'invalid_input': None,
        'exit_called': None,
        'env_patch': None,
        'env_vars': None,
    }