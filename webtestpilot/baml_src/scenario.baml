class Intent {
  condition string
  step string
  expectation string
}

class Scenario {
  name string
  steps Intent[]
}

function ExtractScenario(description: string) -> Scenario {
  client "openai/gpt-4o"
  prompt #"
    You are an expert in semantic intent extraction for web application testing.

    Your goal is to extract structured interaction intents as a list of (condition, step, expectation) triples from natural language requirements or acceptance criteria.
    - `Condition`: The context under which the step is valid (e.g., user is on page)
    - `Step`: A clear user action (e.g., user clicks Submit)
    - `Expectation`: A testable outcome (e.g., page redirects to dashboard)

    If the information is not provided, fill with <unknown> placeholder.

    {{ ctx.output_format }}

    {{ description }}
  "#
}

