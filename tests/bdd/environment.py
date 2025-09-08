"""
Behave environment setup for BDD tests.
Handles test setup and teardown for receipt processing engine tests.
"""
import tempfile
import shutil
import logging
from pathlib import Path


def before_all(context):
    """Set up before all scenarios."""
    # Configure logging for tests
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Store original working directory
    context.original_cwd = Path.cwd()


def before_scenario(context, scenario):
    """Set up before each scenario."""
    # Clean up any previous scenario data
    if hasattr(context, 'cleanup_paths'):
        cleanup_previous_scenario(context)
    
    # Create completely fresh temporary directories for each scenario
    context.temp_base_dir = Path(tempfile.mkdtemp(prefix=f'bdd_test_{scenario.line}_'))
    context.cleanup_paths = [context.temp_base_dir]
    
    # Initialize fresh context attributes for complete isolation
    context.temp_dirs = {}
    context.temp_files = {}
    context.hash_database = set()
    context.session_hashes = {}
    context.processed_files = []
    context.log_messages = []


def cleanup_previous_scenario(context):
    """Clean up resources from previous scenario."""
    # Reset file permissions FIRST before cleanup
    if hasattr(context, 'temp_dirs'):
        restore_permissions(context.temp_dirs)
    
    # Also restore permissions for temp_base_dir if it exists
    if hasattr(context, 'temp_base_dir') and context.temp_base_dir.exists():
        import os
        try:
            os.chmod(context.temp_base_dir, 0o755)
            for item in context.temp_base_dir.rglob('*'):
                try:
                    if item.is_file():
                        os.chmod(item, 0o644)
                    elif item.is_dir():
                        os.chmod(item, 0o755)
                except (PermissionError, OSError, FileNotFoundError):
                    pass
        except (PermissionError, OSError, FileNotFoundError):
            pass
    
    # Clean up temporary files and directories
    if hasattr(context, 'cleanup_paths'):
        for path in context.cleanup_paths:
            if path.exists():
                try:
                    if path.is_dir():
                        shutil.rmtree(path, ignore_errors=True)
                    else:
                        path.unlink(missing_ok=True)
                except (PermissionError, OSError):
                    pass  # Best effort cleanup
    
    # Remove any custom log handlers
    if hasattr(context, 'log_handler'):
        try:
            logging.getLogger().removeHandler(context.log_handler)
        except (ValueError, AttributeError):
            pass  # Handler already removed or doesn't exist


def restore_permissions(temp_dirs):
    """Restore normal permissions to all temp directories and files."""
    import os
    
    # Also restore permissions in temp_base_dir if it exists
    all_paths = list(temp_dirs.values())
    
    for temp_dir in all_paths:
        if temp_dir.exists():
            try:
                # Restore directory permissions first
                os.chmod(temp_dir, 0o755)
                # Then restore file permissions recursively
                for item in temp_dir.rglob('*'):
                    try:
                        if item.is_file():
                            os.chmod(item, 0o644)
                        elif item.is_dir():
                            os.chmod(item, 0o755)
                    except (PermissionError, OSError, FileNotFoundError):
                        # Try to restore at least basic permissions if possible
                        try:
                            os.chmod(item, 0o755 if item.is_dir() else 0o644)
                        except (PermissionError, OSError, FileNotFoundError):
                            pass
            except (PermissionError, OSError, FileNotFoundError):
                pass  # Best effort restoration


def after_scenario(context, scenario):
    """Clean up after each scenario."""
    # Use the same cleanup function for consistency
    cleanup_previous_scenario(context)


def after_all(context):
    """Clean up after all scenarios."""
    # Restore original working directory
    if hasattr(context, 'original_cwd'):
        import os
        os.chdir(context.original_cwd)