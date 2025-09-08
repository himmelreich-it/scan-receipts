Feature: Core Receipt Analysis and Data Extraction
  As a receipt processing system
  I want to analyze receipt files using Claude API to extract structured financial data
  So that I can provide accurate receipt data with validation and error handling

  Background:
    Given the receipt processing system is initialized
    And the Claude Sonnet 4 API is available
    And the failed folder exists for error handling

  Scenario: Successfully extract data from valid PDF receipt
    Given a valid PDF receipt file "receipt_001.pdf"
    When the system processes the receipt file
    Then the Claude Sonnet 4 API should be called with the file
    And the system should extract amount, tax, tax_percentage, description, currency, date, and confidence fields
    And the structured JSON response should contain all required fields
    And the console should display progress message with filename and confidence score
    And a file hash should be generated for duplicate detection

  Scenario: Successfully extract data from valid JPG receipt
    Given a valid JPG receipt file "receipt_002.jpg"
    When the system processes the receipt file
    Then the Claude Sonnet 4 API should be called with the file
    And the system should extract amount, tax, tax_percentage, description, currency, date, and confidence fields
    And the structured JSON response should contain all required fields
    And the console should display progress message with filename and confidence score
    And a file hash should be generated for duplicate detection

  Scenario: Successfully extract data from valid PNG receipt
    Given a valid PNG receipt file "receipt_003.png"
    When the system processes the receipt file
    Then the Claude Sonnet 4 API should be called with the file
    And the system should extract amount, tax, tax_percentage, description, currency, date, and confidence fields
    And the structured JSON response should contain all required fields
    And the console should display progress message with filename and confidence score
    And a file hash should be generated for duplicate detection

  Scenario: Handle multiple dates with purchase date priority
    Given a receipt file "receipt_multiple_dates.pdf" with both purchase date and printed date
    When the system processes the receipt file
    Then the system should prioritize purchase date over printed date
    And the extracted date should be the purchase date
    And the structured JSON response should contain the purchase date

  Scenario: Continue processing with low confidence score
    Given a receipt file "receipt_low_confidence.pdf" that results in low confidence score
    When the system processes the receipt file
    Then the system should continue processing without additional validation
    And the structured JSON response should contain all required fields
    And the console should display progress message with filename and confidence score

  Scenario: Accept any currency code found by AI
    Given a receipt file "receipt_foreign_currency.pdf" with non-standard currency
    When the system processes the receipt file
    Then the system should assume single currency per receipt
    And the system should accept any currency code found by AI
    And the structured JSON response should contain the detected currency

  Scenario Outline: Date validation - reject future dates
    Given a receipt file "<filename>" with extracted date "<extracted_date>"
    When the system processes the receipt file
    And the extracted date is in the future
    Then the system should move the file to failed folder
    And the system should create error log "Date validation failed: future date"
    And processing should continue with next file

    Examples:
      | filename           | extracted_date |
      | future_receipt.pdf | 2026-12-31     |
      | tomorrow.jpg       | 2025-09-09     |

  Scenario Outline: Date validation - reject dates older than 1 year
    Given a receipt file "<filename>" with extracted date "<extracted_date>"
    When the system processes the receipt file
    And the extracted date is older than 1 year
    Then the system should move the file to failed folder
    And the system should create error log "Date validation failed: date too old"
    And processing should continue with next file

    Examples:
      | filename          | extracted_date |
      | old_receipt.pdf   | 2023-01-01     |
      | ancient_receipt.jpg | 2022-06-15   |

  Scenario: Handle API rate limiting
    Given a receipt file "receipt_rate_limit.pdf"
    When the system processes the receipt file
    And the Claude API returns rate limit error
    Then the system should handle API rate limiting appropriately
    And processing should retry or continue based on rate limiting strategy

  Scenario: Handle API network timeout
    Given a receipt file "receipt_timeout.pdf"
    When the system processes the receipt file
    And the Claude API request times out
    Then the system should move the file to failed folder
    And the system should create error log "API failure: network timeout"
    And processing should continue with next file

  Scenario: Handle malformed JSON response
    Given a receipt file "receipt_malformed.pdf"
    When the system processes the receipt file
    And the Claude API returns malformed JSON
    Then the system should move the file to failed folder
    And the system should create error log "JSON parsing failed: malformed response"
    And processing should continue with next file

  Scenario: Handle missing required fields in API response
    Given a receipt file "receipt_incomplete.pdf"
    When the system processes the receipt file
    And the Claude API response is missing required fields
    Then the system should move the file to failed folder
    And the system should create error log with missing field details
    And processing should continue with next file

  Scenario: Handle API service unavailable
    Given a receipt file "receipt_service_down.pdf"
    When the system processes the receipt file
    And the Claude API service is unavailable
    Then the system should move the file to failed folder
    And the system should create error log "API failure: service unavailable"
    And processing should continue with next file

  Scenario: Validate JSON schema on successful API response
    Given a receipt file "receipt_schema_test.pdf"
    When the system processes the receipt file
    And the Claude API returns valid JSON response
    Then the system should validate all required fields are present
    And the system should validate field types match expected schema
    And the confidence score should be integer between 0-100
    And the amount and tax should be valid float values

  Scenario: Generate file hash for duplicate detection
    Given a receipt file "receipt_hash_test.pdf"
    When the system processes the receipt file
    Then the system should generate a file hash for duplicate detection
    And the file hash should be stored with extracted data
    And the file hash should be available for session duplicate comparison