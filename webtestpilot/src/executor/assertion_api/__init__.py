import re
from executor.assertion_api.session import Session
from executor.assertion_api.state import State
from executor.assertion_api.element import Element


def execute_assertion(response: str, session: Session) -> tuple[bool, str]:
    """
    Execute assertion code string defining `def assertion(session: Session)`.

    - If assertion passes (returns True or does not raise), return True.
    - If assertion fails (returns False or AssertionError), return failure message.
    - If compile or exec error, raise exception.
    """
    pattern = r"```python\s+([\s\S]*?)```"
    code_blocks = re.findall(pattern, response, re.MULTILINE)
    code = "\n\n".join(code_blocks)

    local_vars = {}
    allowed_globals = {
        "__builtins__": __builtins__,
        "Session": Session,
        "State": State,
        "Element": Element,
    }

    # Compile and exec the code, exceptions propagate
    exec(code, allowed_globals, local_vars)

    assertion_func = local_vars.get("assertion")
    if assertion_func is None or not callable(assertion_func):
        return False, "No callable 'assertion' function found in generated code."

    try:
        result = assertion_func(session)
        if result is True or result is None:
            return True, "Success."

        if isinstance(result, str) and result.strip():
            return False, result

        return False, "Assertion failed without message."

    except AssertionError as ae:
        return False, str(ae)

    except Exception:
        raise
