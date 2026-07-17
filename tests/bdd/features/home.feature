Feature: Home page
  As a visitor
  I want to see the Piggyback landing page
  So that I understand what the product offers

  Scenario: View the home page
    Given the piggyback sample catalog is loaded
    When I visit "/"
    Then I should see "Send joy on"
    And I should see "Browse Cards"
