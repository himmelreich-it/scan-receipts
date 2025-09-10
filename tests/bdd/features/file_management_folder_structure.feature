Feature: Four-Folder Structure Management and Validation
  As a receipt processing system
  I want to manage a complete four-folder structure 
  So that files are properly organized through the processing workflow

  Background:
    Given the system is configured with test folder paths
    And I have file system permissions

  Scenario: Create missing folders automatically
    Given the folders "incoming", "scanned", "imported", "failed" do not exist
    When I ensure folder structure exists
    Then all four folders should be created successfully
    And each folder should be writable

  Scenario: Clear scanned folder while preserving others
    Given all folders exist with test files
    When I begin analysis workflow
    Then the scanned folder should be empty
    And the "incoming", "imported", "failed" folders should retain their files

  Scenario Outline: Handle folder permission errors
    Given folder "<folder_name>" cannot be created due to permissions
    When I try to ensure folder structure
    Then I should receive error code "FOLDER_PERMISSION_DENIED"
    And the error should include the folder path

    Examples:
      | folder_name |
      | incoming    |
      | scanned     |
      | imported    |
      | failed      |

  Scenario Outline: Validate folder write permissions
    Given all folders exist
    But folder "<folder_name>" is not writable
    When I validate folder permissions
    Then I should receive error code "FOLDER_NOT_WRITABLE"
    And the error should specify the folder path

    Examples:
      | folder_name |
      | incoming    |
      | scanned     |
      | imported    |
      | failed      |

  Scenario: Continue processing when incoming folder is empty
    Given the incoming folder exists but is empty
    When I check for files to process
    Then the system should continue without error
    And no files should be processed

  Scenario: Preserve imported folder contents permanently
    Given the imported folder contains existing files
    When any system operation is performed
    Then all imported folder files should remain unchanged

  Scenario: Preserve failed folder contents permanently
    Given the failed folder contains existing error logs and files
    When any system operation is performed
    Then all failed folder contents should remain unchanged