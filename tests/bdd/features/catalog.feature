Feature: Card catalog
  As a visitor
  I want to browse occasion cards
  So that I can find a design to personalise

  Background:
    Given the piggyback sample catalog is loaded

  Scenario: Browse the card shop
    When I visit "/catalog/"
    Then I should see "Card Shop"
    And I should see a card template

  Scenario: Filter catalog via API
    When I request "/api/templates/"
    Then the API response status should be 200
    And the API response should include templates
