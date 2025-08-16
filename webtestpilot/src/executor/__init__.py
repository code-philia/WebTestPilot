import base64
import logging

from baml_py import Image
from baml_py import ClientRegistry
from executor.assertion_api.session import Session

from config import Config
from baml_client.sync_client import b
from baml_client.types import Feedback
from executor.assertion_api import execute_assertion


logger = logging.getLogger(__name__)


class BugReport(Exception):
    def __init__(self, message, screenshots=None, steps=None):
        super().__init__(message)
        self.screenshots = screenshots or []
        self.steps = steps or []


def verify_precondition(session: Session, condition: str, action: str, config: Config) -> None:
    client_registry = config.assertion_generation
    screenshot = base64.b64encode(session.page.screenshot(type="png")).decode("utf-8")
    screenshot = Image.from_base64("image/png", screenshot)
    history = session.get_history()

    response = b.GeneratePrecondition(
        screenshot,
        history,
        action,
        condition,
        feedback=[],
        baml_options={"client_registry": client_registry},
    )
    passed, message = execute_assertion(response, session)
    if passed:
        logger.info("Precondition passed.")
        return
    else:
        logger.info(f"Precondition failed: {message}")
        raise BugReport(message)


def execute_action(session: Session, action: str, config: Config) -> None:
    logger.info(f"Action: {action}")
    client_registry: ClientRegistry = config.action_proposer
    client_name = config.action_proposer_name
    screenshot = base64.b64encode(session.page.screenshot(type="png")).decode("utf-8")
    screenshot = Image.from_base64("image/png", screenshot)

    code = b.ProposeActions(
        screenshot, action, baml_options={"client_registry": client_registry}
    )

    if client_name == "UITARS":
        import executor.automators.uitars as automator
    elif client_name == "InternVL3":
        import executor.automators.pyautogui as automator
    else:
        import executor.automators.custom as automator

    trace = automator.execute(code, session.page, config)
    session.trace.extend(trace)
    session.capture_state(prev_action=action)


def verify_postcondition(session: Session, action: str, expectation: str, config: Config) -> None:
    logger.info(f"Expectation: {expectation}")
    client_registry: ClientRegistry = config.assertion_generation
    max_retries = config.max_retries
    screenshot = base64.b64encode(session.page.screenshot(type="png")).decode("utf-8")
    screenshot = Image.from_base64("image/png", screenshot)
    history = session.get_history()

    feedback = []
    for _ in range(0, max_retries + 1):
        response = b.GeneratePostcondition(
            screenshot,
            history,
            action,
            expectation,
            feedback,
            baml_options={"client_registry": client_registry},
        )
        logger.info(f"Postcondition: {response}")
        passed, message = execute_assertion(response, session)
        if passed:
            logger.info("Postcondition passed.")
            return
        else:
            logger.info(f"Postcondition failed: {message}")
            feedback_item = Feedback(response=response, reason=message)
            feedback.append(feedback_item)

    raise BugReport(message)
