Feature: Add items to the shopping cart

  As a customer
  I want to add items to my cart
  So that I can purchase them later

  Scenario: Add a single item to the cart
    Given I am on the product page
    When I click a product to view details
    And I add the product to the shopping cart
    Then the product count on the shopping cart icon should increase