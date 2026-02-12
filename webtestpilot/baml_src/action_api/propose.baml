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