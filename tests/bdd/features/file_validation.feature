Feature: File Format Validation and Error Handling
  As a receipt processing system
  I want to validate input file formats and handle various error scenarios
  So that I can ensure processing continuity with proper error management and failed folder handling

  Background:
    Given the receipt processing system is initialized
    And the failed folder exists for error handling
    And there are multiple files to process in queue

  Scenario Outline: Process supported file formats successfully
    Given a file "<filename>" with format "<format>"
    When the system validates the file format
    Then the system should proceed with processing
    And the file should not be moved to failed folder

    Examples:
      | filename        | format |
      | receipt.pdf     | PDF    |
      | receipt.jpg     | JPG    |
      | receipt.png     | PNG    |

  Scenario Outline: Handle unsupported file formats
    Given a file "<filename>" with unsupported format "<format>"
    When the system validates the file format
    Then the system should move the file to failed folder
    And the system should create error log "Unsupported file format"
    And the system should continue with next file
    And processing should not be interrupted

    Examples:
      | filename        | format |
      | document.txt    | TXT    |
      | image.gif       | GIF    |
      | data.xlsx       | XLSX   |
      | archive.zip     | ZIP    |

  Scenario Outline: Handle corrupted or unreadable files
    Given a corrupted file "<filename>" that cannot be read
    When the system attempts to process the file
    Then the system should move the file to failed folder
    And the system should create error log "File unreadable or corrupted"
    And the system should continue processing remaining files
    And processing should not be interrupted

    Examples:
      | filename              |
      | corrupted_receipt.pdf |
      | damaged_image.jpg     |
      | broken_file.png       |

  Scenario: Handle Claude API failure during processing
    Given a valid file "receipt_api_fail.pdf"
    When the system processes the file
    And the Claude API returns an error "Service temporarily unavailable"
    Then the system should move the file to failed folder
    And the system should create error log "API failure: Service temporarily unavailable"
    And the system should continue processing remaining files
    And processing should not be interrupted

  Scenario: Handle Claude API network timeout
    Given a valid file "receipt_timeout.pdf"
    When the system processes the file
    And the Claude API request times out
    Then the system should move the file to failed folder
    And the system should create error log "API failure: Request timeout"
    And the system should continue processing remaining files
    And processing should not be interrupted

  Scenario: Handle Claude API rate limiting
    Given a valid file "receipt_rate_limit.pdf"
    When the system processes the file
    And the Claude API returns rate limit exceeded error
    Then the system should move the file to failed folder
    And the system should create error log "API failure: Rate limit exceeded"
    And the system should continue processing remaining files
    And processing should not be interrupted

  Scenario Outline: Handle JSON parsing failures
    Given a valid file "<filename>"
    When the system processes the file
    And the Claude API returns malformed JSON response "<json_error>"
    Then the system should move the file to failed folder
    And the system should create error log "JSON parsing failed: <json_details>"
    And the system should continue processing remaining files
    And processing should not be interrupted

    Examples:
      | filename              | json_error           | json_details        |
      | receipt_bad_json.pdf  | Invalid JSON syntax  | Invalid JSON syntax |
      | receipt_incomplete.jpg| Missing closing brace| Missing closing brace|
      | receipt_malformed.png | Unexpected token     | Unexpected token    |

  Scenario Outline: Handle date extraction failures
    Given a valid file "<filename>"
    When the system processes the file
    And date extraction fails completely with error "<date_error>"
    Then the system should move the file to failed folder
    And the system should create error log "Date extraction failed: no valid date found"
    And the system should continue processing remaining files
    And processing should not be interrupted

    Examples:
      | filename               | date_error              |
      | receipt_no_date.pdf    | No date found on receipt|
      | receipt_garbled.jpg    | Date text unreadable    |

  Scenario: Handle file permission errors
    Given a file "protected_receipt.pdf" with restricted read permissions
    When the system attempts to read the file
    Then the system should move the file to failed folder
    And the system should create error log "File unreadable or corrupted"
    And the system should continue processing remaining files
    And processing should not be interrupted

  Scenario: Handle disk space issues during error logging
    Given a valid file "receipt_disk_full.pdf"
    And the system has insufficient disk space
    When the system attempts to create error log in failed folder
    Then the system should handle the disk space error gracefully
    And the system should continue processing remaining files
    And processing should not be interrupted

  Scenario: Verify processing continuity after multiple errors
    Given multiple files in processing queue:
      | filename              | expected_error_type    |
      | unsupported.txt       | Unsupported format     |
      | corrupted.pdf         | File unreadable        |
      | valid_receipt.jpg     | Success                |
      | api_fail.png          | API failure            |
      | another_valid.pdf     | Success                |
    When the system processes all files in sequence
    Then the system should handle each error appropriately
    And the system should continue processing after each error
    And valid files should be processed successfully
    And error files should be moved to failed folder with appropriate logs
    And no processing should be interrupted by individual file failures

  Scenario: Verify failed folder management
    Given the failed folder is empty
    When multiple files fail processing with different error types
    Then each failed file should be moved to failed folder
    And each failed file should have corresponding error log
    And error logs should contain detailed error information
    And no CSV entries should be created for failed files
    And failed folder should be organized properly

  Scenario: Verify error log content and format
    Given a file "test_error_log.pdf" that will fail processing
    When the file fails with specific error details
    Then the error log should contain filename
    And the error log should contain timestamp
    And the error log should contain specific error message
    And the error log should contain error context information
    And the error log should be readable and properly formatted