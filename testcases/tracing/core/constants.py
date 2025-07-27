"""
Constants for the tracing system.
"""


class ErrorTypes:
    """XPath extraction error identifiers"""

    LOCATOR_ERROR = "LOCATOR_ERROR"
    ASSERTION_ERROR = "ASSERTION_ERROR"
    PAGE = "PAGE"
    TRACE_ERROR = "TRACE_ERROR"
    EXECUTION_ERROR = "EXECUTION_ERROR"
    NO_PAGE = "NO_PAGE"
    UNKNOWN = "UNKNOWN"


class ActionType:
    """Action type categorization"""

    ACTION = "action"
    ASSERTION = "assertion"
