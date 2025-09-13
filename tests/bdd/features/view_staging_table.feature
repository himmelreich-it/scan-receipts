Feature: View Staging Table functionality
  As a user of the receipt processor
  I want to view the staging table contents
  So that I can see all processed receipts before importing to XLSX

  Scenario: View staging table when CSV file does not exist
    Given the application is running
    And the receipts.csv file does not exist
    When the user selects "View Staging Table"
    Then it should display "receipts.csv does not exist"
    And return to the main menu

  Scenario: View staging table when CSV file is empty
    Given the application is running
    And the receipts.csv file exists but is empty
    When the user selects "View Staging Table"
    Then it should display "receipts.csv is empty"
    And return to the main menu

  Scenario: View staging table with receipt data
    Given the application is running
    And the receipts.csv file exists with data:
      | Amount | Tax  | TaxPercentage | Description    | Currency | Date       | Confidence | Hash    | DoneFilename    |
      | 100.00 | 10.00| 10           | Coffee Receipt | USD      | 2024-01-01 | 0.95       | abc123  | receipt_001.pdf |
      | 200.00 | 20.00| 10           | Lunch Receipt  | EUR      | 2024-01-02 | 0.90       | def456  | receipt_002.pdf |
    When the user selects "View Staging Table"
    Then it should display a formatted table with headers:
      | Amount | Tax | TaxPercentage | Description | Currency | Date | Confidence | Hash | DoneFilename |
    And the table should contain the receipt data
    And it should show "Total entries: 2"
    And return to the main menu

  Scenario: View staging table with large hash values
    Given the application is running
    And the receipts.csv file exists with data:
      | Amount | Tax  | TaxPercentage | Description    | Currency | Date       | Confidence | Hash             | DoneFilename    |
      | 50.00  | 5.00 | 10           | Store Receipt  | USD      | 2024-01-03 | 0.99       | abcdef123456789  | receipt_003.pdf |
    When the user selects "View Staging Table"
    Then it should display a formatted table
    And the Hash column should show "abcdef12..." for long hashes
    And return to the main menu

  Scenario: Handle CSV parsing errors gracefully
    Given the application is running
    And the receipts.csv file exists but is corrupted
    When the user selects "View Staging Table"
    Then it should display "Error reading staging table."
    And return to the main menu