class Step {
  condition string
  action string
  expectation string
}

class TestCase {
  name string
  steps Step[]
}

function ExtractTestCase(description: string) -> TestCase {
  client "Base"
  prompt #"
    You are an expert in semantic intent extraction for web application testing.

    Your goal is to extract structured interaction intents as a list of step = (condition, action, expectation) triples from natural language requirements or acceptance criteria.
    - `Condition`: The context under which the step is valid (e.g., user is on page)
    - `Action`: A clear user action (e.g., user clicks Submit)
    - `Expectation`: A testable outcome (e.g., page redirects to dashboard)

    If the information is not provided, fill with <unknown> placeholder.

    {{ ctx.output_format }}

    {{ description }}
  "#
}

function ImplicitGeneration(testcase: TestCase) -> TestCase {
  client "Base"
  prompt #"
    You are an expert in semantic intent understanding for web application testing.
    Fill in the <unknown> blanks by inferring contextual information from other steps.
    Return in the same format.

    {{ testcase }}
  "#
}