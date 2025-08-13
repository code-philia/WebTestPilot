import base64

from baml_py import Image
from baml_py import ClientRegistry
from executor.assertion_api.session import Session

from baml_client.sync_client import b
from baml_client.types import Feedback
from executor.assertion_api import execute_assertion


MODEL = "GPT"
MAX_RETRIES = 3
cr = ClientRegistry()
cr.set_primary(MODEL)


if MODEL == "UITARS":
    import executor.automators.uitars as automator
elif MODEL == "InternVL3":
    import executor.automators.pyautogui as automator
else:
    import executor.automators.custom as automator


class BugReport(Exception):
    def __init__(self, message, screenshots=None, steps=None):
        super().__init__(message)
        self.screenshots = screenshots or []
        self.steps = steps or []


def verify_precondition(session: Session, condition: str) -> None:
    screenshot = base64.b64encode(session.page.screenshot(type="png")).decode("utf-8")
    screenshot = Image.from_base64("image/png", screenshot)
    history = session.format_history()
    response = b.GenerateAssertion(
        condition,
        history,
        screenshot,
        feedback=[],
        baml_options={"client_registry": cr},
    )
    passed, message = execute_assertion(response, session)
    if passed:
        return
    else:
        raise BugReport(message)


def execute_action(session: Session, action: str) -> None:
    screenshot = base64.b64encode(session.page.screenshot(type="png")).decode("utf-8")
    screenshot = Image.from_base64("image/png", screenshot)

    if MODEL == "UITARS":
        code = b.ProposeActions_UITARS(
            screenshot, action, baml_options={"client_registry": cr}
        )
    elif MODEL == "InternVL3":
        code = b.ProposeActions_InternVL(
            screenshot, action, baml_options={"client_registry": cr}
        )
    else:
        code = b.ProposeActions(
            screenshot, action, baml_options={"client_registry": cr}
        )

    automator.execute(code, session.page)
    session.capture_state(prev_action=action)


def verify_postcondition(session: Session, expectation: str):
    screenshot = base64.b64encode(session.page.screenshot(type="png")).decode("utf-8")
    screenshot = Image.from_base64("image/png", screenshot)
    history = session.format_history()
    feedback = []

    for _ in range(1, MAX_RETRIES + 1):
        response = b.GenerateAssertion(
            expectation,
            history,
            screenshot,
            feedback,
            baml_options={"client_registry": cr},
        )
        passed, message = execute_assertion(response, session)
        if passed:
            return
        else:
            feedback_item = Feedback(response=response, reason=message)
            feedback.append(feedback_item)

    raise BugReport(message)
