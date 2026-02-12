class History {
    page_id string
    layout string?
    description string?
    prev_action string?
}

template_string FormatHistory(history: History[]) #"
    {% for state in history %}
    {% if loop.index == loop.length %}
    Current State:
    {% else %}
    State (Index {{ loop.index0 }}):
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