Feature: File Movement and Naming Convention Pipeline
  As a receipt processing system
  I want to move files between folders with proper naming
  So that files follow the correct workflow and naming conventions

  Background:
    Given all folders exist and are writable
    And I have a test receipt file "test_receipt.pdf"

  Scenario: Copy file from incoming to scanned
    Given a file exists in incoming folder
    When I copy the file to scanned folder with name "20231215-grocery_store.pdf"
    Then the file should exist in both incoming and scanned folders
    And the scanned file should have the exact name "20231215-grocery_store.pdf"

  Scenario: Move file from scanned to imported  
    Given a file exists in scanned folder named "20231215-grocery_store.pdf"
    When I move the file to imported folder with name "001-20231215-grocery_store.pdf"
    Then the file should exist only in imported folder
    And the imported file should have the exact name "001-20231215-grocery_store.pdf"

  Scenario: Copy file to failed folder preserving original name
    Given a file "problem_receipt.jpg" exists in incoming folder
    When I copy the file to failed folder
    Then the file should exist in both incoming and failed folders
    And the failed folder file should retain the original name "problem_receipt.jpg"

  Scenario Outline: Handle file operation errors
    Given a file operation encounters "<error_condition>"
    When I attempt the file operation
    Then I should receive file operation error code "<error_code>"
    And the error should include relevant file path information
    
    Examples:
      | error_condition      | error_code             |
      | file locked          | FILE_LOCKED            |
      | target exists        | FILE_EXISTS            |
      | source missing       | FILE_NOT_FOUND         |
      | permission denied    | FILE_PERMISSION_DENIED |
      | disk space full      | DISK_SPACE_FULL        |

  Scenario: Verify file copy preserves original in source location
    Given a file "original.pdf" exists in incoming folder
    When I copy the file to scanned folder with any name
    Then the original file should still exist in incoming folder
    And the file content should be identical in both locations

  Scenario: Verify file move removes original from source location
    Given a file "temp.pdf" exists in scanned folder
    When I move the file to imported folder with any name
    Then the file should not exist in scanned folder
    And the file should exist only in imported folder

  Scenario: Handle large file operations
    Given a large file over 10MB exists in incoming folder
    When I copy the file to scanned folder
    Then the operation should complete successfully
    And both files should have identical content and size