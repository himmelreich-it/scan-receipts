Feature: File Hash Generation and Duplicate Detection Support
  As a receipt processing system
  I want to generate SHA-256 hashes for files
  So that duplicate detection can be performed across folders and sessions

  Background:
    Given I have test files with known content

  Scenario: Generate hash for normal file
    Given a file "test_receipt.pdf" with known content
    When I generate a hash for the file
    Then I should receive a 64-character hexadecimal string
    And the hash should match the expected SHA-256 value

  Scenario: Generate hash for empty file
    Given an empty file "empty.txt"
    When I generate a hash for the file
    Then I should receive the SHA-256 hash of empty content
    And the operation should succeed

  Scenario: Generate consistent hashes for identical content
    Given two files with identical content but different names
    When I generate hashes for both files
    Then both hashes should be identical
    And both should be valid 64-character hexadecimal strings

  Scenario: Generate different hashes for different content
    Given two files with different content
    When I generate hashes for both files
    Then the hashes should be different
    And both should be valid 64-character hexadecimal strings

  Scenario: Handle large file processing
    Given a large file "large_receipt.pdf" over 10MB
    When I generate a hash for the file
    Then the operation should complete without memory overflow
    And I should receive a valid SHA-256 hash

  Scenario: Generate fresh hash each time (no caching)
    Given a file "test.pdf" that I previously hashed
    When I generate a hash for the file again
    Then the hash generation should process the file completely
    And the hash should match the previous result

  Scenario Outline: Handle hash generation errors
    Given a file with "<error_condition>"
    When I try to generate a hash
    Then I should receive error code "<error_code>"
    And the error should include the file path
    
    Examples:
      | error_condition | error_code             |
      | file not found  | FILE_NOT_FOUND         |
      | file unreadable | FILE_PERMISSION_DENIED |
      | file corrupted  | FILE_CORRUPTED         |
      | no permission   | FILE_PERMISSION_DENIED |

  Scenario: Handle various file formats
    Given files with different formats: "receipt.pdf", "scan.jpg", "document.png"
    When I generate hashes for all files
    Then each file should produce a unique valid SHA-256 hash
    And all operations should succeed

  Scenario: Process files with zero bytes
    Given a file with zero bytes
    When I generate a hash for the file
    Then I should receive the standard SHA-256 hash for empty content
    And the operation should succeed without error