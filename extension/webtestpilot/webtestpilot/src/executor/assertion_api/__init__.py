import re
import sys
import pprint
from typing import Any, Callable, Union, Literal, Optional, List, Set, Dict
from enum import Enum
from uuid import UUID
from datetime import datetime, date

from pydantic import BaseModel, Field, EmailStr, HttpUrl, constr, conint, confloat

from executor.assertion_api.session import Session
from executor.assertion_api.state import State
from executor.assertion_api.element import Element


PRIMITIVE_TYPES = (int, float, str, bool, type(None))


def _run_assertion_with_trace(
    assertion_func: Callable[[Session], Any], session: Session
) -> tuple[bool, str]:
    """
    Executes a given assertion function and captures variable traces
    (only primitives, dicts, lists, or BaseModel instances).
    """
    captured_vars = []

    def filter_locals(locals_dict):
        filtered = {}
        for k, v in locals_dict.items():
            if isinstance(v, PRIMITIVE_TYPES):
                filtered[k] = v
            elif isinstance(v, (dict, list)):
                filtered[k] = v
            elif isinstance(v, BaseModel):
                filtered[k] = v.dict()
        return filtered

    def tracer(frame, event, arg):
        if event == "line" and frame.f_code.co_name == assertion_func.__name__:
            # Filter locals to only include allowed types
            captured_vars.append((frame.f_lineno, filter_locals(frame.f_locals.copy())))
        return tracer

    try:
        sys.settrace(tracer)
        result = assertion_func(session)
        sys.settrace(None)

        if result is True or result is None:
            return True, "Success."

        if isinstance(result, str) and result.strip():
            return False, result

        return (
            False,
            f"Assertion failed without message.\nVariable trace:\n{pprint.pformat(captured_vars)}",
        )

    except AssertionError as ae:
        sys.settrace(None)
        msg = str(ae) if str(ae).strip() else "AssertionError raised without message."
        return False, f"{msg}\nVariable trace:\n{pprint.pformat(captured_vars)}"

    except Exception:
        sys.settrace(None)
        raise


def execute_assertion(response: str, session: Session) -> tuple[bool, str]:
    """
    Executes assertion code blocks extracted from response.

    Looks for code blocks formatted as ```python ... ``` and expects
    either `precondition(session)` or `postcondition(session)`.

    Returns (success, message). On failure, includes variable trace for debugging.
    """
    # Extract python code blocks
    pattern = r"```python\s+([\s\S]*?)```"
    code_blocks = re.findall(pattern, response, re.MULTILINE)
    code = "\n\n".join(code_blocks)

    # Prepare safe globals for exec
    allowed_globals = {
        "__builtins__": __builtins__,
        "Session": Session,
        "State": State,
        "Element": Element,
        # Pydantic
        "BaseModel": BaseModel,
        "Field": Field,
        "EmailStr": EmailStr,
        "HttpUrl": HttpUrl,
        "constr": constr,
        "conint": conint,
        "confloat": confloat,
        # Typing
        "Any": Any,
        "Union": Union,
        "Literal": Literal,
        "Optional": Optional,
        "List": List,
        "Set": Set,
        "Dict": Dict,
        # Enum
        "Enum": Enum,
        # Common value types
        "UUID": UUID,
        "datetime": datetime,
        "date": date,
    }

    local_vars = {}

    # Execute the dynamic code
    exec(code, allowed_globals, local_vars)

    # Find the assertion function
    assertion_func = local_vars.get("precondition") or local_vars.get("postcondition")
    if assertion_func is None or not callable(assertion_func):
        return (
            False,
            "No callable 'precondition' or 'postcondition' function found in generated code.",
        )

    # Run the assertion with variable tracing
    return _run_assertion_with_trace(assertion_func, session)
