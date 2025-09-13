Feature: Run Analysis - Initial Implementation
  As a user of the receipt processor
  I want to run receipt analysis on files in the incoming folder
  So that I can process receipts without actual AI integration yet

  Background:
    Given the application is running
    And all required folders exist

  Scenario: Menu displays "Run Analysis" when no receipts.csv exists
    Given no receipts.csv file exists
    When the menu is displayed
    Then it should show "[1] Run Analysis"

  Scenario: Menu displays "Re-run Analysis" when receipts.csv exists
    Given a receipts.csv file exists
    When the menu is displayed
    Then it should show "[1] Re-run Analysis"

  Scenario: No supported files in incoming folder
    Given no files exist in the incoming folder
    When the user selects "Run Analysis"
    Then it should display "No files in incoming folder"
    And return to the main menu after analysis

  Scenario: Process supported files with progress messages
    Given 5 supported files exist in the incoming folder:
      | filename     | type |
      | receipt1.pdf | pdf  |
      | receipt2.jpg | jpg  |
      | receipt3.png | png  |
      | receipt4.jpeg| jpeg |
      | receipt5.pdf | pdf  |
    When the user selects "Run Analysis"
    Then it should display "Processing 1/5: receipt1.pdf"
    And display "Processing 2/5: receipt2.jpg"
    And display "Processing 3/5: receipt3.png"
    And display "Processing 4/5: receipt4.jpeg"
    And display "Processing 5/5: receipt5.pdf"
    And display "Successfully processed 5 files"
    And return to the main menu after analysis

  Scenario: Clear existing receipts.csv when re-running
    Given a receipts.csv file exists with content
    And 2 supported files exist in the incoming folder
    When the user selects "Re-run Analysis"
    Then the receipts.csv file should be deleted
    And processing should continue with progress messages

  Scenario: Clear scanned folder when re-running
    Given the scanned folder contains existing files:
      | filename         |
      | old_receipt1.pdf |
      | old_receipt2.jpg |
    And 1 supported file exists in the incoming folder
    When the user selects "Run Analysis"
    Then the scanned folder should be cleared
    And processing should continue

  Scenario: Only process supported file types
    Given files exist in the incoming folder:
      | filename     | type | supported |
      | receipt.pdf  | pdf  | yes       |
      | receipt.jpg  | jpg  | yes       |
      | receipt.png  | png  | yes       |
      | receipt.jpeg | jpeg | yes       |
      | document.txt | txt  | no        |
      | image.gif    | gif  | no        |
      | readme.md    | md   | no        |
    When the user selects "Run Analysis"
    Then it should process exactly 4 files
    And display progress for only supported files

  Scenario: Process files in sorted order
    Given files exist in the incoming folder:
      | filename        |
      | z_receipt.pdf   |
      | a_receipt.jpg   |
      | m_receipt.png   |
    When the user selects "Run Analysis"
    Then it should display "Processing 1/3: a_receipt.jpg"
    And display "Processing 2/3: m_receipt.png"
    And display "Processing 3/3: z_receipt.pdf"

  Scenario: Handle case-insensitive file extensions
    Given files exist in the incoming folder:
      | filename       |
      | receipt1.PDF   |
      | receipt2.JPG   |
      | receipt3.PNG   |
      | receipt4.JPEG  |
    When the user selects "Run Analysis"
    Then it should process exactly 4 files
    And display progress messages for all files