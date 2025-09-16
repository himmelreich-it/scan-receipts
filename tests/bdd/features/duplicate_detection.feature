Feature: Duplicate Detection During Analysis
  As a user
  I want the system to skip duplicate files during analysis
  So that I avoid unnecessary API calls and processing time

  Background:
    Given the system is initialized with test folders
    And the incoming folder contains some receipt files
    And the CSV staging file is cleared

  Scenario: Skip file that exists in imported folder
    Given a receipt file "receipt1.pdf" exists in the incoming folder
    And an identical file "existing1.pdf" exists in the imported folder
    When I run the receipt analysis
    Then the system should detect the duplicate
    And the file should be skipped with a message about "imported" folder
    And no AI analysis should be performed for this file

  Scenario: Skip duplicate files within same incoming batch
    Given a receipt file "receipt2.pdf" exists in the incoming folder
    And an identical file "receipt2_copy.pdf" exists in the incoming folder
    And an identical file "existing2.pdf" exists in the imported folder
    When I run the receipt analysis
    Then the system should detect the duplicate
    And the file should be skipped with a message about "imported" folder
    And no AI analysis should be performed for this file

  Scenario: Process unique file normally
    Given a receipt file "unique.pdf" exists in the incoming folder
    And no duplicate exists in imported or scanned folders
    When I run the receipt analysis
    Then the system should not detect any duplicates
    And the file should proceed to AI analysis

  Scenario: Handle hash calculation error gracefully
    Given a corrupted file "corrupted.pdf" exists in the incoming folder
    When I run the receipt analysis
    Then the system should display a hash calculation error
    And the system should continue processing remaining files

  Scenario: Process mix of duplicate and unique files
    Given multiple files exist in the incoming folder:
      | filename      | has_duplicate | duplicate_location |
      | receipt1.pdf  | yes           | imported           |
      | receipt2.pdf  | yes           | scanned            |
      | unique1.pdf   | no            |                    |
      | unique2.pdf   | no            |                    |
    When I run the receipt analysis
    Then the system should show a summary:
      | processed | duplicates_skipped | errors |
      | 2         | 2                  | 0      |

  Scenario: Continue processing after hash calculation errors
    Given multiple files exist in the incoming folder:
      | filename      | type        |
      | valid1.pdf    | valid       |
      | corrupted.pdf | corrupted   |
      | valid2.pdf    | valid       |
    When I run the receipt analysis
    Then the system should show a summary with:
      | processed | duplicates_skipped | errors |
      | 2         | 0                  | 1      |