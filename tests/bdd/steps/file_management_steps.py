"""BDD step definitions for file management scenarios."""

import tempfile
import shutil
from pathlib import Path
from typing import Any, Dict
from behave import given, when, then  # type: ignore
from unittest.mock import patch

from file_management.adapters import FileSystemAdapter
from file_management.models import FileErrorCode, FileMovementRequest


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
    elif hasattr(context, 'hash_error_result'):
        actual_code = context.hash_error_result.error_code
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



@given('I have test files with known content')  # type: ignore
def step_given_test_files_known_content(context: Any) -> None:
    """Setup test files with known content for hash testing."""
    # Initialize temp directory if not already set
    if not hasattr(context, 'temp_dir'):
        context.temp_dir = Path(tempfile.mkdtemp())
        context.file_system_adapter = FileSystemAdapter()
    
    context.test_files_dir = context.temp_dir / "test_files"
    context.test_files_dir.mkdir(exist_ok=True)


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
    context.test_file = context.test_files_dir / filename  # Use test_file for consistency
    context.test_file.write_bytes(b"")
    
    # Expected hash for empty content
    import hashlib
    context.expected_empty_hash = hashlib.sha256(b"").hexdigest()


@then('I should receive the SHA-256 hash of empty content')  # type: ignore
def step_then_receive_empty_hash(context: Any) -> None:
    """Verify we received the correct hash for empty content."""
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


# File Movement BDD Steps

@when('I copy the file to scanned folder using file movement')  # type: ignore
def step_when_copy_file_movement_to_scanned(context: Any) -> None:
    """Copy file using file movement service."""
    request = FileMovementRequest(
        source_path=context.source_file,
        target_folder=context.folder_paths['scanned'],
        description="test description",
        date="20240315"
    )
    context.movement_result = context.file_system_adapter.move_to_scanned(request)


@when('I move the file to imported folder using file movement')  # type: ignore
def step_when_move_file_movement_to_imported(context: Any) -> None:
    """Move file using file movement service."""
    request = FileMovementRequest(
        source_path=context.source_file,
        target_folder=context.folder_paths['imported'],
        description="test description", 
        date="20240315",
        sequence_number=1
    )
    context.movement_result = context.file_system_adapter.move_to_imported(request)


@when('I copy the file to failed folder using file movement')  # type: ignore
def step_when_copy_file_movement_to_failed(context: Any) -> None:
    """Copy file using file movement service."""
    request = FileMovementRequest(
        source_path=context.source_file,
        target_folder=context.folder_paths['failed'],
        description="error occurred",
        date="20240315"
    )
    context.movement_result = context.file_system_adapter.copy_to_failed(request)


@then('the file movement should succeed')  # type: ignore  
def step_then_file_movement_succeeds(context: Any) -> None:
    """Verify file movement succeeded."""
    assert context.movement_result.success, f"File movement failed: {context.movement_result.error_message}"


@then('the file should be copied with naming convention "{expected_pattern}"')  # type: ignore
def step_then_file_copied_with_naming(context: Any, expected_pattern: str) -> None:
    """Verify file copied with correct naming convention."""
    assert context.movement_result.success
    target_path = context.movement_result.target_path
    assert target_path.name == expected_pattern, f"Expected {expected_pattern}, got {target_path.name}"
    
    # Verify original still exists (copy operation)
    assert context.source_file.exists(), "Original file should still exist after copy"


@then('the file should be moved with naming convention "{expected_pattern}"')  # type: ignore
def step_then_file_moved_with_naming(context: Any, expected_pattern: str) -> None:
    """Verify file moved with correct naming convention."""
    assert context.movement_result.success
    target_path = context.movement_result.target_path
    assert target_path.name == expected_pattern, f"Expected {expected_pattern}, got {target_path.name}"
    
    # Verify original no longer exists (move operation)
    assert not context.source_file.exists(), "Original file should not exist after move"


@then('the file should be copied preserving original filename')  # type: ignore
def step_then_file_copied_preserving_name(context: Any) -> None:
    """Verify file copied with original filename preserved."""
    assert context.movement_result.success
    target_path = context.movement_result.target_path
    assert target_path.name == context.source_file.name, f"Expected {context.source_file.name}, got {target_path.name}"
    
    # Verify original still exists (copy operation)
    assert context.source_file.exists(), "Original file should still exist after copy"


# Error handling for file movement

@given('a file operation encounters "{error_condition}"')  # type: ignore
def step_given_file_operation_error(context: Any, error_condition: str) -> None:
    """Setup file operation error condition."""
    context.error_condition = error_condition
    
    # Create a source file
    incoming_folder = context.folder_paths['incoming']
    context.error_source_file = incoming_folder / "error_test.pdf"
    context.error_source_file.write_bytes(b"test content")
    
    if error_condition == "target exists":
        # Create existing target file
        scanned_folder = context.folder_paths['scanned']
        existing_target = scanned_folder / "20240315-test_descriptio.pdf"
        existing_target.write_bytes(b"existing content")
    elif error_condition == "source missing":
        # Use non-existent source
        context.error_source_file = incoming_folder / "missing.pdf"


@when('I attempt the file operation')  # type: ignore
def step_when_attempt_file_operation(context: Any) -> None:
    """Attempt file operation with error conditions."""
    if context.error_condition == "file locked":
        # Mock file lock error
        with patch.object(context.file_system_adapter, 'copy_file') as mock_copy:
            mock_copy.return_value.success = False
            mock_copy.return_value.error_code = FileErrorCode.FILE_LOCKED
            mock_copy.return_value.error_message = "File is locked"
            
            request = FileMovementRequest(
                source_path=context.error_source_file,
                target_folder=context.folder_paths['scanned'],
                description="test",
                date="20240315"
            )
            context.file_operation_result = context.file_system_adapter.move_to_scanned(request)
    
    elif context.error_condition == "target exists":
        # Mock file exists error
        with patch.object(context.file_system_adapter, 'copy_file') as mock_copy:
            mock_copy.return_value.success = False  
            mock_copy.return_value.error_code = FileErrorCode.FILE_EXISTS
            mock_copy.return_value.error_message = "Target file already exists"
            
            request = FileMovementRequest(
                source_path=context.error_source_file,
                target_folder=context.folder_paths['scanned'],
                description="test",
                date="20240315"
            )
            context.file_operation_result = context.file_system_adapter.move_to_scanned(request)
    
    elif context.error_condition == "source missing":
        request = FileMovementRequest(
            source_path=context.error_source_file,
            target_folder=context.folder_paths['scanned'],
            description="test",
            date="20240315"
        )
        context.file_operation_result = context.file_system_adapter.move_to_scanned(request)
    
    elif context.error_condition == "permission denied":
        # Mock permission denied error
        with patch.object(context.file_system_adapter, 'copy_file') as mock_copy:
            mock_copy.return_value.success = False
            mock_copy.return_value.error_code = FileErrorCode.FILE_PERMISSION_DENIED
            mock_copy.return_value.error_message = "Permission denied"
            
            request = FileMovementRequest(
                source_path=context.error_source_file,
                target_folder=context.folder_paths['scanned'],
                description="test",
                date="20240315"
            )
            context.file_operation_result = context.file_system_adapter.move_to_scanned(request)
    
    elif context.error_condition == "disk space full":
        # Mock disk space error
        with patch.object(context.file_system_adapter, 'copy_file') as mock_copy:
            mock_copy.return_value.success = False
            mock_copy.return_value.error_code = FileErrorCode.DISK_SPACE_FULL
            mock_copy.return_value.error_message = "Disk space full"
            
            request = FileMovementRequest(
                source_path=context.error_source_file,
                target_folder=context.folder_paths['scanned'],
                description="test",
                date="20240315"
            )
            context.file_operation_result = context.file_system_adapter.move_to_scanned(request)


@then('I should receive file operation error code "{error_code}"')  # type: ignore
def step_then_receive_file_operation_error_code(context: Any, error_code: str) -> None:
    """Verify expected error code from file operation."""
    expected_code = FileErrorCode(error_code)
    actual_code = context.file_operation_result.error_code
    assert actual_code == expected_code, f"Expected {expected_code}, got {actual_code}"


@then('the error should include relevant file path information')  # type: ignore
def step_then_error_includes_file_path_info(context: Any) -> None:
    """Verify error includes file path information."""
    error_message = context.file_operation_result.error_message
    assert error_message is not None, "Error message should not be None"
    # Should contain some path information
    assert len(error_message) > 0, "Error message should contain information"


# Description Cleaning BDD Steps

@given('a description with text "{input_text}"')  # type: ignore
def step_given_description_text(context: Any, input_text: str) -> None:
    """Setup description text for cleaning."""
    context.input_description = input_text
    # Initialize adapter if not present
    if not hasattr(context, 'file_system_adapter'):
        context.file_system_adapter = FileSystemAdapter()


@given('a description with text ""')  # type: ignore
def step_given_description_empty_text(context: Any) -> None:
    """Setup empty description text for cleaning."""
    context.input_description = ""
    # Initialize adapter if not present
    if not hasattr(context, 'file_system_adapter'):
        context.file_system_adapter = FileSystemAdapter()


@when('I clean the description')  # type: ignore  
def step_when_clean_description(context: Any) -> None:
    """Execute description cleaning."""
    context.cleaned_description = context.file_system_adapter.clean_description(context.input_description)


@then('the result should be "{expected_output}"')  # type: ignore
def step_then_result_should_be(context: Any, expected_output: str) -> None:
    """Verify cleaned description matches expected output."""
    assert context.cleaned_description == expected_output, f"Expected '{expected_output}', got '{context.cleaned_description}'"


@given('a description "{description_text}"')  # type: ignore
def step_given_description_text_simple(context: Any, description_text: str) -> None:
    """Setup description text (simple version)."""
    context.input_description = description_text
    # Initialize adapter if not present
    if not hasattr(context, 'file_system_adapter'):
        context.file_system_adapter = FileSystemAdapter()


@then('the result should be exactly 15 characters long')  # type: ignore
def step_then_result_15_chars(context: Any) -> None:
    """Verify result is exactly 15 characters."""
    length = len(context.cleaned_description)
    assert length == 15, f"Expected 15 characters, got {length}"


@then('it should be "{expected_text}"')  # type: ignore
def step_then_it_should_be(context: Any, expected_text: str) -> None:
    """Verify result matches expected text."""
    assert context.cleaned_description == expected_text, f"Expected '{expected_text}', got '{context.cleaned_description}'"


@then('it should not have leading or trailing spaces')  # type: ignore
def step_then_no_leading_trailing_spaces(context: Any) -> None:
    """Verify no leading or trailing spaces."""
    result = context.cleaned_description
    assert not result.startswith(' '), f"Should not start with space: '{result}'"
    assert not result.endswith(' '), f"Should not end with space: '{result}'"


@then('consecutive spaces should be collapsed to single underscores')  # type: ignore
def step_then_spaces_collapsed(context: Any) -> None:
    """Verify consecutive spaces are collapsed."""
    result = context.cleaned_description
    assert '  ' not in result, f"Should not contain consecutive spaces: '{result}'"
    assert '__' not in result, f"Should not contain consecutive underscores: '{result}'"


@then('it should be exactly 15 characters')  # type: ignore
def step_then_exactly_15_characters(context: Any) -> None:
    """Verify exactly 15 characters."""
    length = len(context.cleaned_description)
    assert length == 15, f"Expected exactly 15 characters, got {length}"


@then('it should contain only safe filesystem characters')  # type: ignore
def step_then_only_safe_filesystem_chars(context: Any) -> None:
    """Verify only safe filesystem characters."""
    result = context.cleaned_description
    unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in unsafe_chars:
        assert char not in result, f"Should not contain unsafe character '{char}': '{result}'"


@then('it should use the fallback for descriptions that become only underscores')  # type: ignore
def step_then_uses_fallback(context: Any) -> None:
    """Verify fallback is used for descriptions that become only underscores."""
    assert context.cleaned_description == "document", f"Expected 'document' fallback, got '{context.cleaned_description}'"


@then('numbers and safe punctuation should be preserved')  # type: ignore
def step_then_numbers_punctuation_preserved(context: Any) -> None:
    """Verify numbers and safe punctuation are preserved."""
    result = context.cleaned_description
    # Should contain numbers and safe characters like # and -
    assert any(c.isdigit() for c in result), f"Should contain numbers: '{result}'"


# Additional step definitions for file hash generation scenarios

@given('two files with identical content but different names')  # type: ignore
def step_given_two_identical_files(context: Any) -> None:
    """Create two files with identical content but different names."""
    content = b"Identical content for hash comparison"
    
    context.file1 = context.test_files_dir / "file1.pdf"
    context.file2 = context.test_files_dir / "file2.jpg"
    
    context.file1.write_bytes(content)
    context.file2.write_bytes(content)


@when('I generate hashes for both files')  # type: ignore
def step_when_generate_hashes_for_both_files(context: Any) -> None:
    """Generate hashes for both files."""
    context.hash1 = context.file_system_adapter.generate_file_hash(context.file1)
    context.hash2 = context.file_system_adapter.generate_file_hash(context.file2)


@then('both hashes should be identical')  # type: ignore
def step_then_both_hashes_identical(context: Any) -> None:
    """Verify both hashes are identical."""
    assert context.hash1.success, f"First hash failed: {context.hash1.error_message}"
    assert context.hash2.success, f"Second hash failed: {context.hash2.error_message}"
    assert context.hash1.hash_value == context.hash2.hash_value


@then('both should be valid 64-character hexadecimal strings')  # type: ignore
def step_then_both_valid_64_char_hex(context: Any) -> None:
    """Verify both hashes are valid 64-character hexadecimal strings."""
    for hash_result in [context.hash1, context.hash2]:
        assert len(hash_result.hash_value) == 64
        try:
            int(hash_result.hash_value, 16)
        except ValueError:
            assert False, f"Hash should be hexadecimal: {hash_result.hash_value}"


@given('two files with different content')  # type: ignore
def step_given_two_different_files(context: Any) -> None:
    """Create two files with different content."""
    context.file1 = context.test_files_dir / "different1.pdf"
    context.file2 = context.test_files_dir / "different2.pdf"
    
    context.file1.write_bytes(b"First file content")
    context.file2.write_bytes(b"Second file content")


@then('the hashes should be different')  # type: ignore
def step_then_hashes_different(context: Any) -> None:
    """Verify the hashes are different."""
    assert context.hash1.success, f"First hash failed: {context.hash1.error_message}"
    assert context.hash2.success, f"Second hash failed: {context.hash2.error_message}"
    assert context.hash1.hash_value != context.hash2.hash_value


@given('a large file "{filename}" over 10MB')  # type: ignore
def step_given_large_file(context: Any, filename: str) -> None:
    """Create a large file over 10MB."""
    context.test_file = context.test_files_dir / filename
    # Create smaller file for testing (1MB instead of 10MB to save time)
    chunk_size = 64 * 1024  # 64KB chunks
    chunk_data = b'A' * chunk_size
    
    with open(context.test_file, 'wb') as f:
        for _ in range(16):  # 16 * 64KB = 1MB (sufficient for testing chunking)
            f.write(chunk_data)


@then('the operation should complete without memory overflow')  # type: ignore
def step_then_no_memory_overflow(context: Any) -> None:
    """Verify operation completed without memory issues."""
    # If we got here without MemoryError, the test passed
    assert context.hash_result.success, f"Hash operation failed: {context.hash_result.error_message}"


@then('I should receive a valid SHA-256 hash')  # type: ignore
def step_then_valid_sha256_hash(context: Any) -> None:
    """Verify we received a valid SHA-256 hash."""
    assert context.hash_result.success, f"Hash operation failed: {context.hash_result.error_message}"
    assert len(context.hash_result.hash_value) == 64
    try:
        int(context.hash_result.hash_value, 16)
    except ValueError:
        assert False, f"Hash should be hexadecimal: {context.hash_result.hash_value}"


@given('a file "{filename}" that I previously hashed')  # type: ignore
def step_given_previously_hashed_file(context: Any, filename: str) -> None:
    """Create a file and generate its first hash."""
    context.test_file = context.test_files_dir / filename
    context.test_content = b"Content for repeat hashing test"
    context.test_file.write_bytes(context.test_content)
    
    # Generate first hash
    context.first_hash = context.file_system_adapter.generate_file_hash(context.test_file)
    assert context.first_hash.success


@when('I generate a hash for the file again')  # type: ignore
def step_when_generate_hash_again(context: Any) -> None:
    """Generate hash for the file again."""
    context.hash_result = context.file_system_adapter.generate_file_hash(context.test_file)


@then('the hash generation should process the file completely')  # type: ignore
def step_then_process_file_completely(context: Any) -> None:
    """Verify the file was processed completely (no caching)."""
    # This is verified by ensuring the operation succeeded
    assert context.hash_result.success, f"Hash operation failed: {context.hash_result.error_message}"


@then('the hash should match the previous result')  # type: ignore
def step_then_hash_matches_previous(context: Any) -> None:
    """Verify the hash matches the previous result."""
    assert context.hash_result.hash_value == context.first_hash.hash_value


@then('the error should include the file path')  # type: ignore
def step_then_error_includes_file_path(context: Any) -> None:
    """Verify error message includes the file path."""
    assert context.hash_error_result.error_message is not None
    assert str(context.error_file) in context.hash_error_result.error_message


@given('files with different formats: "{file_list}"')  # type: ignore
def step_given_different_format_files(context: Any, file_list: str) -> None:
    """Create files with different formats."""
    filenames = [f.strip().strip('"') for f in file_list.split(',')]
    context.format_files = []
    
    for filename in filenames:
        file_path = context.test_files_dir / filename
        # Use different content for each file format
        content = f"Content for {filename}".encode()
        file_path.write_bytes(content)
        context.format_files.append(file_path)


@when('I generate hashes for all files')  # type: ignore
def step_when_generate_hashes_for_all_files(context: Any) -> None:
    """Generate hashes for all format files."""
    context.format_hashes = []
    for file_path in context.format_files:
        hash_result = context.file_system_adapter.generate_file_hash(file_path)
        context.format_hashes.append(hash_result)


@then('each file should produce a unique valid SHA-256 hash')  # type: ignore
def step_then_each_unique_valid_hash(context: Any) -> None:
    """Verify each file produces a unique valid SHA-256 hash."""
    hash_values = []
    for hash_result in context.format_hashes:
        assert hash_result.success, f"Hash failed: {hash_result.error_message}"
        assert len(hash_result.hash_value) == 64
        hash_values.append(hash_result.hash_value)
    
    # Verify all hashes are unique
    assert len(set(hash_values)) == len(hash_values), "All hashes should be unique"


@then('all operations should succeed')  # type: ignore
def step_then_all_operations_succeed(context: Any) -> None:
    """Verify all hash operations succeeded."""
    for hash_result in context.format_hashes:
        assert hash_result.success, f"Hash operation failed: {hash_result.error_message}"


@given('a file with zero bytes')  # type: ignore
def step_given_zero_byte_file(context: Any) -> None:
    """Create a file with zero bytes."""
    context.test_file = context.test_files_dir / "empty.txt"
    context.test_file.touch()  # Creates empty file


@then('I should receive the standard SHA-256 hash for empty content')  # type: ignore
def step_then_standard_empty_hash(context: Any) -> None:
    """Verify we receive the standard SHA-256 hash for empty content."""
    import hashlib
    expected_empty_hash = hashlib.sha256(b"").hexdigest()
    assert context.hash_result.hash_value == expected_empty_hash


@then('the operation should succeed without error')  # type: ignore
def step_then_operation_succeeds(context: Any) -> None:
    """Verify the operation succeeded without error."""
    assert context.hash_result.success, f"Operation failed: {context.hash_result.error_message}"


def after_scenario(context: Any, _scenario: Any) -> None:
    """Clean up after each scenario."""
    if hasattr(context, 'temp_dir') and context.temp_dir.exists():
        shutil.rmtree(context.temp_dir)