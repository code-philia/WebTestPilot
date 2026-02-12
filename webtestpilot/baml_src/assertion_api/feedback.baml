class Feedback {
    response string
    reason string
}

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