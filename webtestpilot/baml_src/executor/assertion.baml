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
    - `extract(instruction: str, schema: BaseModel) -> BaseModel`: Extract structured data from the state.
    - `get_element(description: str) -> Element`: Obtain an Element object via visual description.

    ### Element API
    - `extract(instruction: str, schema: BaseModel) -> BaseModel`: Extract structured data from the element.
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