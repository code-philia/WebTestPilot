function GeneratePlaywrightCode(
  screenshot: image,
  task: string,
  page_context: string,
  dom_context: string,
  previous_failure: string,
  attempt: int
) -> string {
  client "Base"
  prompt #"
  {{_.role("user")}}
    You are a UI/UX expert skilled at interacting with websites using Playwright.

    You are provided with:
    1. A screenshot of the current web application state.
    2. A short page context containing the current URL, title, and viewport.
    3. A compact list of visible interactive DOM elements.
    4. The previous execution failure, if this is a retry.

    Please generate a short Python Playwright sync action body that performs exactly the requested task on the current page.
    The caller will execute your code in an existing browser page.

    Runtime variables available to your code:
    - page: playwright.sync_api.Page for the current browser tab.
    - helpers.log(message): append a diagnostic message to the execution trace.
    - helpers.wait_for_stable(timeout_ms): wait briefly and let the DOM settle.
    - re and json modules are available.

    Output only a JSON object. Do not output markdown or explanatory text.

    JSON schema:
    {
      "output_type": "code",
      "code": "page.get_by_role('button', name='Save').click(timeout=3000)",
      "rationale": "Short reason for the locator and action strategy.",
      "expected_effect": "The expected immediate page effect.",
      "error_type": null,
      "target": null,
      "message": null,
      "evidence": {}
    }

    The `output_type` field must be either:
    - "code": code is a runnable Python Playwright sync action body.
    - "error": the target UI is absent, disabled, unsafe, or the evidence is insufficient. In this case code must be an empty string and error_type, target, message, and evidence must explain the issue.

    Please follow these rules:
    - Generate synchronous Python Playwright code. Do not use await.
    - Do not use imports, file access, shell commands, environment variables, network clients, eval, exec, loops, or browser creation.
    - Prefer role, label, placeholder, text, visible locator, or stable DOM attributes from the DOM context.
    - Every Playwright action must use a short timeout, normally 3000 to 5000 ms.
    - Do not use coordinates unless the DOM evidence is not enough and the screenshot clearly identifies the target.
    - Do not force-click disabled controls.
    - Do not invent selectors or labels not supported by page_context, dom_context, or screenshot.
    - If a prior attempt failed, revise the locator or action instead of repeating the same code.
    - The code should perform the current task only. Do not add final business assertions; WebTestPilot's assertion API verifies postconditions separately.
    - After a page-changing action, call helpers.wait_for_stable(500) or helpers.wait_for_stable(1000).

    Example valid code string:
    "page.get_by_role('button', name='Submit').click(timeout=3000)\nhelpers.wait_for_stable(500)"

    Example structured error:
    {
      "output_type": "error",
      "code": "",
      "rationale": "The requested Submit button is not present in the visible DOM candidates.",
      "expected_effect": "The form would be submitted.",
      "error_type": "target_ui_unavailable",
      "target": "Submit button",
      "message": "No visible enabled control matching Submit is available on the current page.",
      "evidence": {"candidate_texts": ["Cancel", "Search"]}
    }

    Task:
    {{ task }}

    Attempt:
    {{ attempt }}

    Page context:
    {{ page_context }}

    Visible interactive DOM context:
    {{ dom_context }}

    Previous failure, if any:
    {{ previous_failure }}

    Screenshot:
    {{ screenshot }}
  "#
}
