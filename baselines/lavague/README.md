This baseline is adapted from the official LaVague guide: [Quick tour - LaVague](https://www.google.com/search?q=https://lavague.ai/docs/qa).

# LaVague QA Usage Example

This document introduces LaVague QA, which serves as a standard baseline model for our tests.

The following example demonstrates how the model converts a Gherkin feature file (`.feature`) into executable Pytest code and covers its basic configuration and usage.

All commands in this document assume they are run from the root directory of the project.

## 1. Environment Setup (Important)

You must configure your OpenAI API key before running any examples. LaVague utilizes a Large Language Model (LLM) to understand instructions and generate code, which requires this key for authentication.

#### Get Your API Key

First, obtain your API key from the official OpenAI website: [platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)

#### Set the Environment Variable

Next, set the environment variable in your terminal. Please replace `sk-...` with your actual key.

- **Windows (PowerShell):**

  ```powershell
  $env:OPENAI_API_KEY = "sk-..."
  ```

- **Windows (CMD):**

  ```cmd
  set OPENAI_API_KEY=sk-...
  ```

- **macOS / Linux:**

  ```bash
  export OPENAI_API_KEY="sk-..."
  ```

**Note:** This setting is temporary and only applies to the current terminal session. You will need to set it again if you open a new terminal window.

## 2. Example Test Case

The following LaVague QA test case is provided as a baseline. While the process is end-to-end runnable, the test code it generates is known to be flawed. This makes it a suitable example for demonstrating the baseline's capabilities and limitations

### Sauce Labs - Testing Shopping Cart Functionality

- **目的**：To test if the add-to-cart functionality works as expected.

#### Feature File (`test.feature`)

```gherkin
Feature: Add items to the shopping cart

  As a customer
  I want to add items to my cart
  So that I can purchase them later

  Scenario: Add a single item to the cart
    Given I am on the product page
    When I click a product to view details
    And I add the product to the shopping cart
    Then the product count on the shopping cart icon should increase
```

#### Generate Pytest Code

```bash
 lavague-qa --url https://www.saucedemo.com/v1/inventory.html  --feature ./test.feature
```

#### Run the Test Code with Pytest

```bash
 pytest .\generated_tests\test.py 
```

