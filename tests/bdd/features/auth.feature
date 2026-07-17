Feature: Authentication and library
  As a signed-in user
  I want to access my card library
  So that I can manage my saved designs

  Background:
    Given the piggyback sample catalog is loaded

  Scenario: Demo user opens their library
    Given I am signed in as the demo user
    When I visit "/library/"
    Then I should see "My Card Library"

  Scenario: Demo user views system profile details
    Given I am signed in as the demo user
    When I request "/api/me/details/"
    Then the API response status should be 200
    And the API response should include "demo@piggyback.example"
