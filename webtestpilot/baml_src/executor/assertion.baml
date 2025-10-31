class Feedback {
    response string
    reason string
}

class History {
    page_id string
    layout string?
    description string?
    prev_action string?
}

template_string Specification() #"
    # API Specification

    ### Session API
    - `history -> list[State]`: Chronological sequence of all captured states in the current test session.

    ### State API
    - `page_id -> str`: Canonical identifier for logical page/state identity.
    - `title -> str`: Browser tab's visible title.
    - `url -> str`: Current browser URL.
    - `extract(instruction: str, schema: Type[BaseModel]) -> Type[BaseModel]`: Extract structured data from the state. `schema` should be a class inherited from `BaseModel`, NOT `BaseModel` itself.

    Important requirements for `schema`:
      - `schema` must be a concrete subclass of `BaseModel` (a class that inherits from `BaseModel` and defines fields). Do NOT pass `BaseModel` itself.
      - The subclass should declare the expected fields and their types. Example:
        ```python
        class User(BaseModel):
            id: int
            name: str
        ```
      - The extractor will populate and return an instance of the provided subclass (or data matching its schema). Provide only class objects, not instances or the `BaseModel` base class.
      - If you provide a schema that is not a subclass of `BaseModel` or omits required fields, extraction will fail. Ensure the schema accurately reflects the structure you expect to extract from the state.

    Examples:
    - Correct: `extract("get user", schema=User)` where `User` inherits from `BaseModel`.
    - Incorrect: `extract("get user", schema=BaseModel)` (do not pass the base type).
"#

template_string FormatHistory(history: History[]) #"
    {% for state in history %}
    {% if loop.index == loop.length %}
    Current State:
    {% else %}
    State ({{ loop.index0 }}):
    {% endif %}
        Page: {{ state.page_id or 'Unknown' }}
    {% if state.description %}
        Description: {{ state.description }}
    {% endif %}
    {% if state.layout %}
        Layout: {{ state.layout }}
    {% endif %}
    {% if loop.index < loop.length %}
        Action: {{ history[loop.index].prev_action }}
    {% endif %}
    {% endfor %}
"#

template_string FormatFeedback(feedback: Feedback[]) #"
    {% if feedback %}
    {% for f in feedback %}
    {{ _.role("user") }}
    # Feedback

    Your previous assertion(s) might be incorrect:

    {{ f.response }}

    Reason: {{ f.reason }}

    If you insist that it is correct, please output the same thing
    Otherwise, modify the assertion
    {% endfor %}
    {% endif %}
"#