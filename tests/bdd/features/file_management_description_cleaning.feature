Feature: Description Cleaning and Filesystem Safety
  As a receipt processing system
  I want to clean file descriptions for filesystem compatibility
  So that filenames are safe across different operating systems

  Scenario Outline: Convert non-latin characters
    Given a description with text "<input_text>"
    When I clean the description
    Then the result should be "<expected_output>"
    
    Examples:
      | input_text        | expected_output |
      | Café André        | Cafe Andre      |
      | Müller & Söhne    | Muller & Sohne  |
      | Niño's Restaurant | Nino's Restaurant |
      | Škoda Auto        | Skoda Auto      |
      | Zürich Bank       | Zurich Bank     |

  Scenario Outline: Replace unsafe filesystem characters
    Given a description with text "<input_text>"  
    When I clean the description
    Then the result should be "<expected_output>"
    
    Examples:
      | input_text      | expected_output |
      | File/Name       | File_Name       |
      | Test:File       | Test_File       |
      | Name<>File      | Name__File      |
      | Path\File       | Path_File       |
      | Name*File       | Name_File       |
      | File?Name       | File_Name       |
      | "Quoted"        | _Quoted_        |
      | Name\|File      | Name_File       |

  Scenario: Truncate long descriptions
    Given a description "This is a very long description that exceeds fifteen characters"
    When I clean the description
    Then the result should be exactly 15 characters long
    And it should be "This is a very "

  Scenario: Trim whitespace before processing
    Given a description "  test description  "
    When I clean the description
    Then the result should be "test descriptio"
    And it should not have leading or trailing spaces

  Scenario: Collapse multiple spaces and underscores
    Given a description "test    multiple   spaces"
    When I clean the description
    Then the result should be "test_multiple_"
    And consecutive spaces should be collapsed to single underscores

  Scenario Outline: Handle edge cases
    Given a description with text "<input_text>"
    When I clean the description  
    Then the result should be "<expected_output>"
    
    Examples:
      | input_text | expected_output |
      | ""         | unknown         |
      | "   "      | unknown         |
      | "_____"    | document        |
      | "  test  " | test            |
      | "a"        | a               |
      | "12345"    | 12345           |

  Scenario: Combine multiple cleaning rules
    Given a description "  Café/André: Müller's Store!!!  "
    When I clean the description
    Then the result should be "Cafe_Andre_ Mul"
    And it should be exactly 15 characters
    And it should contain only safe filesystem characters

  Scenario: Handle descriptions with only unsafe characters
    Given a description "///***???"
    When I clean the description
    Then the result should be "document"
    And it should use the fallback for descriptions that become only underscores

  Scenario: Preserve numbers and common punctuation
    Given a description "Store #123 - Sale!"
    When I clean the description
    Then the result should be "Store #123 - Sa"
    And numbers and safe punctuation should be preserved