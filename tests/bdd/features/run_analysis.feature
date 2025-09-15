Feature: Run Analysis - Initial Implementation
  As a user of the receipt processor
  I want to run analysis on receipt files
  So that I can process receipts with clear progress feedback

  Background:
    Given the application environment is properly configured
    And required folders exist

  Scenario: Menu shows "Run Analysis" when receipts.csv doesn't exist
    Given no receipts.csv file exists
    When the application displays the menu
    Then it should show "[1] Run Analysis"

  Scenario: Menu shows "Re-run Analysis" when receipts.csv exists
    Given a receipts.csv file exists
    When the application displays the menu
    Then it should show "[1] Re-run Analysis"

  Scenario: Run Analysis with no supported files
    Given no supported files exist in the incoming folder
    When the user selects "Run Analysis"
    Then it should display "No files in {incoming} folder"
    And return to the main menu

  Scenario: Run Analysis with supported files
    Given 3 supported files exist in the incoming folder:
      | filename      |
      | receipt1.pdf  |
      | receipt2.jpg  |
      | receipt3.png  |
    When the user selects "Run Analysis"
    Then it should display progress messages:
      | message                    |
      | Processing 1/3: receipt1.pdf |
      | Processing 2/3: receipt2.jpg |
      | Processing 3/3: receipt3.png |
    And display "TODO: Implement actual processing"
    And return to the main menu

  Scenario: Re-run Analysis clears existing data
    Given a receipts.csv file exists with data
    And the scanned folder contains files:
      | filename         |
      | old_receipt.jpg  |
      | old_receipt.pdf  |
    And 2 supported files exist in the incoming folder:
      | filename      |
      | new1.pdf      |
      | new2.jpg      |
    When the user selects "Re-run Analysis"
    Then the receipts.csv file should be removed
    And the scanned folder should be cleared
    And it should display progress messages:
      | message               |
      | Processing 1/2: new1.pdf |
      | Processing 2/2: new2.jpg |
    And display "TODO: Implement actual processing"

  Scenario: Run Analysis handles mixed file types
    Given files exist in the incoming folder:
      | filename          | supported |
      | receipt.pdf       | yes       |
      | image.jpg         | yes       |
      | document.txt      | no        |
      | photo.png         | yes       |
      | spreadsheet.xlsx  | no        |
    When the user selects "Run Analysis"
    Then it should display progress messages for 3 supported files only
    And display "TODO: Implement actual processing"

  Scenario: Run Analysis with unsupported files only
    Given files exist in the incoming folder:
      | filename          |
      | document.txt      |
      | spreadsheet.xlsx  |
      | readme.md         |
    When the user selects "Run Analysis"
    Then it should display "No files in {incoming} folder"
    And return to the main menu