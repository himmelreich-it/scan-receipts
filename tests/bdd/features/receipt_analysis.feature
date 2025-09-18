Feature: Receipt Analysis with Anthropic AI
  As a business owner
  I want the system to automatically extract receipt data using Anthropic's Claude API
  So that I can review structured data before importing it to my expense tracker

  Background:
    Given the system is configured with test folders
    And the incoming folder contains receipt files
    And the duplicate detection service is available

  Scenario: Successfully analyze a single receipt
    Given a test receipt file "coffee_receipt.jpg" exists in the incoming folder
    And the AI service returns valid receipt data
    When I run the AI receipt analysis
    Then the receipt should be analyzed successfully
    And the extracted data should be written to the CSV file
    And the receipt file should be copied to the scanned folder
    And the processing summary should show 1 processed file

  Scenario: Handle AI extraction failure gracefully
    Given a test receipt file "corrupted_receipt.pdf" exists in the incoming folder
    And the AI service fails with an error
    When I run the AI receipt analysis
    Then the receipt processing should fail
    And the receipt file should be copied to the failed folder
    And an error log should be created in the failed folder
    And the processing summary should show 1 failed file

  Scenario: Skip duplicate files during analysis
    Given a test receipt file "duplicate_receipt.png" exists in the incoming folder
    And an identical file already exists in the scanned folder
    When I run the AI receipt analysis
    Then the duplicate should be detected and skipped
    And no AI analysis should be performed
    And the file should remain in the incoming folder
    And the processing summary should show 1 duplicate skipped

  Scenario: Process multiple receipts with mixed results
    Given receipt files exist in the incoming folder:
      | filename          | type      |
      | good_receipt.jpg  | valid     |
      | bad_receipt.png   | invalid   |
      | dup_receipt.pdf   | duplicate |
    When I run the AI receipt analysis
    Then the processing should complete with mixed results
    And the CSV should contain data for successful receipts
    And failed receipts should be in the failed folder
    And duplicate receipts should be skipped
    And the final summary should show all processing results

  Scenario: Display extracted receipt data in real-time
    Given a test receipt file "detailed_receipt.jpg" exists in the incoming folder
    And the AI service returns detailed receipt data with:
      | field           | value        |
      | amount          | 42.75        |
      | tax             | 3.42         |
      | tax_percentage  | 8.5          |
      | description     | Restaurant   |
      | currency        | USD          |
      | date            | 2024-03-15   |
      | confidence      | 92           |
    When I run the AI receipt analysis
    Then the extracted data should be displayed during processing
    And the success message should show "42.75 USD - Restaurant (92% confidence)"

  Scenario: Handle missing required fields in AI response
    Given a test receipt file "incomplete_receipt.jpg" exists in the incoming folder
    And the AI service returns incomplete data missing required fields
    When I run the AI receipt analysis
    Then the processing should fail due to validation errors
    And the receipt should be moved to the failed folder
    And the error log should indicate missing required fields

  Scenario: Show CSV contents and failed items in final summary
    Given multiple receipt files have been processed
    And some receipts were successful and others failed
    When the analysis is complete
    Then the final summary should display CSV contents
    And the summary should list all failed files
    And the summary should show accurate counts for each category

  Scenario: Handle file hash calculation failure
    Given a test receipt file "unhashable_receipt.jpg" exists in the incoming folder
    And the file hash calculation fails
    When I run the AI receipt analysis
    Then the processing should fail gracefully
    And the receipt should be moved to the failed folder
    And the error should be logged appropriately

  Scenario: Process receipts with special characters in filenames
    Given receipt files with special characters exist:
      | filename              |
      | café_receipt_€50.jpg  |
      | receipt with spaces.png |
      | receipt-with_symbols!@#.pdf |
    And the AI service returns valid data for all files
    When I run the AI receipt analysis
    Then all receipts should be processed successfully
    And the CSV should contain entries for all files
    And all files should be copied to the scanned folder

  Scenario: Validate CSV format and headers
    Given receipt files exist in the incoming folder
    And the AI service returns valid receipt data
    When I run the AI receipt analysis
    Then the CSV file should be created with correct headers
    And the headers should match: "Amount,Tax,TaxPercentage,Description,Currency,Date,Confidence,Hash,DoneFilename"
    And the data rows should follow the correct format
    And file hashes should be included in the CSV