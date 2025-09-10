"""BDD step definitions for file management scenarios."""

import tempfile
import shutil
from pathlib import Path
from typing import Any, Dict
from behave import given, when, then  # type: ignore
from unittest.mock import patch

from file_management.adapters import FileSystemAdapter
from file_management.models import FileErrorCode


@given('the system is configured with test folder paths')  # type: ignore
def step_given_test_folder_paths(context: Any) -> None:
    """Setup test folder configuration."""
    context.temp_dir = Path(tempfile.mkdtemp())
    context.file_system_adapter = FileSystemAdapter()
    context.folder_paths = {
        'incoming': context.temp_dir / 'incoming',
        'scanned': context.temp_dir / 'scanned',
        'imported': context.temp_dir / 'imported',
        'failed': context.temp_dir / 'failed'
    }


@given('I have file system permissions')  # type: ignore
def step_given_file_system_permissions(_context: Any) -> None:
    """Verify file system permissions are available."""
    # This is implicit in our test setup
    pass


@given('the folders "{folder_list}" do not exist')  # type: ignore
def step_given_folders_do_not_exist(context: Any, folder_list: str) -> None:
    """Ensure specified folders don't exist."""
    folder_names = [name.strip().strip('"') for name in folder_list.split(',')]
    for folder_name in folder_names:
        folder_path = context.folder_paths[folder_name]
        if folder_path.exists():
            shutil.rmtree(folder_path)
        assert not folder_path.exists()


@when('I ensure folder structure exists')  # type: ignore
def step_when_ensure_folder_structure(context: Any) -> None:
    """Call folder validation through File System Port."""
    results: Dict[str, Any] = {}
    for folder_name, folder_path in context.folder_paths.items():
        result = context.file_system_adapter.ensure_folder_exists(folder_path)
        results[folder_name] = result
    context.results = results


@then('all four folders should be created successfully')  # type: ignore
def step_then_folders_created(context: Any) -> None:
    """Verify folder creation success."""
    for folder_name, result in context.results.items():
        assert result.success, f"Failed to create {folder_name} folder: {result.error_message}"
        assert result.exists, f"{folder_name} folder should exist"
        assert result.is_writable, f"{folder_name} folder should be writable"


@then('each folder should be writable')  # type: ignore
def step_then_each_folder_writable(context: Any) -> None:
    """Verify each folder is writable."""
    for folder_name, result in context.results.items():
        assert result.is_writable, f"{folder_name} folder should be writable"


@given('all folders exist with test files')  # type: ignore
def step_given_all_folders_exist_with_files(context: Any) -> None:
    """Create all folders with test files."""
    test_files: Dict[str, Path] = {}
    for folder_name, folder_path in context.folder_paths.items():
        folder_path.mkdir(parents=True, exist_ok=True)
        test_file = folder_path / f"test_{folder_name}.txt"
        test_file.write_text(f"content from {folder_name}")
        test_files[folder_name] = test_file
    context.test_files = test_files


@when('I begin analysis workflow')  # type: ignore
def step_when_begin_analysis_workflow(context: Any) -> None:
    """Begin analysis workflow by clearing scanned folder."""
    scanned_folder = context.folder_paths['scanned']
    context.clear_result = context.file_system_adapter.clear_folder(scanned_folder)


@then('the scanned folder should be empty')  # type: ignore
def step_then_scanned_folder_empty(context: Any) -> None:
    """Verify scanned folder is empty."""
    assert context.clear_result.success, f"Failed to clear scanned folder: {context.clear_result.error_message}"
    scanned_folder = context.folder_paths['scanned']
    files = list(scanned_folder.iterdir())
    assert len(files) == 0, f"Scanned folder should be empty but contains: {files}"


@then('the "{folder_list}" folders should retain their files')  # type: ignore
def step_then_folders_retain_files(context: Any, folder_list: str) -> None:
    """Verify specified folders retain their files."""
    folder_names = [name.strip().strip('"') for name in folder_list.split(',')]
    for folder_name in folder_names:
        test_file = context.test_files[folder_name]
        assert test_file.exists(), f"Test file in {folder_name} should still exist"
        assert test_file.read_text() == f"content from {folder_name}"


@given('folder "{folder_name}" cannot be created due to permissions')  # type: ignore
def step_given_folder_permission_denied(context: Any, folder_name: str) -> None:
    """Mock permission denied error for folder creation."""
    context.restricted_folder = folder_name
    context.mock_permission_error = patch(
        'pathlib.Path.mkdir',
        side_effect=PermissionError("Permission denied")
    )


@when('I try to ensure folder structure')  # type: ignore
def step_when_try_ensure_folder_structure(context: Any) -> None:
    """Try to create folder structure with permission restrictions."""
    folder_path = context.folder_paths[context.restricted_folder]
    
    with context.mock_permission_error:
        context.permission_result = context.file_system_adapter.ensure_folder_exists(folder_path)


@then('I should receive error code "{expected_error_code}"')  # type: ignore
def step_then_receive_error_code(context: Any, expected_error_code: str) -> None:
    """Verify expected error code is received."""
    expected_code = FileErrorCode(expected_error_code)
    
    # Check which context attribute has the result
    if hasattr(context, 'permission_result'):
        actual_code = context.permission_result.error_code
    elif hasattr(context, 'validation_result'):
        actual_code = context.validation_result.error_code
    else:
        assert False, "No result context attribute found"
        
    assert actual_code == expected_code, f"Expected {expected_code}, got {actual_code}"


@then('the error should include the folder path')  # type: ignore
def step_then_error_includes_folder_path(context: Any) -> None:
    """Verify error message includes the folder path."""
    folder_path = context.folder_paths[context.restricted_folder]
    
    # Check which context attribute has the result
    if hasattr(context, 'permission_result'):
        error_message = context.permission_result.error_message
    elif hasattr(context, 'validation_result'):
        error_message = context.validation_result.error_message
    else:
        assert False, "No result context attribute found"
        
    assert str(folder_path) in error_message, f"Error message should include folder path: {error_message}"


@given('all folders exist and are writable')  # type: ignore
def step_given_all_folders_writable(context: Any) -> None:
    """Create all folders and verify they are writable."""
    for _folder_name, folder_path in context.folder_paths.items():
        folder_path.mkdir(parents=True, exist_ok=True)
        # Test writability by creating a temp file
        test_file = folder_path / '.test_write'
        test_file.touch()
        test_file.unlink()


@given('I have a test receipt file "{filename}"')  # type: ignore
def step_given_test_receipt_file(context: Any, filename: str) -> None:
    """Create a test receipt file."""
    context.test_filename = filename
    context.test_file_content = b"fake PDF content for testing"


@given('a file exists in incoming folder')  # type: ignore
def step_given_file_in_incoming(context: Any) -> None:
    """Create a test file in incoming folder."""
    incoming_folder = context.folder_paths['incoming']
    context.source_file = incoming_folder / context.test_filename
    context.source_file.write_bytes(context.test_file_content)


@when('I copy the file to scanned folder with name "{target_filename}"')  # type: ignore
def step_when_copy_to_scanned(context: Any, target_filename: str) -> None:
    """Execute file copy operation."""
    scanned_folder = context.folder_paths['scanned']
    context.target_file = scanned_folder / target_filename
    context.copy_result = context.file_system_adapter.copy_file(
        context.source_file, context.target_file
    )


@then('the file should exist in both incoming and scanned folders')  # type: ignore
def step_then_file_in_both_folders(context: Any) -> None:
    """Verify file exists in both source and target folders."""
    assert context.copy_result.success, f"Copy operation failed: {context.copy_result.error_message}"
    assert context.source_file.exists(), "Source file should still exist after copy"
    assert context.target_file.exists(), "Target file should exist after copy"


@then('the scanned file should have the exact name "{expected_name}"')  # type: ignore
def step_then_scanned_file_has_name(context: Any, expected_name: str) -> None:
    """Verify scanned file has expected name."""
    assert context.target_file.name == expected_name, f"Expected {expected_name}, got {context.target_file.name}"


@given('a file exists in scanned folder named "{filename}"')  # type: ignore
def step_given_file_in_scanned(context: Any, filename: str) -> None:
    """Create a file in scanned folder."""
    scanned_folder = context.folder_paths['scanned']
    context.source_file = scanned_folder / filename
    context.source_file.write_bytes(context.test_file_content)


@when('I move the file to imported folder with name "{target_filename}"')  # type: ignore
def step_when_move_to_imported(context: Any, target_filename: str) -> None:
    """Execute file move operation."""
    imported_folder = context.folder_paths['imported']
    context.target_file = imported_folder / target_filename
    context.move_result = context.file_system_adapter.move_file(
        context.source_file, context.target_file
    )


@then('the file should exist only in imported folder')  # type: ignore
def step_then_file_only_in_imported(context: Any) -> None:
    """Verify file exists only in target folder after move."""
    assert context.move_result.success, f"Move operation failed: {context.move_result.error_message}"
    assert not context.source_file.exists(), "Source file should not exist after move"
    assert context.target_file.exists(), "Target file should exist after move"


@then('the imported file should have the exact name "{expected_name}"')  # type: ignore
def step_then_imported_file_has_name(context: Any, expected_name: str) -> None:
    """Verify imported file has expected name."""
    assert context.target_file.name == expected_name, f"Expected {expected_name}, got {context.target_file.name}"


@given('a file operation encounters "{error_condition}"')  # type: ignore
def step_given_file_operation_error(context: Any, error_condition: str) -> None:
    """Setup file operation error conditions."""
    context.error_condition = error_condition
    
    if error_condition == "file locked":
        # Mock OSError with errno 16 (Device or resource busy)
        error = OSError()
        error.errno = 16
        context.error_mock = patch('shutil.copy2', side_effect=error)
    elif error_condition == "target exists":
        context.error_setup_target_exists = True
    elif error_condition == "source missing":
        context.error_setup_source_missing = True  
    elif error_condition == "no permission":
        context.error_mock = patch('shutil.copy2', side_effect=PermissionError("Permission denied"))


@when('I attempt the file operation')  # type: ignore
def step_when_attempt_file_operation(context: Any) -> None:
    """Attempt file operation with error conditions."""
    incoming_folder = context.folder_paths['incoming']
    scanned_folder = context.folder_paths['scanned']
    
    if hasattr(context, 'error_setup_target_exists'):
        # Create source and target files
        source_file = incoming_folder / "test.pdf"
        target_file = scanned_folder / "test.pdf"
        source_file.write_bytes(b"test")
        target_file.write_bytes(b"existing")
        context.error_result = context.file_system_adapter.copy_file(source_file, target_file)
    elif hasattr(context, 'error_setup_source_missing'):
        # Try to copy non-existent file
        source_file = incoming_folder / "missing.pdf"
        target_file = scanned_folder / "target.pdf"
        context.error_result = context.file_system_adapter.copy_file(source_file, target_file)
    else:
        # Use mock for other errors
        source_file = incoming_folder / "test.pdf"
        target_file = scanned_folder / "test.pdf"
        source_file.write_bytes(b"test")
        
        with context.error_mock:
            context.error_result = context.file_system_adapter.copy_file(source_file, target_file)


@then('I should receive file error code "{expected_error}"')  # type: ignore
def step_then_receive_file_error_code(context: Any, expected_error: str) -> None:
    """Verify expected file operation error code."""
    expected_code = FileErrorCode(expected_error)
    actual_code = context.error_result.error_code
    assert actual_code == expected_code, f"Expected {expected_code}, got {actual_code}"


@given('I have test files with known content')  # type: ignore
def step_given_test_files_known_content(context: Any) -> None:
    """Setup test files with known content for hash testing."""
    context.test_files_dir = context.temp_dir / "test_files"
    context.test_files_dir.mkdir()


@given('a file "{filename}" with known content')  # type: ignore
def step_given_file_known_content(context: Any, filename: str) -> None:
    """Create a file with known content."""
    context.test_file = context.test_files_dir / filename
    context.test_content = b"This is test content for hashing"
    context.test_file.write_bytes(context.test_content)
    
    # Calculate expected hash
    import hashlib
    context.expected_hash = hashlib.sha256(context.test_content).hexdigest()


@when('I generate a hash for the file')  # type: ignore
def step_when_generate_hash(context: Any) -> None:
    """Execute hash generation through port."""
    context.hash_result = context.file_system_adapter.generate_file_hash(context.test_file)


@then('I should receive a 64-character hexadecimal string')  # type: ignore
def step_then_receive_64_char_hex(context: Any) -> None:
    """Verify hash is 64-character hexadecimal string."""
    assert context.hash_result.success, f"Hash generation failed: {context.hash_result.error_message}"
    hash_value = context.hash_result.hash_value
    assert len(hash_value) == 64, f"Hash should be 64 characters, got {len(hash_value)}"
    # Verify it's hexadecimal
    try:
        int(hash_value, 16)
    except ValueError:
        assert False, f"Hash should be hexadecimal: {hash_value}"


@then('the hash should match the expected SHA-256 value')  # type: ignore
def step_then_hash_matches_expected(context: Any) -> None:
    """Verify hash matches expected SHA-256 value."""
    actual_hash = context.hash_result.hash_value
    assert actual_hash == context.expected_hash, f"Expected {context.expected_hash}, got {actual_hash}"


@given('an empty file "{filename}"')  # type: ignore
def step_given_empty_file(context: Any, filename: str) -> None:
    """Create an empty file."""
    context.empty_file = context.test_files_dir / filename
    context.empty_file.write_bytes(b"")
    
    # Expected hash for empty content
    import hashlib
    context.expected_empty_hash = hashlib.sha256(b"").hexdigest()


@then('I should receive the SHA-256 hash of empty content')  # type: ignore
def step_then_receive_empty_hash(context: Any) -> None:
    """Verify hash of empty file."""
    assert context.hash_result.success, f"Hash generation failed: {context.hash_result.error_message}"
    actual_hash = context.hash_result.hash_value
    assert actual_hash == context.expected_empty_hash, f"Expected empty hash {context.expected_empty_hash}, got {actual_hash}"


@then('the operation should succeed')  # type: ignore
def step_then_operation_succeeds(context: Any) -> None:
    """Verify operation succeeded."""
    assert context.hash_result.success, f"Operation should succeed: {context.hash_result.error_message}"


@given('a file with "{error_condition}"')  # type: ignore
def step_given_file_with_error(context: Any, error_condition: str) -> None:
    """Setup file with specific error condition."""
    context.error_file_condition = error_condition
    
    if error_condition == "file not found":
        context.error_file = context.test_files_dir / "nonexistent.pdf"
    elif error_condition == "file unreadable":
        context.error_file = context.test_files_dir / "unreadable.pdf"
        context.error_file.write_bytes(b"test")
        context.permission_mock = patch('builtins.open', side_effect=PermissionError("Permission denied"))
    elif error_condition == "file corrupted":
        context.error_file = context.test_files_dir / "corrupted.pdf"
        context.error_file.write_bytes(b"test")
        io_error = OSError()
        io_error.errno = 5  # Input/output error
        context.corruption_mock = patch('builtins.open', side_effect=io_error)
    elif error_condition == "no permission":
        context.error_file = context.test_files_dir / "noperm.pdf" 
        context.error_file.write_bytes(b"test")
        context.permission_mock = patch('builtins.open', side_effect=PermissionError("Permission denied"))


@when('I try to generate a hash')  # type: ignore
def step_when_try_generate_hash(context: Any) -> None:
    """Try to generate hash with error conditions."""
    if hasattr(context, 'permission_mock'):
        with context.permission_mock:
            context.hash_error_result = context.file_system_adapter.generate_file_hash(context.error_file)
    elif hasattr(context, 'corruption_mock'):
        with context.corruption_mock:
            context.hash_error_result = context.file_system_adapter.generate_file_hash(context.error_file)
    else:
        context.hash_error_result = context.file_system_adapter.generate_file_hash(context.error_file)


@then('I should receive hash error code "{expected_hash_error}"')  # type: ignore
def step_then_receive_hash_error_code(context: Any, expected_hash_error: str) -> None:
    """Verify expected hash error code."""
    expected_code = FileErrorCode(expected_hash_error)
    actual_code = context.hash_error_result.error_code
    assert actual_code == expected_code, f"Expected {expected_code}, got {actual_code}"


@given('all folders exist')  # type: ignore
def step_given_all_folders_exist(context: Any) -> None:
    """Create all folders for testing."""
    for _folder_name, folder_path in context.folder_paths.items():
        folder_path.mkdir(parents=True, exist_ok=True)


@given('folder "{folder_name}" is not writable')  # type: ignore
def step_given_folder_not_writable(context: Any, folder_name: str) -> None:
    """Setup folder that is not writable."""
    context.non_writable_folder = folder_name
    # We'll mock this in the validation step


@when('I validate folder permissions')  # type: ignore
def step_when_validate_folder_permissions(context: Any) -> None:
    """Validate folder permissions with mock for non-writable folder."""
    folder_path = context.folder_paths[context.non_writable_folder]
    
    # Mock the write test to simulate non-writable folder
    with patch('pathlib.Path.touch', side_effect=PermissionError("Permission denied")):
        context.validation_result = context.file_system_adapter.ensure_folder_exists(folder_path)


@then('the error should specify the folder path')  # type: ignore
def step_then_error_specifies_folder_path(context: Any) -> None:
    """Verify error message specifies the folder path."""
    folder_path = context.folder_paths[context.non_writable_folder]
    error_message = context.validation_result.error_message
    assert str(folder_path) in error_message, f"Error message should specify folder path: {error_message}"


@given('the incoming folder exists but is empty')  # type: ignore
def step_given_incoming_folder_empty(context: Any) -> None:
    """Create empty incoming folder."""
    incoming_folder = context.folder_paths['incoming']
    incoming_folder.mkdir(parents=True, exist_ok=True)
    # Ensure it's empty
    for item in incoming_folder.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)


@when('I check for files to process')  # type: ignore
def step_when_check_files_to_process(context: Any) -> None:
    """Check for files in incoming folder."""
    incoming_folder = context.folder_paths['incoming']
    context.files_to_process = context.file_system_adapter.list_files(incoming_folder)


@then('the system should continue without error')  # type: ignore
def step_then_system_continues_without_error(context: Any) -> None:
    """Verify no errors occur when checking empty folder."""
    # The list_files operation should complete without error
    assert isinstance(context.files_to_process, list), "File listing should return a list"


@then('no files should be processed')  # type: ignore
def step_then_no_files_processed(context: Any) -> None:
    """Verify no files are found to process."""
    assert len(context.files_to_process) == 0, f"Expected no files, found {len(context.files_to_process)}"


@given('the imported folder contains existing files')  # type: ignore
def step_given_imported_folder_has_files(context: Any) -> None:
    """Create imported folder with existing files."""
    imported_folder = context.folder_paths['imported']
    imported_folder.mkdir(parents=True, exist_ok=True)
    
    context.existing_imported_files = [
        "001-20231215-receipt1.pdf",
        "002-20231216-receipt2.pdf"
    ]
    
    for filename in context.existing_imported_files:
        file_path = imported_folder / filename
        file_path.write_text("existing imported file content")


@when('any system operation is performed')  # type: ignore
def step_when_any_system_operation_performed(context: Any) -> None:
    """Perform a typical system operation like folder validation."""
    # Simulate system operation by validating all folders
    for _folder_name, folder_path in context.folder_paths.items():
        context.file_system_adapter.ensure_folder_exists(folder_path)


@then('all imported folder files should remain unchanged')  # type: ignore
def step_then_imported_files_unchanged(context: Any) -> None:
    """Verify imported folder files are preserved."""
    imported_folder = context.folder_paths['imported']
    
    for filename in context.existing_imported_files:
        file_path = imported_folder / filename
        assert file_path.exists(), f"Imported file {filename} should still exist"
        content = file_path.read_text()
        assert content == "existing imported file content", f"Content of {filename} should be unchanged"


@given('the failed folder contains existing error logs and files')  # type: ignore
def step_given_failed_folder_has_error_logs(context: Any) -> None:
    """Create failed folder with error logs and files."""
    failed_folder = context.folder_paths['failed']
    failed_folder.mkdir(parents=True, exist_ok=True)
    
    context.existing_failed_files = [
        "corrupted_receipt.pdf",
        "corrupted_receipt.pdf.log",
        "unreadable_file.jpg"
    ]
    
    for filename in context.existing_failed_files:
        file_path = failed_folder / filename
        if filename.endswith('.log'):
            file_path.write_text("Error: File corrupted during processing")
        else:
            file_path.write_bytes(b"corrupted file content")


@then('all failed folder contents should remain unchanged')  # type: ignore
def step_then_failed_folder_unchanged(context: Any) -> None:
    """Verify failed folder contents are preserved."""
    failed_folder = context.folder_paths['failed']
    
    for filename in context.existing_failed_files:
        file_path = failed_folder / filename
        assert file_path.exists(), f"Failed folder file {filename} should still exist"
        
        if filename.endswith('.log'):
            content = file_path.read_text()
            assert content == "Error: File corrupted during processing", "Log content should be unchanged"
        else:
            content = file_path.read_bytes()
            assert content == b"corrupted file content", "File content should be unchanged"


def after_scenario(context: Any, _scenario: Any) -> None:
    """Clean up after each scenario."""
    if hasattr(context, 'temp_dir') and context.temp_dir.exists():
        shutil.rmtree(context.temp_dir)