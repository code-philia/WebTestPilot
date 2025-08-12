function ProposeActions(screenshot: image, task: string) -> string {
  client "GPT"
  prompt #"
    {{_.role("user")}}
    You are a UI/UX expert skilled at interacting with websites.

    Given a task and current page screenshot, your goal is to propose one or more of the following actions in Python format, calling the functions directly as shown below (within a Python code block):

    ```python
    click(target_description="...") # Click on the element matching the description
    type(target_description="...", content="...") # Focus on the element matching the description and type the specified content
    drag(source_description="...", target_description="...") # Drag from the source element to the target element, both specified by descriptions
    scroll(target_description="...", direction="...") # Focus on the described element (or None to scroll the page) and scroll in the given direction ("up", "down", "left", or "right")
    wait(duration=...) # Wait for the specified duration in milliseconds
    ```

    Do not provide any explanations in your output; only return the Python code block with the required actions.
  
    {{ task }}
    {{ screenshot }}
  "#
}

function ProposeActions_InternVL(screenshot: image, task: string) -> string {
  client "InternVL"
  prompt #"
    {{_.role("system")}}
    You are InternVL, a GUI agent.
    You are given a task and a screenshot of the screen. You need to perform a series of pyautogui actions to complete the task. 
  
    {{_.role("user")}}
    {{ task }}
    {{ screenshot }}
  "#
}

function ProposeActions_UITARS(screenshot: image, task: string) -> string {
  client "UITARS"
  prompt #"
    {{_.role("user")}}
    You are a GUI agent. You are given a task and your action history, with screenshots. You need to perform the next action to complete the task.

    ## Output Format
    ```
    Thought: ...
    Action: ...
    ```

    ## Action Space

    click(point='<point>x1 y1</point>')
    left_double(point='<point>x1 y1</point>')
    right_single(point='<point>x1 y1</point>')
    drag(start_point='<point>x1 y1</point>', end_point='<point>x2 y2</point>')
    hotkey(key='ctrl c') # Split keys with a space and use lowercase. Also, do not use more than 3 keys in one hotkey action.
    type(content='xxx') # Use escape characters \\', \\\", and \\n in content part to ensure we can parse the content in normal python string format. If you want to submit your input, use \\n at the end of content. 
    scroll(point='<point>x1 y1</point>', direction='down or up or right or left') # Show more information on the `direction` side.
    wait() #Sleep for 5s and take a screenshot to check for any changes.
    finished(content='xxx') # Use escape characters \\', \\", and \\n in content part to ensure we can parse the content in normal python string format.


    ## Note
    - Use English in `Thought` part.
    - Write a small plan and finally summarize your next action (with its target element) in one sentence in `Thought` part.

    ## User Instruction
    {{ task }}
    {{ screenshot }}
  "#
}

function LocateUIElement(screenshot: image, description: string) -> string {
  client "UGround"
  prompt #"
    {{_.role("user")}}

    {{ screenshot }}

    Your task is to help the user identify the precise coordinates (x, y) of a specific area/element/object on the screen based on a description.

    - Your response should aim to point to the center or a representative point within the described area/element/object as accurately as possible.
    - If the description is unclear or ambiguous, infer the most relevant area or element based on its likely context or purpose.
    - Your answer should be a single string (x, y) corresponding to the point of the interest.

    Description: {{ description }}

    Answer:
  "#
}