function ProposeActions(screenshot: image, task: string, active_elements: string) -> string {
  client "Base"
  prompt #"
  {{_.role("user")}}
    You are a UI/UX expert skilled at interacting with websites.

    You are provided with:
    1. A screenshot of the current web application state.
    2. A mapping of active elements in the form [ID] -> [XPATH].
        - Each active element has been overlaid with a colored box and labeled with a numerical [ID] visible on the screenshot.

    Please follow these steps in order:
    1. Analyze the screenshot and mapping to determine the next action required to complete the task.
    2. List all active elements as [ID] -> [Expected Function], describing what each element likely does.
    3. Propose one or more of the following actions in Python format, calling the functions directly as shown below (within a Python code block):
    
    ```python
    click_by_label(label="...") # Click on an element given its label. Arg: label (int)
    type(label="...", content="...") # Type text into an input element given its label. Args: label (int), content (string)
    press(key="...") # Press Playwright keyboard key or character. Args: key (str)
    no_answer() # If none of the colored boxes is the target, use this to request new boxes
    wait() # Wait for 5s to load changes.
    scroll_up() # Scroll to the top by one page height
    scroll_down() # Scroll to the bottom by one page height
    finished() # No action required
    ```

    Pay attention to numerical labels that overlap other active elements; each label corresponds to the box of the same color.
    Output by only following the steps.
    If no GUI element matches the task, use `no_answer()`.
    
    Example output:
    ```python
    # Active elements:
    # 55 -> 选择日期 12-28
    # 56 -> 选择日期 12-29

    click_by_label(label="56")
    ```

    Task description: {{ task }}
    Active elements:
    {{ active_elements }}
    Screenshot: {{ screenshot }}
  "#
}

class CandidateDecision {
  action_type string
  selected_label int?
  input_text string?
  key string?
  confidence float
  reason string
  rejected_labels int[]
  fallback_needed bool
}

function DecideDomRagCandidate(screenshot: image, task: string, active_elements: string, previous_failure: string) -> CandidateDecision {
  client "Base"
  prompt #"
  {{_.role("user")}}

  You are a UI grounding evaluator for web test execution.

  You are provided with:
  1. A screenshot of the current web application state.
  2. A ranked DOM-RAG candidate list.
  3. Each candidate has a numerical label [ID], semantic DOM metadata, context, XPath, selector hint, and rectangle.

  Your job:
  Select the operationally correct executable action for the task using only the candidate list and screenshot.

  Return a structured decision using this schema:
  {{ ctx.output_format }}

  Decision rules:
  - `action_type` must be one of: "click", "type", "press", "select", "scroll_up", "scroll_down", "wait", "finished", "no_answer".
  - Use `selected_label` only when the action needs a DOM candidate: click, type, or select.
  - For type/select actions, include `input_text`.
  - For press actions, include `key`.
  - Set `fallback_needed=true` and `action_type="no_answer"` if no candidate satisfies the task.
  - Do not choose a candidate merely because it is semantically related. It must be the element that should actually receive the action.
  - For table or list rows, first satisfy row constraints from the task, then choose the requested cell/action within that row.
  - For tasks like "first product name", identify the relevant collection and choose the product name/control, not price/status/image/checkbox/menu.
  - For type actions, choose only textbox/searchbox/combobox/input-like candidates.
  - For dropdown option selection, choose an option only if visible; otherwise choose the dropdown/combobox to open first.
  - For press Enter or keyboard-only tasks, return action_type="press" without selected_label.
  - If candidate roles, text, context, row relationship, or column relationship are insufficient, return no_answer.
  - Confidence must be between 0 and 1. Use confidence below 0.70 when the decision is uncertain.
  - Explain briefly why the selected candidate is correct in `reason`.
  - Put plausible but rejected labels in `rejected_labels`.

  Previous failure context:
  {{ previous_failure }}

  Task description: {{ task }}

  Ranked DOM-RAG candidates:
  {{ active_elements }}

  Screenshot:
  {{ screenshot }}
  "#
}
