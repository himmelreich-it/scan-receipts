Feature: TUI Interface with System Status and Menu
  As a user of the receipt processor
  I want a TUI showing system status and menu options
  So that I can see receipt counts and navigate features

  Scenario: Configuration validation fails with missing environment variables
    Given no environment variables are set
    When the application starts
    Then it should fail with "Missing environment variables"
    And list all 6 missing variables

  Scenario: Successful startup with all environment variables
    Given all required environment variables are set
    When the application starts
    Then all 4 folders should be created if missing
    And the TUI should display successfully

  Scenario: Display system status with no data
    Given the application is running
    And no receipt files exist
    And no staging CSV exists
    When the status is displayed
    Then it should show configured folder paths
    And show "Input Folder: 0 files"
    And show "Failed Folder: 0 files"
    And show "Staging: No staging data"

  Scenario: Display system status with receipt files
    Given the application is running
    And 15 files exist in the incoming folder
    And 2 files exist in the failed folder
    And staging CSV contains 8 entries
    When the status is displayed
    Then it should show configured folder paths
    And show "Input Folder: 15 files"
    And show "Failed Folder: 2 files"
    And show staging file with "8 entries"

  Scenario: Navigate menu options 1-3
    Given the application is running
    When the user selects option 1
    Then it should display "Not yet implemented..."
    And return to the menu
    When the user selects option 2
    Then it should display "Not yet implemented..."
    And return to the menu
    When the user selects option 3
    Then it should display "Not yet implemented..."
    And return to the menu

  Scenario: Exit application with option 4
    Given the application is running
    When the user selects option 4
    Then it should display "Goodbye"
    And exit the application

  Scenario: Handle invalid menu input
    Given the application is running
    When the user enters invalid input "5"
    Then it should display error message
    And re-prompt for input
    When the user enters invalid input "abc"
    Then it should display error message
    And re-prompt for input

  Scenario: Handle Ctrl+C gracefully
    Given the application is running
    When the user presses Ctrl+C
    Then it should display "Goodbye"
    And exit cleanly

  Scenario: Display configured folder paths on startup
    Given the application is running with test configuration
    When the status is displayed
    Then it should show all 6 configured paths as absolute paths
    And paths should have short labels
    And paths should be displayed above file counts