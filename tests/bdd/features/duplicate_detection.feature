Feature: Duplicate Detection and Management
  As a receipt processing system
  I want to detect and skip duplicate files using comprehensive hash comparison
  So that files are not reprocessed and API costs are minimized

  Background:
    Given a receipt processing system is initialized
    And an imported folder exists with processed receipts
    And a failed folder exists with failed receipts
    And an input folder exists with receipts to process

  Scenario: Initialize imported folder hash database at session start
    Given the imported folder contains existing processed receipt files:
      | filename        | file_content  |
      | receipt1.pdf    | binary_data_1 |
      | receipt2.jpg    | binary_data_2 |
      | receipt3.png    | binary_data_3 |
    When the processing session starts
    Then the system scans the imported folder
    And generates SHA-256 hashes for all existing files
    And stores the hash database in memory
    And logs "Scanned imported folder: found 3 existing files for duplicate detection"

  Scenario: Skip duplicate file that matches imported folder
    Given the imported folder contains a file "original_receipt.pdf" with hash "abc123hash"
    And the hash database is initialized with imported folder hashes
    When processing a file "duplicate_receipt.pdf" with the same hash "abc123hash"
    Then the system detects the file as a duplicate
    And skips processing without sending to API
    And logs "Duplicate file skipped: duplicate_receipt.pdf (matches file in imported folder)"
    And continues processing the next file
    And does not create a CSV entry for the duplicate

  Scenario: Skip duplicate file that matches current session
    Given the current processing session has already processed "first_file.pdf" with hash "def456hash"
    When processing another file "second_file.pdf" with the same hash "def456hash"
    Then the system detects the file as a duplicate within the session
    And skips processing without sending to API
    And logs "Duplicate file skipped: second_file.pdf (matches first_file.pdf in current session)"
    And continues processing the next file
    And does not create a CSV entry for the duplicate

  Scenario: Process file from failed folder (no duplicate check against failed folder)
    Given the failed folder contains a file "failed_receipt.pdf" with hash "ghi789hash"
    And the imported folder hash database does not contain "ghi789hash"
    And the current session has not processed "ghi789hash"
    When processing a file "retry_receipt.pdf" with hash "ghi789hash" from the input folder
    Then the system does not check the failed folder for duplicates
    And processes the file normally
    And sends the file to the API for extraction
    And allows retry of previously failed files

  Scenario: Generate and store file hash for future duplicate comparison
    Given a file "new_receipt.pdf" is being processed
    When the system generates the file hash
    Then it calculates SHA-256 hash of the binary file content
    And stores the hash with the extracted data
    And adds the hash to the current session tracking
    And uses the hash for future duplicate comparisons within the session

  Scenario Outline: Hash generation for different file types
    Given a receipt file "<filename>" of type "<file_type>"
    When the system generates the file hash
    Then it successfully calculates SHA-256 hash regardless of file type
    And the hash is stored for duplicate detection

    Examples:
      | filename        | file_type |
      | receipt.pdf     | PDF       |
      | receipt.jpg     | JPEG      |
      | receipt.jpeg    | JPEG      |
      | receipt.png     | PNG       |

  Scenario: Continue processing after duplicate detection
    Given multiple files in the input folder:
      | filename        | hash        | is_duplicate |
      | file1.pdf       | hash1       | false        |
      | file2.jpg       | hash2       | true         |
      | file3.png       | hash3       | false        |
    When the system processes the files in sequence
    Then it processes file1.pdf normally
    And skips file2.jpg as duplicate without interruption
    And continues to process file3.png normally
    And completes the entire batch processing workflow

  Scenario: Handle hash generation failure
    Given a file "corrupted_receipt.pdf" that cannot be read properly
    When the system attempts to generate the file hash
    Then hash generation fails with an error
    And the system logs "Hash generation failed for corrupted_receipt.pdf"
    And moves the file to failed folder with error log "Hash generation failure"
    And continues processing the next file

  Scenario: Handle hash comparison error
    Given the hash database is corrupted or inaccessible
    When the system attempts to compare a file hash for duplicate detection
    Then hash comparison fails with an error
    And the system logs "Hash comparison error during duplicate detection"
    And continues processing the file as non-duplicate
    And reports the error for investigation

  Scenario: Handle imported folder access error at session start
    Given the imported folder is inaccessible due to permissions or missing directory
    When the processing session starts
    Then the system fails to scan the imported folder
    And logs "Imported folder access error: cannot initialize duplicate detection"
    And initializes with empty hash database
    And continues processing without imported folder duplicate detection

  Scenario: Handle logging failure during duplicate detection
    Given the logging system is unavailable or failing
    And a duplicate file is detected
    When the system attempts to log the duplicate detection
    Then logging fails but duplicate detection continues
    And the file is still skipped as duplicate
    And processing continues with the next file
    And duplicate detection functionality remains operational